# Yurtiçi Kargo SOAP API Client

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PHP](https://img.shields.io/badge/PHP-8.0+-777BB4.svg)](https://php.net)
[![.NET](https://img.shields.io/badge/.NET-8.0+-512BD4.svg)](https://dotnet.microsoft.com)
[![Java](https://img.shields.io/badge/Java-11+-ED8B00.svg)](https://java.com)
[![Node.js](https://img.shields.io/badge/Node.js-18+-339933.svg)](https://nodejs.org)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://python.org)
[![Go](https://img.shields.io/badge/Go-1.21+-00ADD8.svg)](https://golang.org)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)](#)
[![SOAP](https://img.shields.io/badge/Protocol-SOAP%2FXML-orange.svg)](#)

Yurtiçi Kargo SOAP Web Service entegrasyonu için **6 programlama dilinde** yazılmış istemci kütüphanesi. Hiçbir harici bağımlılık gerektirmez.

---

## Desteklenen Diller

| Dil | Minimum Versiyon | Klasör | README |
|-----|-----------------|--------|--------|
| PHP | 8.0+ (ext-soap) | [`php/`](./php) | [📖](./php/README.md) |
| C# / .NET | 8.0+ | [`dotnet/`](./dotnet) | [📖](./dotnet/README.md) |
| Java | 11+ | [`java/`](./java) | [📖](./java/README.md) |
| JavaScript | Node.js 18+ (ESM) | [`javascript/`](./javascript) | [📖](./javascript/README.md) |
| Python | 3.10+ | [`python/`](./python) | [📖](./python/README.md) |
| Go | 1.21+ | [`go/`](./go) | [📖](./go/README.md) |

---

## Özellikler

- ✅ **4 API Fonksiyonu:** createShipment, cancelShipment, queryShipment, saveReturnShipmentCode
- ✅ **Sıfır Bağımlılık:** Tüm dillerde sadece standard library
- ✅ **Test Edilmiş:** Gerçek Yurtiçi Kargo test ortamına bağlanarak doğrulanmış
- ✅ **Modüler:** Her fonksiyon ayrı dosyada, tek controller'da birleşik
- ✅ **All-in-One:** Her dilde tek dosyada bağımsız çalışan versiyon
- ✅ **Kapsamlı Dokümantasyon:** Her dil için ayrı README + troubleshooting

---

## Hızlı Başlangıç

### PHP
```php
require_once 'php/YurticiKargoClient.php';
$client = new YurticiKargoClient(username: 'YKTEST', password: 'YK', language: 'TR', testMode: true);
$result = $client->createShipment([['cargoKey' => 'TEST001', 'invoiceKey' => 'INV001', 'receiverCustName' => 'Ali Veli', 'receiverAddress' => 'Atatürk Cad. No:1 Ankara', 'receiverPhone1' => '05551234567']]);
```

### C# / .NET
```csharp
var client = new YurticiKargoClient("YKTEST", "YK", "TR", testMode: true);
var result = await client.CreateShipmentAsync(shipments);
```

### Java
```java
YurticiKargoClient client = new YurticiKargoClient("YKTEST", "YK", "TR", true);
ShipmentResult result = client.createShipment(List.of(shipment));
```

### JavaScript (Node.js)
```javascript
import { YurticiKargoClient } from './YurticiKargoClient.js';
const client = new YurticiKargoClient({ username: 'YKTEST', password: 'YK', language: 'TR', testMode: true });
const result = await client.createShipment([{cargoKey: 'TEST001', invoiceKey: 'INV001', receiverCustName: 'Ali Veli', receiverAddress: 'Atatürk Cad. No:1 Ankara', receiverPhone1: '05551234567'}]);
```

### Python
```python
from yurticikargo_client import YurticiKargoClient
client = YurticiKargoClient('YKTEST', 'YK', 'TR', test_mode=True)
result = client.create_shipment([{'cargo_key': 'TEST001', 'invoice_key': 'INV001', 'receiver_cust_name': 'Ali Veli', 'receiver_address': 'Atatürk Cad. No:1 Ankara', 'receiver_phone1': '05551234567'}])
```

### Go
```go
client := yurticikargo.NewClient("YKTEST", "YK", "TR", true)
result, err := client.CreateShipment([]models.ShipmentOrder{{CargoKey: "TEST001", InvoiceKey: "INV001", ReceiverCustName: "Ali Veli", ReceiverAddress: "Atatürk Cad. No:1 Ankara", ReceiverPhone1: "05551234567"}})
```

---

## API Fonksiyonları

| # | Fonksiyon | Açıklama |
|---|-----------|----------|
| 1 | `createShipment` | Gönderi oluşturma |
| 2 | `cancelShipment` | Gönderi iptal (düzenlenmeden önce) |
| 3 | `queryShipment` | Gönderi durumu sorgulama |
| 4 | `saveReturnShipmentCode` | İade kodu oluşturma |

---

## Test Ortamı

| Parametre | Değer |
|-----------|-------|
| Username | `YKTEST` |
| Password | `YK` |
| Language | `TR` |
| WSDL (Test) | `https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl` |
| Endpoint (Test) | `https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices` |

---

## Proje Yapısı

```
├── php/                    # PHP 8.0+, ext-soap
├── dotnet/                 # .NET 8.0+, HttpClient + XDocument
├── java/                   # Java 11+, HttpClient + javax.xml
├── javascript/             # Node.js 18+, https module, ESM
├── python/                 # Python 3.10+, urllib + xml.etree
├── go/                     # Go 1.21+, net/http + encoding/xml
├── .ai-context.md          # AI asistan skill dosyası
├── AGENTS.md               # Claude/Kiro context
├── .cursorrules            # Cursor context
└── .github/copilot-instructions.md  # GitHub Copilot context
```

Her dil klasörü aynı yapıda:
```
<dil>/
├── functions/              # Her fonksiyon ayrı dosyada
├── tests/                  # Gerçek API'ye bağlanan testler
├── YurticiKargoClient.*    # Controller (tüm fonksiyonları birleştirir)
├── YurticiKargoAllInOne.*  # Tek dosyada bağımsız çalışan versiyon
└── README.md               # Dile özel kapsamlı dokümantasyon
```

---

## Kritik Bilgi: Dil Parametresi

> ⚠️ Bu API'nin en önemli "gotcha"sı — farklı metodlar farklı dil parametresi kullanır:

| Metod | Dil Parametresi |
|-------|----------------|
| `createShipment` | `userLanguage` |
| `cancelShipment` | `userLanguage` |
| `queryShipment` | `wsLanguage` |
| `saveReturnShipmentCode` | `wsLanguage` |

---

## Lisans

[MIT](LICENSE) — Ticari kullanıma açık, minimum kısıtlama.

---

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Commit edin (`git commit -m 'feat: yeni özellik'`)
4. Push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

---

**Yurtiçi Kargo Entegrasyon Desteği:** Canlı ortam için Bölge Müdürlüğü Satış Temsilciniz ile iletişime geçin.
