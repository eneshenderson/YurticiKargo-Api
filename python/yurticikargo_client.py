"""
Yurtiçi Kargo Python API Client - Controller

Tüm API fonksiyonlarını tek bir sınıf altında birleştirir.
Sadece Python standard library kullanır (urllib, xml.etree, ssl, dataclasses).
"""

from __future__ import annotations

from typing import Any

from functions import (
    create_shipment as _create_shipment_fn,
    cancel_shipment as _cancel_shipment_fn,
    query_shipment as _query_shipment_fn,
    save_return_shipment_code as _save_return_code_fn,
)
from functions.create_shipment import ShipmentResult
from functions.cancel_shipment import CancelResult
from functions.query_shipment import QueryResult
from functions.save_return_shipment_code import ReturnCodeResult


class YurticiKargoClient:
    """
    Yurtiçi Kargo SOAP API istemcisi.

    Tüm API metodlarını method olarak sunar.
    Sadece Python standard library kullanır.

    Kullanım:
        client = YurticiKargoClient(username="YKTEST", password="YK", test_mode=True)
        result = client.create_shipment([{...}])
    """

    WSDL_TEST = "https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl"
    WSDL_LIVE = "https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl"

    def __init__(
        self,
        username: str = "YKTEST",
        password: str = "YK",
        language: str = "TR",
        test_mode: bool = True,
    ) -> None:
        """
        Args:
            username: WS kullanıcı adı
            password: WS şifresi
            language: Dil (TR/EN)
            test_mode: True ise test ortamı kullanılır
        """
        self.username = username
        self.password = password
        self.language = language
        self.test_mode = test_mode

    @property
    def wsdl_url(self) -> str:
        """Aktif WSDL URL'si."""
        return self.WSDL_TEST if self.test_mode else self.WSDL_LIVE

    def create_shipment(self, shipments: list[dict[str, Any]]) -> ShipmentResult:
        """
        Gönderi oluşturma.

        Args:
            shipments: Gönderi bilgileri listesi. Her dict en az şu alanları içermeli:
                - cargo_key (str): Benzersiz kargo anahtarı
                - invoice_key (str): Fatura anahtarı
                - receiver_cust_name (str): Alıcı adı
                - receiver_address (str): Alıcı adresi
                - receiver_phone1 (str): Alıcı telefon

        Returns:
            ShipmentResult: Sonuç bilgisi
        """
        return _create_shipment_fn(
            shipments=shipments,
            username=self.username,
            password=self.password,
            language=self.language,
            test_mode=self.test_mode,
        )

    def cancel_shipment(self, cargo_keys: list[str]) -> CancelResult:
        """
        Gönderi iptal etme.

        Args:
            cargo_keys: İptal edilecek kargo anahtarları

        Returns:
            CancelResult: Sonuç bilgisi
        """
        return _cancel_shipment_fn(
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
        """
        Gönderi sorgulama.

        Args:
            keys: Sorgulanacak anahtar değerleri
            key_type: 0=Cargo Key, 1=Invoice Key
            add_historical_data: Hareket geçmişi dahil edilsin mi
            only_tracking: Sadece takip URL dönsün mü

        Returns:
            QueryResult: Sonuç bilgisi
        """
        return _query_shipment_fn(
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
        """
        İade kodu oluşturma.

        Args:
            return_code: İade kodu (benzersiz)
            start_date: Geçerlilik başlangıç tarihi (YYYYMMDD)
            end_date: Geçerlilik bitiş tarihi (YYYYMMDD)
            max_count: Kullanım adedi
            field_name: Özel alan bilgisi (test: '53' veya '3', canlı: '16')

        Returns:
            ReturnCodeResult: Sonuç bilgisi
        """
        return _save_return_code_fn(
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
