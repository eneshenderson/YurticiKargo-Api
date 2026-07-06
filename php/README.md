# Yurtiçi Kargo PHP API Client

Yurtiçi Kargo SOAP Web Service entegrasyonu için PHP istemci kütüphanesi.

---

## Gereksinimler

- PHP >= 8.0
- PHP SOAP Extension (`ext-soap`)
- PHP OpenSSL Extension (`ext-openssl`)

---

## Kurulum

Manuel kurulum ile dosyaları projenize dahil edin:

```php
// Controller yaklaşımı (önerilen)
require_once 'YurticiKargoClient.php';

// veya tek dosya yaklaşımı
require_once 'YurticiKargoAllInOne.php';
```

---

## Proje Yapısı

```
php/
├── functions/
│   ├── CreateShipment.php          # Gönderi oluşturma fonksiyonu
│   ├── CancelShipment.php          # Gönderi iptal fonksiyonu
│   ├── QueryShipment.php           # Gönderi sorgulama fonksiyonu
│   └── SaveReturnShipmentCode.php  # İade kodu oluşturma fonksiyonu
├── YurticiKargoClient.php          # Ana controller sınıfı
├── tests/
│   ├── CreateShipmentTest.php      # Gönderi oluşturma testi
│   ├── CancelShipmentTest.php      # Gönderi iptal testi
│   ├── QueryShipmentTest.php       # Gönderi sorgulama testi
│   └── SaveReturnShipmentCodeTest.php  # İade kodu testi
└── YurticiKargoAllInOne.php        # Tüm fonksiyonları içeren tek dosya
```

---

## Hızlı Başlangıç

### Controller ile (Modüler Yaklaşım)

```php
<?php
require_once 'YurticiKargoClient.php';

$client = new YurticiKargoClient(
    username: 'YKTEST',
    password: 'YK',
    language: 'TR',
    testMode: true
);
```

### AllInOne ile (Tek Dosya Yaklaşımı)

```php
<?php
require_once 'YurticiKargoAllInOne.php';

$client = new YurticiKargoAllInOne('YKTEST', 'YK', 'TR', true);
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

## API Metodları

### 1. createShipment — Gönderi Oluşturma

Müşterinin kargo bilgilerini Yurtiçi Kargo sistemine ileten servistir.

#### Kullanım

```php
$result = $client->createShipment([
    [
        'cargoKey'         => 'TEST001',
        'invoiceKey'       => 'INV001',
        'receiverCustName' => 'Mehmet Yılmaz',
        'receiverAddress'  => 'Eski Büyükdere Cad. No:3 Maslak',
        'receiverPhone1'   => '05321234567',
        'cityName'         => 'İstanbul',
        'townName'         => 'Sarıyer',
    ]
]);

if ($result->isSuccess()) {
    echo "Başarılı! Job ID: {$result->jobId}\n";
    foreach ($result->details as $detail) {
        echo "Cargo Key: {$detail->cargoKey} - Durum: {$detail->errMessage}\n";
    }
} else {
    echo "Hata: {$result->outResult}\n";
    foreach ($result->getErrors() as $error) {
        echo "  [{$error->errCode}] {$error->errMessage}\n";
    }
}
```

#### Zorunlu Parametreler

| Parametre | Tip | Maks. Uzunluk | Açıklama | Örnek |
|-----------|-----|---------------|----------|-------|
| `cargoKey` | string | 20 | Benzersiz kargo anahtarı | `TEST001` |
| `invoiceKey` | string | 20 | Fatura anahtarı | `INV001` |
| `receiverCustName` | string | 100 | Alıcı müşteri adı | `Mehmet Yılmaz` |
| `receiverAddress` | string | 500 | Alıcı adresi | `Eski Büyükdere Cad. No:3` |
| `receiverPhone1` | string | 20 | Alıcı telefon numarası | `05321234567` |

#### Opsiyonel Parametreler

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `receiverPhone2` | string(20) | Alıcı telefon 2 |
| `receiverPhone3` | string(20) | Alıcı telefon 3 |
| `cityName` | string(40) | Alıcı şehir |
| `townName` | string(40) | Alıcı ilçe |
| `custProdId` | string | Ürün kodu |
| `desi` | float(9,3) | Kargo desi bilgisi |
| `kg` | float(9,3) | Kargo kg bilgisi |
| `cargoCount` | int(4) | Gönderilen kargo adedi |
| `waybillNo` | string(20) | Müşteri irsaliye numarası |
| `specialField1` | string(200) | Özel alan 1 (format: `numara$deger#`) |
| `specialField2` | string(100) | Özel alan 2 |
| `specialField3` | string(100) | Özel alan 3 |
| `ttCollectionType` | string(1) | Tahsilat ödeme tipi: `0`=Nakit, `1`=Kredi Kartı |
| `ttInvoiceAmount` | float(18,2) | Tahsilat tutarı (ayraç `.` nokta) |
| `ttDocumentId` | string(12) | Tahsilat belge numarası |
| `ttDocumentSaveType` | string(1) | Fatura tipi: `0`=Aynı, `1`=Ayrı |
| `orgReceiverCustId` | string(50) | Alıcı müşteri kodu |
| `description` | string(255) | Serbest açıklama |
| `taxNumber` | string(15) | Vergi numarası |
| `taxOfficeId` | int(8) | Vergi dairesi ID |
| `taxOfficeName` | string(60) | Vergi dairesi adı |
| `orgGeoCode` | string(20) | Müşteri adres kodu |
| `privilegeOrder` | string(10) | Ayrıcalıklı gönderim merkezi |
| `dcSelectedCredit` | int(2) | Taksit sayısı seçimi |
| `dcCreditRule` | int(2) | Kredi kuralı: `0`=Anlaşmalı banka, `1`=Tek çekim |
| `emailAddress` | string(200) | Alıcı e-posta adresi |

#### Tahsilatlı Teslimat (Kapıda Ödeme)

**Nakit tahsilat** (`ttCollectionType = "0"`) için zorunlu alanlar:
- `ttInvoiceAmount` — Tahsilat tutarı
- `ttDocumentId` — Belge numarası
- `ttDocumentSaveType` — Belge kayıt tipi

**Kredi kartlı tahsilat** (`ttCollectionType = "1"`) için ek zorunlu alanlar:
- `dcSelectedCredit` — Taksit sayısı
- `dcCreditRule` — Kredi kuralı

#### Kargo Bazlı Çalışma (Çoklu Paket)

Aynı alıcıya birden fazla paket gönderildiğinde, her paket için farklı `cargoKey`, aynı `invoiceKey` kullanılır:

```php
$result = $client->createShipment([
    [
        'cargoKey'         => '10012',
        'invoiceKey'       => 'A123456',  // Hepsi aynı fatura
        'receiverCustName' => 'Ali Veli',
        'receiverAddress'  => 'Adres bilgisi',
        'receiverPhone1'   => '05551234567',
        'waybillNo'        => 'A123456',
        'cargoCount'       => 1,
    ],
    [
        'cargoKey'         => '10013',
        'invoiceKey'       => 'A123456',
        'receiverCustName' => 'Ali Veli',
        'receiverAddress'  => 'Adres bilgisi',
        'receiverPhone1'   => '05551234567',
        'waybillNo'        => 'A123456',
        'cargoCount'       => 1,
    ],
    [
        'cargoKey'         => '10014',
        'invoiceKey'       => 'A123456',
        'receiverCustName' => 'Ali Veli',
        'receiverAddress'  => 'Adres bilgisi',
        'receiverPhone1'   => '05551234567',
        'waybillNo'        => 'A123456',
        'cargoCount'       => 1,
    ],
]);
```

#### Sonuç Yapısı (ShipmentResult)

| Alan | Tip | Açıklama |
|------|-----|----------|
| `outFlag` | int | `0`=Başarılı, `1`=Hata, `2`=Beklenmeyen hata |
| `outResult` | string | Sonuç mesajı |
| `jobId` | int | YK talep numarası (başarılı ise) |
| `count` | int | İşlem yapılan gönderi sayısı |
| `details[]` | array | Her gönderi için detay |
| `details[].cargoKey` | string | Kargo anahtarı |
| `details[].invoiceKey` | string | Fatura anahtarı |
| `details[].errCode` | int | Hata kodu (0=başarılı) |
| `details[].errMessage` | string | Hata mesajı |

---

### 2. cancelShipment — Gönderi İptal

Web servis ile sisteme gönderilmiş bilgilerin iptal edilmesini ve kargonun çıkışının engellenmesini sağlar.

> ⚠️ **Önemli:** Gönderi düzenlendikten sonra iptal yapılamaz.

#### Kullanım

```php
$result = $client->cancelShipment(['TEST001', 'TEST002']);

if ($result->isSuccess()) {
    foreach ($result->details as $d) {
        echo "{$d->cargoKey}: {$d->operationMessage} ({$d->operationStatus})\n";
    }
} else {
    echo "Hata: {$result->outResult}\n";
}
```

#### İptal Durum Kodları

| operationStatus | operationCode | Açıklama |
|-----------------|---------------|----------|
| `NOP` | 0 | İşlem yapılmadı, düzenlenmemiş |
| `IND` | 1 | Kargo teslimattadır |
| `ISR` | 2 | Düzenlenmiş, fatura prosedürü tamamlanmamış |
| `CNL` | 3 | Kargo çıkışı engellendi (başarılı iptal) |
| `ISC` | 4 | Kargo zaten iptal edilmiş |
| `DLV` | 5 | Teslim edildi |
| `BI` | 6 | YK acente tarafından iptal edildi |

#### Sonuç Yapısı (CancelResult)

| Alan | Tip | Açıklama |
|------|-----|----------|
| `outFlag` | int | `0`=Başarılı, `1`=Hata, `2`=Beklenmeyen hata |
| `outResult` | string | Sonuç mesajı |
| `senderCustId` | int | Gönderici müşteri kodu |
| `count` | int | İşlem yapılan gönderi sayısı |
| `details[].cargoKey` | string | Kargo anahtarı |
| `details[].invoiceKey` | string | Fatura anahtarı |
| `details[].jobId` | int | YK talep numarası |
| `details[].docId` | string | YK gönderi kodu |
| `details[].operationCode` | int | İşlem kodu |
| `details[].operationMessage` | string | İşlem mesajı |
| `details[].operationStatus` | string | İşlem durumu |
| `details[].errCode` | int | Hata kodu |
| `details[].errMessage` | string | Hata mesajı |

---

### 3. queryShipment — Gönderi Sorgulama

Müşterinin kendi referans kodu ile gönderi geçmişini raporlayan servistir. Tek seferde birden fazla gönderi sorgulanabilir.

#### Kullanım

```php
// Cargo Key ile sorgulama
$result = $client->queryShipment(
    keys: ['TEST001'],
    keyType: 0,                    // 0 = Cargo Key
    addHistoricalData: true,       // Hareket geçmişi dahil
    onlyTracking: false
);

// Invoice Key ile sorgulama
$result = $client->queryShipment(
    keys: ['A123456'],
    keyType: 1                     // 1 = Invoice Key
);

if ($result->isSuccess()) {
    foreach ($result->details as $d) {
        if ($d->isSuccess()) {
            echo "Kargo: {$d->cargoKey}\n";
            echo "Durum: {$d->operationMessage} ({$d->operationStatus})\n";

            if (isset($d->itemDetail)) {
                $item = $d->itemDetail;
                echo "Takip: {$item->trackingUrl}\n";
                echo "Alıcı: {$item->receiverCustName}\n";
                echo "Çıkış: {$item->departureUnitName}\n";
                echo "Teslim: {$item->deliveryDate} {$item->deliveryTime}\n";

                // Hareket geçmişi
                foreach ($item->cargoHistory as $event) {
                    echo "  → {$event['eventDate']} {$event['eventTime']} | ";
                    echo "{$event['unitName']} | {$event['eventName']} | {$event['reasonName']}\n";
                }
            }
        } else {
            echo "Hata [{$d->errCode}]: {$d->errMessage}\n";
        }
    }
}
```

#### Sorgu Parametreleri

| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| `keys` | array | ✅ | Sorgulanacak anahtar değerleri dizisi |
| `keyType` | int | ✅ | `0`=Cargo Key, `1`=Invoice Key |
| `addHistoricalData` | bool | ❌ | Hareket geçmişi dahil edilsin mi? (Performans için `false` önerilir) |
| `onlyTracking` | bool | ❌ | Sadece takip URL'si dönsün mü? |

#### Gönderi Durum Kodları

| operationStatus | operationCode | Açıklama |
|-----------------|---------------|----------|
| `NOP` | 0 | İşlem yapılmadı, düzenlenmemiş |
| `IND` | 1 | Kargo teslimattadır |
| `ISR` | 2 | Düzenlenmiş, fatura prosedürü tamamlanmamış |
| `CNL` | 3 | Çıkış engellendi |
| `ISC` | 4 | İptal edilmiş |
| `DLV` | 5 | Teslim edildi |
| `BI` | 6 | YK acente tarafından iptal edildi |

#### Sonuç Detayları (itemDetail)

| Alan | Tip | Açıklama |
|------|-----|----------|
| `trackingUrl` | string | Kargo takip linki |
| `receiverCustName` | string | Alıcı adı |
| `departureUnitName` | string | Çıkış şubesi |
| `deliveryDate` | string | Teslim tarihi |
| `deliveryTime` | string | Teslim saati |
| `totalDesi` | float | Toplam desi |
| `cargoHistory[]` | array | Hareket geçmişi |

#### Hareket Geçmişi (cargoHistory)

| Alan | Açıklama |
|------|----------|
| `unitName` | Birim/Şube adı |
| `eventName` | Olay adı |
| `reasonName` | Sebep |
| `eventDate` | Olay tarihi |
| `eventTime` | Olay saati |
| `cityName` | Şehir |
| `townName` | İlçe |

#### İade Durum Kodları (rejectStatus)

| Değer | Açıklama | Süreç Durumu |
|-------|----------|--------------|
| 0 | İade talebi yapıldı | Devam ediyor |
| 1 | Çıkış şubesi onayladı | Devam ediyor |
| 2 | İade bölgesi onayladı | Devam ediyor |
| 3 | Müşteri onayladı | Devam ediyor |
| 4 | İade beklemede | İptal edildi |
| 7 | Teslimat iptal edildi | İptal edildi |
| 8 | Borçlandırma iptal edildi | İptal edildi |
| 9 | İade yapıldı | Devam ediyor |
| 10 | İade sonlandırıldı | Devam ediyor |
| 11 | İade onaylanmadı | İptal edildi |

> 📌 `rejectStatus` 0, 1, 2, 3, 9, 10 → İade süreci devam ediyor  
> 📌 `rejectStatus` 4, 7, 8, 11 → İade iptal edildi, normal süreç başladı

---

### 4. saveReturnShipmentCode — İade Kodu Oluşturma

İade müşterilerinin YK birimine ileterek iade işlemini tamamlayacakları kodu oluşturan servistir.

#### Kullanım

```php
$result = $client->saveReturnShipmentCode(
    returnCode: 'RMA-2024-001',  // Sizin belirlediğiniz iade kodu
    startDate: '20240101',        // Geçerlilik başlangıç (YYYYMMDD)
    endDate: '20240131',          // Geçerlilik bitiş (YYYYMMDD)
    maxCount: 1,                  // Kullanım adedi
    fieldName: '53'               // Test ortamında 53 veya 3; canlıda 16
);

if ($result->isSuccess()) {
    echo "İade kodu başarıyla oluşturuldu!\n";
} else {
    echo "Hata [{$result->errCode}]: {$result->outResult}\n";
}
```

#### Parametreler

| Parametre | Tip | Zorunlu | Açıklama | Örnek |
|-----------|-----|---------|----------|-------|
| `returnCode` | string | ✅ | İade kodu (benzersiz değer) | `RMA-2024-001` |
| `startDate` | string | ✅ | Geçerlilik başlangıç tarihi (YYYYMMDD) | `20240101` |
| `endDate` | string | ✅ | Geçerlilik bitiş tarihi (YYYYMMDD) | `20240131` |
| `maxCount` | int | ✅ | İade kodu kullanım adedi | `1` |
| `fieldName` | string | ✅ | Özel alan bilgisi | Test: `53` veya `3`, Canlı: `16` |

> ⚠️ **Not:** Test ortamında `fieldName` olarak `53` veya `3` kullanın. Canlı ortamda sözleşmenize özel `16` değeri tanımlanacaktır.

---

## Özel Alan Bilgileri (specialField1)

`specialField1` alanına birden fazla özel alan bilgisi gönderilebilir.

**Format:** `alan_no$deger#alan_no$deger#`

**Örnek:** `3$SIP001#7$MehmetYilmaz#`

### Alan Numaraları

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

## Hata Kodları Tablosu

### createShipment Hata Kodları

| Kod | Mesaj | Açıklama |
|-----|-------|----------|
| 0 | Başarılı | İşlem başarıyla tamamlandı |
| 936 | Beklenmeyen hata | YK Bilgi Sistemleri ile iletişime geçin |
| 80859 | ERR_INTG_CARGO_KEY_PARAM_NOT_FOUND | Kargo anahtarı bulunamadı |
| 82500 | ERR_INTG_CARGO_KEY_PARAM_LENGHT | Kargo anahtarı uzunluk aşımı |
| 60020 | ERR_EXIST_CARGO_KEY_PARAM | Kargo anahtarı sistemde mevcut |
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
| 60026 | Başlangıç tarih kriteri zorunludur | |
| 60027 | Bitiş tarih kriteri zorunludur | |
| 80838 | Tarih aralığı maksimum yy gün olabilir | |

---

## Debug

```php
// Son SOAP isteğini görüntüle
echo $client->getLastRequest();

// Son SOAP yanıtını görüntüle
echo $client->getLastResponse();

// Mevcut servis fonksiyonlarını listele
print_r($client->getFunctions());

// Mevcut servis tiplerini listele
print_r($client->getTypes());
```

---

## Testleri Çalıştırma

```bash
php tests/CreateShipmentTest.php
php tests/CancelShipmentTest.php
php tests/QueryShipmentTest.php
php tests/SaveReturnShipmentCodeTest.php
```

Her test dosyası bağımsız çalışır ve test ortamına bağlanarak gerçek SOAP çağrısı yapar.

---

## Parametrik Raporlama (Takip Linki)

Entegrasyon gönderileriniz için parametrik takip linki oluşturabilirsiniz:

```
http://selfservis.yurticikargo.com/reports/SswReportsFromParamFields.aspx?ssfldvn=XX&sskurkod=MUSTERI_KODU&refnumber=REF_NO&date=GG.AA.YYYY
```

| Parametre | Açıklama |
|-----------|----------|
| `ssfldvn` | Özel alan adı (yukarıdaki alan numaraları tablosundaki değerler) |
| `sskurkod` | YK müşteri kodu |
| `refnumber` | Takip edilecek özel alan değeri |
| `date` | Gönderi tarihi (dd.mm.yyyy formatında, ±5 gün tolerans) |

---

## IP Yetkilendirme

Yurtiçi Kargo web servislerine erişim için IP yetkilendirmesi zorunludur. Canlı ortama geçmeden önce çıkış IP adresinizi **Bölge Müdürlüğü Satış Temsilcinize** bildirmeniz gerekmektedir.

---

## Önemli Notlar

- `createShipment` ve `cancelShipment` metodları `userLanguage` parametresi kullanır
- `queryShipment` ve `saveReturnShipmentCode` metodları `wsLanguage` parametresi kullanır
- PHP SoapClient'a mutlaka `location` parametresi verilmelidir (WSDL'den otomatik alınmaz)
- WSDL tüm property'leri bekler, eksik olanlar boş string (`''`) veya `0` olarak gönderilmelidir
- Kargo anahtarı (cargoKey) fiziksel olarak kargo üzerinde barkod/metin olarak bulunmalıdır
- Tahsilat tutarında ondalık ayraç olarak `.` (nokta) kullanılmalıdır

---

## Entegrasyon Akışı

### Giden Kargo Akışı

```
1. createShipment ile gönderi bilgileri YK sistemine iletilir
2. Kargo anahtarı (cargoKey) fiziksel olarak kargo üzerinde bulunmalıdır
3. Gönderi düzenlenmeden önce cancelShipment ile iptal edilebilir
4. YK şubesi kargo anahtarını okuyarak sisteme girer
5. Alıcı bilgileri ekranda görünür
6. YK şubesi sevkiyat adresini belirler
7. Kargo adedi ve taşıma adresi girilerek YK irsaliyesi oluşturulur
8. Müşteri gönderisi ile YK taşıma belgesi eşleştirilir
9. queryShipment ile teslimat durumu sorgulanabilir
```

### İade Kodu Akışı

```
1. saveReturnShipmentCode ile iade kodu oluşturulur
2. İade kodu müşteriye iletilir
3. Müşteri bu kodu YK birimine ileterek iade işlemini başlatır
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
- Ör: `'TEST' . time()` veya `uniqid('CK-')`

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

### 16. PHP: SoapClient location parametresi
**Sorun:** PHP SoapClient WSDL'deki endpoint'i bazı durumlarda yanlış alıyor.
**Çözüm:** Constructor'a mutlaka `'location'` parametresi ekleyin:
```php
$client = new SoapClient($wsdl, [
    'location' => 'https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices',
    'trace'    => true,
    'encoding' => 'UTF-8',
]);
```

### 17. PHP: "SOAP-ERROR: Encoding: object has no 'X' property"
**Sorun:** WSDL tanımlı tüm property'ler gönderilmeli.
**Çözüm:** Eksik alanları boş string veya 0 olarak gönderin:
```php
$shipment = [
    'cargoKey'         => 'TEST001',
    'invoiceKey'       => 'INV001',
    'receiverCustName' => 'Test',
    'receiverAddress'  => 'Test Adresi',
    'receiverPhone1'   => '05551234567',
    'receiverPhone2'   => '',  // Boş string olarak gönderin
    'receiverPhone3'   => '',
    'cityName'         => '',
    'townName'         => '',
    // ... diğer alanlar da boş string olarak
];
```

### 18. PHP: ext-soap yüklü değil
**Sorun:** PHP SOAP extension aktif değil.
**Çözüm:**
- `php.ini` dosyasında `extension=soap` satırını aktif edin (başındaki `;` işaretini kaldırın)
- Kontrol: `php -m | grep soap` veya `php -m | findstr soap` (Windows)
- Linux: `sudo apt-get install php-soap` veya `sudo yum install php-soap`
- Restart: `sudo service apache2 restart` veya `sudo service php-fpm restart`

---

## Lisans

MIT
