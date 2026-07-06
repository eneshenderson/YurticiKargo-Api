"""
Yurtiçi Kargo Python API Client - All-in-One

Tüm API fonksiyonlarını tek bir dosyada sunar.
Sadece Python standard library kullanır (urllib, xml.etree, ssl, dataclasses).

Kullanım:
    python yurticikargo_all_in_one.py
"""

from __future__ import annotations

import re
import ssl
import urllib.request
from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# CONFIGURATION
# =============================================================================

WSDL_TEST = "https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices"
WSDL_LIVE = "https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices"
SOAP_NAMESPACE = "http://yurticikargo.com.tr/ShippingOrderDispatcherServices"

# Snake_case → camelCase field mapping for createShipment
_FIELD_MAP: dict[str, str] = {
    "cargo_key": "cargoKey",
    "invoice_key": "invoiceKey",
    "receiver_cust_name": "receiverCustName",
    "receiver_address": "receiverAddress",
    "receiver_phone1": "receiverPhone1",
    "receiver_phone2": "receiverPhone2",
    "receiver_phone3": "receiverPhone3",
    "city_name": "cityName",
    "town_name": "townName",
    "cust_prod_id": "custProdId",
    "desi": "desi",
    "kg": "kg",
    "cargo_count": "cargoCount",
    "waybill_no": "waybillNo",
    "special_field1": "specialField1",
    "special_field2": "specialField2",
    "special_field3": "specialField3",
    "tt_collection_type": "ttCollectionType",
    "tt_invoice_amount": "ttInvoiceAmount",
    "tt_document_id": "ttDocumentId",
    "tt_document_save_type": "ttDocumentSaveType",
    "org_receiver_cust_id": "orgReceiverCustId",
    "description": "description",
    "tax_number": "taxNumber",
    "tax_office_id": "taxOfficeId",
    "tax_office_name": "taxOfficeName",
    "org_geo_code": "orgGeoCode",
    "privilege_order": "privilegeOrder",
    "dc_selected_credit": "dcSelectedCredit",
    "dc_credit_rule": "dcCreditRule",
    "email_address": "emailAddress",
}

REQUIRED_SHIPMENT_FIELDS = ["cargo_key", "invoice_key", "receiver_cust_name", "receiver_address", "receiver_phone1"]


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class ShipmentDetail:
    """createShipment tek gönderi sonuç detayı."""
    cargo_key: str = ""
    invoice_key: str = ""
    err_code: int = 0
    err_message: str = ""

    def is_success(self) -> bool:
        return self.err_code == 0


@dataclass
class ShipmentResult:
    """createShipment sonucu."""
    out_flag: int = -1
    out_result: str = ""
    job_id: int = 0
    count: int = 0
    details: list[ShipmentDetail] = field(default_factory=list)

    def is_success(self) -> bool:
        return self.out_flag == 0


@dataclass
class CancelDetail:
    """cancelShipment tek iptal sonuç detayı."""
    cargo_key: str = ""
    invoice_key: str = ""
    job_id: int = 0
    doc_id: str = ""
    operation_code: int = 0
    operation_message: str = ""
    operation_status: str = ""
    err_code: int = 0
    err_message: str = ""

    def is_success(self) -> bool:
        return self.operation_code == 3 or self.err_code == 0


@dataclass
class CancelResult:
    """cancelShipment sonucu."""
    out_flag: int = -1
    out_result: str = ""
    sender_cust_id: int = 0
    count: int = 0
    details: list[CancelDetail] = field(default_factory=list)

    def is_success(self) -> bool:
        return self.out_flag == 0


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
    """queryShipment tek sorgu sonuç detayı."""
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


@dataclass
class ReturnCodeResult:
    """saveReturnShipmentCode sonucu."""
    out_flag: int = -1
    out_result: str = ""
    err_code: int = 0

    def is_success(self) -> bool:
        return self.out_flag == 0


# =============================================================================
# HELPERS
# =============================================================================

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


def _get_ssl_context() -> ssl.SSLContext:
    """SSL context (verification kapalı - test ortamı)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _get_endpoint(test_mode: bool) -> str:
    """API endpoint URL."""
    return WSDL_TEST if test_mode else WSDL_LIVE


def _send_soap_request(url: str, envelope: str) -> str:
    """SOAP isteği gönderir ve yanıt XML'ini döner."""
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "",
    }
    ssl_context = _get_ssl_context()
    req = urllib.request.Request(url, data=envelope.encode("utf-8"), headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        response_text = e.read().decode("utf-8") if e.fp else ""
        if response_text:
            return response_text
        raise
    except Exception:
        raise


# =============================================================================
# 1. CREATE SHIPMENT
# =============================================================================

def create_shipment(
    shipments: list[dict[str, Any]],
    username: str = "YKTEST",
    password: str = "YK",
    language: str = "TR",
    test_mode: bool = True,
) -> ShipmentResult:
    """
    Yurtiçi Kargo'ya gönderi oluşturma isteği gönderir.

    Args:
        shipments: Gönderi bilgileri listesi.
        username: WS kullanıcı adı
        password: WS şifresi
        language: Dil (TR/EN)
        test_mode: True ise test ortamı

    Returns:
        ShipmentResult
    """
    # Doğrulama
    for i, shipment in enumerate(shipments):
        for req_field in REQUIRED_SHIPMENT_FIELDS:
            if req_field not in shipment or not shipment[req_field]:
                raise ValueError(f"Gönderi #{i+1}: '{req_field}' alanı zorunludur.")

    # SOAP envelope
    shipping_orders = ""
    for shipment in shipments:
        fields_xml = ""
        for snake_key, camel_key in _FIELD_MAP.items():
            value = shipment.get(snake_key)
            if value is not None:
                fields_xml += f"            <{camel_key}>{value}</{camel_key}>\n"
        shipping_orders += f"          <ShippingOrderVO>\n{fields_xml}          </ShippingOrderVO>\n"

    envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ship="{SOAP_NAMESPACE}">
  <soapenv:Header/>
  <soapenv:Body>
    <ship:dispatch>
      <wsUserName>{username}</wsUserName>
      <wsPassword>{password}</wsPassword>
      <wsLanguage>{language}</wsLanguage>
      <ShippingOrderList>
{shipping_orders}      </ShippingOrderList>
    </ship:dispatch>
  </soapenv:Body>
</soapenv:Envelope>"""

    # Gönder
    try:
        response_text = _send_soap_request(_get_endpoint(test_mode), envelope)
    except Exception as e:
        return ShipmentResult(out_flag=2, out_result=f"Bağlantı hatası: {str(e)}")

    # Parse
    result = ShipmentResult()
    out_flag = _extract_tag_value(response_text, "outFlag")
    if out_flag is not None:
        result.out_flag = int(out_flag)
    out_result = _extract_tag_value(response_text, "outResult")
    if out_result is not None:
        result.out_result = out_result
    job_id = _extract_tag_value(response_text, "jobId")
    if job_id:
        try:
            result.job_id = int(job_id)
        except ValueError:
            pass
    count = _extract_tag_value(response_text, "count")
    if count:
        try:
            result.count = int(count)
        except ValueError:
            pass

    # Details
    pattern = r"<(?:\w+:)?ShippingOrderResultVO>(.*?)</(?:\w+:)?ShippingOrderResultVO>"
    matches = re.findall(pattern, response_text, re.DOTALL)
    for block in matches:
        detail = ShipmentDetail()
        v = _extract_tag_value(block, "cargoKey")
        if v:
            detail.cargo_key = v
        v = _extract_tag_value(block, "invoiceKey")
        if v:
            detail.invoice_key = v
        v = _extract_tag_value(block, "errCode")
        if v:
            try:
                detail.err_code = int(v)
            except ValueError:
                pass
        v = _extract_tag_value(block, "errMessage")
        if v:
            detail.err_message = v
        result.details.append(detail)

    return result


# =============================================================================
# 2. CANCEL SHIPMENT
# =============================================================================

def cancel_shipment(
    cargo_keys: list[str],
    username: str = "YKTEST",
    password: str = "YK",
    language: str = "TR",
    test_mode: bool = True,
) -> CancelResult:
    """
    Yurtiçi Kargo'da gönderi iptal eder.

    Args:
        cargo_keys: İptal edilecek kargo anahtarları
        username: WS kullanıcı adı
        password: WS şifresi
        language: Dil (TR/EN)
        test_mode: True ise test ortamı

    Returns:
        CancelResult
    """
    if not cargo_keys:
        raise ValueError("En az bir cargo_key gereklidir.")

    keys_xml = ""
    for key in cargo_keys:
        keys_xml += f"      <cargoKeys>{key}</cargoKeys>\n"

    envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ship="{SOAP_NAMESPACE}">
  <soapenv:Header/>
  <soapenv:Body>
    <ship:cancelShipment>
      <wsUserName>{username}</wsUserName>
      <wsPassword>{password}</wsPassword>
      <wsLanguage>{language}</wsLanguage>
{keys_xml}    </ship:cancelShipment>
  </soapenv:Body>
</soapenv:Envelope>"""

    try:
        response_text = _send_soap_request(_get_endpoint(test_mode), envelope)
    except Exception as e:
        return CancelResult(out_flag=2, out_result=f"Bağlantı hatası: {str(e)}")

    # Parse
    result = CancelResult()
    out_flag = _extract_tag_value(response_text, "outFlag")
    if out_flag is not None:
        result.out_flag = int(out_flag)
    out_result = _extract_tag_value(response_text, "outResult")
    if out_result is not None:
        result.out_result = out_result
    sender_cust_id = _extract_tag_value(response_text, "senderCustId")
    if sender_cust_id:
        try:
            result.sender_cust_id = int(sender_cust_id)
        except ValueError:
            pass
    count = _extract_tag_value(response_text, "count")
    if count:
        try:
            result.count = int(count)
        except ValueError:
            pass

    # Details
    pattern = r"<(?:\w+:)?(?:CancelShipmentResultVO|ShippingOrderResultVO)>(.*?)</(?:\w+:)?(?:CancelShipmentResultVO|ShippingOrderResultVO)>"
    matches = re.findall(pattern, response_text, re.DOTALL)
    for block in matches:
        detail = CancelDetail()
        v = _extract_tag_value(block, "cargoKey")
        if v:
            detail.cargo_key = v
        v = _extract_tag_value(block, "invoiceKey")
        if v:
            detail.invoice_key = v
        v = _extract_tag_value(block, "jobId")
        if v:
            try:
                detail.job_id = int(v)
            except ValueError:
                pass
        v = _extract_tag_value(block, "docId")
        if v:
            detail.doc_id = v
        v = _extract_tag_value(block, "operationCode")
        if v:
            try:
                detail.operation_code = int(v)
            except ValueError:
                pass
        v = _extract_tag_value(block, "operationMessage")
        if v:
            detail.operation_message = v
        v = _extract_tag_value(block, "operationStatus")
        if v:
            detail.operation_status = v
        v = _extract_tag_value(block, "errCode")
        if v:
            try:
                detail.err_code = int(v)
            except ValueError:
                pass
        v = _extract_tag_value(block, "errMessage")
        if v:
            detail.err_message = v
        result.details.append(detail)

    return result


# =============================================================================
# 3. QUERY SHIPMENT
# =============================================================================

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
        test_mode: True ise test ortamı

    Returns:
        QueryResult
    """
    if not keys:
        raise ValueError("En az bir key gereklidir.")
    if key_type not in (0, 1):
        raise ValueError("key_type 0 (Cargo Key) veya 1 (Invoice Key) olmalıdır.")

    keys_xml = ""
    for key in keys:
        keys_xml += f"      <keys>{key}</keys>\n"

    historical = "true" if add_historical_data else "false"
    tracking = "true" if only_tracking else "false"

    envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ship="{SOAP_NAMESPACE}">
  <soapenv:Header/>
  <soapenv:Body>
    <ship:deliveryReportShipment>
      <wsUserName>{username}</wsUserName>
      <wsPassword>{password}</wsPassword>
      <wsLanguage>{language}</wsLanguage>
{keys_xml}      <keyType>{key_type}</keyType>
      <addHistoricalData>{historical}</addHistoricalData>
      <onlyTracking>{tracking}</onlyTracking>
    </ship:deliveryReportShipment>
  </soapenv:Body>
</soapenv:Envelope>"""

    try:
        response_text = _send_soap_request(_get_endpoint(test_mode), envelope)
    except Exception as e:
        return QueryResult(out_flag=2, out_result=f"Bağlantı hatası: {str(e)}")

    # Parse
    result = QueryResult()
    out_flag = _extract_tag_value(response_text, "outFlag")
    if out_flag is not None:
        result.out_flag = int(out_flag)
    out_result = _extract_tag_value(response_text, "outResult")
    if out_result is not None:
        result.out_result = out_result
    sender_cust_id = _extract_tag_value(response_text, "senderCustId")
    if sender_cust_id:
        try:
            result.sender_cust_id = int(sender_cust_id)
        except ValueError:
            pass
    count = _extract_tag_value(response_text, "count")
    if count:
        try:
            result.count = int(count)
        except ValueError:
            pass

    # Details - ShippingDeliveryDetailVO
    pattern = r"<(?:\w+:)?ShippingDeliveryDetailVO>(.*?)</(?:\w+:)?ShippingDeliveryDetailVO>"
    matches = re.findall(pattern, response_text, re.DOTALL)

    for block in matches:
        detail = QueryDetail()
        v = _extract_tag_value(block, "cargoKey")
        if v:
            detail.cargo_key = v
        v = _extract_tag_value(block, "invoiceKey")
        if v:
            detail.invoice_key = v
        v = _extract_tag_value(block, "operationStatus")
        if v:
            detail.operation_status = v
        v = _extract_tag_value(block, "operationMessage")
        if v:
            detail.operation_message = v
        v = _extract_tag_value(block, "errCode")
        if v:
            try:
                detail.err_code = int(v)
            except ValueError:
                pass
        v = _extract_tag_value(block, "errMessage")
        if v:
            detail.err_message = v

        # Item detail
        item_pattern = r"<(?:\w+:)?(?:invDocDetailVO|itemDetail)>(.*?)</(?:\w+:)?(?:invDocDetailVO|itemDetail)>"
        item_match = re.search(item_pattern, block, re.DOTALL)
        if item_match:
            item_block = item_match.group(1)
            item = ItemDetail()
            v = _extract_tag_value(item_block, "trackingUrl")
            if v:
                item.tracking_url = v
            v = _extract_tag_value(item_block, "receiverCustName")
            if v:
                item.receiver_cust_name = v
            v = _extract_tag_value(item_block, "departureUnitName")
            if v:
                item.departure_unit_name = v
            v = _extract_tag_value(item_block, "deliveryDate")
            if v:
                item.delivery_date = v
            v = _extract_tag_value(item_block, "deliveryTime")
            if v:
                item.delivery_time = v

            # Cargo history
            event_pattern = r"<(?:\w+:)?CargoEventVO>(.*?)</(?:\w+:)?CargoEventVO>"
            event_matches = re.findall(event_pattern, item_block, re.DOTALL)
            for event_block in event_matches:
                event = CargoHistoryEvent()
                v = _extract_tag_value(event_block, "unitName")
                if v:
                    event.unit_name = v
                v = _extract_tag_value(event_block, "eventName")
                if v:
                    event.event_name = v
                v = _extract_tag_value(event_block, "reasonName")
                if v:
                    event.reason_name = v
                v = _extract_tag_value(event_block, "eventDate")
                if v:
                    event.event_date = v
                v = _extract_tag_value(event_block, "eventTime")
                if v:
                    event.event_time = v
                v = _extract_tag_value(event_block, "cityName")
                if v:
                    event.city_name = v
                v = _extract_tag_value(event_block, "townName")
                if v:
                    event.town_name = v
                item.cargo_history.append(event)

            detail.item_detail = item

        result.details.append(detail)

    return result


# =============================================================================
# 4. SAVE RETURN SHIPMENT CODE
# =============================================================================

def save_return_shipment_code(
    return_code: str,
    start_date: str,
    end_date: str,
    max_count: int = 1,
    field_name: str = "53",
    username: str = "YKTEST",
    password: str = "YK",
    language: str = "TR",
    test_mode: bool = True,
) -> ReturnCodeResult:
    """
    Yurtiçi Kargo'da iade kodu oluşturur.

    Args:
        return_code: İade kodu (benzersiz)
        start_date: Geçerlilik başlangıç tarihi (YYYYMMDD)
        end_date: Geçerlilik bitiş tarihi (YYYYMMDD)
        max_count: Kullanım adedi
        field_name: Özel alan bilgisi (test: '53' veya '3', canlı: '16')
        username: WS kullanıcı adı
        password: WS şifresi
        language: Dil (TR/EN)
        test_mode: True ise test ortamı

    Returns:
        ReturnCodeResult
    """
    if not return_code:
        raise ValueError("return_code boş olamaz.")
    if not start_date or not end_date:
        raise ValueError("start_date ve end_date zorunludur (YYYYMMDD formatında).")

    envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ship="{SOAP_NAMESPACE}">
  <soapenv:Header/>
  <soapenv:Body>
    <ship:saveReturnShipmentCode>
      <wsUserName>{username}</wsUserName>
      <wsPassword>{password}</wsPassword>
      <wsLanguage>{language}</wsLanguage>
      <fieldName>{field_name}</fieldName>
      <returnCode>{return_code}</returnCode>
      <startDate>{start_date}</startDate>
      <endDate>{end_date}</endDate>
      <maxCount>{max_count}</maxCount>
    </ship:saveReturnShipmentCode>
  </soapenv:Body>
</soapenv:Envelope>"""

    try:
        response_text = _send_soap_request(_get_endpoint(test_mode), envelope)
    except Exception as e:
        return ReturnCodeResult(out_flag=2, out_result=f"Bağlantı hatası: {str(e)}")

    # Parse
    result = ReturnCodeResult()
    out_flag = _extract_tag_value(response_text, "outFlag")
    if out_flag is not None:
        result.out_flag = int(out_flag)
    out_result = _extract_tag_value(response_text, "outResult")
    if out_result is not None:
        result.out_result = out_result
    err_code = _extract_tag_value(response_text, "errCode")
    if err_code:
        try:
            result.err_code = int(err_code)
        except ValueError:
            pass

    return result


# =============================================================================
# CLIENT CLASS
# =============================================================================

class YurticiKargoClient:
    """
    Yurtiçi Kargo SOAP API istemcisi.

    Tüm API metodlarını method olarak sunar.
    Sadece Python standard library kullanır.

    Kullanım:
        client = YurticiKargoClient(username="YKTEST", password="YK", test_mode=True)
        result = client.create_shipment([{...}])
    """

    def __init__(
        self,
        username: str = "YKTEST",
        password: str = "YK",
        language: str = "TR",
        test_mode: bool = True,
    ) -> None:
        self.username = username
        self.password = password
        self.language = language
        self.test_mode = test_mode

    def create_shipment(self, shipments: list[dict[str, Any]]) -> ShipmentResult:
        """Gönderi oluşturma."""
        return create_shipment(
            shipments=shipments,
            username=self.username,
            password=self.password,
            language=self.language,
            test_mode=self.test_mode,
        )

    def cancel_shipment(self, cargo_keys: list[str]) -> CancelResult:
        """Gönderi iptal etme."""
        return cancel_shipment(
            cargo_keys=cargo_keys,
            username=self.username,
            password=self.password,
            language=self.language,
            test_mode=self.test_mode,
        )

    def query_shipment(
        self,
        keys: list[str],
        key_type: int = 0,
        add_historical_data: bool = False,
        only_tracking: bool = False,
    ) -> QueryResult:
        """Gönderi sorgulama."""
        return query_shipment(
            keys=keys,
            key_type=key_type,
            add_historical_data=add_historical_data,
            only_tracking=only_tracking,
            username=self.username,
            password=self.password,
            language=self.language,
            test_mode=self.test_mode,
        )

    def save_return_shipment_code(
        self,
        return_code: str,
        start_date: str,
        end_date: str,
        max_count: int = 1,
        field_name: str = "53",
    ) -> ReturnCodeResult:
        """İade kodu oluşturma."""
        return save_return_shipment_code(
            return_code=return_code,
            start_date=start_date,
            end_date=end_date,
            max_count=max_count,
            field_name=field_name,
            username=self.username,
            password=self.password,
            language=self.language,
            test_mode=self.test_mode,
        )

    def __repr__(self) -> str:
        mode = "TEST" if self.test_mode else "CANLI"
        return f"YurticiKargoClient(user={self.username!r}, mode={mode})"


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Yurtiçi Kargo Python API Client - Demo")
    print("=" * 60)

    client = YurticiKargoClient(username="YKTEST", password="YK", test_mode=True)
    print(f"\nClient: {client}")
    print(f"Endpoint: {_get_endpoint(client.test_mode)}")

    # 1. Gönderi Oluşturma
    print("\n" + "-" * 60)
    print("1. GÖNDERI OLUŞTURMA (createShipment)")
    print("-" * 60)

    shipment_data = [
        {
            "cargo_key": "PYTEST001",
            "invoice_key": "PYINV001",
            "receiver_cust_name": "Mehmet Yılmaz",
            "receiver_address": "Eski Büyükdere Cad. No:3 Maslak",
            "receiver_phone1": "02123652426",
            "city_name": "İstanbul",
            "town_name": "Maslak",
        }
    ]

    print(f"Gönderilen veri: cargo_key={shipment_data[0]['cargo_key']}")
    result = client.create_shipment(shipment_data)
    print(f"Sonuç: out_flag={result.out_flag}, out_result={result.out_result}")
    if result.is_success():
        print(f"  Job ID: {result.job_id}")
    for detail in result.details:
        print(f"  Detail: cargo_key={detail.cargo_key}, err_code={detail.err_code}, msg={detail.err_message}")

    # 2. Gönderi Sorgulama
    print("\n" + "-" * 60)
    print("2. GÖNDERI SORGULAMA (queryShipment)")
    print("-" * 60)

    print("Sorgu: keys=['PYTEST001'], key_type=0")
    result = client.query_shipment(keys=["PYTEST001"], key_type=0, add_historical_data=True)
    print(f"Sonuç: out_flag={result.out_flag}, out_result={result.out_result}")
    for detail in result.details:
        print(f"  Kargo: {detail.cargo_key}, Durum: {detail.operation_status} - {detail.operation_message}")
        if detail.item_detail:
            print(f"    Takip: {detail.item_detail.tracking_url}")
            print(f"    Alıcı: {detail.item_detail.receiver_cust_name}")
            for event in detail.item_detail.cargo_history:
                print(f"    → {event.event_date} {event.event_time} | {event.unit_name} | {event.event_name}")

    # 3. Gönderi İptal
    print("\n" + "-" * 60)
    print("3. GÖNDERI İPTAL (cancelShipment)")
    print("-" * 60)

    print("İptal: cargo_keys=['PYTEST001']")
    result = client.cancel_shipment(["PYTEST001"])
    print(f"Sonuç: out_flag={result.out_flag}, out_result={result.out_result}")
    for detail in result.details:
        print(f"  {detail.cargo_key}: {detail.operation_message} ({detail.operation_status})")

    # 4. İade Kodu Oluşturma
    print("\n" + "-" * 60)
    print("4. İADE KODU OLUŞTURMA (saveReturnShipmentCode)")
    print("-" * 60)

    print("İade kodu: RMA-PY-001, tarih: 20240101-20240131")
    result = client.save_return_shipment_code(
        return_code="RMA-PY-001",
        start_date="20240101",
        end_date="20240131",
        max_count=1,
        field_name="53",
    )
    print(f"Sonuç: out_flag={result.out_flag}, out_result={result.out_result}, err_code={result.err_code}")

    print("\n" + "=" * 60)
    print("Demo tamamlandı.")
    print("=" * 60)
