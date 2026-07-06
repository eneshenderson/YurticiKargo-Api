# Yurtiçi Kargo JavaScript (Node.js) API Client

Yurtiçi Kargo SOAP Web Service entegrasyonu için Node.js istemci kütüphanesi. Sıfır harici bağımlılık, native `https` modülü ile çalışır.

## Gereksinimler

- Node.js >= 18.0 (built-in `https` modülü)
- Sıfır harici bağımlılık
- ESM (import/export) formatı

## Proje Yapısı

```
javascript/
├── package.json              (type: module, zero dependencies)
├── YurticiKargoClient.js     (controller - tüm metodları barındırır)
├── YurticiKargoAllInOne.js   (tek dosya - bağımsız çalışır)
├── functions/
│   ├── createShipment.js     (gönderi oluşturma)
│   ├── cancelShipment.js     (gönderi iptal)
│   ├── queryShipment.js      (gönderi sorgulama)
│   └── saveReturnShipmentCode.js (iade kodu oluşturma)
└── tests/
    ├── createShipment.test.js
    ├── cancelShipment.test.js
    ├── queryShipment.test.js
    └── saveReturnShipmentCode.test.js
```

## Çalıştırma

```bash
# Tek dosya ile tüm testler
node YurticiKargoAllInOne.js

# Ayrı ayrı test dosyaları
node tests/createShipment.test.js
node tests/cancelShipment.test.js
node tests/queryShipment.test.js
node tests/saveReturnShipmentCode.test.js
```

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

```javascript
import { YurticiKargoClient } from './YurticiKargoClient.js';

// Test ortamı
const client = new YurticiKargoClient({
    username: 'YKTEST',
    password: 'YK',
    language: 'TR',
    testMode: true
});

// Canlı ortam
const client = new YurticiKargoClient({
    username: 'KULLANICI_ADINIZ',
    password: 'SIFRENIZ',
    language: 'TR',
    testMode: false
});
```

### Fonksiyon Bazlı Kullanım

Her fonksiyon bağımsız olarak import edilip kullanılabilir:

```javascript
import { createShipment } from './functions/createShipment.js';
import { cancelShipment } from './functions/cancelShipment.js';
import { queryShipment } from './functions/queryShipment.js';
import { saveReturnShipmentCode } from './functions/saveReturnShipmentCode.js';

const config = {
    username: 'YKTEST',
    password: 'YK',
    language: 'TR',
    testMode: true
};

const result = await createShipment(config, shipments);
```

---

## API Metodları

Tüm metodlar `async/await` destekler ve `Promise` döner.

---

### 1. createShipment — Gönderi Oluşturma

Müşterinin kargo bilgilerini Yurtiçi Kargo sistemine ileten servistir.

**SOAP Parametresi:** `userLanguage`

```javascript
const result = await client.createShipment([
    {
        cargoKey: 'TEST001',           // Benzersiz kargo anahtarı (zorunlu)
        invoiceKey: 'INV001',          // Fatura anahtarı (zorunlu)
        receiverCustName: 'Mehmet Yılmaz',  // Alıcı adı (zorunlu)
        receiverAddress: 'Eski Büyükdere Cad. No:3', // Alıcı adresi (zorunlu)
        receiverPhone1: '05321234567', // Alıcı telefon (zorunlu)
        cityName: 'İstanbul',          // Şehir (opsiyonel)
        townName: 'Maslak',            // İlçe (opsiyonel)
    }
]);

if (result.outFlag === 0) {
    console.log(`Başarılı! Job ID: ${result.jobId}`);
    for (const detail of result.details) {
        console.log(`Cargo Key: ${detail.cargoKey} - Durum: ${detail.errMessage}`);
    }
} else {
    console.log(`Hata: ${result.outResult}`);
    for (const detail of result.details) {
        if (detail.errCode !== 0) {
            console.log(`  [${detail.errCode}] ${detail.errMessage}`);
        }
    }
}
```

#### Gönderi Parametreleri

| Parametre | Tip | Zorunlu | Açıklama | Örnek |
|-----------|-----|---------|----------|-------|
| `cargoKey` | string(20) | ✅ | Benzersiz kargo anahtarı. YK şubesi bu bilgiyi gönderi üzerinde barkod/metin olarak görmelidir. | `'TEST001'` |
| `invoiceKey` | string(20) | ✅ | Fatura anahtarı. Kargo bazlı çalışmada her paket için farklı cargoKey, aynı invoiceKey kullanılır. | `'INV001'` |
| `receiverCustName` | string(100) | ✅ | Alıcı müşteri adı | `'Mehmet Yılmaz'` |
| `receiverAddress` | string(500) | ✅ | Alıcı müşteri adresi | `'Eski Büyükdere Cad. No:3'` |
| `receiverPhone1` | string(20) | ✅ | Alıcı telefon numarası | `'02123652426'` |
| `receiverPhone2` | string(20) | ❌ | Alıcı telefon 2 | |
| `receiverPhone3` | string(20) | ❌ | Alıcı telefon 3 | |
| `cityName` | string(40) | ❌ | Alıcı adres şehir | `'İstanbul'` |
| `townName` | string(40) | ❌ | Alıcı adres ilçe | `'Maslak'` |
| `custProdId` | string | ❌ | Ürün kodu (desi/kg bilgisi ürün bazlı ise) | `'1'` |
| `desi` | float(9,3) | ❌ | Kargo desi bilgisi | `3.5` |
| `kg` | float(9,3) | ❌ | Kargo kg bilgisi | `7.6` |
| `cargoCount` | int(4) | ❌ | Gönderilen kargo adedi | `2` |
| `waybillNo` | string(20) | ❌ | Müşteri irsaliye numarası (ticari gönderilerde zorunlu) | `'AA110125T'` |
| `specialField1` | string(200) | ❌ | Özel alan 1 (format: `numara$deger#`) | `'1$426031#2$397427#'` |
| `specialField2` | string(100) | ❌ | Özel alan 2 | |
| `specialField3` | string(100) | ❌ | Özel alan 3 | |
| `ttCollectionType` | string(1) | ❌ | Tahsilatlı teslimat ödeme tipi: `'0'`=Nakit, `'1'`=Kredi Kartı | `'0'` |
| `ttInvoiceAmount` | float(18,2) | ❌ | Tahsilat tutarı (ayraç `.` nokta olmalı) | `20.5` |
| `ttDocumentId` | string(12) | ❌ | Tahsilat belge (fatura) numarası | `'TT00666'` |
| `ttDocumentSaveType` | string(1) | ❌ | Hizmet bedeli fatura tipi: `'0'`=Aynı fatura, `'1'`=Ayrı fatura | `'0'` |
| `orgReceiverCustId` | string(50) | ❌ | Alıcı müşteri kodu (ör. temsilci no) | `'59874736'` |
| `description` | string(255) | ❌ | Serbest açıklama | `'Kargo'` |
| `taxNumber` | string(15) | ❌ | Vergi numarası | `'123123123'` |
| `taxOfficeId` | int(8) | ❌ | Vergi dairesi ID | `340055` |
| `taxOfficeName` | string(60) | ❌ | Vergi dairesi adı | `'Şişli'` |
| `orgGeoCode` | string(20) | ❌ | Müşteri adres kodu | `'36656'` |
| `privilegeOrder` | string(10) | ❌ | Ayrıcalıklı gönderim merkezi tanımı | `'1'` |
| `dcSelectedCredit` | int(2) | ❌ | Taksit sayısı seçimi (kredi kartlı tahsilat için) | `2` |
| `dcCreditRule` | int(2) | ❌ | Kredi kuralı: `0`=Sadece anlaşmalı banka, `1`=Tek çekim izin | `1` |
| `emailAddress` | string(200) | ❌ | Alıcı e-posta adresi | `'alici@mail.com'` |

#### Tahsilatlı Teslimat (Kapıda Ödeme)

**Nakit tahsilat** için `ttCollectionType = "0"` olduğunda şu alanlar zorunludur:
- `ttInvoiceAmount`
- `ttDocumentId`
- `ttDocumentSaveType`

**Kredi kartlı tahsilat** için `ttCollectionType = "1"` olduğunda ek olarak şu alanlar da zorunludur:
- `dcSelectedCredit`
- `dcCreditRule`

```javascript
// Kapıda nakit ödeme örneği
const result = await client.createShipment([
    {
        cargoKey: 'COD001',
        invoiceKey: 'CODINV001',
        receiverCustName: 'Ali Veli',
        receiverAddress: 'Test Mahallesi Test Sok. No:1',
        receiverPhone1: '05551234567',
        ttCollectionType: '0',        // Nakit
        ttInvoiceAmount: 150.00,      // 150 TL tahsilat
        ttDocumentId: 'FTR001',       // Fatura no
        ttDocumentSaveType: '0'       // Aynı fatura
    }
]);
```

#### Çalışma Modları

**Fatura Bazlı (İrsaliye Bazlı):**
Her gönderi için bir kayıt iletilir. Her `cargoKey` için bir gönderi düzenlenir.

**Kargo Bazlı (Çoklu Paket):**
Aynı alıcıya birden fazla paket gönderildiğinde, her paket için farklı `cargoKey`, aynı `invoiceKey` kullanılır.

```javascript
// 3 paketli bir gönderi örneği (kargo bazlı)
const result = await client.createShipment([
    {
        cargoKey: '10012',
        invoiceKey: 'A123456',       // Hepsi aynı fatura
        receiverCustName: 'Ali Veli',
        receiverAddress: 'Adres bilgisi',
        receiverPhone1: '05551234567',
        waybillNo: 'A123456',
        cargoCount: 1,
    },
    {
        cargoKey: '10013',
        invoiceKey: 'A123456',
        receiverCustName: 'Ali Veli',
        receiverAddress: 'Adres bilgisi',
        receiverPhone1: '05551234567',
        waybillNo: 'A123456',
        cargoCount: 1,
    },
    {
        cargoKey: '10014',
        invoiceKey: 'A123456',
        receiverCustName: 'Ali Veli',
        receiverAddress: 'Adres bilgisi',
        receiverPhone1: '05551234567',
        waybillNo: 'A123456',
        cargoCount: 1,
    },
]);
```

#### Sonuç Yapısı

| Alan | Tip | Açıklama |
|------|-----|----------|
| `outFlag` | number | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
| `outResult` | string | Sonuç mesajı |
| `jobId` | number | YK talep numarası (başarılı ise) |
| `count` | number | İşlem yapılan gönderi sayısı |
| `details[]` | array | Her gönderi için detay |
| `details[].cargoKey` | string | Kargo anahtarı |
| `details[].invoiceKey` | string | Fatura anahtarı |
| `details[].errCode` | number | Hata kodu (0=başarılı) |
| `details[].errMessage` | string | Hata mesajı |

---

### 2. cancelShipment — Gönderi İptal

Web servis ile sisteme gönderilmiş bilgilerin iptal edilmesini ve kargonun çıkışının engellenmesini sağlar.

**SOAP Parametresi:** `userLanguage`

> ⚠️ Gönderi düzenlendikten sonra iptal yapılamaz.

```javascript
const result = await client.cancelShipment(['TEST001', 'TEST002']);

if (result.outFlag === 0) {
    for (const detail of result.details) {
        console.log(`${detail.cargoKey}: ${detail.operationMessage} (${detail.operationStatus})`);
    }
} else {
    console.log(`Hata: ${result.outResult}`);
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

#### Sonuç Yapısı

| Alan | Tip | Açıklama |
|------|-----|----------|
| `outFlag` | number | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
| `outResult` | string | Sonuç mesajı |
| `senderCustId` | number | Gönderici müşteri kodu |
| `count` | number | İşlem yapılan gönderi sayısı |
| `details[].cargoKey` | string | Kargo anahtarı |
| `details[].invoiceKey` | string | Fatura anahtarı |
| `details[].jobId` | number | YK talep numarası |
| `details[].docId` | string | YK gönderi kodu |
| `details[].operationCode` | number | İşlem kodu |
| `details[].operationMessage` | string | İşlem mesajı |
| `details[].operationStatus` | string | İşlem durumu |
| `details[].errCode` | number | Hata kodu |
| `details[].errMessage` | string | Hata mesajı |

---

### 3. queryShipment — Gönderi Sorgulama

Müşterinin kendi referans kodu ile gönderi geçmişini raporlayan servistir. Tek seferde birden fazla gönderi sorgulanabilir.

**SOAP Parametresi:** `wsLanguage`

```javascript
// Cargo Key ile sorgulama
const result = await client.queryShipment(
    ['12520', '12521'],  // keys - sorgulanacak anahtarlar
    0,                    // keyType: 0=Cargo Key, 1=Invoice Key
    true,                 // addHistoricalData: hareket geçmişi dahil
    false                 // onlyTracking: sadece takip URL'si
);

// Invoice Key ile sorgulama
const result = await client.queryShipment(
    ['A123456'],
    1     // keyType: 1 = Invoice Key
);

if (result.outFlag === 0) {
    for (const detail of result.details) {
        if (detail.errCode === 0) {
            console.log(`Kargo: ${detail.cargoKey}`);
            console.log(`Durum: ${detail.operationMessage} (${detail.operationStatus})`);

            if (detail.itemDetail) {
                const item = detail.itemDetail;
                console.log(`Takip: ${item.trackingUrl}`);
                console.log(`Alıcı: ${item.receiverCustName}`);
                console.log(`Çıkış: ${item.departureUnitName}`);
                console.log(`Teslim: ${item.deliveryDate} ${item.deliveryTime}`);

                // Hareket geçmişi
                if (item.cargoHistory) {
                    for (const event of item.cargoHistory) {
                        console.log(`  → ${event.eventDate} ${event.eventTime} | ${event.unitName} | ${event.eventName} | ${event.reasonName}`);
                    }
                }
            }
        } else {
            console.log(`Hata [${detail.errCode}]: ${detail.errMessage}`);
        }
    }
}
```

#### Sorgu Parametreleri

| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| `keys` | array | ✅ | Sorgulanacak anahtar değerleri dizisi |
| `keyType` | number | ✅ | 0=Cargo Key, 1=Invoice Key |
| `addHistoricalData` | boolean | ❌ | Hareket geçmişi dahil edilsin mi? (Performans için `false` önerilir) |
| `onlyTracking` | boolean | ❌ | Sadece takip URL'si dönsün mü? |

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

**SOAP Parametresi:** `wsLanguage`

```javascript
const result = await client.saveReturnShipmentCode(
    'RMA-2024-001',   // returnCode: sizin belirlediğiniz iade kodu
    '20240101',       // startDate: geçerlilik başlangıç (YYYYMMDD)
    '20240131',       // endDate: geçerlilik bitiş (YYYYMMDD)
    1,                // maxCount: kullanım adedi
    '53'              // fieldName: test ortamında 53 veya 3; canlıda 16
);

if (result.outFlag === 0) {
    console.log('İade kodu başarıyla oluşturuldu!');
} else {
    console.log(`Hata [${result.errCode}]: ${result.outResult}`);
}
```

#### Parametreler

| Parametre | Tip | Zorunlu | Açıklama | Örnek |
|-----------|-----|---------|----------|-------|
| `returnCode` | string | ✅ | İade kodu (sizin belirleyeceğiniz benzersiz değer) | `'RMA-2024-001'` |
| `startDate` | string | ✅ | Kod geçerlilik başlangıç tarihi (YYYYMMDD) | `'20240101'` |
| `endDate` | string | ✅ | Kod geçerlilik bitiş tarihi (YYYYMMDD) | `'20240131'` |
| `maxCount` | number | ✅ | İade kodu kullanım adedi | `1` |
| `fieldName` | string | ✅ | Özel alan bilgisi | Test: `'53'` veya `'3'`, Canlı: `'16'` |

> ⚠️ **Not:** Test ortamında `fieldName` olarak `'53'` veya `'3'` kullanın. Canlı ortamda sözleşmenize özel `'16'` değeri tanımlanacaktır.

#### Sonuç Yapısı

| Alan | Tip | Açıklama |
|------|-----|----------|
| `outFlag` | number | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
| `outResult` | string | Sonuç mesajı |
| `errCode` | number | Hata kodu |

---

## Özel Alan Bilgileri (specialField1)

`specialField1` alanına birden fazla özel alan bilgisi gönderilebilir.

**Format:** `alan_no$deger#alan_no$deger#`

**Örnek:** `'1$426031#2$397427#'`

```javascript
const result = await client.createShipment([
    {
        cargoKey: 'SF001',
        invoiceKey: 'SFINV001',
        receiverCustName: 'Test Alıcı',
        receiverAddress: 'Test Adresi',
        receiverPhone1: '05551234567',
        specialField1: '1$426031#2$397427#'
    }
]);
```

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

## SOAP Dil Parametreleri

Farklı metodlar farklı SOAP dil parametreleri kullanır:

| Metod | SOAP Parametre Adı | Açıklama |
|-------|---------------------|----------|
| `createShipment` | `userLanguage` | Kullanıcı dili |
| `cancelShipment` | `userLanguage` | Kullanıcı dili |
| `queryShipment` | `wsLanguage` | Web servis dili |
| `saveReturnShipmentCode` | `wsLanguage` | Web servis dili |

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

## Debug

SOAP istek ve yanıtlarını incelemek için:

```javascript
// Son SOAP isteğini görüntüle
console.log(client.getLastRequest());

// Son SOAP yanıtını görüntüle
console.log(client.getLastResponse());
```

### Hata Yakalama

```javascript
try {
    const result = await client.createShipment(shipments);
    if (result.outFlag === 0) {
        // Başarılı
    } else if (result.outFlag === 1) {
        // İş kuralı hatası
        console.error('Hata:', result.outResult);
    } else if (result.outFlag === 2) {
        // Beklenmeyen hata
        console.error('Sistem hatası:', result.outResult);
    }
} catch (error) {
    // Ağ hatası, timeout vb.
    console.error('Bağlantı hatası:', error.message);
}
```

---

## Parametrik Raporlama (Takip Linki)

Entegrasyon gönderileriniz için parametrik takip linki oluşturabilirsiniz:

```
http://selfservis.yurticikargo.com/reports/SswReportsFromParamFields.aspx?ssfldvn=XX&sskurkod=MUSTERI_KODU&refnumber=REFERANS_NO&date=GG.AA.YYYY
```

| Parametre | Açıklama |
|-----------|----------|
| `ssfldvn` | Özel alan adı (yukarıdaki tablo değerleri) |
| `sskurkod` | YK müşteri kodu |
| `refnumber` | Takip edilecek özel alan değeri |
| `date` | Gönderi tarihi (dd.mm.yyyy, ±5 gün tolerans) |

```javascript
// Takip linki oluşturma yardımcı fonksiyonu
function buildTrackingUrl(fieldNo, customerCode, refNumber, date) {
    return `http://selfservis.yurticikargo.com/reports/SswReportsFromParamFields.aspx?ssfldvn=${fieldNo}&sskurkod=${customerCode}&refnumber=${refNumber}&date=${date}`;
}

const url = buildTrackingUrl('53', '12345', 'REF001', '01.07.2024');
console.log(url);
```

---

## IP Yetkilendirme

Yurtiçi Kargo web servislerine erişim için IP yetkilendirmesi zorunludur. Canlı ortama geçmeden önce çıkış IP adresinizi Bölge Müdürlüğü Satış Temsilcinize bildirmeniz gerekmektedir.

> ⚠️ Test ortamında IP kısıtlaması yoktur. Canlı ortamda (`ws.yurticikargo.com`) yetkilendirilmemiş IP'lerden gelen istekler reddedilir.

---

## Teknik Notlar

- Tüm SOAP istekleri HTTPS üzerinden gönderilir
- XML body UTF-8 encoding ile oluşturulur
- Yanıtlar XML olarak parse edilir, JSON objesine dönüştürülür
- Timeout varsayılan olarak 30 saniyedir
- Node.js 18+ gereklidir (native `https` ve `crypto` modülleri)
- Harici bağımlılık yoktur (`node-soap`, `axios` vb. gerekmez)

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
- Ör: `'TEST-' + Date.now()` veya `crypto.randomUUID().slice(0, 20)`

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

### 16. Node.js: UNABLE_TO_VERIFY_LEAF_SIGNATURE
**Sorun:** SSL sertifika doğrulama hatası alınıyor.
**Çözüm:** Test ortamında TLS doğrulamayı devre dışı bırakın:
```javascript
// Yöntem 1: Environment variable (tüm istekler için)
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

// Yöntem 2: Agent bazlı (sadece bu istek için)
import https from 'https';
const agent = new https.Agent({ rejectUnauthorized: false });
```
> ⚠️ Bu ayarı sadece test ortamında kullanın. Canlı ortamda sertifika doğrulaması aktif olmalıdır.

### 17. Node.js: ECONNREFUSED
**Sorun:** DNS çözümleme veya port erişim sorunu.
**Çözüm:**
- `nslookup testws.yurticikargo.com` ile DNS çözümleme kontrol edin
- Firewall'da 443 portunun açık olduğunu doğrulayın
- Proxy arkasındaysanız `HTTPS_PROXY` environment variable'ını ayarlayın:
```bash
export HTTPS_PROXY=http://proxy.sirket.com:8080
```

### 18. Node.js: Timeout hatası
**Sorun:** İstek varsayılan 30 saniye timeout'u aşıyor.
**Çözüm:** Timeout değerini artırın:
```javascript
const client = new YurticiKargoClient({
    username: 'YKTEST',
    password: 'YK',
    language: 'TR',
    testMode: true,
    timeout: 60000  // 60 saniye
});
```

---

## Lisans

MIT
