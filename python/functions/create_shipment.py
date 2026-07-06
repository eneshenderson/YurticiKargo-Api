"""Yurtiçi Kargo - Gönderi Oluşturma (createShipment / dispatch)."""

from __future__ import annotations

import re
import ssl
import urllib.request
from dataclasses import dataclass, field
from typing import Any


# Snake_case → camelCase field mapping
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

REQUIRED_FIELDS = ["cargo_key", "invoice_key", "receiver_cust_name", "receiver_address", "receiver_phone1"]


@dataclass
class ShipmentDetail:
    """Tek bir gönderi sonuç detayı."""
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


def _build_soap_envelope(
    username: str,
    password: str,
    language: str,
    shipments: list[dict[str, Any]],
) -> str:
    """SOAP XML envelope oluşturur."""
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
                  xmlns:ship="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
  <soapenv:Header/>
  <soapenv:Body>
    <ship:createShipment>
      <wsUserName>{username}</wsUserName>
      <wsPassword>{password}</wsPassword>
      <userLanguage>{language}</userLanguage>
{shipping_orders}    </ship:createShipment>
  </soapenv:Body>
</soapenv:Envelope>"""
    return envelope


def _parse_response(xml_text: str) -> ShipmentResult:
    """SOAP yanıtını parse eder."""
    result = ShipmentResult()

    body_text = xml_text

    # outFlag
    out_flag_match = _extract_tag_value(body_text, "outFlag")
    if out_flag_match is not None:
        result.out_flag = int(out_flag_match)

    # outResult
    out_result_match = _extract_tag_value(body_text, "outResult")
    if out_result_match is not None:
        result.out_result = out_result_match

    # jobId
    job_id_match = _extract_tag_value(body_text, "jobId")
    if job_id_match is not None:
        try:
            result.job_id = int(job_id_match)
        except ValueError:
            pass

    # count
    count_match = _extract_tag_value(body_text, "count")
    if count_match is not None:
        try:
            result.count = int(count_match)
        except ValueError:
            pass

    # Details - ShippingOrderResultVO
    details = _extract_shipment_details(body_text)
    result.details = details

    return result


def _extract_tag_value(xml_text: str, tag_name: str) -> str | None:
    """Basit tag değeri çıkarma (ilk bulunan)."""
    # Hem namespace'li hem namespace'siz ara
    patterns = [
        rf"<(?:\w+:)?{tag_name}>(.*?)</(?:\w+:)?{tag_name}>",
        rf"<{tag_name}>(.*?)</{tag_name}>",
    ]
    for pattern in patterns:
        match = re.search(pattern, xml_text, re.DOTALL)
        if match:
            return match.group(1).strip()
    return None


def _extract_shipment_details(xml_text: str) -> list[ShipmentDetail]:
    """Gönderi detaylarını çıkarır."""
    details: list[ShipmentDetail] = []

    # ShippingOrderResultVO blokları
    pattern = r"<(?:\w+:)?ShippingOrderResultVO>(.*?)</(?:\w+:)?ShippingOrderResultVO>"
    matches = re.findall(pattern, xml_text, re.DOTALL)

    for block in matches:
        detail = ShipmentDetail()
        cargo_key = _extract_tag_value(block, "cargoKey")
        if cargo_key:
            detail.cargo_key = cargo_key
        invoice_key = _extract_tag_value(block, "invoiceKey")
        if invoice_key:
            detail.invoice_key = invoice_key
        err_code = _extract_tag_value(block, "errCode")
        if err_code:
            try:
                detail.err_code = int(err_code)
            except ValueError:
                pass
        err_message = _extract_tag_value(block, "errMessage")
        if err_message:
            detail.err_message = err_message
        details.append(detail)

    return details


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
        shipments: Gönderi bilgileri listesi. Her dict en az şu alanları içermeli:
            cargo_key, invoice_key, receiver_cust_name, receiver_address, receiver_phone1
        username: WS kullanıcı adı
        password: WS şifresi
        language: Dil (TR/EN)
        test_mode: True ise test WSDL kullanılır

    Returns:
        ShipmentResult dataclass
    """
    # Zorunlu alan kontrolü
    for i, shipment in enumerate(shipments):
        for req_field in REQUIRED_FIELDS:
            if req_field not in shipment or not shipment[req_field]:
                raise ValueError(f"Gönderi #{i+1}: '{req_field}' alanı zorunludur.")

    # WSDL endpoint
    if test_mode:
        url = "https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices"
    else:
        url = "https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices"

    # SOAP envelope
    envelope = _build_soap_envelope(username, password, language, shipments)

    # HTTP isteği
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "",
    }

    # SSL context (test ortamı için verification kapalı)
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
            result = ShipmentResult(out_flag=2, out_result=f"HTTP Hatası: {e.code}")
            return result
    except Exception as e:
        return ShipmentResult(out_flag=2, out_result=f"Bağlantı hatası: {str(e)}")

    return _parse_response(response_text)
