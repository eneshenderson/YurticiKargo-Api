"""Tests for query_shipment function."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.query_shipment import (
    query_shipment,
    QueryResult,
    QueryDetail,
    ItemDetail,
    CargoHistoryEvent,
    _build_soap_envelope,
    _parse_response,
)


class TestQueryShipmentValidation(unittest.TestCase):
    """Doğrulama testleri."""

    def test_empty_keys_raises(self):
        with self.assertRaises(ValueError) as ctx:
            query_shipment([])
        self.assertIn("En az bir key", str(ctx.exception))

    def test_invalid_key_type_raises(self):
        with self.assertRaises(ValueError) as ctx:
            query_shipment(["K1"], key_type=5)
        self.assertIn("key_type", str(ctx.exception))


class TestBuildSoapEnvelope(unittest.TestCase):
    """SOAP envelope oluşturma testleri."""

    def test_envelope_contains_credentials(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", ["K1"], 0, False, False)
        self.assertIn("<wsUserName>YKTEST</wsUserName>", envelope)
        self.assertIn("<wsPassword>YK</wsPassword>", envelope)

    def test_envelope_contains_keys(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", ["K1", "K2"], 0, False, False)
        self.assertIn("<keys>K1</keys>", envelope)
        self.assertIn("<keys>K2</keys>", envelope)

    def test_envelope_key_type(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", ["K1"], 1, False, False)
        self.assertIn("<keyType>1</keyType>", envelope)

    def test_envelope_historical_data_true(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", ["K1"], 0, True, False)
        self.assertIn("<addHistoricalData>true</addHistoricalData>", envelope)

    def test_envelope_historical_data_false(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", ["K1"], 0, False, False)
        self.assertIn("<addHistoricalData>false</addHistoricalData>", envelope)

    def test_envelope_only_tracking_true(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", ["K1"], 0, False, True)
        self.assertIn("<onlyTracking>true</onlyTracking>", envelope)

    def test_envelope_uses_delivery_report(self):
        envelope = _build_soap_envelope("YKTEST", "YK", "TR", ["K1"], 0, False, False)
        self.assertIn("deliveryReportShipment", envelope)


class TestParseResponse(unittest.TestCase):
    """SOAP yanıt parse testleri."""

    def test_parse_success_with_details(self):
        xml = """<?xml version="1.0"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <ns2:deliveryReportShipmentResponse xmlns:ns2="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
              <DeliveryReportResponseVO>
                <outFlag>0</outFlag>
                <outResult>Başarılı</outResult>
                <senderCustId>123456</senderCustId>
                <count>1</count>
                <deliveryReportDetailVO>
                  <ShippingDeliveryDetailVO>
                    <cargoKey>12520</cargoKey>
                    <invoiceKey>INV001</invoiceKey>
                    <operationStatus>DLV</operationStatus>
                    <operationMessage>Teslim edildi</operationMessage>
                    <errCode>0</errCode>
                    <errMessage></errMessage>
                    <invDocDetailVO>
                      <trackingUrl>http://track.yurticikargo.com/xxx</trackingUrl>
                      <receiverCustName>Mehmet Yılmaz</receiverCustName>
                      <departureUnitName>İstanbul TM</departureUnitName>
                      <deliveryDate>2024-01-15</deliveryDate>
                      <deliveryTime>14:30</deliveryTime>
                    </invDocDetailVO>
                  </ShippingDeliveryDetailVO>
                </deliveryReportDetailVO>
              </DeliveryReportResponseVO>
            </ns2:deliveryReportShipmentResponse>
          </soap:Body>
        </soap:Envelope>"""
        result = _parse_response(xml)
        self.assertEqual(result.out_flag, 0)
        self.assertTrue(result.is_success())
        self.assertEqual(result.count, 1)
        self.assertEqual(len(result.details), 1)

        detail = result.details[0]
        self.assertEqual(detail.cargo_key, "12520")
        self.assertEqual(detail.operation_status, "DLV")
        self.assertTrue(detail.is_success())
        self.assertIsNotNone(detail.item_detail)
        self.assertIn("track.yurticikargo.com", detail.item_detail.tracking_url)
        self.assertEqual(detail.item_detail.receiver_cust_name, "Mehmet Yılmaz")

    def test_parse_with_cargo_history(self):
        xml = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <deliveryReportShipmentResponse>
              <DeliveryReportResponseVO>
                <outFlag>0</outFlag>
                <outResult>OK</outResult>
                <count>1</count>
                <deliveryReportDetailVO>
                  <ShippingDeliveryDetailVO>
                    <cargoKey>K1</cargoKey>
                    <operationStatus>IND</operationStatus>
                    <errCode>0</errCode>
                    <invDocDetailVO>
                      <trackingUrl>http://example.com</trackingUrl>
                      <receiverCustName>Ali</receiverCustName>
                      <departureUnitName>Ankara TM</departureUnitName>
                      <cargoEventDetailVO>
                        <CargoEventVO>
                          <unitName>Ankara Şube</unitName>
                          <eventName>Kargo teslim alındı</eventName>
                          <reasonName></reasonName>
                          <eventDate>2024-01-10</eventDate>
                          <eventTime>09:00</eventTime>
                          <cityName>Ankara</cityName>
                          <townName>Çankaya</townName>
                        </CargoEventVO>
                        <CargoEventVO>
                          <unitName>İstanbul TM</unitName>
                          <eventName>Transfer merkezi</eventName>
                          <reasonName></reasonName>
                          <eventDate>2024-01-11</eventDate>
                          <eventTime>03:00</eventTime>
                          <cityName>İstanbul</cityName>
                          <townName>Esenyurt</townName>
                        </CargoEventVO>
                      </cargoEventDetailVO>
                    </invDocDetailVO>
                  </ShippingDeliveryDetailVO>
                </deliveryReportDetailVO>
              </DeliveryReportResponseVO>
            </deliveryReportShipmentResponse>
          </soap:Body>
        </soap:Envelope>"""
        result = _parse_response(xml)
        self.assertTrue(result.is_success())
        detail = result.details[0]
        self.assertIsNotNone(detail.item_detail)
        self.assertEqual(len(detail.item_detail.cargo_history), 2)
        self.assertEqual(detail.item_detail.cargo_history[0].unit_name, "Ankara Şube")
        self.assertEqual(detail.item_detail.cargo_history[1].city_name, "İstanbul")

    def test_parse_error_response(self):
        xml = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <deliveryReportShipmentResponse>
              <DeliveryReportResponseVO>
                <outFlag>1</outFlag>
                <outResult>Hata</outResult>
                <count>0</count>
              </DeliveryReportResponseVO>
            </deliveryReportShipmentResponse>
          </soap:Body>
        </soap:Envelope>"""
        result = _parse_response(xml)
        self.assertFalse(result.is_success())


class TestQueryResult(unittest.TestCase):
    """QueryResult dataclass testleri."""

    def test_is_success(self):
        r = QueryResult(out_flag=0)
        self.assertTrue(r.is_success())
        r2 = QueryResult(out_flag=1)
        self.assertFalse(r2.is_success())


class TestQueryShipmentHTTP(unittest.TestCase):
    """HTTP çağrı testleri (mock)."""

    @patch("urllib.request.urlopen")
    def test_successful_call(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <deliveryReportShipmentResponse>
              <DeliveryReportResponseVO>
                <outFlag>0</outFlag>
                <outResult>OK</outResult>
                <count>1</count>
                <deliveryReportDetailVO>
                  <ShippingDeliveryDetailVO>
                    <cargoKey>K1</cargoKey>
                    <operationStatus>DLV</operationStatus>
                    <errCode>0</errCode>
                  </ShippingDeliveryDetailVO>
                </deliveryReportDetailVO>
              </DeliveryReportResponseVO>
            </deliveryReportShipmentResponse>
          </soap:Body>
        </soap:Envelope>"""
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = query_shipment(["K1"], key_type=0)
        self.assertTrue(result.is_success())
        self.assertEqual(result.details[0].operation_status, "DLV")

    @patch("urllib.request.urlopen")
    def test_connection_error(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Timeout")
        result = query_shipment(["K1"])
        self.assertEqual(result.out_flag, 2)
        self.assertIn("Bağlantı hatası", result.out_result)


if __name__ == "__main__":
    unittest.main()
