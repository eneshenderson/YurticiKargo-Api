/**
 * cancelShipment - Gönderi İptal
 * Web servis ile sisteme gönderilmiş bilgilerin iptal edilmesini sağlar.
 */

import { sendSoapRequest, parseXml, escapeXml } from '../YurticiKargoClient.js';

/**
 * @param {Object} config - {username, password, language, endpoint}
 * @param {Array<string>} cargoKeys - İptal edilecek kargo anahtarları
 * @returns {Promise<Object>} - {outFlag, outResult, senderCustId, count, details}
 */
export async function cancelShipment(config, cargoKeys) {
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
  return parseCancelShipmentResponse(responseXml);
}

/**
 * cancelShipment yanıtını parse eder
 */
function parseCancelShipmentResponse(xml) {
  const parsed = parseXml(xml);

  const outFlag = parseInt(extractValue(parsed, 'outFlag') || '-1');
  const outResult = extractValue(parsed, 'outResult') || '';
  const senderCustId = extractValue(parsed, 'senderCustId') || '';
  const count = parseInt(extractValue(parsed, 'count') || '0');

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

export default cancelShipment;
