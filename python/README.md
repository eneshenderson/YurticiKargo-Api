# Yurtiçi Kargo Python API Client

Yurtiçi Kargo SOAP Web Service entegrasyonu için Python istemci kütüphanesi.

> **Sıfır bağımlılık** — Sadece Python standart kütüphanesi kullanılır. Harici paket gerektirmez.

---

## Gereksinimler

- Python >= 3.10
- Standart kütüphane modülleri:
  - `urllib.request` — HTTP istekleri
  - `xml.etree.ElementTree` — SOAP XML oluşturma ve ayrıştırma
  - `ssl` — HTTPS bağlantı güvenliği
  - `dataclasses` — Sonuç modelleri

> ⚠️ Harici paket (requests, zeep, lxml vb.) kurulumu **gerekmez**.

---

## Proje Yapısı

```
python/
├── functions/
│   ├── __init__.py
│   ├── create_shipment.py        # Gönderi oluşturma
│   ├── cancel_shipment.py        # Gönderi iptal
│   ├── query_shipment.py         # Gönderi sorgulama
│   └── save_return_shipment_code.py  # İade kodu oluşturma
├── yurticikargo_client.py        # Controller (tüm metodları birleştirir)
├── tests/
│   ├── test_create_shipment.py
│   ├── test_cancel_shipment.py
│   ├── test_query_shipment.py
│   └── test_save_return_shipment_code.py
└── yurticikargo_all_in_one.py    # Tek dosyada tüm işlevsellik
```

### Kullanım Seçenekleri

| Yöntem | Açıklama | Dosya |
|--------|----------|-------|
| **Controller** | OOP yaklaşım, tüm metodlar tek sınıfta | `yurticikargo_client.py` |
| **Fonksiyon bazlı** | Her metod bağımsız fonksiyon | `functions/*.py` |
| **All-in-one** | Tek dosyada tüm işlevsellik | `yurticikargo_all_in_one.py` |

---

## Kurulum

Herhangi bir kurulum adımı gerekmez. Dosyaları projenize kopyalamanız yeterlidir.

```bash
# Projeyi klonlayın veya dosyaları kopyalayın
cd python/
```

---

## Çalıştırma

```bash
# All-in-one demo çalıştırma
python yurticikargo_all_in_one.py

# Testleri çalıştırma
python -m unittest discover tests/ -v

# Tek bir test dosyası çalıştırma
python -m unittest tests.test_create_shipment -v
```

---

## Test Ortamı Bilgileri

| Parametre | Değer |
|-----------|-------|
| Username | `YKTEST` |
| Password | `YK` |
| Language | `TR` |
| WSDL (Test) | `https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl` |
| WSDL (Canlı) | `https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl` |

---

## Hızlı Başlangıç

### Controller Kullanımı

```python
from yurticikargo_client import YurticiKargoClient

# Test ortamı
client = YurticiKargoClient('YKTEST', 'YK', 'TR', test_mode=True)

# Canlı ortam
client = YurticiKargoClient('KULLANICI_ADINIZ', 'SIFRENIZ', 'TR', test_mode=False)
```

### Fonksiyon Bazlı Kullanım

```python
from functions.create_shipment import create_shipment
from functions.cancel_shipment import cancel_shipment
from functions.query_shipment import query_shipment
from functions.save_return_shipment_code import save_return_shipment_code

# Her fonksiyon bağımsız çalışır
result = create_shipment(
    shipments=[{...}],
    username='YKTEST',
    password='YK',
    language='TR',
    test_mode=True
)
```

---

## API Metodları

Python `snake_case` convention kullanır; SOAP XML tarafında `camelCase` dönüşümü otomatik yapılır.

---

### 1. create_shipment — Gönderi Oluşturma

Müşterinin kargo bilgilerini Yurtiçi Kargo sistemine ileten servistir.

**SOAP Operasyonu:** `ship:createShipment` (parametre: `userLanguage`)

```python
result = client.create_shipment([
    {
        'cargo_key': 'TEST001',
        'invoice_key': 'INV001',
        'receiver_cust_name': 'Mehmet Yılmaz',
        'receiver_address': 'Eski Büyükdere Cad. No:3 Maslak Istanbul',
        'receiver_phone1': '05321234567',
        'city_name': 'Istanbul',
        'town_name': 'Sariyer',
    }
])

if result.is_success():
    print(f'Başarılı! Job ID: {result.job_id}')
    for detail in result.details:
        print(f'  Cargo Key: {detail.cargo_key} - Durum: {detail.err_message}')
else:
    print(f'Hata: {result.out_result}')
    for error in result.get_errors():
        print(f'  [{error.err_code}] {error.err_message}')
```

#### Gönderi Parametreleri

| Python Parametre | SOAP Parametre | Tip | Zorunlu | Açıklama | Örnek |
|------------------|----------------|-----|---------|----------|-------|
| `cargo_key` | `cargoKey` | string(20) | ✅ | Benzersiz kargo anahtarı | `TEST001` |
| `invoice_key` | `invoiceKey` | string(20) | ✅ | Fatura anahtarı | `INV001` |
| `receiver_cust_name` | `receiverCustName` | string(100) | ✅ | Alıcı müşteri adı | `Mehmet Yılmaz` |
| `receiver_address` | `receiverAddress` | string(500) | ✅ | Alıcı müşteri adresi | `Eski Büyükdere Cad. No:3` |
| `receiver_phone1` | `receiverPhone1` | string(20) | ✅ | Alıcı telefon numarası | `05321234567` |
| `receiver_phone2` | `receiverPhone2` | string(20) | ❌ | Alıcı telefon 2 | |
| `receiver_phone3` | `receiverPhone3` | string(20) | ❌ | Alıcı telefon 3 | |
| `city_name` | `cityName` | string(40) | ❌ | Alıcı adres şehir | `Istanbul` |
| `town_name` | `townName` | string(40) | ❌ | Alıcı adres ilçe | `Sariyer` |
| `cust_prod_id` | `custProdId` | string | ❌ | Ürün kodu | `1` |
| `desi` | `desi` | float(9,3) | ❌ | Kargo desi bilgisi | `3.5` |
| `kg` | `kg` | float(9,3) | ❌ | Kargo kg bilgisi | `7.6` |
| `cargo_count` | `cargoCount` | int(4) | ❌ | Gönderilen kargo adedi | `2` |
| `waybill_no` | `waybillNo` | string(20) | ❌ | Müşteri irsaliye numarası | `AA110125T` |
| `special_field1` | `specialField1` | string(200) | ❌ | Özel alan 1 | `1$426031#2$397427#` |
| `special_field2` | `specialField2` | string(100) | ❌ | Özel alan 2 | |
| `special_field3` | `specialField3` | string(100) | ❌ | Özel alan 3 | |
| `tt_collection_type` | `ttCollectionType` | string(1) | ❌ | Tahsilat ödeme tipi: `0`=Nakit, `1`=KK | `0` |
| `tt_invoice_amount` | `ttInvoiceAmount` | float(18,2) | ❌ | Tahsilat tutarı | `20.5` |
| `tt_document_id` | `ttDocumentId` | string(12) | ❌ | Tahsilat belge numarası | `TT00666` |
| `tt_document_save_type` | `ttDocumentSaveType` | string(1) | ❌ | Fatura tipi: `0`=Aynı, `1`=Ayrı | `0` |
| `org_receiver_cust_id` | `orgReceiverCustId` | string(50) | ❌ | Alıcı müşteri kodu | `59874736` |
| `description` | `description` | string(255) | ❌ | Serbest açıklama | `Kargo` |
| `tax_number` | `taxNumber` | string(15) | ❌ | Vergi numarası | `123123123` |
| `tax_office_id` | `taxOfficeId` | int(8) | ❌ | Vergi dairesi ID | `340055` |
| `tax_office_name` | `taxOfficeName` | string(60) | ❌ | Vergi dairesi adı | `Şişli` |
| `org_geo_code` | `orgGeoCode` | string(20) | ❌ | Müşteri adres kodu | `36656` |
| `privilege_order` | `privilegeOrder` | string(10) | ❌ | Ayrıcalıklı gönderim merkezi | `1` |
| `dc_selected_credit` | `dcSelectedCredit` | int(2) | ❌ | Taksit sayısı seçimi | `2` |
| `dc_credit_rule` | `dcCreditRule` | int(2) | ❌ | Kredi kuralı | `1` |
| `email_address` | `emailAddress` | string(200) | ❌ | Alıcı e-posta adresi | `alici@mail.com` |

#### Tahsilatlı Teslimat (Kapıda Ödeme)

**Nakit tahsilat** (`tt_collection_type = "0"`) için zorunlu alanlar:
- `tt_invoice_amount`
- `tt_document_id`
- `tt_document_save_type`

**Kredi kartlı tahsilat** (`tt_collection_type = "1"`) için ek zorunlu alanlar:
- `dc_selected_credit`
- `dc_credit_rule`

```python
# Nakit tahsilatlı gönderi örneği
result = client.create_shipment([
    {
        'cargo_key': 'COD001',
        'invoice_key': 'CODINV001',
        'receiver_cust_name': 'Ali Veli',
        'receiver_address': 'Bağdat Cad. No:100 Kadıköy',
        'receiver_phone1': '05551234567',
        'tt_collection_type': '0',       # Nakit
        'tt_invoice_amount': '150.00',
        'tt_document_id': 'FTR001',
        'tt_document_save_type': '0',    # Aynı fatura
    }
])
```

#### Çalışma Modları

**Fatura Bazlı (İrsaliye Bazlı):**
Her gönderi için bir kayıt iletilir. Her `cargo_key` için bir gönderi düzenlenir.

**Kargo Bazlı (Çoklu Paket):**
Aynı alıcıya birden fazla paket gönderildiğinde, her paket için farklı `cargo_key`, aynı `invoice_key` kullanılır.

```python
# 3 paketli bir gönderi örneği
result = client.create_shipment([
    {
        'cargo_key': '10012',
        'invoice_key': 'A123456',       # Hepsi aynı fatura
        'receiver_cust_name': 'Ali Veli',
        'receiver_address': 'Adres bilgisi',
        'receiver_phone1': '05551234567',
        'waybill_no': 'A123456',
        'cargo_count': 1,
    },
    {
        'cargo_key': '10013',
        'invoice_key': 'A123456',
        'receiver_cust_name': 'Ali Veli',
        'receiver_address': 'Adres bilgisi',
        'receiver_phone1': '05551234567',
        'waybill_no': 'A123456',
        'cargo_count': 1,
    },
    {
        'cargo_key': '10014',
        'invoice_key': 'A123456',
        'receiver_cust_name': 'Ali Veli',
        'receiver_address': 'Adres bilgisi',
        'receiver_phone1': '05551234567',
        'waybill_no': 'A123456',
        'cargo_count': 1,
    },
])
```

#### Sonuç Yapısı — ShipmentResult

| Alan | Tip | Açıklama |
|------|-----|----------|
| `out_flag` | int | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
| `out_result` | str | Sonuç mesajı |
| `job_id` | int | YK talep numarası (başarılı ise) |
| `count` | int | İşlem yapılan gönderi sayısı |
| `details[]` | list | Her gönderi için detay listesi |
| `details[].cargo_key` | str | Kargo anahtarı |
| `details[].invoice_key` | str | Fatura anahtarı |
| `details[].err_code` | int | Hata kodu (0=başarılı) |
| `details[].err_message` | str | Hata mesajı |

---

### 2. cancel_shipment — Gönderi İptal

Web servis ile sisteme gönderilmiş bilgilerin iptal edilmesini ve kargonun çıkışının engellenmesini sağlar.

**SOAP Operasyonu:** `ship:cancelShipment` (parametre: `userLanguage`)

> ⚠️ Gönderi düzenlendikten sonra iptal yapılamaz.

```python
result = client.cancel_shipment(['TEST001', 'TEST002'])

if result.is_success():
    for detail in result.details:
        print(f'{detail.cargo_key}: {detail.operation_message} ({detail.operation_status})')
else:
    print(f'Hata: {result.out_result}')
```

#### İptal Durum Kodları

| operation_status | operation_code | Açıklama |
|------------------|----------------|----------|
| `NOP` | 0 | İşlem yapılmadı, düzenlenmemiş |
| `IND` | 1 | Kargo teslimattadır |
| `ISR` | 2 | Düzenlenmiş, fatura prosedürü tamamlanmamış |
| `CNL` | 3 | Kargo çıkışı engellendi (başarılı iptal) |
| `ISC` | 4 | Kargo zaten iptal edilmiş |

#### Sonuç Yapısı — CancelResult

| Alan | Tip | Açıklama |
|------|-----|----------|
| `out_flag` | int | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
| `out_result` | str | Sonuç mesajı |
| `sender_cust_id` | int | Gönderici müşteri kodu |
| `count` | int | İşlem yapılan gönderi sayısı |
| `details[].cargo_key` | str | Kargo anahtarı |
| `details[].invoice_key` | str | Fatura anahtarı |
| `details[].job_id` | int | YK talep numarası |
| `details[].doc_id` | str | YK gönderi kodu |
| `details[].operation_code` | int | İşlem kodu |
| `details[].operation_message` | str | İşlem mesajı |
| `details[].operation_status` | str | İşlem durumu |
| `details[].err_code` | int | Hata kodu |
| `details[].err_message` | str | Hata mesajı |

---

### 3. query_shipment — Gönderi Sorgulama

Müşterinin kendi referans kodu ile gönderi geçmişini raporlayan servistir. Tek seferde birden fazla gönderi sorgulanabilir.

**SOAP Operasyonu:** `ship:queryShipment` (parametre: `wsLanguage`)

```python
# Cargo Key ile sorgulama
result = client.query_shipment(
    keys=['12520', '12521'],
    key_type=0,                    # 0 = Cargo Key
    add_historical_data=True,      # Hareket geçmişi dahil
    only_tracking=False
)

# Invoice Key ile sorgulama
result = client.query_shipment(
    keys=['A123456'],
    key_type=1                     # 1 = Invoice Key
)

if result.is_success():
    for detail in result.details:
        if detail.is_success():
            print(f'Kargo: {detail.cargo_key}')
            print(f'Durum: {detail.operation_message} ({detail.operation_status})')

            if detail.item_detail:
                item = detail.item_detail
                print(f'Takip: {item.tracking_url}')
                print(f'Alıcı: {item.receiver_cust_name}')
                print(f'Çıkış: {item.departure_unit_name}')
                print(f'Teslim: {item.delivery_date} {item.delivery_time}')

                # Hareket geçmişi
                for event in item.cargo_history:
                    print(f"  → {event['event_date']} {event['event_time']} | "
                          f"{event['unit_name']} | {event['event_name']} | {event['reason_name']}")
        else:
            print(f'Hata [{detail.err_code}]: {detail.err_message}')
```

#### Sorgu Parametreleri

| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| `keys` | list[str] | ✅ | Sorgulanacak anahtar değerleri listesi |
| `key_type` | int | ✅ | 0=Cargo Key, 1=Invoice Key |
| `add_historical_data` | bool | ❌ | Hareket geçmişi dahil edilsin mi? (Performans için `False` önerilir) |
| `only_tracking` | bool | ❌ | Sadece takip URL'si dönsün mü? |

#### Gönderi Durum Kodları

| operation_status | operation_code | Açıklama |
|------------------|----------------|----------|
| `NOP` | 0 | İşlem yapılmadı, düzenlenmemiş |
| `IND` | 1 | Kargo teslimattadır |
| `ISR` | 2 | Düzenlenmiş, fatura prosedürü tamamlanmamış |
| `CNL` | 3 | Çıkış engellendi |
| `ISC` | 4 | İptal edilmiş |
| `DLV` | 5 | Teslim edildi |
| `BI` | 6 | YK acente tarafından iptal edildi |

#### İade Durum Kodları (reject_status)

| Değer | Açıklama |
|-------|----------|
| 0 | İade talebi yapıldı |
| 1 | Çıkış şubesi onayladı |
| 2 | İade bölgesi onayladı |
| 3 | Müşteri onayladı |
| 4 | İade beklemede |
| 7 | Teslimat iptal edildi |
| 8 | Borçlandırma iptal edildi |
| 9 | İade yapıldı |
| 10 | İade sonlandırıldı |
| 11 | İade onaylanmadı |

> 📌 `reject_status` 0, 1, 2, 3, 9, 10 → İade süreci devam ediyor  
> 📌 `reject_status` 4, 7, 8, 11 → İade iptal edildi, normal süreç başladı

#### Sonuç Yapısı — QueryResult

| Alan | Tip | Açıklama |
|------|-----|----------|
| `out_flag` | int | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
| `out_result` | str | Sonuç mesajı |
| `count` | int | İşlem yapılan gönderi sayısı |
| `details[].cargo_key` | str | Kargo anahtarı |
| `details[].operation_code` | int | İşlem kodu |
| `details[].operation_message` | str | İşlem mesajı |
| `details[].operation_status` | str | İşlem durumu |
| `details[].item_detail` | object | Gönderi detay bilgisi |
| `details[].item_detail.tracking_url` | str | Takip linki |
| `details[].item_detail.receiver_cust_name` | str | Alıcı adı |
| `details[].item_detail.departure_unit_name` | str | Çıkış birimi |
| `details[].item_detail.delivery_date` | str | Teslim tarihi |
| `details[].item_detail.delivery_time` | str | Teslim saati |
| `details[].item_detail.cargo_history[]` | list | Hareket geçmişi |

---

### 4. save_return_shipment_code — İade Kodu Oluşturma

İade müşterilerinin YK birimine ileterek iade işlemini tamamlayacakları kodu oluşturan servistir.

**SOAP Operasyonu:** `ship:saveReturnShipmentCode` (parametre: `wsLanguage`)

```python
result = client.save_return_shipment_code(
    return_code='RMA-2024-001',   # Sizin belirlediğiniz iade kodu
    start_date='20240101',         # Geçerlilik başlangıç (YYYYMMDD)
    end_date='20240131',           # Geçerlilik bitiş (YYYYMMDD)
    max_count=1,                   # Kullanım adedi
    field_name='53'                # Test ortamında 53 veya 3; canlıda 16
)

if result.is_success():
    print('İade kodu başarıyla oluşturuldu!')
else:
    print(f'Hata [{result.err_code}]: {result.out_result}')
```

#### Parametreler

| Parametre | Tip | Zorunlu | Açıklama | Örnek |
|-----------|-----|---------|----------|-------|
| `return_code` | str | ✅ | İade kodu (benzersiz değer) | `RMA-2024-001` |
| `start_date` | str | ✅ | Kod geçerlilik başlangıç tarihi (YYYYMMDD) | `20240101` |
| `end_date` | str | ✅ | Kod geçerlilik bitiş tarihi (YYYYMMDD) | `20240131` |
| `max_count` | int | ✅ | İade kodu kullanım adedi | `1` |
| `field_name` | str | ✅ | Özel alan bilgisi | Test: `53` veya `3`, Canlı: `16` |

> ⚠️ **Not:** Test ortamında `field_name` olarak `53` veya `3` kullanın. Canlı ortamda sözleşmenize özel `16` değeri tanımlanacaktır.

#### Sonuç Yapısı — ReturnCodeResult

| Alan | Tip | Açıklama |
|------|-----|----------|
| `out_flag` | int | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
| `out_result` | str | Sonuç mesajı |
| `err_code` | int | Hata kodu (0=başarılı) |

---

## Python ↔ SOAP Alan Eşleştirme (Field Mapping)

Python `snake_case` parametreleri otomatik olarak SOAP `camelCase` formatına dönüştürülür:

| Python (snake_case) | SOAP (camelCase) |
|---------------------|------------------|
| `cargo_key` | `cargoKey` |
| `invoice_key` | `invoiceKey` |
| `receiver_cust_name` | `receiverCustName` |
| `receiver_address` | `receiverAddress` |
| `receiver_phone1` | `receiverPhone1` |
| `receiver_phone2` | `receiverPhone2` |
| `receiver_phone3` | `receiverPhone3` |
| `city_name` | `cityName` |
| `town_name` | `townName` |
| `cust_prod_id` | `custProdId` |
| `cargo_count` | `cargoCount` |
| `waybill_no` | `waybillNo` |
| `special_field1` | `specialField1` |
| `special_field2` | `specialField2` |
| `special_field3` | `specialField3` |
| `tt_collection_type` | `ttCollectionType` |
| `tt_invoice_amount` | `ttInvoiceAmount` |
| `tt_document_id` | `ttDocumentId` |
| `tt_document_save_type` | `ttDocumentSaveType` |
| `org_receiver_cust_id` | `orgReceiverCustId` |
| `tax_number` | `taxNumber` |
| `tax_office_id` | `taxOfficeId` |
| `tax_office_name` | `taxOfficeName` |
| `org_geo_code` | `orgGeoCode` |
| `privilege_order` | `privilegeOrder` |
| `dc_selected_credit` | `dcSelectedCredit` |
| `dc_credit_rule` | `dcCreditRule` |
| `email_address` | `emailAddress` |

---

## Dataclass Sonuç Modelleri

Tüm API çağrıları `dataclass` tabanlı sonuç nesneleri döndürür:

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ShipmentResult:
    out_flag: int              # 0=Başarılı, 1=Hata, 2=Beklenmeyen
    out_result: str            # Sonuç mesajı
    job_id: Optional[int]      # YK talep numarası
    count: int                 # İşlem sayısı
    details: list              # Gönderi detayları

    def is_success(self) -> bool:
        return self.out_flag == 0

    def get_errors(self) -> list:
        return [d for d in self.details if d.err_code != 0]

@dataclass
class CancelResult:
    out_flag: int
    out_result: str
    sender_cust_id: Optional[int]
    count: int
    details: list

    def is_success(self) -> bool:
        return self.out_flag == 0

@dataclass
class QueryResult:
    out_flag: int
    out_result: str
    count: int
    details: list

    def is_success(self) -> bool:
        return self.out_flag == 0

@dataclass
class ReturnCodeResult:
    out_flag: int
    out_result: str
    err_code: Optional[int]

    def is_success(self) -> bool:
        return self.out_flag == 0
```

---

## Özel Alan Bilgileri (special_field1)

`special_field1` alanına birden fazla özel alan bilgisi gönderilebilir.

**Format:** `alan_no$deger#alan_no$deger#`

**Örnek:**
```python
'special_field1': '1$426031#2$397427#'
```

### Özel Alan Numaraları

| Alan No | Açıklama | Alan No | Açıklama |
|---------|----------|---------|----------|
| 2 | Müşteri Seri No | 12 | Masraf Kodu |
| 3 | Sipariş No | 13 | Ürün |
| 4 | Poşet No | 14 | Müşteri Kargo Ref Kodu |
| 5 | Ambalaj No | 16 | İade Onay Kodu |
| 6 | Müşteri Kimlik No | 51 | Dergi Türü |
| 7 | Müşteri Ad Soyad | 52 | Temsilci No |
| 8 | Bölge | 53 | Anahtar Alan |
| 9 | Departman/Personel İsmi | 54 | Sevk İrsaliye No |
| 10 | Cep Tel | 55 | Alıcı Vergi No |
| 11 | Poliçe No | 56 | Takım Öncüsü Temsilci No |

---

## Hata Kodları

### createShipment Hata Kodları

| Kod | Mesaj | Açıklama |
|-----|-------|----------|
| 0 | Başarılı | İşlem başarıyla tamamlandı |
| 936 | Beklenmeyen hata | YK Bilgi Sistemleri ile iletişime geçin |
| 80859 | ERR_INTG_CARGO_KEY_PARAM_NOT_FOUND | Kargo anahtarı bulunamadı |
| 82500 | ERR_INTG_CARGO_KEY_PARAM_LENGHT | Kargo anahtarı uzunluk aşımı |
| 60020 | ERR_EXIST_CARGO_KEY_PARAM | Kargo anahtarı sistemde mevcut |
| 80057 | MSG_JOB_ID_NOT_FOUND | YK talep numarası bulunamadı |
| 60017 | ERR_INTG_INVOICE_KEY_PARAM_NOT_FOUND | Fatura anahtarı bulunamadı |
| 82501 | ERR_INTG_INVOICE_KEY_PARAM_LENGHT | Fatura anahtarı uzunluk aşımı |
| 60018 | ERR_INTG_RECEIVER_CUST_NAME_PARAM_NOT_FOUND | Alıcı müşteri adı bulunamadı |
| 82503 | ERR_INTG_RECEIVER_CUST_NAME_PARAM_LENGHT | Alıcı adı uzunluk aşımı |
| 60019 | ERR_INTG_RECEIVER_ADDRESS_PARAM_NOT_FOUND | Alıcı adresi bulunamadı |
| 82502 | ERR_INTG_RECEIVER_ADDRESS_PARAM_LENGHT | Alıcı adresi uzunluk aşımı |
| 82505 | ERR_INTG_TT_INVOICE_AMOUNT_PARAM_NOT_FOUND | Tahsilat tutarı bulunamadı |
| 82506 | ERR_INTG_TT_INVOICE_AMOUNT_PARAM_LENGHT | Tahsilat tutarı uzunluk aşımı |
| 82507 | ERR_INTG_TT_DOCUMENT_ID_PARAM_NOT_FOUND | Tahsilat belge no bulunamadı |
| 82508 | ERR_INTG_TT_DOCUMENT_ID_PARAM_LENGHT | Tahsilat belge no uzunluk aşımı |
| 82509 | ERR_INTG_DC_SELECTED_CREDIT_NOT_FOUND | Taksit seçimi bulunamadı |
| 82510 | ERR_INTG_DC_SELECTED_CREDIT_PARAM_LENGHT | Taksit seçimi uzunluk aşımı |
| 82511 | ERR_INTG_DC_CREDIT_RULE_NOT_FOUND | Kredi kuralı bulunamadı |
| 82512 | ERR_INTG_DC_COLL_CC_WRONG_PARAMETER | Müşteri anlaşması ödeme tipi uyuşmuyor |
| 82513 | ERR_INTG_TT_COLL_TYPE | Hatalı ödeme tipi (0=nakit, 1=kredi kartı) |
| 82514 | ERR_INTG_TT_DOC_SAVE_TYPE | Hatalı belge kayıt tipi (0=aynı, 1=ayrı) |
| 82515 | ERR_INTG_EMAIL_ADDRESS_INVALID_PARAMETER | Geçersiz e-posta adresi |
| 82516 | ERR_INTG_RECEIVER_PHONE_INVALID_PARAMETER | Geçersiz telefon numarası |
| 82517 | ERR_INTG_INVALID_PARAMETER | Geçersiz format bilgisi |
| 82518 | ERR_INTG_DC_CREDIT_RULE_WRONG_PARAMETER | Kredi kuralı hatalı parametre |

### cancelShipment Hata Kodları

| Kod | Mesaj | Açıklama |
|-----|-------|----------|
| 0 | Başarılı | İşlem başarılı |
| 936 | Beklenmeyen hata | YK Bilgi Sistemleri ile iletişime geçin |
| 82519 | ERR_INTG_CARGO_KEY_NOT_FOUND | Kullanıcıya ait kargo anahtarı bulunamadı |
| 82520 | ERR_INTG_CARGO_KEY_OPERATION_CANCELLED | Kargo anahtarı daha önceden iptal edilmiş |

### queryShipment Hata Kodları

| Kod | Mesaj | Açıklama |
|-----|-------|----------|
| 0 | Başarılı | İşlem başarılı |
| 936 | Bilinmeyen hata | YK IT ile iletişime geçin |
| 82527 | ERR_INTG_KEY_TYPE_NOT_FOUND | KEY_TYPE parametresi boş veya eksik |
| 82526 | ERR_INTG_KEYS_NOT_FOUND | KEYS parametresi boş veya eksik |

### saveReturnShipmentCode Hata Kodları

| Kod | Mesaj | Açıklama |
|-----|-------|----------|
| 0 | Başarılı | İşlem başarılı |
| 80063 | Başlangıç tarihi girilmedi | |
| 82651 | İade kodu boş olamaz | |
| 82652 | İade koduna ait kullanım adedi boş olamaz | |
| 82653 | İade kodu xx adetten fazla kullanılamaz | |
| 82654 | FieldName bilgisi geçersizdir | |
| 82655 | İade kodu daha önceden kaydedilmiştir | |
| 82656 | İade kodu sistemde bulunmamaktadır | |
| 60109 | Özel alan adı boş bırakılmamalıdır | |
| 60027 | Bitiş tarih kriteri zorunludur | |
| 60026 | Başlangıç tarih kriteri zorunludur | |
| 80838 | Tarih aralığı maksimum yy gün olabilir | |

---

## Entegrasyon Akışı

### Giden Kargo Akışı

```
1. create_shipment ile gönderi bilgileri YK sistemine iletilir
2. Kargo anahtarı (cargo_key) fiziksel olarak kargo üzerinde bulunmalıdır
3. Gönderi düzenlenmeden önce cancel_shipment ile iptal edilebilir
4. YK şubesi kargo anahtarını okuyarak sisteme girer
5. Alıcı bilgileri ekranda görünür
6. YK şubesi sevkiyat adresini belirler
7. Kargo adedi ve taşıma adresi girilerek YK irsaliyesi oluşturulur
8. Müşteri gönderisi ile YK taşıma belgesi eşleştirilir
9. query_shipment ile teslimat durumu sorgulanabilir
```

### İade Kodu Akışı

```
1. save_return_shipment_code ile iade kodu oluşturulur
2. İade kodu müşteriye iletilir
3. Müşteri bu kodu YK birimine ileterek iade işlemini başlatır
```

---

## Parametrik Raporlama (Takip Linki)

Entegrasyon gönderileriniz için parametrik takip linki oluşturabilirsiniz:

```
http://selfservis.yurticikargo.com/reports/SswReportsFromParamFields.aspx?ssfldvn=XX&sskurkod=MUSTERI_KODU&refnumber=REFERANS_NO&date=GG.AA.YYYY
```

| Parametre | Açıklama |
|-----------|----------|
| `ssfldvn` | Özel alan adı (yukarıdaki tablodaki değerler) |
| `sskurkod` | YK müşteri kodu |
| `refnumber` | Takip edilecek özel alan değeri |
| `date` | Gönderi tarihi (dd.mm.yyyy, ±5 gün tolerans) |

**Python ile link oluşturma:**

```python
from urllib.parse import urlencode

params = {
    'ssfldvn': '53',
    'sskurkod': 'MUSTERI_KODU',
    'refnumber': 'REF001',
    'date': '15.01.2024',
}
base_url = 'http://selfservis.yurticikargo.com/reports/SswReportsFromParamFields.aspx'
tracking_url = f'{base_url}?{urlencode(params)}'
print(tracking_url)
```

---

## Debug

```python
# Son SOAP isteğini görüntüle
print(client.get_last_request())

# Son SOAP yanıtını görüntüle
print(client.get_last_response())
```

---

## IP Yetkilendirme

Yurtiçi Kargo web servislerine erişim için IP yetkilendirmesi zorunludur.

> ⚠️ Canlı ortama geçmeden önce sunucu çıkış IP adresinizi **Bölge Müdürlüğü Satış Temsilcinize** bildirmeniz gerekmektedir.

Test ortamı için IP yetkilendirmesi gerekmez.

---

## SOAP Endpoint Bilgileri

| Ortam | Endpoint |
|-------|----------|
| Test | `https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl` |
| Canlı | `https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl` |

### SOAP Operasyonları

| Metod | SOAP Action | Dil Parametresi |
|-------|-------------|-----------------|
| `create_shipment` | `ship:createShipment` | `userLanguage` |
| `cancel_shipment` | `ship:cancelShipment` | `userLanguage` |
| `query_shipment` | `ship:queryShipment` | `wsLanguage` |
| `save_return_shipment_code` | `ship:saveReturnShipmentCode` | `wsLanguage` |

---

## Tam Kullanım Örneği

```python
from yurticikargo_client import YurticiKargoClient

# Client oluştur
client = YurticiKargoClient('YKTEST', 'YK', 'TR', test_mode=True)

# 1. Gönderi oluştur
shipment_result = client.create_shipment([
    {
        'cargo_key': 'PY-2024-001',
        'invoice_key': 'PYINV-001',
        'receiver_cust_name': 'Ahmet Yılmaz',
        'receiver_address': 'Atatürk Mah. Cumhuriyet Cad. No:42 Kadıköy',
        'receiver_phone1': '05321234567',
        'city_name': 'Istanbul',
        'town_name': 'Kadikoy',
        'description': 'Python API test gönderisi',
    }
])

if shipment_result.is_success():
    print(f'✅ Gönderi oluşturuldu! Job ID: {shipment_result.job_id}')

    # 2. Gönderi sorgula
    query_result = client.query_shipment(
        keys=['PY-2024-001'],
        key_type=0,
        add_historical_data=True
    )

    if query_result.is_success():
        for detail in query_result.details:
            print(f'📦 Durum: {detail.operation_message}')
else:
    print(f'❌ Hata: {shipment_result.out_result}')

    # 3. Gerekirse iptal et
    cancel_result = client.cancel_shipment(['PY-2024-001'])
    if cancel_result.is_success():
        print('🗑️ Gönderi iptal edildi')

# 4. İade kodu oluştur
return_result = client.save_return_shipment_code(
    return_code='RMA-PY-001',
    start_date='20240101',
    end_date='20240201',
    max_count=1,
    field_name='53'
)

if return_result.is_success():
    print('↩️ İade kodu oluşturuldu')
```

---

## Sık Karşılaşılan Sorunlar ve Çözümleri

### 1. "Could not connect to host" / Bağlantı Hatası
**Sorun:** SOAP servise bağlanılamıyor.
**Olası Nedenler:**
- IP yetkilendirmesi yapılmamış (canlı ortam)
- Firewall/proxy engeli
- SSL sertifika doğrulama hatası
- DNS çözümleme sorunu
- Servis geçici olarak erişilemez

**Çözüm:**
- Canlı ortam için IP adresinizi Bölge Müdürlüğü'ne bildirin
- Kurumsal ağda proxy ayarlarını kontrol edin
- SSL verification'ı devre dışı bırakın (sadece test için)
- `telnet testws.yurticikargo.com 443` ile bağlantı test edin
- VPN kullanıyorsanız doğrudan bağlantı deneyin

### 2. "Web servis kullanıcı dili boş olamaz" Hatası
**Sorun:** Dil parametresi servis tarafında alınamıyor.
**Neden:** Yanlış parametre adı kullanılıyor.
**Çözüm:**
- `createShipment` ve `cancelShipment` → `userLanguage` kullanın
- `queryShipment` ve `saveReturnShipmentCode` → `wsLanguage` kullanın
- Bu iki farklı parametre adı Yurtiçi Kargo API'sinin tasarım farkıdır

### 3. "CARGO_KEY sistemde mevcuttur" (Hata 60020)
**Sorun:** Aynı cargoKey ile tekrar gönderi oluşturulmaya çalışılıyor.
**Çözüm:**
- Her gönderi için benzersiz cargoKey kullanın (timestamp, UUID vb.)
- Test ortamında cargoKey'ler kalıcıdır, her test için yeni key üretin
- Ör: `f'TEST-{int(time.time())}'` veya `str(uuid.uuid4())[:20]`

### 4. "RECEIVER_ADDRESS parametresi min: 10 max: 500 uzunluğunda olmalıdır" (Hata 82502)
**Sorun:** Adres alanı çok kısa veya çok uzun.
**Çözüm:**
- Adres en az 10 karakter olmalıdır
- En fazla 500 karakter olmalıdır
- Kısa adreslere ilçe/şehir ekleyerek uzatın

### 5. "Sözleşme Üzerinde Tanımlı Özel Alan Bilgisi Bulunamadı"
**Sorun:** saveReturnShipmentCode'da fieldName değeri geçersiz.
**Çözüm:**
- Test ortamında `fieldName` olarak `'53'` veya `'3'` kullanın
- Canlı ortamda `'16'` kullanın (sözleşmeye özel tanımlanır)
- YKTEST hesabında bu fonksiyon kısıtlıdır, SOAP iletişimi doğruysa sorun yoktur

### 6. "Başlangıç Tarih kriteri zorunludur" (Hata 60026)
**Sorun:** saveReturnShipmentCode tarih formatı yanlış.
**Çözüm:**
- Tarih formatı kesinlikle `YYYYMMDD` olmalıdır (ör: `20240115`)
- Tire, nokta veya slash kullanmayın
- Geçmiş tarih kabul edilmez, gelecek tarih kullanın

### 7. Timeout Sorunları
**Sorun:** İstek zaman aşımına uğruyor.
**Çözüm:**
- connection_timeout değerini artırın (varsayılan 30 saniye)
- Toplu gönderilerde (>50 kayıt) parçalara bölün
- Ağ gecikmesi yüksekse retry mekanizması ekleyin
- Peak saatlerde (09:00-18:00) yoğunluk olabilir

### 8. Karakter Encoding Sorunları (Türkçe karakterler)
**Sorun:** Türkçe karakterler (ç, ş, ğ, ü, ö, ı, İ) bozuk görünüyor.
**Çözüm:**
- SOAP isteğinde encoding `UTF-8` olarak belirtin
- XML header: `<?xml version="1.0" encoding="UTF-8"?>`
- HTTP header: `Content-Type: text/xml; charset=utf-8`
- Kaynak dosyalarınızı UTF-8 olarak kaydedin

### 9. "Kargo Teslimattadır" - İptal Edilemiyor
**Sorun:** cancelShipment operationStatus=IND dönüyor.
**Çözüm:**
- Kargo YK şubesine teslim edildikten ve düzenlendikten sonra iptal yapılamaz
- Sadece düzenlenmemiş (NOP/ISR) gönderiler iptal edilebilir
- Düzenlenmiş gönderiler için iade süreci başlatın (saveReturnShipmentCode)

### 10. queryShipment Boş Detay Dönüyor
**Sorun:** Sorgu başarılı ama itemDetail null/boş.
**Çözüm:**
- Gönderi henüz düzenlenmemişse (NOP) detay bilgisi olmaz
- Gönderi oluşturulduktan sonra YK şubesinin düzenlemesini bekleyin
- `addHistoricalData: false` olduğunda hareket geçmişi gelmez
- Yeni oluşturulan gönderi birkaç dakika içinde sorgulanabilir hale gelir

### 11. Tahsilatlı Teslimat Hataları
**Sorun:** ttCollectionType set edildiğinde ek hatalar.
**Çözüm:**
- Nakit (ttCollectionType=0): `ttInvoiceAmount`, `ttDocumentId`, `ttDocumentSaveType` zorunlu
- Kredi Kartı (ttCollectionType=1): Ek olarak `dcSelectedCredit`, `dcCreditRule` de zorunlu
- `ttInvoiceAmount` ayracı `.` (nokta) olmalı, virgül kullanmayın
- `ttDocumentSaveType`: 0=aynı fatura, 1=ayrı fatura

### 12. Çoklu Paket (Kargo Bazlı) Gönderimde Hata
**Sorun:** Aynı alıcıya birden fazla paket gönderirken sorun.
**Çözüm:**
- Her paket için FARKLI `cargoKey` kullanın
- Tüm paketler için AYNI `invoiceKey` kullanın
- Her pakete `cargoCount: 1` verin
- Alıcı bilgileri (ad, adres, telefon) tüm paketlerde aynı olmalı

### 13. IP Değişikliği Sonrası Erişim Sorunu
**Sorun:** Daha önce çalışan servis aniden erişilemez.
**Çözüm:**
- Sunucu IP'niz değiştiyse (cloud, dynamic IP) yeni IP'yi bildirin
- Birden fazla IP kullanıyorsanız hepsini yetkilendirin
- Test ortamı IP kısıtlaması yoktur, sorun canlıda ise IP kontrolü yapın

### 14. WSDL Yükleme Hatası
**Sorun:** WSDL dosyası yüklenemiyor.
**Çözüm:**
- WSDL URL'ini tarayıcıda açarak erişilebilirliği kontrol edin
- Kurumsal proxy varsa proxy ayarlarını yapın
- WSDL cache'ini temizleyin
- Offline çalışma için WSDL'yi lokal dosya olarak indirin

### 15. "HTTP 500" SOAP Fault
**Sorun:** Servis internal server error dönüyor.
**Çözüm:**
- SOAP XML yapısının doğruluğunu kontrol edin (namespace, tag isimleri)
- Method adlarını doğrulayın: `createShipment`, `cancelShipment`, `queryShipment`, `saveReturnShipmentCode`
- SOAP namespace: `http://yurticikargo.com.tr/ShippingOrderDispatcherServices`
- Endpoint URL'de `?wsdl` OLMAMALIDIR (POST hedefi)

### 16. Python: ssl.SSLCertVerificationError
**Sorun:** SSL sertifika doğrulama hatası alınıyor.
**Çözüm:** Test ortamında SSL doğrulamayı devre dışı bırakın:
```python
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# urllib ile kullanım
import urllib.request
opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=ctx)
)
```
> ⚠️ Bu ayarı sadece test ortamında kullanın. Canlı ortamda sertifika doğrulaması aktif olmalıdır.

### 17. Python: urllib.error.URLError: urlopen error [Errno 11001]
**Sorun:** DNS çözümleme hatası — host adı çözümlenemiyor.
**Çözüm:**
- İnternet bağlantınızı kontrol edin
- `nslookup testws.yurticikargo.com` ile DNS çözümleme testi yapın
- Proxy arkasındaysanız proxy ayarlarını yapın:
```python
import urllib.request

proxy_handler = urllib.request.ProxyHandler({
    'https': 'http://proxy.sirket.com:8080'
})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)
```

### 18. Python: UnicodeEncodeError
**Sorun:** Türkçe karakterler gönderilirken encoding hatası alınıyor.
**Çözüm:** Tüm string'lerin UTF-8 olarak encode edildiğinden emin olun:
```python
# XML body oluşturulurken
xml_body = soap_envelope.encode('utf-8')

# Dosya okurken
with open('data.txt', 'r', encoding='utf-8') as f:
    content = f.read()
```

---

## Lisans

MIT
