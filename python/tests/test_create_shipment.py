"""Tests for create_shipment function."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.create_shipment import (
    create_shipment,
    ShipmentResult,
    ShipmentDetail,
    _build_soap_envelope,
    _parse_response,
    REQUIRED_FIELDS,
)


class TestCreateShipmentValidation(unittest.TestCase):
    """Zorunlu alan doğrulama testleri."""

    def test_missing_cargo_key_raises(self):
        with self.assertRaises(ValueError) as ctx:
            create_shipment([{"invoice_key": "A1", "receiver_cust_name": "X", "receiver_address": "Y", "receiver_phone1": "Z"}])
        self.assertIn("cargo_key", str(ctx.exception))

    def test_missing_invoice_key_raises(self):
        with self.assertRaises(ValueError) as ctx:
            create_shipment([{"cargo_key": "A1", "receiver_cust_name": "X", "receiver_address": "Y", "receiver_phone1": "Z"}])
        self.assertIn("invoice_key", str(ctx.exception))

    def test_missing_receiver_cust_name_raises(self):
        with self.assertRaises(ValueError) as ctx:
            create_shipment([{"cargo_key": "A1", "invoice_key": "B1", "receiver_address": "Y", "receiver_phone1": "Z"}])
        self.assertIn("receiver_cust_name", str(ctx.exception))

    def test_missing_receiver_address_raises(self):
        with self.assertRaises(ValueError) as ctx:
            create_shipment([{"cargo_key": "A1", "invoice_key": "B1", "receiver_cust_name": "X", "receiver_phone1": "Z"}])
        self.assertIn("receiver_address", str(ctx.exception))

    def test_missing_receiver_phone1_raises(self):
        with self.assertRaises(ValueError) as ctx:
            create_shipment([{"cargo_key": "A1", "invoice_key": "B1", "receiver_cust_name": "X", "receiver_address": "Y"}])
        self.assertIn("receiver_phone1", str(ctx.exception))

    def test_empty_shipments_no_error(self):
        """Boş liste gönderildiğinde HTTP isteği yapılır, validasyon hatası olmaz."""
        with patch("urllib.request.urlopen") as mock_open:
            mock_response = MagicMock()
            mock_response.read.return_value = b"<outFlag>0</outFlag><outResult>OK</outResult>"
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_response
            result = create_shipment([])
            self.assertIsInstance(result, ShipmentResult)


class TestBuildSoapEnvelope(unittest.TestCase):
    """SOAP envelope oluşturma testleri."""

    def test_envelope_contains_credentials(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", [])
        self.assertIn("<wsUserName>YKTEST</wsUserName>", envelope)
        self.assertIn("<wsPassword>YK</wsPassword>", envelope)
        self.assertIn("<wsLanguage>TR</wsLanguage>", envelope)

    def test_envelope_contains_namespace(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", [])
        self.assertIn("http://yurticikargo.com.tr/ShippingOrderDispatcherServices", envelope)

    def test_envelope_contains_shipment_data(self):
        shipments = [{"cargo_key": "KEY001", "invoice_key": "INV001", "receiver_cust_name": "Test", "receiver_address": "Addr", "receiver_phone1": "05551234567"}]
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", shipments)
        self.assertIn("<cargoKey>KEY001</cargoKey>", envelope)
        self.assertIn("<invoiceKey>INV001</invoiceKey>", envelope)
        self.assertIn("<receiverCustName>Test</receiverCustName>", envelope)
        self.assertIn("<receiverAddress>Addr</receiverAddress>", envelope)
        self.assertIn("<receiverPhone1>05551234567</receiverPhone1>", envelope)

    def test_envelope_optional_fields(self):
        shipments = [{"cargo_key": "K1", "invoice_key": "I1", "receiver_cust_name": "N", "receiver_address": "A", "receiver_phone1": "P", "city_name": "Istanbul", "desi": 3.5}]
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", shipments)
        self.assertIn("<cityName>Istanbul</cityName>", envelope)
        self.assertIn("<desi>3.5</desi>", envelope)

    def test_envelope_multiple_shipments(self):
        shipments = [
            {"cargo_key": "K1", "invoice_key": "I1", "receiver_cust_name": "N1", "receiver_address": "A1", "receiver_phone1": "P1"},
            {"cargo_key": "K2", "invoice_key": "I1", "receiver_cust_name": "N1", "receiver_address": "A1", "receiver_phone1": "P1"},
        ]
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", shipments)
        self.assertIn("<cargoKey>K1</cargoKey>", envelope)
        self.assertIn("<cargoKey>K2</cargoKey>", envelope)
        self.assertEqual(envelope.count("<ShippingOrderVO>"), 2)


class TestParseResponse(unittest.TestCase):
    """SOAP yanıt parse testleri."""

    def test_parse_success_response(self):
        xml = """<?xml version="1.0"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <ns2:dispatchResponse xmlns:ns2="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
              <ShippingOrderResultVO>
                <outFlag>0</outFlag>
                <outResult>Başarılı</outResult>
                <jobId>12345</jobId>
                <count>1</count>
                <shippingOrderDetailVO>
                  <ShippingOrderResultVO>
                    <cargoKey>KEY001</cargoKey>
                    <invoiceKey>INV001</invoiceKey>
                    <errCode>0</errCode>
                    <errMessage>Başarılı</errMessage>
                  </ShippingOrderResultVO>
                </shippingOrderDetailVO>
              </ShippingOrderResultVO>
            </ns2:dispatchResponse>
          </soap:Body>
        </soap:Envelope>"""
        result = _parse_response(xml)
        self.assertEqual(result.out_flag, 0)
        self.assertTrue(result.is_success())
        self.assertEqual(result.job_id, 12345)

    def test_parse_error_response(self):
        xml = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <ns2:dispatchResponse xmlns:ns2="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
              <ShippingOrderResultVO>
                <outFlag>1</outFlag>
                <outResult>Hata oluştu</outResult>
                <jobId>0</jobId>
                <count>0</count>
              </ShippingOrderResultVO>
            </ns2:dispatchResponse>
          </soap:Body>
        </soap:Envelope>"""
        result = _parse_response(xml)
        self.assertEqual(result.out_flag, 1)
        self.assertFalse(result.is_success())
        self.assertEqual(result.out_result, "Hata oluştu")

    def test_parse_detail_error_code(self):
        xml = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <dispatchResponse>
              <ShippingOrderResultVO>
                <outFlag>0</outFlag>
                <outResult>OK</outResult>
                <jobId>99</jobId>
                <count>1</count>
                <shippingOrderDetailVO>
                  <ShippingOrderResultVO>
                    <cargoKey>K1</cargoKey>
                    <invoiceKey>I1</invoiceKey>
                    <errCode>60020</errCode>
                    <errMessage>ERR_EXIST_CARGO_KEY_PARAM</errMessage>
                  </ShippingOrderResultVO>
                </shippingOrderDetailVO>
              </ShippingOrderResultVO>
            </dispatchResponse>
          </soap:Body>
        </soap:Envelope>"""
        result = _parse_response(xml)
        # İlk ShippingOrderResultVO outFlag'ı taşır
        self.assertEqual(result.out_flag, 0)


class TestShipmentResult(unittest.TestCase):
    """ShipmentResult dataclass testleri."""

    def test_is_success_true(self):
        r = ShipmentResult(out_flag=0, out_result="OK")
        self.assertTrue(r.is_success())

    def test_is_success_false(self):
        r = ShipmentResult(out_flag=1, out_result="Error")
        self.assertFalse(r.is_success())

    def test_detail_is_success(self):
        d = ShipmentDetail(cargo_key="K1", err_code=0)
        self.assertTrue(d.is_success())
        d2 = ShipmentDetail(cargo_key="K2", err_code=60020)
        self.assertFalse(d2.is_success())


if __name__ == "__main__":
    unittest.main()
