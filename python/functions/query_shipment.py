"""Yurtiçi Kargo - Gönderi Sorgulama (queryShipment / deliveryReportShipment)."""

from __future__ import annotations

import re
import ssl
import urllib.request
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CargoHistoryEvent:
    """Kargo hareket geçmişi olayı."""
    unit_name: str = ""
    event_name: str = ""
    reason_name: str = ""
    event_date: str = ""
    event_time: str = ""
    city_name: str = ""
    town_name: str = ""


@dataclass
class ItemDetail:
    """Gönderi detay bilgileri."""
    tracking_url: str = ""
    receiver_cust_name: str = ""
    departure_unit_name: str = ""
    delivery_date: str = ""
    delivery_time: str = ""
    cargo_history: list[CargoHistoryEvent] = field(default_factory=list)


@dataclass
class QueryDetail:
    """Tek bir sorgu sonuç detayı."""
    cargo_key: str = ""
    invoice_key: str = ""
    operation_status: str = ""
    operation_message: str = ""
    err_code: int = 0
    err_message: str = ""
    item_detail: ItemDetail | None = None

    def is_success(self) -> bool:
        return self.err_code == 0


@dataclass
class QueryResult:
    """queryShipment sonucu."""
    out_flag: int = -1
    out_result: str = ""
    sender_cust_id: int = 0
    count: int = 0
    details: list[QueryDetail] = field(default_factory=list)

    def is_success(self) -> bool:
        return self.out_flag == 0


def _build_soap_envelope(
    username: str,
    password: str,
    language: str,
    keys: list[str],
    key_type: int,
    add_historical_data: bool,
    only_tracking: bool,
) -> str:
    """SOAP XML envelope oluşturur."""
    keys_xml = ""
    for key in keys:
        keys_xml += f"      <keys>{key}</keys>\n"

    historical = "true" if add_historical_data else "false"
    tracking = "true" if only_tracking else "false"

    envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ship="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
  <soapenv:Header/>
  <soapenv:Body>
    <ship:queryShipment>
      <wsUserName>{username}</wsUserName>
      <wsPassword>{password}</wsPassword>
      <wsLanguage>{language}</wsLanguage>
{keys_xml}      <keyType>{key_type}</keyType>
      <addHistoricalData>{historical}</addHistoricalData>
      <onlyTracking>{tracking}</onlyTracking>
    </ship:queryShipment>
  </soapenv:Body>
</soapenv:Envelope>"""
    return envelope


def _extract_tag_value(xml_text: str, tag_name: str) -> str | None:
    """Basit tag değeri çıkarma (ilk bulunan)."""
    patterns = [
        rf"<(?:\w+:)?{tag_name}>(.*?)</(?:\w+:)?{tag_name}>",
        rf"<{tag_name}>(.*?)</{tag_name}>",
    ]
    for pattern in patterns:
        match = re.search(pattern, xml_text, re.DOTALL)
        if match:
            return match.group(1).strip()
    return None


def _extract_all_tag_values(xml_text: str, tag_name: str) -> list[str]:
    """Tüm eşleşen tag değerlerini çıkarır."""
    patterns = [
        rf"<(?:\w+:)?{tag_name}>(.*?)</(?:\w+:)?{tag_name}>",
        rf"<{tag_name}>(.*?)</{tag_name}>",
    ]
    results = []
    for pattern in patterns:
        matches = re.findall(pattern, xml_text, re.DOTALL)
        if matches:
            results = [m.strip() for m in matches]
            break
    return results


def _parse_cargo_history(block: str) -> list[CargoHistoryEvent]:
    """Kargo hareket geçmişini parse eder."""
    events: list[CargoHistoryEvent] = []

    # CargoEventVO blokları
    pattern = r"<(?:\w+:)?CargoEventVO>(.*?)</(?:\w+:)?CargoEventVO>"
    matches = re.findall(pattern, block, re.DOTALL)

    for event_block in matches:
        event = CargoHistoryEvent()

        unit_name = _extract_tag_value(event_block, "unitName")
        if unit_name:
            event.unit_name = unit_name

        event_name = _extract_tag_value(event_block, "eventName")
        if event_name:
            event.event_name = event_name

        reason_name = _extract_tag_value(event_block, "reasonName")
        if reason_name:
            event.reason_name = reason_name

        event_date = _extract_tag_value(event_block, "eventDate")
        if event_date:
            event.event_date = event_date

        event_time = _extract_tag_value(event_block, "eventTime")
        if event_time:
            event.event_time = event_time

        city_name = _extract_tag_value(event_block, "cityName")
        if city_name:
            event.city_name = city_name

        town_name = _extract_tag_value(event_block, "townName")
        if town_name:
            event.town_name = town_name

        events.append(event)

    return events


def _parse_item_detail(block: str) -> ItemDetail | None:
    """itemDetail bilgisini parse eder."""
    # invDocDetailVO veya itemDetail bloku ara
    item_pattern = r"<(?:\w+:)?(?:invDocDetailVO|itemDetail)>(.*?)</(?:\w+:)?(?:invDocDetailVO|itemDetail)>"
    match = re.search(item_pattern, block, re.DOTALL)
    if not match:
        return None

    item_block = match.group(1)
    item = ItemDetail()

    tracking_url = _extract_tag_value(item_block, "trackingUrl")
    if tracking_url:
        item.tracking_url = tracking_url

    receiver_name = _extract_tag_value(item_block, "receiverCustName")
    if receiver_name:
        item.receiver_cust_name = receiver_name

    departure = _extract_tag_value(item_block, "departureUnitName")
    if departure:
        item.departure_unit_name = departure

    delivery_date = _extract_tag_value(item_block, "deliveryDate")
    if delivery_date:
        item.delivery_date = delivery_date

    delivery_time = _extract_tag_value(item_block, "deliveryTime")
    if delivery_time:
        item.delivery_time = delivery_time

    item.cargo_history = _parse_cargo_history(item_block)

    return item


def _parse_response(xml_text: str) -> QueryResult:
    """SOAP yanıtını parse eder."""
    result = QueryResult()

    # outFlag
    out_flag = _extract_tag_value(xml_text, "outFlag")
    if out_flag is not None:
        result.out_flag = int(out_flag)

    # outResult
    out_result = _extract_tag_value(xml_text, "outResult")
    if out_result is not None:
        result.out_result = out_result

    # senderCustId
    sender_cust_id = _extract_tag_value(xml_text, "senderCustId")
    if sender_cust_id is not None:
        try:
            result.sender_cust_id = int(sender_cust_id)
        except ValueError:
            pass

    # count
    count = _extract_tag_value(xml_text, "count")
    if count is not None:
        try:
            result.count = int(count)
        except ValueError:
            pass

    # Details - ShippingDeliveryDetailVO
    pattern = r"<(?:\w+:)?ShippingDeliveryDetailVO>(.*?)</(?:\w+:)?ShippingDeliveryDetailVO>"
    matches = re.findall(pattern, xml_text, re.DOTALL)

    for block in matches:
        detail = QueryDetail()

        cargo_key = _extract_tag_value(block, "cargoKey")
        if cargo_key:
            detail.cargo_key = cargo_key

        invoice_key = _extract_tag_value(block, "invoiceKey")
        if invoice_key:
            detail.invoice_key = invoice_key

        operation_status = _extract_tag_value(block, "operationStatus")
        if operation_status:
            detail.operation_status = operation_status

        operation_message = _extract_tag_value(block, "operationMessage")
        if operation_message:
            detail.operation_message = operation_message

        err_code = _extract_tag_value(block, "errCode")
        if err_code:
            try:
                detail.err_code = int(err_code)
            except ValueError:
                pass

        err_message = _extract_tag_value(block, "errMessage")
        if err_message:
            detail.err_message = err_message

        # Item detail
        detail.item_detail = _parse_item_detail(block)

        result.details.append(detail)

    return result


def query_shipment(
    keys: list[str],
    key_type: int = 0,
    add_historical_data: bool = False,
    only_tracking: bool = False,
    username: str = "YKTEST",
    password: str = "YK",
    language: str = "TR",
    test_mode: bool = True,
) -> QueryResult:
    """
    Yurtiçi Kargo gönderi durumu sorgular.

    Args:
        keys: Sorgulanacak anahtar değerleri
        key_type: 0=Cargo Key, 1=Invoice Key
        add_historical_data: Hareket geçmişi dahil edilsin mi
        only_tracking: Sadece takip URL dönsün mü
        username: WS kullanıcı adı
        password: WS şifresi
        language: Dil (TR/EN)
        test_mode: True ise test WSDL kullanılır

    Returns:
        QueryResult dataclass
    """
    if not keys:
        raise ValueError("En az bir key gereklidir.")
    if key_type not in (0, 1):
        raise ValueError("key_type 0 (Cargo Key) veya 1 (Invoice Key) olmalıdır.")

    # Endpoint
    if test_mode:
        url = "https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices"
    else:
        url = "https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices"

    # SOAP envelope
    envelope = _build_soap_envelope(username, password, language, keys, key_type, add_historical_data, only_tracking)

    # HTTP isteği
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "",
    }

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, data=envelope.encode("utf-8"), headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            response_text = response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        response_text = e.read().decode("utf-8") if e.fp else ""
        if not response_text:
            return QueryResult(out_flag=2, out_result=f"HTTP Hatası: {e.code}")
    except Exception as e:
        return QueryResult(out_flag=2, out_result=f"Bağlantı hatası: {str(e)}")

    return _parse_response(response_text)
