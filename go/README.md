# Yurtiçi Kargo Go API Client

Yurtiçi Kargo SOAP Web Service entegrasyonu için Go istemci kütüphanesi. Harici bağımlılık kullanmadan, sadece Go standart kütüphanesi ile SOAP/XML iletişimi sağlar.

---

## Gereksinimler

- **Go 1.21+**
- Sadece standard library kullanılır:
  - `net/http` — HTTP istemcisi
  - `encoding/xml` — SOAP XML marshal/unmarshal
  - `crypto/tls` — TLS yapılandırması
- **Harici bağımlılık yok** (`go.sum` dosyası boştur)

---

## Proje Yapısı

```
go/
├── go.mod                          # Module: github.com/yurticikargo/api-client
├── client.go                       # YurticiKargoClient struct ve temel SOAP iletişimi
├── functions/
│   ├── create_shipment.go          # Gönderi oluşturma
│   ├── cancel_shipment.go          # Gönderi iptal
│   ├── query_shipment.go           # Gönderi sorgulama
│   └── save_return_shipment_code.go # İade kodu oluşturma
├── models/
│   ├── shipment_result.go          # ShipmentResult, ShipmentDetail structs
│   ├── cancel_result.go            # CancelResult, CancelDetail structs
│   ├── query_result.go             # QueryResult, QueryDetail, ItemDetail structs
│   └── return_code_result.go       # ReturnCodeResult struct
├── tests/
│   ├── create_shipment_test.go     # Gönderi oluşturma testleri
│   ├── cancel_shipment_test.go     # Gönderi iptal testleri
│   ├── query_shipment_test.go      # Gönderi sorgulama testleri
│   └── save_return_shipment_code_test.go # İade kodu testleri
├── cmd/main.go                     # Demo runner (modüler kullanım örneği)
└── all_in_one/main.go              # Tek dosyada tüm fonksiyonlar
```

---

## Kurulum

```bash
go get github.com/yurticikargo/api-client
```

### Manuel Kullanım

Projeyi klonlayın ve doğrudan kullanın:

```bash
git clone https://github.com/yurticikargo/api-client.git
cd api-client/go
go mod tidy
```

---

## Çalıştırma

```bash
# AllInOne — Tek dosyada tüm örnekler
go run all_in_one/main.go

# Demo — Modüler yapı ile çalıştırma
go run cmd/main.go

# Testler
go test ./tests/ -v

# Belirli bir test
go test ./tests/ -v -run TestCreateShipment

# Tüm testler (coverage ile)
go test ./tests/ -v -cover
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

> ⚠️ Test ortamında TLS sertifika doğrulaması `InsecureSkipVerify: true` olarak ayarlanmıştır.

---

## Hızlı Başlangıç

```go
package main

import (
    "fmt"
    "log"

    yurticikargo "github.com/yurticikargo/api-client"
    "github.com/yurticikargo/api-client/models"
)

func main() {
    // Test ortamı
    client := yurticikargo.NewClient("YKTEST", "YK", "TR", true)

    // Canlı ortam
    // client := yurticikargo.NewClient("KULLANICI_ADINIZ", "SIFRENIZ", "TR", false)

    // Gönderi oluştur
    result, err := client.CreateShipment([]models.ShipmentOrder{
        {
            CargoKey:         "TEST001",
            InvoiceKey:       "INV001",
            ReceiverCustName: "Mehmet Yılmaz",
            ReceiverAddress:  "Eski Büyükdere Cad. No:3",
            ReceiverPhone1:   "05321234567",
            CityName:         "İstanbul",
            TownName:         "Maslak",
        },
    })
    if err != nil {
        log.Fatal(err)
    }

    if result.IsSuccess() {
        fmt.Printf("Başarılı! Job ID: %d\n", result.JobId)
    } else {
        fmt.Printf("Hata: %s\n", result.OutResult)
    }
}
```

---

## Client Yapılandırması

```go
// YurticiKargoClient struct
type YurticiKargoClient struct {
    Username string
    Password string
    Language string
    TestMode bool
    BaseURL  string
}

// Constructor
func NewClient(username, password, language string, testMode bool) *YurticiKargoClient
```

| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| `username` | string | ✅ | YK web servis kullanıcı adı |
| `password` | string | ✅ | YK web servis şifresi |
| `language` | string | ✅ | Dil kodu (`TR`, `EN`) |
| `testMode` | bool | ✅ | `true`=Test ortamı, `false`=Canlı ortam |

**SOAP Endpoint Seçimi:**
- `testMode=true` → `https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices`
- `testMode=false` → `https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices`

**TLS Yapılandırması:**
```go
// Test ortamında sertifika doğrulama devre dışı
tlsConfig := &tls.Config{
    InsecureSkipVerify: true, // Sadece test ortamı için
}
```

---

## API Metodları

Her metod Go idiomatic `(result, error)` tuple döner.

---

### 1. CreateShipment — Gönderi Oluşturma

Müşterinin kargo bilgilerini Yurtiçi Kargo sistemine ileten servistir.

**SOAP Action:** `ship:createShipment` (parametre: `userLanguage`)

```go
func (c *YurticiKargoClient) CreateShipment(orders []models.ShipmentOrder) (*models.ShipmentResult, error)
```

#### Kullanım

```go
result, err := client.CreateShipment([]models.ShipmentOrder{
    {
        CargoKey:         "0000113",
        InvoiceKey:       "AB00113",
        ReceiverCustName: "Mehmet Yılmaz",
        ReceiverAddress:  "Eski Büyükdere Cad. No:3",
        ReceiverPhone1:   "02123652426",
        CityName:         "İstanbul",
        TownName:         "Maslak",
    },
})
if err != nil {
    log.Fatal(err)
}

if result.IsSuccess() {
    fmt.Printf("Başarılı! Job ID: %d\n", result.JobId)
    for _, detail := range result.Details {
        fmt.Printf("Cargo Key: %s - Durum: %s\n", detail.CargoKey, detail.ErrMessage)
    }
} else {
    fmt.Printf("Hata: %s\n", result.OutResult)
    for _, detail := range result.GetErrors() {
        fmt.Printf("  [%d] %s\n", detail.ErrCode, detail.ErrMessage)
    }
}
```

#### Tahsilatlı Teslimat (Kapıda Ödeme)

```go
// Nakit tahsilat
result, err := client.CreateShipment([]models.ShipmentOrder{
    {
        CargoKey:           "COD001",
        InvoiceKey:         "CODINV001",
        ReceiverCustName:   "Ali Veli",
        ReceiverAddress:    "Test Adresi",
        ReceiverPhone1:     "05551234567",
        TtCollectionType:   "0",       // 0=Nakit
        TtInvoiceAmount:    "150.50",
        TtDocumentId:       "TT00666",
        TtDocumentSaveType: "0",       // 0=Aynı fatura
    },
})

// Kredi kartlı tahsilat
result, err := client.CreateShipment([]models.ShipmentOrder{
    {
        CargoKey:           "CC001",
        InvoiceKey:         "CCINV001",
        ReceiverCustName:   "Ali Veli",
        ReceiverAddress:    "Test Adresi",
        ReceiverPhone1:     "05551234567",
        TtCollectionType:   "1",       // 1=Kredi Kartı
        TtInvoiceAmount:    "250.00",
        TtDocumentId:       "TT00667",
        TtDocumentSaveType: "0",
        DcSelectedCredit:   "3",       // 3 taksit
        DcCreditRule:       "1",       // 1=Tek çekim izin
    },
})
```

#### Çoklu Paket (Kargo Bazlı Çalışma)

Aynı alıcıya birden fazla paket gönderildiğinde, her paket için farklı `CargoKey`, aynı `InvoiceKey` kullanılır:

```go
result, err := client.CreateShipment([]models.ShipmentOrder{
    {
        CargoKey:         "10012",
        InvoiceKey:       "A123456",  // Hepsi aynı fatura
        ReceiverCustName: "Ali Veli",
        ReceiverAddress:  "Adres bilgisi",
        ReceiverPhone1:   "05551234567",
        WaybillNo:        "A123456",
        CargoCount:       1,
    },
    {
        CargoKey:         "10013",
        InvoiceKey:       "A123456",
        ReceiverCustName: "Ali Veli",
        ReceiverAddress:  "Adres bilgisi",
        ReceiverPhone1:   "05551234567",
        WaybillNo:        "A123456",
        CargoCount:       1,
    },
    {
        CargoKey:         "10014",
        InvoiceKey:       "A123456",
        ReceiverCustName: "Ali Veli",
        ReceiverAddress:  "Adres bilgisi",
        ReceiverPhone1:   "05551234567",
        WaybillNo:        "A123456",
        CargoCount:       1,
    },
})
```

#### ShipmentOrder Struct

```go
type ShipmentOrder struct {
    CargoKey           string  // Benzersiz kargo anahtarı (zorunlu, max 20)
    InvoiceKey         string  // Fatura anahtarı (zorunlu, max 20)
    ReceiverCustName   string  // Alıcı müşteri adı (zorunlu, max 100)
    ReceiverAddress    string  // Alıcı adresi (zorunlu, max 500)
    ReceiverPhone1     string  // Alıcı telefon (zorunlu, max 20)
    ReceiverPhone2     string  // Alıcı telefon 2 (opsiyonel)
    ReceiverPhone3     string  // Alıcı telefon 3 (opsiyonel)
    CityName           string  // Şehir (opsiyonel, max 40)
    TownName           string  // İlçe (opsiyonel, max 40)
    CustProdId         string  // Ürün kodu (opsiyonel)
    Desi               float64 // Kargo desi bilgisi (opsiyonel)
    Kg                 float64 // Kargo kg bilgisi (opsiyonel)
    CargoCount         int     // Kargo adedi (opsiyonel)
    WaybillNo          string  // İrsaliye numarası (opsiyonel, max 20)
    SpecialField1      string  // Özel alan 1 (opsiyonel, max 200)
    SpecialField2      string  // Özel alan 2 (opsiyonel, max 100)
    SpecialField3      string  // Özel alan 3 (opsiyonel, max 100)
    TtCollectionType   string  // Tahsilat ödeme tipi: "0"=Nakit, "1"=Kredi Kartı
    TtInvoiceAmount    string  // Tahsilat tutarı (ayraç "." nokta)
    TtDocumentId       string  // Tahsilat belge numarası (max 12)
    TtDocumentSaveType string  // Fatura tipi: "0"=Aynı, "1"=Ayrı
    OrgReceiverCustId  string  // Alıcı müşteri kodu (opsiyonel, max 50)
    Description        string  // Açıklama (opsiyonel, max 255)
    TaxNumber          string  // Vergi numarası (opsiyonel, max 15)
    TaxOfficeId        int     // Vergi dairesi ID (opsiyonel)
    TaxOfficeName      string  // Vergi dairesi adı (opsiyonel, max 60)
    OrgGeoCode         string  // Müşteri adres kodu (opsiyonel, max 20)
    PrivilegeOrder     string  // Ayrıcalıklı gönderim merkezi (opsiyonel)
    DcSelectedCredit   string  // Taksit sayısı (kredi kartlı tahsilat için)
    DcCreditRule       string  // Kredi kuralı: "0"=Sadece anlaşmalı, "1"=Tek çekim izin
    EmailAddress       string  // Alıcı e-posta (opsiyonel, max 200)
}
```

#### Gönderi Parametreleri Detay Tablosu

| Parametre | Tip | Zorunlu | Açıklama | Örnek |
|-----------|-----|---------|----------|-------|
| `CargoKey` | string(20) | ✅ | Benzersiz kargo anahtarı. YK şubesi bu bilgiyi gönderi üzerinde barkod/metin olarak görmelidir. | `0000113` |
| `InvoiceKey` | string(20) | ✅ | Fatura anahtarı. Kargo bazlı çalışmada her paket için farklı CargoKey, aynı InvoiceKey kullanılır. | `AB00113` |
| `ReceiverCustName` | string(100) | ✅ | Alıcı müşteri adı | `Mehmet Yılmaz` |
| `ReceiverAddress` | string(500) | ✅ | Alıcı müşteri adresi | `Eski Büyükdere Cad. No:3` |
| `ReceiverPhone1` | string(20) | ✅ | Alıcı telefon numarası | `02123652426` |
| `ReceiverPhone2` | string(20) | ❌ | Alıcı telefon 2 | |
| `ReceiverPhone3` | string(20) | ❌ | Alıcı telefon 3 | |
| `CityName` | string(40) | ❌ | Alıcı adres şehir | `İstanbul` |
| `TownName` | string(40) | ❌ | Alıcı adres ilçe | `Maslak` |
| `CustProdId` | string | ❌ | Ürün kodu (desi/kg bilgisi ürün bazlı ise) | `1` |
| `Desi` | float64 | ❌ | Kargo desi bilgisi | `3.5` |
| `Kg` | float64 | ❌ | Kargo kg bilgisi | `7.6` |
| `CargoCount` | int | ❌ | Gönderilen kargo adedi | `2` |
| `WaybillNo` | string(20) | ❌ | Müşteri irsaliye numarası (ticari gönderilerde zorunlu) | `AA110125T` |
| `SpecialField1` | string(200) | ❌ | Özel alan 1 (format: `numara$deger#`) | `1$426031#2$397427#` |
| `SpecialField2` | string(100) | ❌ | Özel alan 2 | |
| `SpecialField3` | string(100) | ❌ | Özel alan 3 | |
| `TtCollectionType` | string(1) | ❌ | Tahsilatlı teslimat ödeme tipi: `0`=Nakit, `1`=Kredi Kartı | `0` |
| `TtInvoiceAmount` | string | ❌ | Tahsilat tutarı (ayraç `.` nokta olmalı) | `20.5` |
| `TtDocumentId` | string(12) | ❌ | Tahsilat belge (fatura) numarası | `TT00666` |
| `TtDocumentSaveType` | string(1) | ❌ | Hizmet bedeli fatura tipi: `0`=Aynı fatura, `1`=Ayrı fatura | `0` |
| `OrgReceiverCustId` | string(50) | ❌ | Alıcı müşteri kodu (ör. temsilci no) | `59874736` |
| `Description` | string(255) | ❌ | Serbest açıklama | `Kargo` |
| `TaxNumber` | string(15) | ❌ | Vergi numarası | `123123123` |
| `TaxOfficeId` | int | ❌ | Vergi dairesi ID | `340055` |
| `TaxOfficeName` | string(60) | ❌ | Vergi dairesi adı | `Şişli` |
| `OrgGeoCode` | string(20) | ❌ | Müşteri adres kodu | `36656` |
| `PrivilegeOrder` | string(10) | ❌ | Ayrıcalıklı gönderim merkezi tanımı | `1` |
| `DcSelectedCredit` | string | ❌ | Taksit sayısı seçimi (kredi kartlı tahsilat için) | `2` |
| `DcCreditRule` | string | ❌ | Kredi kuralı: `0`=Sadece anlaşmalı banka, `1`=Tek çekim izin | `1` |
| `EmailAddress` | string(200) | ❌ | Alıcı e-posta adresi | `alici@mail.com` |

#### Tahsilatlı Teslimat Kuralları

**Nakit tahsilat** (`TtCollectionType = "0"`) için zorunlu alanlar:
- `TtInvoiceAmount`
- `TtDocumentId`
- `TtDocumentSaveType`

**Kredi kartlı tahsilat** (`TtCollectionType = "1"`) için ek zorunlu alanlar:
- `DcSelectedCredit`
- `DcCreditRule`

#### ShipmentResult Struct

```go
type ShipmentResult struct {
    OutFlag   int              // 0=Başarılı, 1=Hata, 2=Beklenmeyen hata
    OutResult string           // Sonuç mesajı
    JobId     int              // YK talep numarası (başarılı ise)
    Count     int              // İşlem yapılan gönderi sayısı
    Details   []ShipmentDetail // Her gönderi için detay
}

type ShipmentDetail struct {
    CargoKey   string // Kargo anahtarı
    InvoiceKey string // Fatura anahtarı
    ErrCode    int    // Hata kodu (0=başarılı)
    ErrMessage string // Hata mesajı
}

func (r *ShipmentResult) IsSuccess() bool    // OutFlag == 0
func (r *ShipmentResult) GetErrors() []ShipmentDetail // ErrCode != 0 olanlar
```

---

### 2. CancelShipment — Gönderi İptal

Web servis ile sisteme gönderilmiş bilgilerin iptal edilmesini ve kargonun çıkışının engellenmesini sağlar.

**SOAP Action:** `ship:cancelShipment` (parametre: `userLanguage`)

> ⚠️ Gönderi düzenlendikten sonra iptal yapılamaz.

```go
func (c *YurticiKargoClient) CancelShipment(cargoKeys []string) (*models.CancelResult, error)
```

#### Kullanım

```go
result, err := client.CancelShipment([]string{"0000113", "0000114"})
if err != nil {
    log.Fatal(err)
}

if result.IsSuccess() {
    for _, detail := range result.Details {
        fmt.Printf("%s: %s (%s)\n", detail.CargoKey, detail.OperationMessage, detail.OperationStatus)
    }
} else {
    fmt.Printf("Hata: %s\n", result.OutResult)
}
```

#### CancelResult Struct

```go
type CancelResult struct {
    OutFlag      int            // 0=Başarılı, 1=Hata, 2=Beklenmeyen hata
    OutResult    string         // Sonuç mesajı
    SenderCustId int            // Gönderici müşteri kodu
    Count        int            // İşlem yapılan gönderi sayısı
    Details      []CancelDetail // Her gönderi için detay
}

type CancelDetail struct {
    CargoKey         string // Kargo anahtarı
    InvoiceKey       string // Fatura anahtarı
    JobId            int    // YK talep numarası
    DocId            string // YK gönderi kodu
    OperationCode    int    // İşlem kodu
    OperationMessage string // İşlem mesajı
    OperationStatus  string // İşlem durumu
    ErrCode          int    // Hata kodu
    ErrMessage       string // Hata mesajı
}

func (r *CancelResult) IsSuccess() bool
```

#### İptal Durum Kodları

| OperationStatus | OperationCode | Açıklama |
|-----------------|---------------|----------|
| `NOP` | 0 | İşlem yapılmadı, düzenlenmemiş |
| `IND` | 1 | Kargo teslimattadır |
| `ISR` | 2 | Düzenlenmiş, fatura prosedürü tamamlanmamış |
| `CNL` | 3 | Kargo çıkışı engellendi (başarılı iptal) |
| `ISC` | 4 | Kargo zaten iptal edilmiş |

---

### 3. QueryShipment — Gönderi Sorgulama

Müşterinin kendi referans kodu ile gönderi geçmişini raporlayan servistir. Tek seferde birden fazla gönderi sorgulanabilir.

**SOAP Action:** `ship:queryShipment` (parametre: `wsLanguage`)

```go
func (c *YurticiKargoClient) QueryShipment(keys []string, keyType int, addHistoricalData bool, onlyTracking bool) (*models.QueryResult, error)
```

#### Parametreler

| Parametre | Tip | Zorunlu | Açıklama |
|-----------|-----|---------|----------|
| `keys` | []string | ✅ | Sorgulanacak anahtar değerleri dizisi |
| `keyType` | int | ✅ | `0`=Cargo Key, `1`=Invoice Key |
| `addHistoricalData` | bool | ❌ | Hareket geçmişi dahil edilsin mi? (Performans için `false` önerilir) |
| `onlyTracking` | bool | ❌ | Sadece takip URL'si dönsün mü? |

#### Kullanım

```go
// Cargo Key ile sorgulama
result, err := client.QueryShipment(
    []string{"12520", "12521"},
    0,     // keyType: 0 = Cargo Key
    true,  // addHistoricalData
    false, // onlyTracking
)
if err != nil {
    log.Fatal(err)
}

// Invoice Key ile sorgulama
result, err := client.QueryShipment(
    []string{"A123456"},
    1,     // keyType: 1 = Invoice Key
    false,
    false,
)

if result.IsSuccess() {
    for _, detail := range result.Details {
        if detail.IsSuccess() {
            fmt.Printf("Kargo: %s\n", detail.CargoKey)
            fmt.Printf("Durum: %s (%s)\n", detail.OperationMessage, detail.OperationStatus)

            if detail.ItemDetail != nil {
                item := detail.ItemDetail
                fmt.Printf("Takip: %s\n", item.TrackingUrl)
                fmt.Printf("Alıcı: %s\n", item.ReceiverCustName)
                fmt.Printf("Çıkış: %s\n", item.DepartureUnitName)
                fmt.Printf("Teslim: %s %s\n", item.DeliveryDate, item.DeliveryTime)

                // Hareket geçmişi
                for _, event := range item.CargoHistory {
                    fmt.Printf("  → %s %s | %s | %s | %s\n",
                        event.EventDate, event.EventTime,
                        event.UnitName, event.EventName, event.ReasonName)
                }
            }
        } else {
            fmt.Printf("Hata [%d]: %s\n", detail.ErrCode, detail.ErrMessage)
        }
    }
}
```

#### QueryResult Struct

```go
type QueryResult struct {
    OutFlag   int           // 0=Başarılı, 1=Hata, 2=Beklenmeyen hata
    OutResult string        // Sonuç mesajı
    Count     int           // İşlem yapılan gönderi sayısı
    Details   []QueryDetail // Her gönderi için detay
}

type QueryDetail struct {
    CargoKey         string      // Kargo anahtarı
    InvoiceKey       string      // Fatura anahtarı
    OperationCode    int         // İşlem kodu
    OperationMessage string      // İşlem mesajı
    OperationStatus  string      // İşlem durumu
    ErrCode          int         // Hata kodu
    ErrMessage       string      // Hata mesajı
    ItemDetail       *ItemDetail // Gönderi detayı (nil olabilir)
}

type ItemDetail struct {
    TrackingUrl        string         // Takip URL'si
    ReceiverCustName   string         // Alıcı adı
    ReceiverAddress    string         // Alıcı adresi
    DepartureUnitName  string         // Çıkış şubesi
    ArrivalUnitName    string         // Varış şubesi
    DeliveryDate       string         // Teslim tarihi
    DeliveryTime       string         // Teslim saati
    ReceiverName       string         // Teslim alan kişi
    Desi               float64        // Desi
    Kg                 float64        // Kg
    CargoCount         int            // Parça sayısı
    RejectStatus       int            // İade durumu
    CargoHistory       []CargoEvent   // Hareket geçmişi
}

type CargoEvent struct {
    EventDate  string // Olay tarihi
    EventTime  string // Olay saati
    UnitName   string // Birim adı
    EventName  string // Olay adı
    ReasonName string // Sebep
}

func (r *QueryResult) IsSuccess() bool
func (d *QueryDetail) IsSuccess() bool // ErrCode == 0
```

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

---

### 4. SaveReturnShipmentCode — İade Kodu Oluşturma

İade müşterilerinin YK birimine ileterek iade işlemini tamamlayacakları kodu oluşturan servistir.

**SOAP Action:** `ship:saveReturnShipmentCode` (parametre: `wsLanguage`)

```go
func (c *YurticiKargoClient) SaveReturnShipmentCode(returnCode, startDate, endDate string, maxCount int, fieldName string) (*models.ReturnCodeResult, error)
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

#### Kullanım

```go
result, err := client.SaveReturnShipmentCode(
    "RMA-2024-001", // returnCode
    "20240101",     // startDate (YYYYMMDD)
    "20240131",     // endDate (YYYYMMDD)
    1,              // maxCount
    "53",           // fieldName (test ortamı)
)
if err != nil {
    log.Fatal(err)
}

if result.IsSuccess() {
    fmt.Println("İade kodu başarıyla oluşturuldu!")
} else {
    fmt.Printf("Hata [%d]: %s\n", result.ErrCode, result.OutResult)
}
```

#### ReturnCodeResult Struct

```go
type ReturnCodeResult struct {
    OutFlag   int    // 0=Başarılı, 1=Hata, 2=Beklenmeyen hata
    OutResult string // Sonuç mesajı
    ErrCode   int    // Hata kodu
}

func (r *ReturnCodeResult) IsSuccess() bool // OutFlag == 0
```

---

## Özel Alan Bilgileri (SpecialField1)

`SpecialField1` alanına birden fazla özel alan bilgisi gönderilebilir.

**Format:** `alan_no$deger#alan_no$deger#`

**Örnek:** `1$426031#2$397427#`

```go
order := models.ShipmentOrder{
    // ...
    SpecialField1: "1$426031#2$397427#",
}
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

## SOAP İletişim Detayları

### SOAP Envelope Yapısı

```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:ship="http://yurticikargo.com.tr/ShippingOrderDispatcherServices">
    <soap:Body>
        <ship:createShipment>
            <userLanguage>TR</userLanguage>
            <!-- parametreler -->
        </ship:createShipment>
    </soap:Body>
</soap:Envelope>
```

### SOAP Action Mapping

| Go Metodu | SOAP Action | Dil Parametresi |
|-----------|-------------|-----------------|
| `CreateShipment()` | `ship:createShipment` | `userLanguage` |
| `CancelShipment()` | `ship:cancelShipment` | `userLanguage` |
| `QueryShipment()` | `ship:queryShipment` | `wsLanguage` |
| `SaveReturnShipmentCode()` | `ship:saveReturnShipmentCode` | `wsLanguage` |

### HTTP Headers

```
Content-Type: text/xml; charset=utf-8
SOAPAction: ""
```

---

## Entegrasyon Akışı

### Giden Kargo Akışı

```
1. CreateShipment ile gönderi bilgileri YK sistemine iletilir
2. Kargo anahtarı (CargoKey) fiziksel olarak kargo üzerinde bulunmalıdır
3. Gönderi düzenlenmeden önce CancelShipment ile iptal edilebilir
4. YK şubesi kargo anahtarını okuyarak sisteme girer
5. Alıcı bilgileri ekranda görünür
6. YK şubesi sevkiyat adresini belirler
7. Kargo adedi ve taşıma adresi girilerek YK irsaliyesi oluşturulur
8. Müşteri gönderisi ile YK taşıma belgesi eşleştirilir
9. QueryShipment ile teslimat durumu sorgulanabilir
```

### İade Kodu Akışı

```
1. SaveReturnShipmentCode ile iade kodu oluşturulur
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
| `ssfldvn` | Özel alan adı (yukarıdaki Özel Alan Numaraları tablosundaki değerler) |
| `sskurkod` | YK müşteri kodu |
| `refnumber` | Takip edilecek özel alan değeri |
| `date` | Gönderi tarihi (dd.mm.yyyy, ±5 gün tolerans) |

### Go ile Takip Linki Oluşturma

```go
func BuildTrackingURL(fieldName, customerCode, refNumber, date string) string {
    return fmt.Sprintf(
        "http://selfservis.yurticikargo.com/reports/SswReportsFromParamFields.aspx?ssfldvn=%s&sskurkod=%s&refnumber=%s&date=%s",
        fieldName, customerCode, refNumber, date,
    )
}

// Kullanım
url := BuildTrackingURL("53", "123456", "REF001", "06.07.2026")
```

---

## Debug

```go
// Son SOAP isteğini görüntüle
fmt.Println(client.GetLastRequest())

// Son SOAP yanıtını görüntüle
fmt.Println(client.GetLastResponse())
```

---

## Error Handling (Go Idiomatic)

```go
// Network/SOAP hatası
result, err := client.CreateShipment(orders)
if err != nil {
    // HTTP bağlantı hatası, XML parse hatası vb.
    log.Fatalf("İstek hatası: %v", err)
}

// İş mantığı hatası
if !result.IsSuccess() {
    // outFlag != 0 — YK tarafından dönen hata
    log.Printf("YK Hatası: %s (flag: %d)", result.OutResult, result.OutFlag)
    for _, detail := range result.GetErrors() {
        log.Printf("  [%d] %s", detail.ErrCode, detail.ErrMessage)
    }
}

// Kısmi başarı (bazı gönderiler başarılı, bazıları hatalı)
if result.IsSuccess() {
    for _, detail := range result.Details {
        if detail.ErrCode != 0 {
            log.Printf("Kısmi hata - %s: [%d] %s",
                detail.CargoKey, detail.ErrCode, detail.ErrMessage)
        }
    }
}
```

---

## IP Yetkilendirme

Yurtiçi Kargo web servislerine erişim için IP yetkilendirmesi zorunludur. Canlı ortama geçmeden önce çıkış IP adresinizi **Bölge Müdürlüğü Satış Temsilcinize** bildirmeniz gerekmektedir.

> ⚠️ Test ortamında IP kısıtlaması yoktur. Canlı ortam için IP yetkilendirmesi mutlaka yapılmalıdır.

---

## Çalışma Modları

### Fatura Bazlı (İrsaliye Bazlı)

Her gönderi için bir kayıt iletilir. Her `CargoKey` için bir gönderi düzenlenir.

### Kargo Bazlı (Çoklu Paket)

Aynı alıcıya birden fazla paket gönderildiğinde, her paket için farklı `CargoKey`, aynı `InvoiceKey` kullanılır.

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
- Ör: `fmt.Sprintf("TEST-%d", time.Now().UnixNano())` veya `uuid.New().String()[:20]`

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

### 16. Go: x509: certificate signed by unknown authority
**Sorun:** SSL sertifika doğrulama hatası alınıyor.
**Çözüm:** Test ortamında TLS config'de sertifika doğrulamayı devre dışı bırakın:
```go
import (
    "crypto/tls"
    "net/http"
)

tr := &http.Transport{
    TLSClientConfig: &tls.Config{
        InsecureSkipVerify: true,
    },
}
httpClient := &http.Client{Transport: tr}
```
> ⚠️ Bu ayarı sadece test ortamında kullanın. Canlı ortamda sertifika doğrulaması aktif olmalıdır.

### 17. Go: dial tcp: lookup testws.yurticikargo.com: no such host
**Sorun:** DNS çözümleme hatası — host adı bulunamıyor.
**Çözüm:**
- İnternet bağlantınızı kontrol edin
- DNS sunucunuzu doğrulayın (`nslookup testws.yurticikargo.com`)
- Gerekirse `/etc/hosts` dosyasına (Linux/Mac) veya `C:\Windows\System32\drivers\etc\hosts` dosyasına (Windows) IP ekleyin
- Kurumsal ağda DNS ayarlarını kontrol edin

### 18. Go: context deadline exceeded
**Sorun:** İstek zaman aşımına uğruyor.
**Çözüm:** HTTP client timeout değerini artırın:
```go
httpClient := &http.Client{
    Timeout: 60 * time.Second,
}
```
Veya context ile daha granüler kontrol:
```go
ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
defer cancel()

req, _ := http.NewRequestWithContext(ctx, "POST", url, body)
```

---

## Lisans

MIT
