# Yurtiçi Kargo SOAP API Client — Proje Bilgi Dosyası

> Bu dosya AI asistanları (Claude, Copilot, Kiro, Cursor, ChatGPT, Gemini vb.) için proje bağlamı sağlar.
> Kod üretirken, hata ayıklarken veya bu projeyi genişletirken bu bilgileri referans olarak kullanın.

---

## Proje Özeti

Yurtiçi Kargo'nun SOAP tabanlı web servis API'si ile entegrasyon sağlayan, 6 programlama dilinde (PHP, C#/.NET, Java, JavaScript/Node.js, Python, Go) yazılmış istemci kütüphanesi.

**Mimari:** Her dil için aynı yapı:
- `functions/` → Her API fonksiyonu ayrı dosyada
- `controller` → Tüm fonksiyonları tek sınıfta birleştiren ana dosya
- `tests/` → Gerçek API'ye bağlanan test dosyaları
- `all-in-one` → Tek dosyada bağımsız çalışan komple istemci

**Temel Prensip:** Sıfır harici bağımlılık. Tüm dillerde sadece standard library kullanılır.

---

## API Endpoint Bilgileri

| Ortam | URL |
|-------|-----|
| Test WSDL | `https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl` |
| Test POST | `https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices` |
| Canlı WSDL | `https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl` |
| Canlı POST | `https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices` |

**SOAP Namespace:** `http://yurticikargo.com.tr/ShippingOrderDispatcherServices`

**Test Kimlik Bilgileri:**
- Username: `YKTEST`
- Password: `YK`
- Language: `TR`

> ⚠️ SOAP POST hedefi URL'de `?wsdl` OLMAMALIDIR. WSDL sadece tanımlama için kullanılır.

---

## KRİTİK: Dil Parametresi Farkı

Bu API'nin en önemli gotcha'sı: Farklı metodlar farklı dil parametresi adı kullanır.

| SOAP Method | XML Element | Dil Parametresi Adı |
|-------------|-------------|---------------------|
| `createShipment` | `<ship:createShipment>` | `<userLanguage>TR</userLanguage>` |
| `cancelShipment` | `<ship:cancelShipment>` | `<userLanguage>TR</userLanguage>` |
| `queryShipment` | `<ship:queryShipment>` | `<wsLanguage>TR</wsLanguage>` |
| `saveReturnShipmentCode` | `<ship:saveReturnShipmentCode>` | `<wsLanguage>TR</wsLanguage>` |

Yanlış parametre adı kullanıldığında servis **"Web servis kullanıcı dili boş olamaz"** hatası döner.

---

## API Fonksiyonları

### 1. createShipment — Gönderi Oluşturma

**SOAP Action:** `<ship:createShipment>`

**Zorunlu Parametreler:**
```xml
<wsUserName>YKTEST</wsUserName>
<wsPassword>YK</wsPassword>
<userLanguage>TR</userLanguage>
<ShippingOrderVO>
  <cargoKey>string(20)</cargoKey>
  <invoiceKey>string(20)</invoiceKey>
  <receiverCustName>string(100)</receiverCustName>
  <receiverAddress>string(10-500)</receiverAddress>
  <receiverPhone1>string(20)</receiverPhone1>
</ShippingOrderVO>
```

**Opsiyonel Parametreler (ShippingOrderVO içinde):**
| Alan | Tip | Açıklama |
|------|-----|----------|
| receiverPhone2 | string(20) | Alıcı telefon 2 |
| receiverPhone3 | string(20) | Alıcı telefon 3 |
| cityName | string(40) | Şehir |
| townName | string(40) | İlçe |
| custProdId | string | Ürün kodu |
| desi | float(9,3) | Desi bilgisi |
| kg | float(9,3) | Kg bilgisi |
| cargoCount | int(4) | Kargo adedi |
| waybillNo | string(20) | İrsaliye no |
| specialField1 | string(200) | Özel alan (format: `no$değer#`) |
| specialField2 | string(100) | Özel alan 2 |
| specialField3 | string(100) | Özel alan 3 |
| ttCollectionType | string(1) | 0=Nakit, 1=Kredi Kartı |
| ttInvoiceAmount | float(18,2) | Tahsilat tutarı (ayraç: nokta) |
| ttDocumentId | string(12) | Tahsilat belge no |
| ttDocumentSaveType | string(1) | 0=Aynı fatura, 1=Ayrı fatura |
| orgReceiverCustId | string(50) | Alıcı müşteri kodu |
| description | string(255) | Açıklama |
| taxNumber | string(15) | Vergi no |
| taxOfficeId | int(8) | Vergi dairesi ID |
| taxOfficeName | string(60) | Vergi dairesi adı |
| orgGeoCode | string(20) | Adres kodu |
| privilegeOrder | string(10) | Ayrıcalıklı merkez |
| dcSelectedCredit | int(2) | Taksit sayısı |
| dcCreditRule | int(2) | 0=Sadece anlaşmalı, 1=Tek çekim izin |
| emailAddress | string(200) | E-posta |

**Tahsilatlı Teslimat Zorunlulukları:**
- `ttCollectionType=0` (Nakit) → `ttInvoiceAmount`, `ttDocumentId`, `ttDocumentSaveType` zorunlu
- `ttCollectionType=1` (KK) → Yukarıdakilere ek: `dcSelectedCredit`, `dcCreditRule` zorunlu

**Response:**
```xml
<ShippingOrderResultVO>
  <outFlag>0</outFlag>          <!-- 0=OK, 1=Hata, 2=Beklenmeyen -->
  <outResult>Başarılı</outResult>
  <jobId>2198836</jobId>
  <count>1</count>
  <shippingOrderDetailVO>
    <cargoKey>TEST001</cargoKey>
    <invoiceKey>INV001</invoiceKey>
    <errCode>0</errCode>
    <errMessage></errMessage>
  </shippingOrderDetailVO>
</ShippingOrderResultVO>
```

**PHP WSDL Notu:** PHP SoapClient kullanıldığında WSDL tanımlı TÜM property'ler gönderilmelidir. Eksik alanlar boş string `''` veya `0` olarak set edilmelidir, aksi halde `SOAP-ERROR: Encoding: object has no 'X' property` hatası alınır.

---

### 2. cancelShipment — Gönderi İptal

**SOAP Action:** `<ship:cancelShipment>`

```xml
<wsUserName>YKTEST</wsUserName>
<wsPassword>YK</wsPassword>
<userLanguage>TR</userLanguage>
<cargoKeys>KEY1</cargoKeys>
<cargoKeys>KEY2</cargoKeys>
```

**Response:**
```xml
<ShippingOrderResultVO>
  <outFlag>0</outFlag>
  <outResult>Başarılı</outResult>
  <senderCustId>1010954</senderCustId>
  <count>1</count>
  <shippingCancelDetailVO>
    <cargoKey>KEY1</cargoKey>
    <invoiceKey>INV1</invoiceKey>
    <jobId>419100</jobId>
    <docId>100365926603</docId>
    <operationCode>3</operationCode>
    <operationMessage>Kargo Çıkışı Engellendi.</operationMessage>
    <operationStatus>CNL</operationStatus>
  </shippingCancelDetailVO>
</ShippingOrderResultVO>
```

**Durum Kodları:**
| operationStatus | operationCode | Açıklama |
|-----------------|---------------|----------|
| NOP | 0 | İşlem yapılmadı, düzenlenmemiş |
| IND | 1 | Kargo teslimatta |
| ISR | 2 | Düzenlenmiş, fatura tamamlanmamış |
| CNL | 3 | Çıkış engellendi (başarılı iptal) |
| ISC | 4 | Zaten iptal edilmiş |
| DLV | 5 | Teslim edildi |
| BI | 6 | YK tarafından iptal |

---

### 3. queryShipment — Gönderi Sorgulama

**SOAP Action:** `<ship:queryShipment>`

```xml
<wsUserName>YKTEST</wsUserName>
<wsPassword>YK</wsPassword>
<wsLanguage>TR</wsLanguage>
<keys>KEY1</keys>
<keys>KEY2</keys>
<keyType>0</keyType>              <!-- 0=cargoKey, 1=invoiceKey -->
<addHistoricalData>true</addHistoricalData>
<onlyTracking>false</onlyTracking>
```

**Response (kısaltılmış):**
```xml
<ShippingDeliveryVO>
  <outFlag>0</outFlag>
  <outResult>Başarılı</outResult>
  <shippingDeliveryDetailVO>
    <cargoKey>KEY1</cargoKey>
    <operationStatus>IND</operationStatus>
    <operationMessage>Kargo Teslimattadır.</operationMessage>
    <shippingDeliveryItemDetailVO>
      <trackingUrl>http://...</trackingUrl>
      <receiverCustName>...</receiverCustName>
      <departureUnitName>...</departureUnitName>
      <deliveryDate>20240115</deliveryDate>
      <deliveryTime>142530</deliveryTime>
      <invDocCargoVOArray>
        <unitName>TRANSFER MERKEZİ</unitName>
        <eventName>Kargo Yüklendi</eventName>
        <reasonName>Sorun Yok</reasonName>
        <eventDate>20240114</eventDate>
        <eventTime>183045</eventTime>
        <cityName>İstanbul</cityName>
        <townName>Bağcılar</townName>
      </invDocCargoVOArray>
    </shippingDeliveryItemDetailVO>
  </shippingDeliveryDetailVO>
</ShippingDeliveryVO>
```

**İade Durum Kodları (rejectStatus):**
| Değer | Açıklama | Süreç |
|-------|----------|-------|
| 0 | İade talebi yapıldı | Devam |
| 1 | Çıkış şubesi onayladı | Devam |
| 2 | İade bölgesi onayladı | Devam |
| 3 | Müşteri onayladı | Devam |
| 4 | İade beklemede | İptal |
| 7 | Teslimat iptal edildi | İptal |
| 8 | Borçlandırma iptal edildi | İptal |
| 9 | İade yapıldı | Devam |
| 10 | İade sonlandırıldı | Devam |
| 11 | İade onaylanmadı | İptal |

---

### 4. saveReturnShipmentCode — İade Kodu Oluşturma

**SOAP Action:** `<ship:saveReturnShipmentCode>`

```xml
<wsUserName>YKTEST</wsUserName>
<wsPassword>YK</wsPassword>
<wsLanguage>TR</wsLanguage>
<fieldName>53</fieldName>           <!-- Test: 53 veya 3, Canlı: 16 -->
<returnCode>RMA-2024-001</returnCode>
<startDate>20240101</startDate>     <!-- YYYYMMDD formatı -->
<endDate>20240131</endDate>
<maxCount>1</maxCount>
```

**Response:**
```xml
<ExtendedBaseResultVO>
  <outFlag>0</outFlag>
  <outResult>Başarılı</outResult>
  <errCode>0</errCode>
</ExtendedBaseResultVO>
```

---

## Özel Alan Formatı (specialField1)

**Format:** `alan_no$değer#alan_no$değer#`  
**Örnek:** `3$SIP-2024-001#7$MehmetYilmaz#53$BARKOD123#`

| No | Açıklama | No | Açıklama |
|----|----------|----|----------|
| 2 | Müşteri Seri No | 12 | Masraf Kodu |
| 3 | Sipariş No | 13 | Ürün |
| 4 | Poşet No | 14 | Müşteri Kargo Ref Kodu |
| 5 | Ambalaj No | 16 | İade Onay Kodu |
| 6 | Müşteri Kimlik No | 51 | Dergi Türü |
| 7 | Müşteri Ad Soyad | 52 | Temsilci No |
| 8 | Bölge | 53 | Anahtar Alan |
| 9 | Departman/Personel | 54 | Sevk İrsaliye No |
| 10 | Cep Tel | 55 | Alıcı Vergi No |
| 11 | Poliçe No | 56 | Takım Öncüsü Temsilci No |

---

## Hata Kodları

### createShipment
| Kod | Sabit | Açıklama |
|-----|-------|----------|
| 0 | — | Başarılı |
| 936 | — | Beklenmeyen hata (YK IT ile iletişim) |
| 80859 | ERR_INTG_CARGO_KEY_PARAM_NOT_FOUND | cargoKey bulunamadı |
| 82500 | ERR_INTG_CARGO_KEY_PARAM_LENGHT | cargoKey uzunluk aşımı (max 20) |
| 60020 | ERR_EXIST_CARGO_KEY_PARAM | cargoKey sistemde mevcut |
| 60017 | ERR_INTG_INVOICE_KEY_PARAM_NOT_FOUND | invoiceKey bulunamadı |
| 82501 | ERR_INTG_INVOICE_KEY_PARAM_LENGHT | invoiceKey uzunluk aşımı |
| 60018 | ERR_INTG_RECEIVER_CUST_NAME_PARAM_NOT_FOUND | Alıcı adı bulunamadı |
| 82503 | ERR_INTG_RECEIVER_CUST_NAME_PARAM_LENGHT | Alıcı adı uzunluk aşımı (max 100) |
| 60019 | ERR_INTG_RECEIVER_ADDRESS_PARAM_NOT_FOUND | Adres bulunamadı |
| 82502 | ERR_INTG_RECEIVER_ADDRESS_PARAM_LENGHT | Adres uzunluk hatası (min 10, max 500) |
| 82505 | ERR_INTG_TT_INVOICE_AMOUNT_PARAM_NOT_FOUND | Tahsilat tutarı bulunamadı |
| 82507 | ERR_INTG_TT_DOCUMENT_ID_PARAM_NOT_FOUND | Tahsilat belge no bulunamadı |
| 82509 | ERR_INTG_DC_SELECTED_CREDIT_NOT_FOUND | Taksit seçimi bulunamadı |
| 82511 | ERR_INTG_DC_CREDIT_RULE_NOT_FOUND | Kredi kuralı bulunamadı |
| 82512 | ERR_INTG_DC_COLL_CC_WRONG_PARAMETER | Ödeme tipi uyuşmuyor |
| 82513 | ERR_INTG_TT_COLL_TYPE | Hatalı ödeme tipi |
| 82514 | ERR_INTG_TT_DOC_SAVE_TYPE | Hatalı belge kayıt tipi |
| 82515 | ERR_INTG_EMAIL_ADDRESS_INVALID_PARAMETER | Geçersiz e-posta |
| 82516 | ERR_INTG_RECEIVER_PHONE_INVALID_PARAMETER | Geçersiz telefon |
| 82517 | ERR_INTG_INVALID_PARAMETER | Geçersiz format |

### cancelShipment
| Kod | Sabit | Açıklama |
|-----|-------|----------|
| 82519 | ERR_INTG_CARGO_KEY_NOT_FOUND | cargoKey kullanıcıya ait değil |
| 82520 | ERR_INTG_CARGO_KEY_OPERATION_CANCELLED | Zaten iptal edilmiş |

### queryShipment
| Kod | Sabit | Açıklama |
|-----|-------|----------|
| 82527 | ERR_INTG_KEY_TYPE_NOT_FOUND | keyType eksik |
| 82526 | ERR_INTG_KEYS_NOT_FOUND | keys eksik |

### saveReturnShipmentCode
| Kod | Açıklama |
|-----|----------|
| 82651 | İade kodu boş olamaz |
| 82652 | Kullanım adedi boş olamaz |
| 82654 | fieldName geçersiz |
| 82655 | İade kodu zaten kaydedilmiş |
| 60026 | Başlangıç tarihi zorunlu |
| 60027 | Bitiş tarihi zorunlu |
| 80838 | Tarih aralığı maksimum gün aşımı |

---

## Çalışma Modları

### Fatura Bazlı (İrsaliye Bazlı)
Her gönderi için bir kayıt. Her `cargoKey` = bir gönderi.

### Kargo Bazlı (Çoklu Paket)
Aynı alıcıya birden fazla paket:
- Her paket → farklı `cargoKey`
- Tüm paketler → aynı `invoiceKey`
- Her pakete `cargoCount: 1`

---

## Entegrasyon Akışı

```
┌─────────────────────────────────────────────────────┐
│ GİDEN KARGO AKIŞI                                   │
├─────────────────────────────────────────────────────┤
│ 1. createShipment → YK sistemine gönderi ilet       │
│ 2. cargoKey fiziksel olarak kargo üzerinde olmalı   │
│ 3. İptal: cancelShipment (düzenlenmeden önce)       │
│ 4. YK şubesi cargoKey okuyarak sisteme girer        │
│ 5. Gönderi düzenlenir (irsaliye/fatura)             │
│ 6. queryShipment ile takip edilir                    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ İADE KODU AKIŞI                                     │
├─────────────────────────────────────────────────────┤
│ 1. saveReturnShipmentCode → iade kodu oluştur       │
│ 2. Kodu müşteriye ilet (SMS, e-posta)               │
│ 3. Müşteri kodu YK şubesine verir                   │
│ 4. YK şubesi iade gönderisini başlatır              │
└─────────────────────────────────────────────────────┘
```

---

## Parametrik Raporlama (Takip Linki)

```
http://selfservis.yurticikargo.com/reports/SswReportsFromParamFields.aspx?ssfldvn=XX&sskurkod=MUSTERI_KODU&refnumber=REF_NO&date=GG.AA.YYYY
```

| Parametre | Açıklama |
|-----------|----------|
| ssfldvn | Özel alan numarası (tablodaki No değerleri) |
| sskurkod | YK müşteri kodu |
| refnumber | Takip edilecek değer |
| date | Gönderi tarihi (dd.mm.yyyy, ±5 gün tolerans) |

---

## Bilinen Sorunlar ve Dikkat Edilecekler

1. **userLanguage vs wsLanguage** — createShipment/cancelShipment `userLanguage`, queryShipment/saveReturnShipmentCode `wsLanguage` kullanır
2. **Endpoint URL** — SOAP POST hedefinde `?wsdl` OLMAMALI
3. **PHP SoapClient** — `location` parametresi mutlaka verilmeli, tüm WSDL property'leri (boş bile olsa) gönderilmeli
4. **cargoKey benzersizliği** — Test ortamında da kalıcıdır, her çalıştırmada yeni key üretin
5. **receiverAddress** — Minimum 10 karakter zorunlu
6. **Tarih formatı** — Kesinlikle `YYYYMMDD` (tire/nokta/slash yok)
7. **ttInvoiceAmount ayracı** — Nokta (.) kullanın, virgül (,) kabul edilmez
8. **fieldName** — Test: `53` veya `3`, Canlı: `16` (sözleşmeye özel)
9. **IP Yetkilendirme** — Canlı ortam için çıkış IP'si bildirilmeli
10. **SSL** — Test ortamında self-signed sertifika kullanılabilir, verification'ı devre dışı bırakın

---

## Dizin Yapısı

```
ykapi/
├── php/                    # PHP 8.0+, ext-soap
├── dotnet/                 # .NET 8.0+, HttpClient + XDocument
├── java/                   # Java 11+, HttpClient + javax.xml
├── javascript/             # Node.js 18+, https module, ESM
├── python/                 # Python 3.10+, urllib + xml.etree
├── go/                     # Go 1.21+, net/http + encoding/xml
├── docs/                   # Orijinal YK teknik dokümanları
└── README.md               # Ana proje dokümantasyonu
```

---

## Kod Üretme Kuralları (AI Asistanlar İçin)

Bu projeye kod eklerken veya düzenlerken:

1. **Sıfır bağımlılık** — Harici paket eklemeyin, standard library kullanın
2. **SOAP XML elle oluşturulur** — WSDL client generator kullanmayın
3. **Her fonksiyon ayrı dosya** — functions/ klasöründe
4. **Controller birleştirir** — Tek sınıf tüm fonksiyonları method olarak sunar
5. **Test gerçek API'ye bağlanır** — Mock değil, YKTEST ortamına
6. **AllInOne bağımsız çalışır** — Tek dosya, hiçbir import/require gerekmez
7. **Dil convention'ına uy** — Python: snake_case, Go: PascalCase, JS: camelCase
8. **XML'de camelCase** — SOAP alanları her zaman camelCase (cargoKey, invoiceKey...)
9. **Error handling** — Her dilde idiomatic hata yönetimi (try/catch, Result/error tuple)
10. **UTF-8** — Tüm dosyalar ve HTTP istekleri UTF-8 encoding
