"""Yurtiçi Kargo - Gönderi İptal (cancelShipment)."""

from __future__ import annotations

import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CancelDetail:
    """Tek bir iptal sonuç detayı."""
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


def _build_soap_envelope(
    username: str,
    password: str,
    language: str,
    cargo_keys: list[str],
) -> str:
    """SOAP XML envelope oluşturur."""
    keys_xml = ""
    for key in cargo_keys:
        keys_xml += f"      <cargoKeys>{key}</cargoKeys>\n"

    envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ship="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
  <soapenv:Header/>
  <soapenv:Body>
    <ship:cancelShipment>
      <wsUserName>{username}</wsUserName>
      <wsPassword>{password}</wsPassword>
      <userLanguage>{language}</userLanguage>
{keys_xml}    </ship:cancelShipment>
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


def _parse_response(xml_text: str) -> CancelResult:
    """SOAP yanıtını parse eder."""
    result = CancelResult()

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

    # Details - CancelShipmentResultVO veya ShippingOrderResultVO
    pattern = r"<(?:\w+:)?(?:CancelShipmentResultVO|ShippingOrderResultVO)>(.*?)</(?:\w+:)?(?:CancelShipmentResultVO|ShippingOrderResultVO)>"
    matches = re.findall(pattern, xml_text, re.DOTALL)

    for block in matches:
        detail = CancelDetail()

        cargo_key = _extract_tag_value(block, "cargoKey")
        if cargo_key:
            detail.cargo_key = cargo_key

        invoice_key = _extract_tag_value(block, "invoiceKey")
        if invoice_key:
            detail.invoice_key = invoice_key

        job_id = _extract_tag_value(block, "jobId")
        if job_id:
            try:
                detail.job_id = int(job_id)
            except ValueError:
                pass

        doc_id = _extract_tag_value(block, "docId")
        if doc_id:
            detail.doc_id = doc_id

        operation_code = _extract_tag_value(block, "operationCode")
        if operation_code:
            try:
                detail.operation_code = int(operation_code)
            except ValueError:
                pass

        operation_message = _extract_tag_value(block, "operationMessage")
        if operation_message:
            detail.operation_message = operation_message

        operation_status = _extract_tag_value(block, "operationStatus")
        if operation_status:
            detail.operation_status = operation_status

        err_code = _extract_tag_value(block, "errCode")
        if err_code:
            try:
                detail.err_code = int(err_code)
            except ValueError:
                pass

        err_message = _extract_tag_value(block, "errMessage")
        if err_message:
            detail.err_message = err_message

        result.details.append(detail)

    return result


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
        cargo_keys: İptal edilecek kargo anahtarları listesi
        username: WS kullanıcı adı
        password: WS şifresi
        language: Dil (TR/EN)
        test_mode: True ise test WSDL kullanılır

    Returns:
        CancelResult dataclass
    """
    if not cargo_keys:
        raise ValueError("En az bir cargo_key gereklidir.")

    # Endpoint
    if test_mode:
        url = "https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices"
    else:
        url = "https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices"

    # SOAP envelope
    envelope = _build_soap_envelope(username, password, language, cargo_keys)

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
            return CancelResult(out_flag=2, out_result=f"HTTP Hatası: {e.code}")
    except Exception as e:
        return CancelResult(out_flag=2, out_result=f"Bağlantı hatası: {str(e)}")

    return _parse_response(response_text)
