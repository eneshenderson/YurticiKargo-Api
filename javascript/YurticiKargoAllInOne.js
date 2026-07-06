/**
 * YurticiKargoAllInOne.js
 * Yurtiçi Kargo SOAP API Client - Tek dosyada tüm fonksiyonlar.
 * Harici modül gerektirmez, tek başına çalışır.
 *
 * Kullanım:
 *   node YurticiKargoAllInOne.js
 *
 * Veya import olarak:
 *   import { YurticiKargoClient } from './YurticiKargoAllInOne.js';
 */

import https from 'https';
import http from 'http';

// ============================================================
// XML Utilities
// ============================================================

function escapeXml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function decodeXmlEntities(str) {
  return str
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'");
}

function stripNamespace(tagName) {
  const colonIndex = tagName.indexOf(':');
  return colonIndex >= 0 ? tagName.substring(colonIndex + 1) : tagName;
}

function addToResult(obj, key, value) {
  if (obj[key] !== undefined) {
    if (!Array.isArray(obj[key])) {
      obj[key] = [obj[key]];
    }
    obj[key].push(value);
  } else {
    obj[key] = value;
  }
}

// ============================================================
// Lightweight XML Parser
// ============================================================

function parseXml(xml) {
  xml = xml.replace(/<\?xml[^?]*\?>/g, '').trim();
  return parseNode(xml);
}

function parseNode(xml) {
  const result = {};
  const tagRegex = /<([^\s/>!]+)([^>]*)>([\s\S]*?)<\/\1>|<([^\s/>!]+)([^>]*)\/>/g;
  let match;
  let found = false;

  while ((match = tagRegex.exec(xml)) !== null) {
    found = true;

    if (match[4]) {
      const tagName = stripNamespace(match[4]);
      addToResult(result, tagName, '');
    } else {
      const tagName = stripNamespace(match[1]);
      const content = match[3].trim();

      if (content.includes('<') && /<[a-zA-Z]/.test(content)) {
        const childObj = parseNode(content);
        addToResult(result, tagName, childObj);
      } else {
        addToResult(result, tagName, decodeXmlEntities(content));
      }
    }
  }

  if (!found) {
    return xml ? decodeXmlEntities(xml) : '';
  }

  return result;
}

// ============================================================
// XML Value Extraction Helpers
// ============================================================

function extractValue(obj, key) {
  if (!obj) return null;
  if (typeof obj === 'string') return null;

  if (obj[key] !== undefined) {
    if (typeof obj[key] === 'object' && obj[key] !== null) {
      return obj[key].__text || '';
    }
    return obj[key];
  }

  for (const k of Object.keys(obj)) {
    if (typeof obj[k] === 'object' && obj[k] !== null) {
      const found = extractValue(obj[k], key);
      if (found !== null) return found;
    }
  }
  return null;
}

function findElement(obj, elementName) {
  if (!obj || typeof obj !== 'object') return null;
  if (obj[elementName]) return obj[elementName];
  for (const k of Object.keys(obj)) {
    if (typeof obj[k] === 'object' && obj[k] !== null) {
      const found = findElement(obj[k], elementName);
      if (found) return found;
    }
  }
  return null;
}

function extractAllElements(obj, elementName) {
  const results = [];
  if (!obj || typeof obj !== 'object') return results;

  if (obj[elementName]) {
    const items = Array.isArray(obj[elementName]) ? obj[elementName] : [obj[elementName]];
    results.push(...items);
  }

  for (const k of Object.keys(obj)) {
    if (k !== elementName && typeof obj[k] === 'object' && obj[k] !== null) {
      results.push(...extractAllElements(obj[k], elementName));
    }
  }

  return results;
}

// ============================================================
// SOAP HTTP Request
// ============================================================

function sendSoapRequest(endpoint, soapBody) {
  const soapEnvelope = `<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ship="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
  <soapenv:Header/>
  <soapenv:Body>
${soapBody}
  </soapenv:Body>
</soapenv:Envelope>`;

  const url = new URL(endpoint);
  const isHttps = url.protocol === 'https:';
  const transport = isHttps ? https : http;

  const options = {
    hostname: url.hostname,
    port: url.port || (isHttps ? 443 : 80),
    path: url.pathname + (url.search || ''),
    method: 'POST',
    headers: {
      'Content-Type': 'text/xml; charset=utf-8',
      'Content-Length': Buffer.byteLength(soapEnvelope, 'utf-8'),
      'SOAPAction': ''
    },
    rejectUnauthorized: true
  };

  return new Promise((resolve, reject) => {
    const req = transport.request(options, (res) => {
      let data = '';
      res.setEncoding('utf-8');

      res.on('data', (chunk) => { data += chunk; });

      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 500) {
          resolve(data);
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data.substring(0, 500)}`));
        }
      });
    });

    req.on('error', (err) => {
      reject(new Error(`SOAP isteği başarısız: ${err.message}`));
    });

    req.setTimeout(30000, () => {
      req.destroy();
      reject(new Error('SOAP isteği zaman aşımına uğradı (30s)'));
    });

    req.write(soapEnvelope);
    req.end();
  });
}

// ============================================================
// API Functions
// ============================================================

/**
 * Gönderi oluşturma
 */
async function createShipment(config, shipments) {
  if (!Array.isArray(shipments) || shipments.length === 0) {
    throw new Error('shipments parametresi boş olamaz');
  }

  const requiredFields = ['cargoKey', 'invoiceKey', 'receiverCustName', 'receiverAddress', 'receiverPhone1'];
  for (const shipment of shipments) {
    for (const field of requiredFields) {
      if (!shipment[field]) {
        throw new Error(`Zorunlu alan eksik: ${field}`);
      }
    }
  }

  const allFields = [
    ...requiredFields,
    'receiverPhone2', 'receiverPhone3', 'cityName', 'townName',
    'custProdId', 'desi', 'kg', 'cargoCount', 'waybillNo',
    'specialField1', 'specialField2', 'specialField3',
    'ttCollectionType', 'ttInvoiceAmount', 'ttDocumentId',
    'ttDocumentSaveType', 'orgReceiverCustId', 'description',
    'taxNumber', 'taxOfficeId', 'taxOfficeName', 'orgGeoCode',
    'privilegeOrder', 'dcSelectedCredit', 'dcCreditRule', 'emailAddress'
  ];

  const shippingOrderVOs = shipments.map(shipment => {
    let fields = '';
    for (const field of allFields) {
      if (shipment[field] !== undefined && shipment[field] !== null && shipment[field] !== '') {
        fields += `        <${field}>${escapeXml(String(shipment[field]))}</${field}>\n`;
      }
    }
    return `      <ShippingOrderVO>\n${fields}      </ShippingOrderVO>`;
  }).join('\n');

  const soapBody = `
    <ship:createShipment>
      <wsUserName>${escapeXml(config.username)}</wsUserName>
      <wsPassword>${escapeXml(config.password)}</wsPassword>
      <userLanguage>${escapeXml(config.language)}</userLanguage>
${shippingOrderVOs}
    </ship:createShipment>`;

  const responseXml = await sendSoapRequest(config.endpoint, soapBody);
  const parsed = parseXml(responseXml);

  const details = [];
  const detailVOs = extractAllElements(parsed, 'shippingOrderDetailVO');
  for (const detail of detailVOs) {
    details.push({
      cargoKey: extractValue(detail, 'cargoKey') || '',
      invoiceKey: extractValue(detail, 'invoiceKey') || '',
      errCode: parseInt(extractValue(detail, 'errCode') || '0'),
      errMessage: extractValue(detail, 'errMessage') || ''
    });
  }

  return {
    outFlag: parseInt(extractValue(parsed, 'outFlag') || '-1'),
    outResult: extractValue(parsed, 'outResult') || '',
    jobId: extractValue(parsed, 'jobId') || '',
    count: parseInt(extractValue(parsed, 'count') || '0'),
    details,
    isSuccess() { return this.outFlag === 0; },
    getErrors() { return this.details.filter(d => d.errCode !== 0); }
  };
}

/**
 * Gönderi iptal
 */
async function cancelShipment(config, cargoKeys) {
  if (!Array.isArray(cargoKeys) || cargoKeys.length === 0) {
    throw new Error('cargoKeys parametresi boş olamaz');
  }

  const cargoKeysXml = cargoKeys
    .map(key => `      <cargoKeys>${escapeXml(String(key))}</cargoKeys>`)
    .join('\n');

  const soapBody = `
    <ship:cancelShipment>
      <wsUserName>${escapeXml(config.username)}</wsUserName>
      <wsPassword>${escapeXml(config.password)}</wsPassword>
      <userLanguage>${escapeXml(config.language)}</userLanguage>
${cargoKeysXml}
    </ship:cancelShipment>`;

  const responseXml = await sendSoapRequest(config.endpoint, soapBody);
  const parsed = parseXml(responseXml);

  const details = [];
  const cancelDetails = extractAllElements(parsed, 'shippingCancelDetailVO');
  for (const detail of cancelDetails) {
    details.push({
      cargoKey: extractValue(detail, 'cargoKey') || '',
      invoiceKey: extractValue(detail, 'invoiceKey') || '',
      jobId: extractValue(detail, 'jobId') || '',
      docId: extractValue(detail, 'docId') || '',
      operationCode: parseInt(extractValue(detail, 'operationCode') || '0'),
      operationMessage: extractValue(detail, 'operationMessage') || '',
      operationStatus: extractValue(detail, 'operationStatus') || '',
      errCode: parseInt(extractValue(detail, 'errCode') || '0'),
      errMessage: extractValue(detail, 'errMessage') || ''
    });
  }

  return {
    outFlag: parseInt(extractValue(parsed, 'outFlag') || '-1'),
    outResult: extractValue(parsed, 'outResult') || '',
    senderCustId: extractValue(parsed, 'senderCustId') || '',
    count: parseInt(extractValue(parsed, 'count') || '0'),
    details,
    isSuccess() { return this.outFlag === 0; }
  };
}

/**
 * Gönderi sorgulama
 */
async function queryShipment(config, keys, keyType = 0, addHistoricalData = false, onlyTracking = false) {
  if (!Array.isArray(keys) || keys.length === 0) {
    throw new Error('keys parametresi boş olamaz');
  }

  const keysXml = keys
    .map(key => `      <keys>${escapeXml(String(key))}</keys>`)
    .join('\n');

  const soapBody = `
    <ship:queryShipment>
      <wsUserName>${escapeXml(config.username)}</wsUserName>
      <wsPassword>${escapeXml(config.password)}</wsPassword>
      <wsLanguage>${escapeXml(config.language)}</wsLanguage>
${keysXml}
      <keyType>${keyType}</keyType>
      <addHistoricalData>${addHistoricalData}</addHistoricalData>
      <onlyTracking>${onlyTracking}</onlyTracking>
    </ship:queryShipment>`;

  const responseXml = await sendSoapRequest(config.endpoint, soapBody);
  const parsed = parseXml(responseXml);

  const details = [];
  const queryDetails = extractAllElements(parsed, 'shippingDeliveryDetailVO');

  for (const detail of queryDetails) {
    const item = {
      cargoKey: extractValue(detail, 'cargoKey') || '',
      invoiceKey: extractValue(detail, 'invoiceKey') || '',
      operationStatus: extractValue(detail, 'operationStatus') || '',
      operationMessage: extractValue(detail, 'operationMessage') || '',
      errCode: parseInt(extractValue(detail, 'errCode') || '0'),
      errMessage: extractValue(detail, 'errMessage') || '',
      itemDetail: null
    };

    const itemDetailNode = findElement(detail, 'shippingDeliveryItemDetailVO');
    if (itemDetailNode) {
      item.itemDetail = {
        trackingUrl: extractValue(itemDetailNode, 'trackingUrl') || '',
        receiverCustName: extractValue(itemDetailNode, 'receiverCustName') || '',
        departureUnitName: extractValue(itemDetailNode, 'departureUnitName') || '',
        deliveryDate: extractValue(itemDetailNode, 'deliveryDate') || '',
        deliveryTime: extractValue(itemDetailNode, 'deliveryTime') || '',
        cargoHistory: []
      };

      const historyItems = extractAllElements(itemDetailNode, 'cargoEventHistory');
      for (const hist of historyItems) {
        item.itemDetail.cargoHistory.push({
          unitName: extractValue(hist, 'unitName') || '',
          eventName: extractValue(hist, 'eventName') || '',
          reasonName: extractValue(hist, 'reasonName') || '',
          eventDate: extractValue(hist, 'eventDate') || '',
          eventTime: extractValue(hist, 'eventTime') || ''
        });
      }
    }

    item.isSuccess = function() { return this.errCode === 0; };
    details.push(item);
  }

  return {
    outFlag: parseInt(extractValue(parsed, 'outFlag') || '-1'),
    outResult: extractValue(parsed, 'outResult') || '',
    senderCustId: extractValue(parsed, 'senderCustId') || '',
    count: parseInt(extractValue(parsed, 'count') || '0'),
    details,
    isSuccess() { return this.outFlag === 0; }
  };
}

/**
 * İade kodu oluşturma
 */
async function saveReturnShipmentCode(config, returnCode, startDate, endDate, maxCount, fieldName) {
  if (!returnCode) throw new Error('returnCode parametresi zorunludur');
  if (!startDate) throw new Error('startDate parametresi zorunludur');
  if (!endDate) throw new Error('endDate parametresi zorunludur');
  if (!maxCount) throw new Error('maxCount parametresi zorunludur');
  if (!fieldName) throw new Error('fieldName parametresi zorunludur');

  const soapBody = `
    <ship:saveReturnShipmentCode>
      <wsUserName>${escapeXml(config.username)}</wsUserName>
      <wsPassword>${escapeXml(config.password)}</wsPassword>
      <wsLanguage>${escapeXml(config.language)}</wsLanguage>
      <fieldName>${escapeXml(String(fieldName))}</fieldName>
      <returnCode>${escapeXml(String(returnCode))}</returnCode>
      <startDate>${escapeXml(String(startDate))}</startDate>
      <endDate>${escapeXml(String(endDate))}</endDate>
      <maxCount>${parseInt(maxCount)}</maxCount>
    </ship:saveReturnShipmentCode>`;

  const responseXml = await sendSoapRequest(config.endpoint, soapBody);
  const parsed = parseXml(responseXml);

  return {
    outFlag: parseInt(extractValue(parsed, 'outFlag') || '-1'),
    outResult: extractValue(parsed, 'outResult') || '',
    errCode: parseInt(extractValue(parsed, 'errCode') || '0'),
    isSuccess() { return this.outFlag === 0; }
  };
}

// ============================================================
// YurticiKargoClient Class
// ============================================================

export class YurticiKargoClient {
  #username;
  #password;
  #language;
  #testMode;
  #endpoint;

  constructor({ username, password, language = 'TR', testMode = true }) {
    if (!username) throw new Error('username zorunludur');
    if (!password) throw new Error('password zorunludur');

    this.#username = username;
    this.#password = password;
    this.#language = language;
    this.#testMode = testMode;

    this.#endpoint = testMode
      ? 'https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl'
      : 'https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl';
  }

  get #config() {
    return {
      username: this.#username,
      password: this.#password,
      language: this.#language,
      endpoint: this.#endpoint
    };
  }

  async createShipment(shipments) {
    return createShipment(this.#config, shipments);
  }

  async cancelShipment(cargoKeys) {
    return cancelShipment(this.#config, cargoKeys);
  }

  async queryShipment({ keys, keyType = 0, addHistoricalData = false, onlyTracking = false }) {
    return queryShipment(this.#config, keys, keyType, addHistoricalData, onlyTracking);
  }

  async saveReturnShipmentCode({ returnCode, startDate, endDate, maxCount, fieldName }) {
    return saveReturnShipmentCode(this.#config, returnCode, startDate, endDate, maxCount, fieldName);
  }

  get isTestMode() {
    return this.#testMode;
  }

  get endpoint() {
    return this.#endpoint;
  }
}

// ============================================================
// Standalone Execution Example
// ============================================================

async function main() {
  const client = new YurticiKargoClient({
    username: 'YKTEST',
    password: 'YK',
    language: 'TR',
    testMode: true
  });

  console.log('Yurtiçi Kargo API Client (AllInOne)');
  console.log('Endpoint:', client.endpoint);
  console.log('Test Mode:', client.isTestMode);
  console.log('');

  try {
    // Gönderi oluşturma testi
    console.log('=== createShipment ===');
    const shipResult = await client.createShipment([
      {
        cargoKey: 'TEST' + Date.now(),
        invoiceKey: 'INV' + Date.now(),
        receiverCustName: 'Test Alıcı',
        receiverAddress: 'Test Adres Mahallesi No:1',
        receiverPhone1: '05551234567',
        cityName: 'İstanbul',
        townName: 'Kadıköy'
      }
    ]);
    console.log('outFlag:', shipResult.outFlag);
    console.log('outResult:', shipResult.outResult);
    console.log('jobId:', shipResult.jobId);
    console.log('Başarılı:', shipResult.isSuccess());
    console.log('');

    // Gönderi sorgulama
    console.log('=== queryShipment ===');
    const queryResult = await client.queryShipment({
      keys: ['12520'],
      keyType: 0,
      addHistoricalData: true
    });
    console.log('outFlag:', queryResult.outFlag);
    console.log('outResult:', queryResult.outResult);
    console.log('Detay sayısı:', queryResult.details.length);
    console.log('');

  } catch (err) {
    console.error('Hata:', err.message);
  }
}

// Doğrudan çalıştırıldığında main() çalışır
const isMainModule = process.argv[1] && (
  process.argv[1].endsWith('YurticiKargoAllInOne.js') ||
  process.argv[1].replace(/\\/g, '/').endsWith('YurticiKargoAllInOne.js')
);

if (isMainModule) {
  main();
}

export default YurticiKargoClient;
