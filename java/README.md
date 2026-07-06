# Yurtiçi Kargo Java API Client

Yurtiçi Kargo SOAP Web Service entegrasyonu için Java istemci kütüphanesi. Harici bağımlılık gerektirmez, Java 11+ built-in `HttpClient` ve `javax.xml.parsers` kullanır.

---

## Gereksinimler

- **Java 11+** (HttpClient built-in)
- `javax.xml.parsers` (built-in)
- `java.net.http.HttpClient` (built-in)
- **Harici bağımlılık yok**

---

## Proje Yapısı

```
java/
├── src/main/java/com/yurticikargo/
│   ├── functions/
│   │   ├── CreateShipment.java        # Gönderi oluşturma
│   │   ├── CancelShipment.java        # Gönderi iptal
│   │   ├── QueryShipment.java         # Gönderi sorgulama
│   │   └── SaveReturnShipmentCode.java # İade kodu oluşturma
│   ├── models/
│   │   ├── ShipmentResult.java        # createShipment sonuç modeli
│   │   ├── CancelResult.java          # cancelShipment sonuç modeli
│   │   ├── QueryResult.java           # queryShipment sonuç modeli
│   │   └── ReturnCodeResult.java      # saveReturnShipmentCode sonuç modeli
│   └── YurticiKargoClient.java        # Ana istemci (controller)
├── src/test/java/com/yurticikargo/
│   ├── CreateShipmentTest.java
│   ├── CancelShipmentTest.java
│   ├── QueryShipmentTest.java
│   └── SaveReturnShipmentCodeTest.java
└── YurticiKargoAllInOne.java          # Tek dosya versiyonu
```

---

## Derleme ve Çalıştırma

### AllInOne (Tek Dosya)

```bash
# Derleme
javac -encoding UTF-8 YurticiKargoAllInOne.java

# Çalıştırma
java YurticiKargoAllInOne
```

### Modüler Yapı

```bash
# Derleme
javac -encoding UTF-8 -d out \
    src/main/java/com/yurticikargo/models/*.java \
    src/main/java/com/yurticikargo/functions/*.java \
    src/main/java/com/yurticikargo/YurticiKargoClient.java

# Çalıştırma
java -cp out com.yurticikargo.YurticiKargoClient
```

### Test Çalıştırma

```bash
# Test derleme ve çalıştırma
javac -encoding UTF-8 -d out \
    src/main/java/com/yurticikargo/models/*.java \
    src/main/java/com/yurticikargo/functions/*.java \
    src/main/java/com/yurticikargo/YurticiKargoClient.java \
    src/test/java/com/yurticikargo/*.java

java -cp out com.yurticikargo.CreateShipmentTest
java -cp out com.yurticikargo.CancelShipmentTest
java -cp out com.yurticikargo.QueryShipmentTest
java -cp out com.yurticikargo.SaveReturnShipmentCodeTest
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

```java
import com.yurticikargo.YurticiKargoClient;
import com.yurticikargo.models.*;

import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {

        // Test ortamı
        YurticiKargoClient client = new YurticiKargoClient(
            "YKTEST",  // username
            "YK",      // password
            "TR",      // language
            true       // testMode
        );

        // Canlı ortam
        YurticiKargoClient prodClient = new YurticiKargoClient(
            "KULLANICI_ADINIZ",  // username
            "SIFRENIZ",          // password
            "TR",                // language
            false                // testMode
        );
    }
}
```

---

## API Metodları

Her metod Java 11 `HttpClient` ile raw SOAP XML gönderir. WSDL ayrıştırma veya kod üretimi yapılmaz; SOAP envelope'lar doğrudan oluşturulur ve XML yanıtlar `javax.xml.parsers.DocumentBuilder` ile parse edilir.

### SOAP Action Bilgileri

| Metod | SOAP Action | Dil Parametresi |
|-------|-------------|-----------------|
| `createShipment` | `ship:createShipment` | `userLanguage` |
| `cancelShipment` | `ship:cancelShipment` | `userLanguage` |
| `queryShipment` | `ship:queryShipment` | `wsLanguage` |
| `saveReturnShipmentCode` | `ship:saveReturnShipmentCode` | `wsLanguage` |

---

### 1. createShipment — Gönderi Oluşturma

Müşterinin kargo bilgilerini Yurtiçi Kargo sistemine ileten servistir.

```java
Map<String, String> shipment = new HashMap<>();
shipment.put("cargoKey", "TEST001");
shipment.put("invoiceKey", "INV001");
shipment.put("receiverCustName", "Mehmet Yılmaz");
shipment.put("receiverAddress", "Eski Büyükdere Cad. No:3");
shipment.put("receiverPhone1", "05321234567");
shipment.put("cityName", "İstanbul");
shipment.put("townName", "Maslak");

ShipmentResult result = client.createShipment(List.of(shipment));

if (result.isSuccess()) {
    System.out.println("Başarılı! Job ID: " + result.getJobId());
    for (ShipmentResult.Detail detail : result.getDetails()) {
        System.out.println("Cargo Key: " + detail.getCargoKey() +
            " - Durum: " + detail.getErrMessage());
    }
} else {
    System.out.println("Hata: " + result.getOutResult());
    for (ShipmentResult.Detail error : result.getErrors()) {
        System.out.println("  [" + error.getErrCode() + "] " + error.getErrMessage());
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

```java
// Kapıda nakit ödeme örneği
Map<String, String> shipment = new HashMap<>();
shipment.put("cargoKey", "COD001");
shipment.put("invoiceKey", "CODINV001");
shipment.put("receiverCustName", "Ali Veli");
shipment.put("receiverAddress", "Bağdat Cad. No:123");
shipment.put("receiverPhone1", "05551234567");
shipment.put("ttCollectionType", "0");
shipment.put("ttInvoiceAmount", "150.00");
shipment.put("ttDocumentId", "FTR001");
shipment.put("ttDocumentSaveType", "0");

ShipmentResult result = client.createShipment(List.of(shipment));
```

#### Çoklu Paket (Kargo Bazlı) Örneği

Aynı alıcıya birden fazla paket gönderildiğinde, her paket için farklı `cargoKey`, aynı `invoiceKey` kullanılır.

```java
List<Map<String, String>> shipments = new ArrayList<>();

for (int i = 1; i <= 3; i++) {
    Map<String, String> pkg = new HashMap<>();
    pkg.put("cargoKey", "PKG00" + i);
    pkg.put("invoiceKey", "A123456");       // Hepsi aynı fatura
    pkg.put("receiverCustName", "Ali Veli");
    pkg.put("receiverAddress", "Adres bilgisi");
    pkg.put("receiverPhone1", "05551234567");
    pkg.put("waybillNo", "A123456");
    pkg.put("cargoCount", "1");
    shipments.add(pkg);
}

ShipmentResult result = client.createShipment(shipments);
```

#### Sonuç Yapısı (ShipmentResult)

| Alan | Tip | Açıklama |
|------|-----|----------|
| `outFlag` | int | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
| `outResult` | String | Sonuç mesajı |
| `jobId` | int | YK talep numarası (başarılı ise) |
| `count` | int | İşlem yapılan gönderi sayısı |
| `details[]` | List | Her gönderi için detay |
| `details[].cargoKey` | String | Kargo anahtarı |
| `details[].invoiceKey` | String | Fatura anahtarı |
| `details[].errCode` | int | Hata kodu (0=başarılı) |
| `details[].errMessage` | String | Hata mesajı |

---

### 2. cancelShipment — Gönderi İptal

Web servis ile sisteme gönderilmiş bilgilerin iptal edilmesini ve kargonun çıkışının engellenmesini sağlar.

> ⚠️ **Önemli:** Gönderi düzenlendikten sonra iptal yapılamaz.

```java
CancelResult result = client.cancelShipment(List.of("TEST001", "TEST002"));

if (result.isSuccess()) {
    for (CancelResult.Detail detail : result.getDetails()) {
        System.out.println(detail.getCargoKey() + ": " +
            detail.getOperationMessage() + " (" + detail.getOperationStatus() + ")");
    }
} else {
    System.out.println("Hata: " + result.getOutResult());
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
| `outResult` | String | Sonuç mesajı |
| `senderCustId` | int | Gönderici müşteri kodu |
| `count` | int | İşlem yapılan gönderi sayısı |
| `details[].cargoKey` | String | Kargo anahtarı |
| `details[].invoiceKey` | String | Fatura anahtarı |
| `details[].jobId` | int | YK talep numarası |
| `details[].docId` | String | YK gönderi kodu |
| `details[].operationCode` | int | İşlem kodu |
| `details[].operationMessage` | String | İşlem mesajı |
| `details[].operationStatus` | String | İşlem durumu |
| `details[].errCode` | int | Hata kodu |
| `details[].errMessage` | String | Hata mesajı |

---

### 3. queryShipment — Gönderi Sorgulama

Müşterinin kendi referans kodu ile gönderi geçmişini raporlayan servistir. Tek seferde birden fazla gönderi sorgulanabilir.

```java
// Cargo Key ile sorgulama
QueryResult result = client.queryShipment(
    List.of("12520", "12521"),  // keys
    0,                          // keyType: 0=CargoKey, 1=InvoiceKey
    true,                       // addHistoricalData: hareket geçmişi
    false                       // onlyTracking
);

// Invoice Key ile sorgulama
QueryResult result2 = client.queryShipment(
    List.of("A123456"),         // keys
    1,                          // keyType: 1=InvoiceKey
    false,                      // addHistoricalData
    false                       // onlyTracking
);

if (result.isSuccess()) {
    for (QueryResult.Detail detail : result.getDetails()) {
        if (detail.isSuccess()) {
            System.out.println("Kargo: " + detail.getCargoKey());
            System.out.println("Durum: " + detail.getOperationMessage() +
                " (" + detail.getOperationStatus() + ")");

            QueryResult.ItemDetail item = detail.getItemDetail();
            if (item != null) {
                System.out.println("Takip: " + item.getTrackingUrl());
                System.out.println("Alıcı: " + item.getReceiverCustName());
                System.out.println("Çıkış: " + item.getDepartureUnitName());
                System.out.println("Teslim: " + item.getDeliveryDate() +
                    " " + item.getDeliveryTime());

                // Hareket geçmişi
                for (Map<String, String> event : item.getCargoHistory()) {
                    System.out.println("  → " + event.get("eventDate") +
                        " " + event.get("eventTime") + " | " +
                        event.get("unitName") + " | " +
                        event.get("eventName") + " | " +
                        event.get("reasonName"));
                }
            }
        } else {
            System.out.println("Hata [" + detail.getErrCode() + "]: " +
                detail.getErrMessage());
        }
    }
}
```

#### Sorgu Parametreleri

| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| `keys` | List\<String\> | ✅ | Sorgulanacak anahtar değerleri listesi |
| `keyType` | int | ✅ | 0=Cargo Key, 1=Invoice Key |
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

```java
ReturnCodeResult result = client.saveReturnShipmentCode(
    "RMA-2024-001",  // returnCode: Sizin belirlediğiniz iade kodu
    "20240101",      // startDate: Geçerlilik başlangıç (YYYYMMDD)
    "20240131",      // endDate: Geçerlilik bitiş (YYYYMMDD)
    1,               // maxCount: Kullanım adedi
    "53"             // fieldName: Test ortamında 53 veya 3; canlıda 16
);

if (result.isSuccess()) {
    System.out.println("İade kodu başarıyla oluşturuldu!");
} else {
    System.out.println("Hata [" + result.getErrCode() + "]: " + result.getOutResult());
}
```

#### Parametreler

| Parametre | Tip | Zorunlu | Açıklama | Örnek |
|-----------|-----|---------|----------|-------|
| `returnCode` | String | ✅ | İade kodu (sizin belirleyeceğiniz benzersiz değer) | `RMA-2024-001` |
| `startDate` | String | ✅ | Kod geçerlilik başlangıç tarihi (YYYYMMDD) | `20240101` |
| `endDate` | String | ✅ | Kod geçerlilik bitiş tarihi (YYYYMMDD) | `20240131` |
| `maxCount` | int | ✅ | İade kodu kullanım adedi | `1` |
| `fieldName` | String | ✅ | Özel alan bilgisi | Test: `53` veya `3`, Canlı: `16` |

> ⚠️ **Not:** Test ortamında `fieldName` olarak `53` veya `3` kullanın. Canlı ortamda sözleşmenize özel `16` değeri tanımlanacaktır.

#### Sonuç Yapısı (ReturnCodeResult)

| Alan | Tip | Açıklama |
|------|-----|----------|
| `outFlag` | int | 0=Başarılı, 1=Hata |
| `outResult` | String | Sonuç mesajı |
| `errCode` | int | Hata kodu (0=başarılı) |

---

## Özel Alan Bilgileri (specialField1)

`specialField1` alanına birden fazla özel alan bilgisi gönderilebilir.

**Format:** `alan_no$deger#alan_no$deger#`

**Örnek:** `1$426031#2$397427#`

```java
shipment.put("specialField1", "1$426031#2$397427#");
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
| `ssfldvn` | Özel alan adı (yukarıdaki özel alan tablosundaki değerler) |
| `sskurkod` | YK müşteri kodu |
| `refnumber` | Takip edilecek özel alan değeri |
| `date` | Gönderi tarihi (dd.mm.yyyy, ±5 gün tolerans) |

### Java ile Takip Linki Oluşturma

```java
String trackingUrl = String.format(
    "http://selfservis.yurticikargo.com/reports/SswReportsFromParamFields.aspx" +
    "?ssfldvn=%s&sskurkod=%s&refnumber=%s&date=%s",
    "53",           // özel alan adı
    "MUSTERI_KODU", // YK müşteri kodu
    "REF123",       // referans numarası
    "01.07.2024"    // gönderi tarihi
);
```

---

## Debug

```java
// Son SOAP isteğini görüntüle
System.out.println(client.getLastRequest());

// Son SOAP yanıtını görüntüle
System.out.println(client.getLastResponse());
```

---

## IP Yetkilendirme

Yurtiçi Kargo web servislerine erişim için IP yetkilendirmesi zorunludur. Canlı ortama geçmeden önce çıkış IP adresinizi **Bölge Müdürlüğü Satış Temsilcinize** bildirmeniz gerekmektedir.

> ⚠️ Test ortamında IP kısıtlaması yoktur. Canlı ortamda yetkilendirilmemiş IP'lerden gelen istekler reddedilir.

---

## Mimari Notlar

### Neden Raw SOAP?

Bu kütüphane WSDL code generation (wsimport, JAX-WS) yerine raw SOAP XML tercih eder:

1. **Sıfır bağımlılık** — Ek JAR dosyası gerektirmez
2. **Java 11+ uyumluluk** — JAX-WS, Java 11'den itibaren JDK'dan kaldırıldı
3. **Şeffaflık** — Gönderilen/alınan XML'i doğrudan görebilirsiniz
4. **Basitlik** — WSDL değişikliklerinden etkilenmez

### Thread Safety

`YurticiKargoClient` thread-safe değildir. Her thread için ayrı instance oluşturun veya synchronized erişim sağlayın.

```java
// Her thread için ayrı client
ExecutorService executor = Executors.newFixedThreadPool(4);
executor.submit(() -> {
    YurticiKargoClient client = new YurticiKargoClient("YKTEST", "YK", "TR", true);
    // ...
});
```

### Timeout Ayarları

Varsayılan HTTP timeout değerleri `HttpClient` içinde ayarlanmıştır. Ağ koşullarına göre ayarlayabilirsiniz.

---

## Çalışma Modları

### Fatura Bazlı (İrsaliye Bazlı)

Her gönderi için bir kayıt iletilir. Her `cargoKey` için bir gönderi düzenlenir.

### Kargo Bazlı (Çoklu Paket)

Aynı alıcıya birden fazla paket gönderildiğinde, her paket için farklı `cargoKey`, aynı `invoiceKey` kullanılır.

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
- Ör: `"TEST" + System.currentTimeMillis()` veya `UUID.randomUUID().toString().substring(0, 20)`

### 4. "RECEIVER_ADDRESS parametresi min: 10 max: 500 uzunluğunda olmalıdır" (Hata 82502)
**Sorun:** Adres alanı çok kısa veya çok uzun.
**Çözüm:**
- Adres en az 10 karakter olmalıdır
- En fazla 500 karakter olmalıdır
- Kısa adreslere ilçe/şehir ekleyerek uzatın

### 5. "Sözleşme Üzerinde Tanımlı Özel Alan Bilgisi Bulunamadı"
**Sorun:** saveReturnShipmentCode'da fieldName değeri geçersiz.
**Çözüm:**
- Test ortamında `fieldName` olarak `"53"` veya `"3"` kullanın
- Canlı ortamda `"16"` kullanın (sözleşmeye özel tanımlanır)
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

### 16. Java: SSLHandshakeException
**Sorun:** SSL sertifika doğrulama hatası alınıyor.
**Çözüm:** Test ortamı için TrustManager'ı devre dışı bırakın:
```java
TrustManager[] trustAllCerts = new TrustManager[]{
    new X509TrustManager() {
        public X509Certificate[] getAcceptedIssuers() { return null; }
        public void checkClientTrusted(X509Certificate[] certs, String authType) {}
        public void checkServerTrusted(X509Certificate[] certs, String authType) {}
    }
};
SSLContext sc = SSLContext.getInstance("SSL");
sc.init(null, trustAllCerts, new java.security.SecureRandom());
HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
```
> ⚠️ Bu ayarı sadece test ortamında kullanın.

### 17. Java: java.net.ConnectException: Connection timed out
**Sorun:** Bağlantı zaman aşımına uğruyor.
**Çözüm:** Firewall kontrolü yapın ve gerekirse proxy ayarlarını verin:
```java
System.setProperty("http.proxyHost", "proxy.sirket.com");
System.setProperty("http.proxyPort", "8080");
System.setProperty("https.proxyHost", "proxy.sirket.com");
System.setProperty("https.proxyPort", "8080");
```

### 18. Java: Encoding hatası (Türkçe karakter bozulması)
**Sorun:** Türkçe karakterler derleme veya çalışma zamanında bozuluyor.
**Çözüm:** Source dosyaları UTF-8 flag'i ile derleyin:
```bash
javac -encoding UTF-8 YurticiKargoAllInOne.java
```
JVM'e de encoding parametresi verin:
```bash
java -Dfile.encoding=UTF-8 YurticiKargoAllInOne
```

---

## Lisans

MIT
