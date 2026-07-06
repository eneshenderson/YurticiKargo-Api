"""Tests for cancel_shipment function."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.cancel_shipment import (
    cancel_shipment,
    CancelResult,
    CancelDetail,
    _build_soap_envelope,
    _parse_response,
)


class TestCancelShipmentValidation(unittest.TestCase):
    """Doğrulama testleri."""

    def test_empty_cargo_keys_raises(self):
        with self.assertRaises(ValueError) as ctx:
            cancel_shipment([])
        self.assertIn("En az bir cargo_key", str(ctx.exception))


class TestBuildSoapEnvelope(unittest.TestCase):
    """SOAP envelope oluşturma testleri."""

    def test_envelope_contains_credentials(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", ["KEY1"])
        self.assertIn("<wsUserName>YKTEST</wsUserName>", envelope)
        self.assertIn("<wsPassword>YK</wsPassword>", envelope)

    def test_envelope_contains_cargo_keys(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", ["KEY1", "KEY2", "KEY3"])
        self.assertIn("<cargoKeys>KEY1</cargoKeys>", envelope)
        self.assertIn("<cargoKeys>KEY2</cargoKeys>", envelope)
        self.assertIn("<cargoKeys>KEY3</cargoKeys>", envelope)

    def test_envelope_uses_cancel_action(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", ["K1"])
        self.assertIn("cancelShipment", envelope)

    def test_envelope_namespace(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", ["K1"])
        self.assertIn("http://yurticikargo.com.tr/ShippingOrderDispatcherServices", envelope)


class TestParseResponse(unittest.TestCase):
    """SOAP yanıt parse testleri."""

    def test_parse_success_response(self):
        xml = """<?xml version="1.0"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <ns2:cancelShipmentResponse xmlns:ns2="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
              <CancelShipmentResponseVO>
                <outFlag>0</outFlag>
                <outResult>Başarılı</outResult>
                <senderCustId>123456</senderCustId>
                <count>2</count>
                <cancelShipmentDetailVO>
                  <CancelShipmentResultVO>
                    <cargoKey>KEY1</cargoKey>
                    <invoiceKey>INV1</invoiceKey>
                    <jobId>100</jobId>
                    <docId>DOC001</docId>
                    <operationCode>3</operationCode>
                    <operationMessage>Kargo çıkışı engellendi</operationMessage>
                    <operationStatus>CNL</operationStatus>
                    <errCode>0</errCode>
                    <errMessage></errMessage>
                  </CancelShipmentResultVO>
                  <CancelShipmentResultVO>
                    <cargoKey>KEY2</cargoKey>
                    <invoiceKey>INV2</invoiceKey>
                    <jobId>101</jobId>
                    <docId>DOC002</docId>
                    <operationCode>4</operationCode>
                    <operationMessage>Kargo zaten iptal edilmiş</operationMessage>
                    <operationStatus>ISC</operationStatus>
                    <errCode>0</errCode>
                    <errMessage></errMessage>
                  </CancelShipmentResultVO>
                </cancelShipmentDetailVO>
              </CancelShipmentResponseVO>
            </ns2:cancelShipmentResponse>
          </soap:Body>
        </soap:Envelope>"""
        result = _parse_response(xml)
        self.assertEqual(result.out_flag, 0)
        self.assertTrue(result.is_success())
        self.assertEqual(result.sender_cust_id, 123456)
        self.assertEqual(result.count, 2)
        self.assertEqual(len(result.details), 2)
        self.assertEqual(result.details[0].cargo_key, "KEY1")
        self.assertEqual(result.details[0].operation_status, "CNL")
        self.assertEqual(result.details[0].operation_code, 3)
        self.assertEqual(result.details[1].operation_status, "ISC")

    def test_parse_error_response(self):
        xml = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <cancelShipmentResponse>
              <CancelShipmentResponseVO>
                <outFlag>1</outFlag>
                <outResult>Hata</outResult>
                <count>0</count>
              </CancelShipmentResponseVO>
            </cancelShipmentResponse>
          </soap:Body>
        </soap:Envelope>"""
        result = _parse_response(xml)
        self.assertEqual(result.out_flag, 1)
        self.assertFalse(result.is_success())


class TestCancelResult(unittest.TestCase):
    """CancelResult dataclass testleri."""

    def test_is_success(self):
        r = CancelResult(out_flag=0)
        self.assertTrue(r.is_success())
        r2 = CancelResult(out_flag=1)
        self.assertFalse(r2.is_success())

    def test_detail_is_success(self):
        d = CancelDetail(operation_code=3, err_code=0)
        self.assertTrue(d.is_success())


class TestCancelShipmentHTTP(unittest.TestCase):
    """HTTP çağrı testleri (mock)."""

    @patch("urllib.request.urlopen")
    def test_successful_call(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <cancelShipmentResponse>
              <CancelShipmentResponseVO>
                <outFlag>0</outFlag>
                <outResult>OK</outResult>
                <count>1</count>
                <cancelShipmentDetailVO>
                  <CancelShipmentResultVO>
                    <cargoKey>K1</cargoKey>
                    <operationCode>3</operationCode>
                    <operationStatus>CNL</operationStatus>
                    <errCode>0</errCode>
                  </CancelShipmentResultVO>
                </cancelShipmentDetailVO>
              </CancelShipmentResponseVO>
            </cancelShipmentResponse>
          </soap:Body>
        </soap:Envelope>"""
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = cancel_shipment(["K1"])
        self.assertTrue(result.is_success())
        self.assertEqual(len(result.details), 1)
        self.assertEqual(result.details[0].operation_status, "CNL")

    @patch("urllib.request.urlopen")
    def test_connection_error(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused")
        result = cancel_shipment(["K1"])
        self.assertEqual(result.out_flag, 2)
        self.assertIn("Bağlantı hatası", result.out_result)


if __name__ == "__main__":
    unittest.main()
