/**
 * YurticiKargoClient - Yurtiçi Kargo SOAP API Client
 * Controller sınıfı: Tüm fonksiyonları birleştirir.
 */

import https from 'https';
import http from 'http';
import { createShipment } from './functions/createShipment.js';
import { cancelShipment } from './functions/cancelShipment.js';
import { queryShipment } from './functions/queryShipment.js';
import { saveReturnShipmentCode } from './functions/saveReturnShipmentCode.js';

// ============================================================
// Lightweight XML Parser
// ============================================================

/**
 * Basit XML parser - SOAP yanıtlarını parse etmek için.
 * Namespace prefix'lerini temizler ve nested yapıları destekler.
 */
export function parseXml(xml) {
  // XML declaration ve whitespace temizle
  xml = xml.replace(/<\?xml[^?]*\?>/g, '').trim();

  return parseNode(xml);
}

function parseNode(xml) {
  const result = {};

  // Tüm elemanları bul
  const tagRegex = /<([^\s/>!]+)([^>]*)>([\s\S]*?)<\/\1>|<([^\s/>!]+)([^>]*)\/>/g;
  let match;
  let found = false;

  while ((match = tagRegex.exec(xml)) !== null) {
    found = true;

    if (match[4]) {
      // Self-closing tag: <tag/>
      const tagName = stripNamespace(match[4]);
      addToResult(result, tagName, '');
    } else {
      // Normal tag: <tag>content</tag>
      const tagName = stripNamespace(match[1]);
      const content = match[3].trim();

      // İç içe eleman var mı kontrol et
      if (content.includes('<') && /<[a-zA-Z]/.test(content)) {
        const childObj = parseNode(content);
        addToResult(result, tagName, childObj);
      } else {
        // Text content
        addToResult(result, tagName, decodeXmlEntities(content));
      }
    }
  }

  if (!found) {
    return xml ? decodeXmlEntities(xml) : '';
  }

  return result;
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

function decodeXmlEntities(str) {
  return str
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'");
}

// ============================================================
// XML Escape Utility
// ============================================================

export function escapeXml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

// ============================================================
// SOAP HTTP Request
// ============================================================

/**
 * SOAP isteği gönderir
 * @param {string} endpoint - WSDL endpoint URL
 * @param {string} soapBody - SOAP body XML
 * @returns {Promise<string>} - Response XML
 */
export function sendSoapRequest(endpoint, soapBody) {
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

      res.on('data', (chunk) => {
        data += chunk;
      });

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
// YurticiKargoClient Class
// ============================================================

export class YurticiKargoClient {
  #username;
  #password;
  #language;
  #testMode;
  #endpoint;
  #lastRequest = '';
  #lastResponse = '';

  /**
   * @param {Object} options
   * @param {string} options.username - API kullanıcı adı
   * @param {string} options.password - API şifresi
   * @param {string} [options.language='TR'] - Dil kodu
   * @param {boolean} [options.testMode=true] - Test modu
   */
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

  /**
   * Yapılandırma nesnesi döner
   */
  get #config() {
    return {
      username: this.#username,
      password: this.#password,
      language: this.#language,
      endpoint: this.#endpoint
    };
  }

  /**
   * Gönderi oluşturma
   * @param {Array} shipments - Gönderi bilgileri dizisi
   */
  async createShipment(shipments) {
    return createShipment(this.#config, shipments);
  }

  /**
   * Gönderi iptal
   * @param {Array<string>} cargoKeys - İptal edilecek kargo anahtarları
   */
  async cancelShipment(cargoKeys) {
    return cancelShipment(this.#config, cargoKeys);
  }

  /**
   * Gönderi sorgulama
   * @param {Object} options
   * @param {Array<string>} options.keys - Sorgulanacak anahtarlar
   * @param {number} [options.keyType=0] - 0=CargoKey, 1=InvoiceKey
   * @param {boolean} [options.addHistoricalData=false] - Hareket geçmişi
   * @param {boolean} [options.onlyTracking=false] - Sadece takip URL
   */
  async queryShipment({ keys, keyType = 0, addHistoricalData = false, onlyTracking = false }) {
    return queryShipment(this.#config, keys, keyType, addHistoricalData, onlyTracking);
  }

  /**
   * İade kodu oluşturma
   * @param {Object} options
   * @param {string} options.returnCode - İade kodu
   * @param {string} options.startDate - Başlangıç tarihi (YYYYMMDD)
   * @param {string} options.endDate - Bitiş tarihi (YYYYMMDD)
   * @param {number} options.maxCount - Kullanım adedi
   * @param {string} options.fieldName - Özel alan bilgisi
   */
  async saveReturnShipmentCode({ returnCode, startDate, endDate, maxCount, fieldName }) {
    return saveReturnShipmentCode(this.#config, returnCode, startDate, endDate, maxCount, fieldName);
  }

  /**
   * Test modunda mı?
   */
  get isTestMode() {
    return this.#testMode;
  }

  /**
   * Endpoint URL
   */
  get endpoint() {
    return this.#endpoint;
  }
}

export default YurticiKargoClient;
