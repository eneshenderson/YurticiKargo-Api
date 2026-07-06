# Yurtiçi Kargo PHP API Client

Yurtiçi Kargo SOAP Web Service entegrasyonu için PHP istemci kütüphanesi.

## Gereksinimler

- PHP >= 8.0
- PHP SOAP Extension (`ext-soap`)
- PHP OpenSSL Extension (`ext-openssl`)

## Kurulum

### Composer ile

```bash
composer require yurticikargo/api-client
```

### Manuel

```php
require_once 'src/YurticiKargoException.php';
require_once 'src/ShipmentResult.php';
require_once 'src/CancelResult.php';
require_once 'src/QueryResult.php';
require_once 'src/ReturnCodeResult.php';
require_once 'src/YurticiKargoClient.php';
```

## Hızlı Başlangıç

```php
<?php
require_once 'vendor/autoload.php';

use YurticiKargo\YurticiKargoClient;

// Test ortamı
$client = new YurticiKargoClient(
    username: 'YKTEST',
    password: 'YK',
    language: 'TR',
    testMode: true
);

// Canlı ortam
$client = new YurticiKargoClient(
    username: 'KULLANICI_ADINIZ',
    password: 'SIFRENIZ',
    language: 'TR',
    testMode: false
);
```

## Test Ortamı Bilgileri

| Parametre | Değer |
|-----------|-------|
| Username | `YKTEST` |
| Password | `YK` |
| Language | `TR` |
| WSDL (Test) | `https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl` |
| WSDL (Canlı) | `https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl` |

## API Metodları

---

### 1. createShipment — Gönderi Oluşturma

Müşterinin kargo bilgilerini Yurtiçi Kargo sistemine ileten servistir.

```php
$result = $client->createShipment([
    [
        'cargoKey'         => '0000113',        // Benzersiz kargo anahtarı (zorunlu)
        'invoiceKey'       => 'AB00113',        // Fatura anahtarı (zorunlu)
        'receiverCustName' => 'Mehmet Yılmaz',  // Alıcı adı (zorunlu)
        'receiverAddress'  => 'Eski Büyükdere Cad. No:3', // Alıcı adresi (zorunlu)
        'receiverPhone1'   => '02123652426',    // Alıcı telefon (zorunlu)
        'cityName'         => 'İstanbul',       // Şehir (opsiyonel)
        'townName'         => 'Maslak',         // İlçe (opsiyonel)
    ]
]);

if ($result->isSuccess()) {
    echo "Başarılı! Job ID: " . $result->jobId . "\n";
    foreach ($result->details as $detail) {
        echo "Cargo Key: {$detail->cargoKey} - Durum: {$detail->errMessage}\n";
    }
} else {
    echo "Hata: " . $result->outResult . "\n";
    foreach ($result->getErrors() as $error) {
        echo "  [{$error->errCode}] {$error->errMessage}\n";
    }
}
```

#### Gönderi Parametreleri

| Parametre | Tip | Zorunlu | Açıklama | Örnek |
|-----------|-----|---------|----------|-------|
| `cargoKey` | string(20) | ✅ | Benzersiz kargo anahtarı. YK şubesi bu bilgiyi gönderi veya kargo üzerinde barkod/metin olarak görmelidir. | `0000113` |
| `invoiceKey` | string(20) | ✅ | Fatura anahtarı. Kargo bazlı çalışmada her paket için farklı cargoKey, aynı invoiceKey kullanılır. | `AB00113` |
| `receiverCustName` | string(100) | ✅ | Alıcı müşteri adı | `Mehmet Yılmaz` |
| `receiverAddress` | string(500) | ✅ | Alıcı müşteri adresi | `Eski Büyükdere Cad. No:3` |
| `receiverPhone1` | string(20) | ✅ | Alıcı telefon numarası | `02123652426` |
| `receiverPhone2` | string(20) | ❌ | Alıcı telefon 2 | |
| `receiverPhone3` | string(20) | ❌ | Alıcı telefon 3 | |
| `cityName` | string(40) | ❌ | Alıcı adres şehir | `İstanbul` |
| `townName` | string(40) | ❌ | Alıcı adres ilçe | `Maslak` |
| `custProdId` | string | ❌ | Ürün kodu (desi/kg bilgisi ürün bazlı ise) | `1` |
| `desi` | float(9,3) | ❌ | Kargo desi bilgisi | `3.5` |
| `kg` | float(9,3) | ❌ | Kargo kg bilgisi | `7.6` |
| `cargoCount` | int(4) | ❌ | Gönderilen kargo adedi | `2` |
| `waybillNo` | string(20) | ❌ | Müşteri irsaliye numarası (ticari gönderilerde zorunlu) | `AA110125T` |
| `specialField1` | string(200) | ❌ | Özel alan 1 (format: `numara$deger#`) | `1$426031#2$397427#` |
| `specialField2` | string(100) | ❌ | Özel alan 2 | |
| `specialField3` | string(100) | ❌ | Özel alan 3 | |
| `ttCollectionType` | string(1) | ❌ | Tahsilatlı teslimat ödeme tipi: `0`=Nakit, `1`=Kredi Kartı | `0` |
| `ttInvoiceAmount` | float(18,2) | ❌ | Tahsilat tutarı (ayraç `.` nokta olmalı) | `20.5` |
| `ttDocumentId` | string(12) | ❌ | Tahsilat belge (fatura) numarası | `TT00666` |
| `ttDocumentSaveType` | string(1) | ❌ | Hizmet bedeli fatura tipi: `0`=Aynı fatura, `1`=Ayrı fatura | `0` |
| `orgReceiverCustId` | string(50) | ❌ | Alıcı müşteri kodu (ör. temsilci no) | `59874736` |
| `description` | string(255) | ❌ | Serbest açıklama | `Kargo` |
| `taxNumber` | string(15) | ❌ | Vergi numarası | `123123123` |
| `taxOfficeId` | int(8) | ❌ | Vergi dairesi ID | `340055` |
| `taxOfficeName` | string(60) | ❌ | Vergi dairesi adı | `Şişli` |
| `orgGeoCode` | string(20) | ❌ | Müşteri adres kodu | `36656` |
| `privilegeOrder` | string(10) | ❌ | Ayrıcalıklı gönderim merkezi tanımı | `1` |
| `dcSelectedCredit` | int(2) | ❌ | Taksit sayısı seçimi (kredi kartlı tahsilat için) | `2` |
| `dcCreditRule` | int(2) | ❌ | Kredi kuralı: `0`=Sadece anlaşmalı banka, `1`=Tek çekim izin | `1` |
| `emailAddress` | string(200) | ❌ | Alıcı e-posta adresi | `alici@mail.com` |

#### Tahsilatlı Teslimat (Kapıda Ödeme)

**Nakit tahsilat** için `ttCollectionType = "0"` olduğunda şu alanlar zorunludur:
- `ttInvoiceAmount`
- `ttDocumentId`
- `ttDocumentSaveType`

**Kredi kartlı tahsilat** için `ttCollectionType = "1"` olduğunda ek olarak şu alanlar da zorunludur:
- `dcSelectedCredit`
- `dcCreditRule`

#### Çalışma Modları

**Fatura Bazlı (İrsaliye Bazlı):**
Her gönderi için bir kayıt iletilir. Her `cargoKey` için bir gönderi düzenlenir.

**Kargo Bazlı (Çoklu Paket):**
Aynı alıcıya birden fazla paket gönderildiğinde, her paket için farklı `cargoKey`, aynı `invoiceKey` kullanılır.

```php
// 3 paketli bir gönderi örneği
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
| `outFlag` | int | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
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

> ⚠️ Gönderi düzenlendikten sonra iptal yapılamaz.

```php
$result = $client->cancelShipment(['0000113', '0000114']);

if ($result->isSuccess()) {
    foreach ($result->details as $detail) {
        echo "{$detail->cargoKey}: {$detail->operationMessage} ({$detail->operationStatus})\n";
    }
} else {
    echo "Hata: " . $result->outResult . "\n";
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

#### Sonuç Yapısı (CancelResult)

| Alan | Tip | Açıklama |
|------|-----|----------|
| `outFlag` | int | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
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

```php
// Cargo Key ile sorgulama
$result = $client->queryShipment(
    keys: ['12520', '12521'],
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
    foreach ($result->details as $detail) {
        if ($detail->isSuccess()) {
            echo "Kargo: {$detail->cargoKey}\n";
            echo "Durum: {$detail->operationMessage} ({$detail->operationStatus})\n";

            if ($detail->itemDetail) {
                $item = $detail->itemDetail;
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
            echo "Hata [{$detail->errCode}]: {$detail->errMessage}\n";
        }
    }
}
```

#### Sorgu Parametreleri

| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| `keys` | array | ✅ | Sorgulanacak anahtar değerleri dizisi |
| `keyType` | int | ✅ | 0=Cargo Key, 1=Invoice Key |
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

#### İade Durum Kodları (rejectStatus)

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

> 📌 `rejectStatus` 0, 1, 2, 3, 9, 10 → İade süreci devam ediyor  
> 📌 `rejectStatus` 4, 7, 8, 11 → İade iptal edildi, normal süreç başladı

---

### 4. saveReturnShipmentCode — İade Kodu Oluşturma

İade müşterilerinin YK birimine ileterek iade işlemini tamamlayacakları kodu oluşturan servistir.

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
| `returnCode` | string | ✅ | İade kodu (sizin belirleyeceğiniz benzersiz değer) | `RMA-2024-001` |
| `startDate` | string | ✅ | Kod geçerlilik başlangıç tarihi (YYYYMMDD) | `20240101` |
| `endDate` | string | ✅ | Kod geçerlilik bitiş tarihi (YYYYMMDD) | `20240131` |
| `maxCount` | int | ✅ | İade kodu kullanım adedi | `1` |
| `fieldName` | string | ✅ | Özel alan bilgisi | Test: `53` veya `3`, Canlı: `16` |

> ⚠️ **Not:** Test ortamında `fieldName` olarak `53` veya `3` kullanın. Canlı ortamda sözleşmenize özel `16` değeri tanımlanacaktır.

---

## Özel Alan Bilgileri (specialField1)

`specialField1` alanına birden fazla özel alan bilgisi gönderilebilir.

**Format:** `alan_no$deger#alan_no$deger#`

**Örnek:** `1$426031#2$397427#`

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

## Parametrik Raporlama (Takip Linki)

Entegrasyon gönderileriniz için parametrik takip linki oluşturabilirsiniz:

```
http://selfservis.yurticikargo.com/reports/SswReportsFromParamFields.aspx?ssfldvn=XX&sskurkod=MUSTERI_KODU&refnumber=REFERANS_NO&date=GG.AA.YYYY
```

| Parametre | Açıklama |
|-----------|----------|
| `ssfldvn` | Özel alan adı (Tablo-1'deki değerler) |
| `sskurkod` | YK müşteri kodu |
| `refnumber` | Takip edilecek özel alan değeri |
| `date` | Gönderi tarihi (dd.mm.yyyy, ±5 gün tolerans) |

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

## IP Yetkilendirme

Yurtiçi Kargo web servislerine erişim için IP yetkilendirmesi zorunludur. Canlı ortama geçmeden önce çıkış IP adresinizi Bölge Müdürlüğü Satış Temsilcinize bildirmeniz gerekmektedir.

---

## Lisans

MIT
