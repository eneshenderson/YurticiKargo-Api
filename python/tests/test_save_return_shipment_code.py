"""Tests for save_return_shipment_code function."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.save_return_shipment_code import (
    save_return_shipment_code,
    ReturnCodeResult,
    _build_soap_envelope,
    _parse_response,
)


class TestSaveReturnShipmentCodeValidation(unittest.TestCase):
    """Doğrulama testleri."""

    def test_empty_return_code_raises(self):
        with self.assertRaises(ValueError) as ctx:
            save_return_shipment_code("", "20240101", "20240131")
        self.assertIn("return_code", str(ctx.exception))

    def test_empty_start_date_raises(self):
        with self.assertRaises(ValueError) as ctx:
            save_return_shipment_code("RMA001", "", "20240131")
        self.assertIn("start_date", str(ctx.exception))

    def test_empty_end_date_raises(self):
        with self.assertRaises(ValueError) as ctx:
            save_return_shipment_code("RMA001", "20240101", "")
        self.assertIn("end_date", str(ctx.exception))


class TestBuildSoapEnvelope(unittest.TestCase):
    """SOAP envelope oluşturma testleri."""

    def test_envelope_contains_credentials(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", "RMA001", "20240101", "20240131", 1, "53")
        self.assertIn("<wsUserName>YKTEST</wsUserName>", envelope)
        self.assertIn("<wsPassword>YK</wsPassword>", envelope)

    def test_envelope_contains_return_code(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", "RMA-2024-001", "20240101", "20240131", 3, "53")
        self.assertIn("<returnCode>RMA-2024-001</returnCode>", envelope)
        self.assertIn("<startDate>20240101</startDate>", envelope)
        self.assertIn("<endDate>20240131</endDate>", envelope)
        self.assertIn("<maxCount>3</maxCount>", envelope)
        self.assertIn("<fieldName>53</fieldName>", envelope)

    def test_envelope_uses_save_return_action(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", "X", "20240101", "20240131", 1, "53")
        self.assertIn("saveReturnShipmentCode", envelope)

    def test_envelope_namespace(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", "X", "20240101", "20240131", 1, "53")
        self.assertIn("http://yurticikargo.com.tr/ShippingOrderDispatcherServices", envelope)


class TestParseResponse(unittest.TestCase):
    """SOAP yanıt parse testleri."""

    def test_parse_success_response(self):
        xml = """<?xml version="1.0"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <ns2:saveReturnShipmentCodeResponse xmlns:ns2="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
              <SaveReturnShipmentCodeResponseVO>
                <outFlag>0</outFlag>
                <outResult>Başarılı</outResult>
                <errCode>0</errCode>
              </SaveReturnShipmentCodeResponseVO>
            </ns2:saveReturnShipmentCodeResponse>
          </soap:Body>
        </soap:Envelope>"""
        result = _parse_response(xml)
        self.assertEqual(result.out_flag, 0)
        self.assertTrue(result.is_success())
        self.assertEqual(result.err_code, 0)

    def test_parse_error_duplicate(self):
        xml = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <saveReturnShipmentCodeResponse>
              <SaveReturnShipmentCodeResponseVO>
                <outFlag>1</outFlag>
                <outResult>İade kodu daha önceden kaydedilmiştir</outResult>
                <errCode>82655</errCode>
              </SaveReturnShipmentCodeResponseVO>
            </saveReturnShipmentCodeResponse>
          </soap:Body>
        </soap:Envelope>"""
        result = _parse_response(xml)
        self.assertEqual(result.out_flag, 1)
        self.assertFalse(result.is_success())
        self.assertEqual(result.err_code, 82655)


class TestReturnCodeResult(unittest.TestCase):
    """ReturnCodeResult dataclass testleri."""

    def test_is_success(self):
        r = ReturnCodeResult(out_flag=0)
        self.assertTrue(r.is_success())
        r2 = ReturnCodeResult(out_flag=1)
        self.assertFalse(r2.is_success())


class TestSaveReturnShipmentCodeHTTP(unittest.TestCase):
    """HTTP çağrı testleri (mock)."""

    @patch("urllib.request.urlopen")
    def test_successful_call(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <saveReturnShipmentCodeResponse>
              <SaveReturnShipmentCodeResponseVO>
                <outFlag>0</outFlag>
                <outResult>OK</outResult>
                <errCode>0</errCode>
              </SaveReturnShipmentCodeResponseVO>
            </saveReturnShipmentCodeResponse>
          </soap:Body>
        </soap:Envelope>"""
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = save_return_shipment_code("RMA001", "20240101", "20240131")
        self.assertTrue(result.is_success())

    @patch("urllib.request.urlopen")
    def test_connection_error(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("DNS failure")
        result = save_return_shipment_code("RMA001", "20240101", "20240131")
        self.assertEqual(result.out_flag, 2)
        self.assertIn("Bağlantı hatası", result.out_result)


if __name__ == "__main__":
    unittest.main()
