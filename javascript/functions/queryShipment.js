/**
 * queryShipment - Gönderi Sorgulama
 * Müşterinin kendi referans kodu ile gönderi geçmişini raporlayan servis.
 */

import { sendSoapRequest, parseXml, escapeXml } from '../YurticiKargoClient.js';

/**
 * @param {Object} config - {username, password, language, endpoint}
 * @param {Array<string>} keys - Sorgulanacak anahtarlar
 * @param {number} keyType - 0=CargoKey, 1=InvoiceKey
 * @param {boolean} addHistoricalData - Hareket geçmişi dahil mi
 * @param {boolean} onlyTracking - Sadece takip URL'si mi
 * @returns {Promise<Object>}
 */
export async function queryShipment(config, keys, keyType = 0, addHistoricalData = false, onlyTracking = false) {
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
  return parseQueryShipmentResponse(responseXml);
}

/**
 * queryShipment yanıtını parse eder
 */
function parseQueryShipmentResponse(xml) {
  const parsed = parseXml(xml);

  const outFlag = parseInt(extractValue(parsed, 'outFlag') || '-1');
  const outResult = extractValue(parsed, 'outResult') || '';
  const senderCustId = extractValue(parsed, 'senderCustId') || '';
  const count = parseInt(extractValue(parsed, 'count') || '0');

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

    // itemDetail parse - ShippingDeliveryItemDetailVO
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

      // Kargo geçmişi - cargoEventHistory
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
    outFlag,
    outResult,
    senderCustId,
    count,
    details,
    isSuccess() { return this.outFlag === 0; }
  };
}

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

export default queryShipment;
