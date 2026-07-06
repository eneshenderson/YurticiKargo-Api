"""Yurtiçi Kargo - İade Kodu Oluşturma (saveReturnShipmentCode)."""

from __future__ import annotations

import re
import ssl
import urllib.request
from dataclasses import dataclass


@dataclass
class ReturnCodeResult:
    """saveReturnShipmentCode sonucu."""
    out_flag: int = -1
    out_result: str = ""
    err_code: int = 0

    def is_success(self) -> bool:
        return self.out_flag == 0


def _build_soap_envelope(
    username: str,
    password: str,
    language: str,
    return_code: str,
    start_date: str,
    end_date: str,
    max_count: int,
    field_name: str,
) -> str:
    """SOAP XML envelope oluşturur."""
    envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ship="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
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


def _parse_response(xml_text: str) -> ReturnCodeResult:
    """SOAP yanıtını parse eder."""
    result = ReturnCodeResult()

    # outFlag
    out_flag = _extract_tag_value(xml_text, "outFlag")
    if out_flag is not None:
        result.out_flag = int(out_flag)

    # outResult
    out_result = _extract_tag_value(xml_text, "outResult")
    if out_result is not None:
        result.out_result = out_result

    # errCode
    err_code = _extract_tag_value(xml_text, "errCode")
    if err_code is not None:
        try:
            result.err_code = int(err_code)
        except ValueError:
            pass

    return result


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
        test_mode: True ise test WSDL kullanılır

    Returns:
        ReturnCodeResult dataclass
    """
    if not return_code:
        raise ValueError("return_code boş olamaz.")
    if not start_date or not end_date:
        raise ValueError("start_date ve end_date zorunludur (YYYYMMDD formatında).")

    # Endpoint
    if test_mode:
        url = "https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices"
    else:
        url = "https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices"

    # SOAP envelope
    envelope = _build_soap_envelope(
        username, password, language, return_code, start_date, end_date, max_count, field_name
    )

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
            return ReturnCodeResult(out_flag=2, out_result=f"HTTP Hatası: {e.code}")
    except Exception as e:
        return ReturnCodeResult(out_flag=2, out_result=f"Bağlantı hatası: {str(e)}")

    return _parse_response(response_text)
