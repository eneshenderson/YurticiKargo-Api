# Yurtiçi Kargo .NET (C#) API Client

Yurtiçi Kargo SOAP Web Service entegrasyonu için .NET (C#) istemci kütüphanesi.

WCF bağımlılığı olmadan, raw SOAP XML over `HttpClient` kullanarak çalışır.

## Gereksinimler

- .NET 8.0+
- Harici paket gerektirmez (`System.Net.Http` + `System.Xml.Linq` kullanır)

## Proje Yapısı

```
dotnet/
├── Functions/
│   ├── CreateShipment.cs          # Gönderi oluşturma
│   ├── CancelShipment.cs          # Gönderi iptal
│   ├── QueryShipment.cs           # Gönderi sorgulama
│   └── SaveReturnShipmentCode.cs  # İade kodu oluşturma
├── Models/
│   ├── ShipmentResult.cs          # Gönderi sonuç modeli
│   ├── CancelResult.cs            # İptal sonuç modeli
│   ├── QueryResult.cs             # Sorgu sonuç modeli
│   └── ReturnCodeResult.cs        # İade kodu sonuç modeli
├── YurticiKargoClient.cs          # Ana controller sınıfı
├── Tests/
│   ├── CreateShipmentTest.cs      # Gönderi oluşturma testi
│   ├── CancelShipmentTest.cs      # İptal testi
│   ├── QueryShipmentTest.cs       # Sorgulama testi
│   └── SaveReturnShipmentCodeTest.cs  # İade kodu testi
└── YurticiKargoAllInOne.cs        # Tüm kodlar tek dosyada
```

## Kurulum ve Çalıştırma

```bash
cd dotnet
dotnet run
```

Testleri çalıştırmak için:

```bash
cd dotnet
dotnet run -- test
```

---

## Hızlı Başlangıç

```csharp
using YurticiKargo;

// Test ortamı
var client = new YurticiKargoClient("YKTEST", "YK", "TR", testMode: true);

// Canlı ortam
var client = new YurticiKargoClient("KULLANICI_ADINIZ", "SIFRENIZ", "TR", testMode: false);
```

## Test Ortamı Bilgileri

| Parametre | Değer |
|-----------|-------|
| Username | `YKTEST` |
| Password | `YK` |
| Language | `TR` |
| Endpoint (Test) | `https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices` |
| Endpoint (Canlı) | `https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices` |

> ⚠️ **Önemli:** Endpoint URL'de `?wsdl` OLMAMALIDIR. SOAP POST hedefi olarak doğrudan servis adresi kullanılır.

---

## API Metodları

### 1. CreateShipmentAsync — Gönderi Oluşturma

Müşterinin kargo bilgilerini Yurtiçi Kargo sistemine ileten servistir.

```csharp
var shipments = new List<Dictionary<string, string>>
{
    new()
    {
        ["cargoKey"]         = "0000113",        // Benzersiz kargo anahtarı (zorunlu)
        ["invoiceKey"]       = "AB00113",        // Fatura anahtarı (zorunlu)
        ["receiverCustName"] = "Mehmet Yılmaz",  // Alıcı adı (zorunlu)
        ["receiverAddress"]  = "Eski Büyükdere Cad. No:3", // Alıcı adresi (zorunlu)
        ["receiverPhone1"]   = "02123652426",    // Alıcı telefon (zorunlu)
        ["cityName"]         = "İstanbul",       // Şehir (opsiyonel)
        ["townName"]         = "Maslak"          // İlçe (opsiyonel)
    }
};

var result = await client.CreateShipmentAsync(shipments);

if (result.IsSuccess)
{
    Console.WriteLine($"Başarılı! Job ID: {result.JobId}");
    foreach (var detail in result.Details)
    {
        Console.WriteLine($"Cargo Key: {detail.CargoKey} - Durum: {detail.ErrMessage}");
    }
}
else
{
    Console.WriteLine($"Hata: {result.OutResult}");
    foreach (var error in result.GetErrors())
    {
        Console.WriteLine($"  [{error.ErrCode}] {error.ErrMessage}");
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

```csharp
// 3 paketli bir gönderi örneği
var shipments = new List<Dictionary<string, string>>
{
    new()
    {
        ["cargoKey"]         = "10012",
        ["invoiceKey"]       = "A123456",  // Hepsi aynı fatura
        ["receiverCustName"] = "Ali Veli",
        ["receiverAddress"]  = "Adres bilgisi",
        ["receiverPhone1"]   = "05551234567",
        ["waybillNo"]        = "A123456",
        ["cargoCount"]       = "1"
    },
    new()
    {
        ["cargoKey"]         = "10013",
        ["invoiceKey"]       = "A123456",
        ["receiverCustName"] = "Ali Veli",
        ["receiverAddress"]  = "Adres bilgisi",
        ["receiverPhone1"]   = "05551234567",
        ["waybillNo"]        = "A123456",
        ["cargoCount"]       = "1"
    },
    new()
    {
        ["cargoKey"]         = "10014",
        ["invoiceKey"]       = "A123456",
        ["receiverCustName"] = "Ali Veli",
        ["receiverAddress"]  = "Adres bilgisi",
        ["receiverPhone1"]   = "05551234567",
        ["waybillNo"]        = "A123456",
        ["cargoCount"]       = "1"
    }
};

var result = await client.CreateShipmentAsync(shipments);
```

#### Sonuç Yapısı (ShipmentResult)

| Alan | Tip | Açıklama |
|------|-----|----------|
| `OutFlag` | int | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
| `OutResult` | string | Sonuç mesajı |
| `JobId` | int | YK talep numarası (başarılı ise) |
| `Count` | int | İşlem yapılan gönderi sayısı |
| `IsSuccess` | bool | `OutFlag == 0` |
| `Details[]` | array | Her gönderi için detay |
| `Details[].CargoKey` | string | Kargo anahtarı |
| `Details[].InvoiceKey` | string | Fatura anahtarı |
| `Details[].ErrCode` | int | Hata kodu (0=başarılı) |
| `Details[].ErrMessage` | string | Hata mesajı |

---

### 2. CancelShipmentAsync — Gönderi İptal

Web servis ile sisteme gönderilmiş bilgilerin iptal edilmesini ve kargonun çıkışının engellenmesini sağlar.

> ⚠️ Gönderi düzenlendikten sonra iptal yapılamaz.

```csharp
var result = await client.CancelShipmentAsync(new[] { "0000113", "0000114" });

if (result.IsSuccess)
{
    foreach (var detail in result.Details)
    {
        Console.WriteLine($"{detail.CargoKey}: {detail.OperationMessage} ({detail.OperationStatus})");
    }
}
else
{
    Console.WriteLine($"Hata: {result.OutResult}");
}
```

#### İptal Durum Kodları

| OperationStatus | OperationCode | Açıklama |
|-----------------|---------------|----------|
| `NOP` | 0 | İşlem yapılmadı, düzenlenmemiş |
| `IND` | 1 | Kargo teslimattadır |
| `ISR` | 2 | Düzenlenmiş, fatura prosedürü tamamlanmamış |
| `CNL` | 3 | Kargo çıkışı engellendi (başarılı iptal) |
| `ISC` | 4 | Kargo zaten iptal edilmiş |

#### Sonuç Yapısı (CancelResult)

| Alan | Tip | Açıklama |
|------|-----|----------|
| `OutFlag` | int | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
| `OutResult` | string | Sonuç mesajı |
| `SenderCustId` | int | Gönderici müşteri kodu |
| `Count` | int | İşlem yapılan gönderi sayısı |
| `IsSuccess` | bool | `OutFlag == 0` |
| `Details[].CargoKey` | string | Kargo anahtarı |
| `Details[].InvoiceKey` | string | Fatura anahtarı |
| `Details[].JobId` | int | YK talep numarası |
| `Details[].DocId` | string | YK gönderi kodu |
| `Details[].OperationCode` | int | İşlem kodu |
| `Details[].OperationMessage` | string | İşlem mesajı |
| `Details[].OperationStatus` | string | İşlem durumu |
| `Details[].ErrCode` | int | Hata kodu |
| `Details[].ErrMessage` | string | Hata mesajı |

---

### 3. QueryShipmentAsync — Gönderi Sorgulama

Müşterinin kendi referans kodu ile gönderi geçmişini raporlayan servistir. Tek seferde birden fazla gönderi sorgulanabilir.

```csharp
// Cargo Key ile sorgulama
var result = await client.QueryShipmentAsync(
    keys: new[] { "12520", "12521" },
    keyType: 0,                    // 0 = Cargo Key
    addHistoricalData: true,       // Hareket geçmişi dahil
    onlyTracking: false
);

// Invoice Key ile sorgulama
var result = await client.QueryShipmentAsync(
    keys: new[] { "A123456" },
    keyType: 1                     // 1 = Invoice Key
);

if (result.IsSuccess)
{
    foreach (var detail in result.Details)
    {
        if (detail.IsSuccess)
        {
            Console.WriteLine($"Kargo: {detail.CargoKey}");
            Console.WriteLine($"Durum: {detail.OperationMessage} ({detail.OperationStatus})");

            if (detail.ItemDetail != null)
            {
                var item = detail.ItemDetail;
                Console.WriteLine($"Takip: {item.TrackingUrl}");
                Console.WriteLine($"Alıcı: {item.ReceiverCustName}");
                Console.WriteLine($"Çıkış: {item.DepartureUnitName}");
                Console.WriteLine($"Teslim: {item.DeliveryDate} {item.DeliveryTime}");

                // Hareket geçmişi
                foreach (var ev in item.CargoHistory)
                {
                    Console.WriteLine($"  → {ev.EventDate} {ev.EventTime} | {ev.UnitName} | {ev.EventName} | {ev.ReasonName}");
                }
            }
        }
        else
        {
            Console.WriteLine($"Hata [{detail.ErrCode}]: {detail.ErrMessage}");
        }
    }
}
```

#### Sorgu Parametreleri

| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| `keys` | string[] | ✅ | Sorgulanacak anahtar değerleri dizisi |
| `keyType` | int | ✅ | 0=Cargo Key, 1=Invoice Key |
| `addHistoricalData` | bool | ❌ | Hareket geçmişi dahil edilsin mi? (Performans için `false` önerilir) |
| `onlyTracking` | bool | ❌ | Sadece takip URL'si dönsün mü? |

#### Gönderi Durum Kodları

| OperationStatus | OperationCode | Açıklama |
|-----------------|---------------|----------|
| `NOP` | 0 | İşlem yapılmadı, düzenlenmemiş |
| `IND` | 1 | Kargo teslimattadır |
| `ISR` | 2 | Düzenlenmiş, fatura prosedürü tamamlanmamış |
| `CNL` | 3 | Çıkış engellendi |
| `ISC` | 4 | İptal edilmiş |
| `DLV` | 5 | Teslim edildi |
| `BI` | 6 | YK acente tarafından iptal edildi |

#### İade Durum Kodları (RejectStatus)

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

> 📌 `RejectStatus` 0, 1, 2, 3, 9, 10 → İade süreci devam ediyor  
> 📌 `RejectStatus` 4, 7, 8, 11 → İade iptal edildi, normal süreç başladı

#### Sonuç Yapısı (QueryResult)

| Alan | Tip | Açıklama |
|------|-----|----------|
| `OutFlag` | int | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
| `OutResult` | string | Sonuç mesajı |
| `IsSuccess` | bool | `OutFlag == 0` |
| `Details[]` | array | Her gönderi için detay |
| `Details[].CargoKey` | string | Kargo anahtarı |
| `Details[].InvoiceKey` | string | Fatura anahtarı |
| `Details[].OperationCode` | int | İşlem kodu |
| `Details[].OperationMessage` | string | İşlem mesajı |
| `Details[].OperationStatus` | string | İşlem durumu |
| `Details[].IsSuccess` | bool | Detay başarılı mı |
| `Details[].ItemDetail` | object | Gönderi detay bilgileri |
| `Details[].ItemDetail.TrackingUrl` | string | Takip linki |
| `Details[].ItemDetail.ReceiverCustName` | string | Alıcı adı |
| `Details[].ItemDetail.DepartureUnitName` | string | Çıkış şubesi |
| `Details[].ItemDetail.DeliveryDate` | string | Teslim tarihi |
| `Details[].ItemDetail.DeliveryTime` | string | Teslim saati |
| `Details[].ItemDetail.CargoHistory[]` | array | Hareket geçmişi |

---

### 4. SaveReturnShipmentCodeAsync — İade Kodu Oluşturma

İade müşterilerinin YK birimine ileterek iade işlemini tamamlayacakları kodu oluşturan servistir.

```csharp
var result = await client.SaveReturnShipmentCodeAsync(
    returnCode: "RMA-2024-001",  // Sizin belirlediğiniz iade kodu
    startDate: "20240101",        // Geçerlilik başlangıç (YYYYMMDD)
    endDate: "20240131",          // Geçerlilik bitiş (YYYYMMDD)
    maxCount: 1,                  // Kullanım adedi
    fieldName: "53"               // Test ortamında 53 veya 3; canlıda 16
);

if (result.IsSuccess)
{
    Console.WriteLine("İade kodu başarıyla oluşturuldu!");
}
else
{
    Console.WriteLine($"Hata [{result.ErrCode}]: {result.OutResult}");
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

#### Sonuç Yapısı (ReturnCodeResult)

| Alan | Tip | Açıklama |
|------|-----|----------|
| `OutFlag` | int | 0=Başarılı, 1=Hata, 2=Beklenmeyen hata |
| `OutResult` | string | Sonuç mesajı |
| `ErrCode` | int | Hata kodu |
| `IsSuccess` | bool | `OutFlag == 0` |

---

## Önemli Teknik Notlar

### SOAP Dil Parametresi Farkı

| Metod | Parametre Adı | Açıklama |
|-------|---------------|----------|
| `CreateShipmentAsync` | `userLanguage` | Kullanıcı dil parametresi |
| `CancelShipmentAsync` | `userLanguage` | Kullanıcı dil parametresi |
| `QueryShipmentAsync` | `wsLanguage` | Web servis dil parametresi |
| `SaveReturnShipmentCodeAsync` | `wsLanguage` | Web servis dil parametresi |

### Endpoint URL Yapısı

```
✅ Doğru: https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices
❌ Yanlış: https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl
```

`?wsdl` eki WSDL tanım dosyasını döndürür. SOAP POST istekleri için `?wsdl` olmadan kullanılmalıdır.

### HttpClient Kullanımı

Bu kütüphane .NET'in built-in `HttpClient` sınıfını kullanır. WCF veya üçüncü parti SOAP kütüphanesine ihtiyaç yoktur. SOAP envelope'ları `System.Xml.Linq` ile oluşturulur ve parse edilir.

---

## Özel Alan Bilgileri (specialField1)

`specialField1` alanına birden fazla özel alan bilgisi gönderilebilir.

**Format:** `alan_no$deger#alan_no$deger#`

**Örnek:** `1$426031#2$397427#`

```csharp
shipment["specialField1"] = "1$426031#2$397427#";
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

## Debug

```csharp
// Son SOAP isteğini görüntüle
Console.WriteLine(client.GetLastRequest());

// Son SOAP yanıtını görüntüle
Console.WriteLine(client.GetLastResponse());
```

Örnek SOAP Request çıktısı:

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ship="http://yurticikargo.com.tr">
  <soapenv:Body>
    <ship:createShipment>
      <wsUserName>YKTEST</wsUserName>
      <wsPassword>YK</wsPassword>
      <userLanguage>TR</userLanguage>
      <ShippingOrderVO>
        <cargoKey>TEST001</cargoKey>
        <invoiceKey>INV001</invoiceKey>
        <receiverCustName>Mehmet Yılmaz</receiverCustName>
        <receiverAddress>Eski Büyükdere Cad. No:3</receiverAddress>
        <receiverPhone1>05321234567</receiverPhone1>
      </ShippingOrderVO>
    </ship:createShipment>
  </soapenv:Body>
</soapenv:Envelope>
```

---

## Entegrasyon Akışı

### Giden Kargo Akışı

```
1. CreateShipmentAsync ile gönderi bilgileri YK sistemine iletilir
2. Kargo anahtarı (cargoKey) fiziksel olarak kargo üzerinde bulunmalıdır
3. Gönderi düzenlenmeden önce CancelShipmentAsync ile iptal edilebilir
4. YK şubesi kargo anahtarını okuyarak sisteme girer
5. Alıcı bilgileri ekranda görünür
6. YK şubesi sevkiyat adresini belirler
7. Kargo adedi ve taşıma adresi girilerek YK irsaliyesi oluşturulur
8. Müşteri gönderisi ile YK taşıma belgesi eşleştirilir
9. QueryShipmentAsync ile teslimat durumu sorgulanabilir
```

### İade Kodu Akışı

```
1. SaveReturnShipmentCodeAsync ile iade kodu oluşturulur
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

C# ile takip linki oluşturma:

```csharp
string trackingUrl = $"http://selfservis.yurticikargo.com/reports/SswReportsFromParamFields.aspx" +
    $"?ssfldvn=53&sskurkod={musteriKodu}&refnumber={referansNo}&date={DateTime.Now:dd.MM.yyyy}";
```

---

## IP Yetkilendirme

Yurtiçi Kargo web servislerine erişim için IP yetkilendirmesi zorunludur. Canlı ortama geçmeden önce çıkış IP adresinizi **Bölge Müdürlüğü Satış Temsilcinize** bildirmeniz gerekmektedir.

Test ortamında IP kısıtlaması bulunmamaktadır.

---

## Tam Kullanım Örneği

```csharp
using YurticiKargo;

// Client oluştur
var client = new YurticiKargoClient("YKTEST", "YK", "TR", testMode: true);

// 1. Gönderi oluştur
var shipments = new List<Dictionary<string, string>>
{
    new()
    {
        ["cargoKey"]         = "TEST-" + DateTime.Now.Ticks,
        ["invoiceKey"]       = "INV-001",
        ["receiverCustName"] = "Test Alıcı",
        ["receiverAddress"]  = "Test Mah. Test Sok. No:1",
        ["receiverPhone1"]   = "05001234567",
        ["cityName"]         = "İstanbul",
        ["townName"]         = "Kadıköy"
    }
};

var createResult = await client.CreateShipmentAsync(shipments);
Console.WriteLine($"Gönderi: {(createResult.IsSuccess ? "Başarılı" : "Hata")}");

// 2. Gönderi sorgula
var queryResult = await client.QueryShipmentAsync(
    keys: new[] { shipments[0]["cargoKey"] },
    keyType: 0
);
Console.WriteLine($"Sorgu: {(queryResult.IsSuccess ? "Başarılı" : "Hata")}");

// 3. Gönderi iptal
var cancelResult = await client.CancelShipmentAsync(
    new[] { shipments[0]["cargoKey"] }
);
Console.WriteLine($"İptal: {(cancelResult.IsSuccess ? "Başarılı" : "Hata")}");

// 4. İade kodu oluştur
var returnResult = await client.SaveReturnShipmentCodeAsync(
    returnCode: "RMA-" + DateTime.Now.Ticks,
    startDate: DateTime.Now.ToString("yyyyMMdd"),
    endDate: DateTime.Now.AddDays(30).ToString("yyyyMMdd"),
    maxCount: 1,
    fieldName: "53"
);
Console.WriteLine($"İade Kodu: {(returnResult.IsSuccess ? "Başarılı" : "Hata")}");

// Debug
Console.WriteLine("\n--- Son İstek ---");
Console.WriteLine(client.GetLastRequest());
Console.WriteLine("\n--- Son Yanıt ---");
Console.WriteLine(client.GetLastResponse());
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
- Ör: `"TEST-" + DateTime.Now.Ticks` veya `Guid.NewGuid().ToString("N")[..20]`

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

### 16. .NET: HttpClient SSL hatası
**Sorun:** SSL sertifika doğrulama hatası alınıyor.
**Çözüm:** Test ortamında `HttpClientHandler` ile sertifika doğrulamayı devre dışı bırakın:
```csharp
var handler = new HttpClientHandler
{
    ServerCertificateCustomValidationCallback = (_, _, _, _) => true
};
var httpClient = new HttpClient(handler);
```
> ⚠️ Bu ayarı sadece test ortamında kullanın. Canlı ortamda sertifika doğrulaması aktif olmalıdır.

### 17. .NET: XDocument parse hatası
**Sorun:** Response parse edilirken hata alınıyor.
**Çözüm:** Response'ta BOM (Byte Order Mark) karakteri olabilir:
```csharp
var content = await response.Content.ReadAsStringAsync();
content = content.Trim();  // BOM ve whitespace temizleme
var doc = XDocument.Parse(content);
```

### 18. .NET: Task cancelled / Timeout
**Sorun:** İstek zaman aşımına uğruyor ve `TaskCanceledException` fırlatılıyor.
**Çözüm:** HttpClient timeout değerini artırın:
```csharp
var httpClient = new HttpClient
{
    Timeout = TimeSpan.FromSeconds(60)
};
```

---

## Lisans

MIT
