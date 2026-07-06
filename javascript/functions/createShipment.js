/**
 * createShipment - Gönderi Oluşturma
 * Müşterinin kargo bilgilerini Yurtiçi Kargo sistemine ileten servis.
 */

import { sendSoapRequest, parseXml, escapeXml } from '../YurticiKargoClient.js';

/**
 * @param {Object} config - {username, password, language, endpoint}
 * @param {Array} shipments - Gönderi bilgileri dizisi
 * @returns {Promise<Object>} - {outFlag, outResult, jobId, count, details}
 */
export async function createShipment(config, shipments) {
  if (!Array.isArray(shipments) || shipments.length === 0) {
    throw new Error('shipments parametresi boş olamaz');
  }

  // Zorunlu alan kontrolü
  const requiredFields = ['cargoKey', 'invoiceKey', 'receiverCustName', 'receiverAddress', 'receiverPhone1'];
  for (const shipment of shipments) {
    for (const field of requiredFields) {
      if (!shipment[field]) {
        throw new Error(`Zorunlu alan eksik: ${field}`);
      }
    }
  }

  const optionalFields = [
    'receiverPhone2', 'receiverPhone3', 'cityName', 'townName',
    'custProdId', 'desi', 'kg', 'cargoCount', 'waybillNo',
    'specialField1', 'specialField2', 'specialField3',
    'ttCollectionType', 'ttInvoiceAmount', 'ttDocumentId',
    'ttDocumentSaveType', 'orgReceiverCustId', 'description',
    'taxNumber', 'taxOfficeId', 'taxOfficeName', 'orgGeoCode',
    'privilegeOrder', 'dcSelectedCredit', 'dcCreditRule', 'emailAddress'
  ];

  const allFields = [...requiredFields, ...optionalFields];

  // ShippingOrderVO elemanları oluştur
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
  return parseCreateShipmentResponse(responseXml);
}

/**
 * createShipment yanıtını parse eder
 */
function parseCreateShipmentResponse(xml) {
  const parsed = parseXml(xml);

  const outFlag = parseInt(extractValue(parsed, 'outFlag') || '-1');
  const outResult = extractValue(parsed, 'outResult') || '';
  const jobId = extractValue(parsed, 'jobId') || '';
  const count = parseInt(extractValue(parsed, 'count') || '0');

  // Detayları parse et
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
    outFlag,
    outResult,
    jobId,
    count,
    details,
    isSuccess() { return this.outFlag === 0; },
    getErrors() { return this.details.filter(d => d.errCode !== 0); }
  };
}

/**
 * Parsed XML nesnesinden değer çıkarır
 */
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

/**
 * Belirli bir eleman adına sahip tüm nesneleri çıkarır
 */
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

export default createShipment;
