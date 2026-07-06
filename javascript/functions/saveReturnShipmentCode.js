/**
 * saveReturnShipmentCode - İade Kodu Oluşturma
 * İade müşterilerinin YK birimine ileterek iade işlemini tamamlayacakları kodu oluşturur.
 */

import { sendSoapRequest, parseXml, escapeXml } from '../YurticiKargoClient.js';

/**
 * @param {Object} config - {username, password, language, endpoint}
 * @param {string} returnCode - İade kodu
 * @param {string} startDate - Başlangıç tarihi (YYYYMMDD)
 * @param {string} endDate - Bitiş tarihi (YYYYMMDD)
 * @param {number} maxCount - Kullanım adedi
 * @param {string} fieldName - Özel alan bilgisi (test: 53 veya 3, canlı: 16)
 * @returns {Promise<Object>} - {outFlag, outResult, errCode}
 */
export async function saveReturnShipmentCode(config, returnCode, startDate, endDate, maxCount, fieldName) {
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
  return parseReturnCodeResponse(responseXml);
}

/**
 * saveReturnShipmentCode yanıtını parse eder
 */
function parseReturnCodeResponse(xml) {
  const parsed = parseXml(xml);

  const outFlag = parseInt(extractValue(parsed, 'outFlag') || '-1');
  const outResult = extractValue(parsed, 'outResult') || '';
  const errCode = parseInt(extractValue(parsed, 'errCode') || '0');

  return {
    outFlag,
    outResult,
    errCode,
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

export default saveReturnShipmentCode;
