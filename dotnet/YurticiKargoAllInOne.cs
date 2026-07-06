// YurticiKargoAllInOne.cs
// Yurtiçi Kargo .NET API Client - Tek dosyada tüm fonksiyonlar
// .NET 6+ | Raw SOAP XML over HttpClient
// Kullanım: dotnet-script YurticiKargoAllInOne.cs veya proje içine dahil edin

using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;

namespace YurticiKargo.AllInOne
{
    #region Models

    public class ShipmentDetail
    {
        public string CargoKey { get; set; } = string.Empty;
        public string InvoiceKey { get; set; } = string.Empty;
        public int ErrCode { get; set; }
        public string ErrMessage { get; set; } = string.Empty;
    }

    public class ShipmentResult
    {
        public int OutFlag { get; set; }
        public string OutResult { get; set; } = string.Empty;
        public long JobId { get; set; }
        public int Count { get; set; }
        public List<ShipmentDetail> Details { get; set; } = new();

        public bool IsSuccess() => OutFlag == 0;
        public List<ShipmentDetail> GetErrors() => Details.Where(d => d.ErrCode != 0).ToList();
    }

    public class CancelDetail
    {
        public string CargoKey { get; set; } = string.Empty;
        public string InvoiceKey { get; set; } = string.Empty;
        public long JobId { get; set; }
        public string DocId { get; set; } = string.Empty;
        public int OperationCode { get; set; }
        public string OperationMessage { get; set; } = string.Empty;
        public string OperationStatus { get; set; } = string.Empty;
        public int ErrCode { get; set; }
        public string ErrMessage { get; set; } = string.Empty;
    }

    public class CancelResult
    {
        public int OutFlag { get; set; }
        public string OutResult { get; set; } = string.Empty;
        public long SenderCustId { get; set; }
        public int Count { get; set; }
        public List<CancelDetail> Details { get; set; } = new();

        public bool IsSuccess() => OutFlag == 0;
    }

    public class CargoHistoryEvent
    {
        public string UnitName { get; set; } = string.Empty;
        public string EventName { get; set; } = string.Empty;
        public string ReasonName { get; set; } = string.Empty;
        public string EventDate { get; set; } = string.Empty;
        public string EventTime { get; set; } = string.Empty;
        public string CityName { get; set; } = string.Empty;
        public string TownName { get; set; } = string.Empty;
    }

    public class ItemDetail
    {
        public string TrackingUrl { get; set; } = string.Empty;
        public string ReceiverCustName { get; set; } = string.Empty;
        public string DepartureUnitName { get; set; } = string.Empty;
        public string DeliveryDate { get; set; } = string.Empty;
        public string DeliveryTime { get; set; } = string.Empty;
        public List<CargoHistoryEvent> CargoHistory { get; set; } = new();
    }

    public class QueryDetail
    {
        public string CargoKey { get; set; } = string.Empty;
        public string InvoiceKey { get; set; } = string.Empty;
        public string OperationStatus { get; set; } = string.Empty;
        public int OperationCode { get; set; }
        public string OperationMessage { get; set; } = string.Empty;
        public int ErrCode { get; set; }
        public string ErrMessage { get; set; } = string.Empty;
        public ItemDetail? ItemDetail { get; set; }

        public bool IsSuccess() => ErrCode == 0;
    }

    public class QueryResult
    {
        public int OutFlag { get; set; }
        public string OutResult { get; set; } = string.Empty;
        public long SenderCustId { get; set; }
        public int Count { get; set; }
        public List<QueryDetail> Details { get; set; } = new();

        public bool IsSuccess() => OutFlag == 0;
    }

    public class ReturnCodeResult
    {
        public int OutFlag { get; set; }
        public string OutResult { get; set; } = string.Empty;
        public int ErrCode { get; set; }

        public bool IsSuccess() => OutFlag == 0;
    }

    #endregion

    #region Client

    public class YurticiKargoClient : IDisposable
    {
        private readonly string _username;
        private readonly string _password;
        private readonly string _language;
        private readonly string _endpointUrl;
        private readonly HttpClient _httpClient;

        private string _lastRequest = string.Empty;
        private string _lastResponse = string.Empty;

        private const string TestEndpoint = "https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices";
        private const string LiveEndpoint = "https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices";
        private const string SoapNamespace = "http://yurticikargo.com.tr/ShippingOrderDispatcherServices";

        public YurticiKargoClient(
            string username,
            string password,
            string language = "TR",
            bool testMode = true,
            HttpClient? httpClient = null)
        {
            _username = username;
            _password = password;
            _language = language;
            _endpointUrl = testMode ? TestEndpoint : LiveEndpoint;
            _httpClient = httpClient ?? new HttpClient();
        }

        #region Public API Methods

        public async Task<ShipmentResult> CreateShipmentAsync(List<Dictionary<string, string>> shipments)
        {
            var xml = BuildCreateShipmentXml(shipments);
            var responseXml = await SendSoapRequestAsync(xml, "createShipment");
            return ParseCreateShipmentResponse(responseXml);
        }

        public async Task<CancelResult> CancelShipmentAsync(List<string> cargoKeys)
        {
            var xml = BuildCancelShipmentXml(cargoKeys);
            var responseXml = await SendSoapRequestAsync(xml, "cancelShipment");
            return ParseCancelShipmentResponse(responseXml);
        }

        public async Task<QueryResult> QueryShipmentAsync(
            List<string> keys,
            int keyType = 0,
            bool addHistoricalData = false,
            bool onlyTracking = false)
        {
            var xml = BuildQueryShipmentXml(keys, keyType, addHistoricalData, onlyTracking);
            var responseXml = await SendSoapRequestAsync(xml, "queryShipment");
            return ParseQueryShipmentResponse(responseXml);
        }

        public async Task<ReturnCodeResult> SaveReturnShipmentCodeAsync(
            string returnCode,
            string startDate,
            string endDate,
            int maxCount,
            string fieldName)
        {
            var xml = BuildSaveReturnShipmentCodeXml(returnCode, startDate, endDate, maxCount, fieldName);
            var responseXml = await SendSoapRequestAsync(xml, "saveReturnShipmentCode");
            return ParseSaveReturnShipmentCodeResponse(responseXml);
        }

        #endregion

        #region Debug

        public string GetLastRequest() => _lastRequest;
        public string GetLastResponse() => _lastResponse;

        #endregion

        #region SOAP XML Builders

        private string BuildCreateShipmentXml(List<Dictionary<string, string>> shipments)
        {
            var fields = new[]
            {
                "cargoKey", "invoiceKey", "receiverCustName", "receiverAddress",
                "receiverPhone1", "receiverPhone2", "receiverPhone3",
                "cityName", "townName", "custProdId", "desi", "kg",
                "cargoCount", "waybillNo", "specialField1", "specialField2", "specialField3",
                "ttCollectionType", "ttInvoiceAmount", "ttDocumentId", "ttDocumentSaveType",
                "orgReceiverCustId", "description", "taxNumber", "taxOfficeId", "taxOfficeName",
                "orgGeoCode", "privilegeOrder", "dcSelectedCredit", "dcCreditRule", "emailAddress"
            };

            var shippingOrdersXml = string.Join("\n", shipments.Select(s =>
            {
                var elements = fields
                    .Where(f => s.ContainsKey(f) && !string.IsNullOrEmpty(s[f]))
                    .Select(f => $"<{f}>{Esc(s[f])}</{f}>");
                return $"<ShippingOrderVO>\n{string.Join("\n", elements)}\n</ShippingOrderVO>";
            }));

            return $@"<?xml version=""1.0"" encoding=""utf-8""?>
<soap:Envelope xmlns:soap=""http://schemas.xmlsoap.org/soap/envelope/""
               xmlns:ship=""{SoapNamespace}"">
    <soap:Body>
        <ship:createShipment>
            <wsUserName>{Esc(_username)}</wsUserName>
            <wsPassword>{Esc(_password)}</wsPassword>
            <wsLanguage>{Esc(_language)}</wsLanguage>
            <ShippingOrderList>
                {shippingOrdersXml}
            </ShippingOrderList>
        </ship:createShipment>
    </soap:Body>
</soap:Envelope>";
        }

        private string BuildCancelShipmentXml(List<string> cargoKeys)
        {
            return $@"<?xml version=""1.0"" encoding=""utf-8""?>
<soap:Envelope xmlns:soap=""http://schemas.xmlsoap.org/soap/envelope/""
               xmlns:ship=""{SoapNamespace}"">
    <soap:Body>
        <ship:cancelShipment>
            <wsUserName>{Esc(_username)}</wsUserName>
            <wsPassword>{Esc(_password)}</wsPassword>
            <wsLanguage>{Esc(_language)}</wsLanguage>
            <cargoKeys>{Esc(string.Join(";", cargoKeys))}</cargoKeys>
        </ship:cancelShipment>
    </soap:Body>
</soap:Envelope>";
        }

        private string BuildQueryShipmentXml(
            List<string> keys, int keyType, bool addHistoricalData, bool onlyTracking)
        {
            return $@"<?xml version=""1.0"" encoding=""utf-8""?>
<soap:Envelope xmlns:soap=""http://schemas.xmlsoap.org/soap/envelope/""
               xmlns:ship=""{SoapNamespace}"">
    <soap:Body>
        <ship:queryShipment>
            <wsUserName>{Esc(_username)}</wsUserName>
            <wsPassword>{Esc(_password)}</wsPassword>
            <wsLanguage>{Esc(_language)}</wsLanguage>
            <keys>{Esc(string.Join(",", keys))}</keys>
            <keyType>{keyType}</keyType>
            <addHistoricalData>{(addHistoricalData ? "true" : "false")}</addHistoricalData>
            <onlyTracking>{(onlyTracking ? "true" : "false")}</onlyTracking>
        </ship:queryShipment>
    </soap:Body>
</soap:Envelope>";
        }

        private string BuildSaveReturnShipmentCodeXml(
            string returnCode, string startDate, string endDate, int maxCount, string fieldName)
        {
            return $@"<?xml version=""1.0"" encoding=""utf-8""?>
<soap:Envelope xmlns:soap=""http://schemas.xmlsoap.org/soap/envelope/""
               xmlns:ship=""{SoapNamespace}"">
    <soap:Body>
        <ship:saveReturnShipmentCode>
            <wsUserName>{Esc(_username)}</wsUserName>
            <wsPassword>{Esc(_password)}</wsPassword>
            <wsLanguage>{Esc(_language)}</wsLanguage>
            <returnCode>{Esc(returnCode)}</returnCode>
            <startDate>{Esc(startDate)}</startDate>
            <endDate>{Esc(endDate)}</endDate>
            <maxCount>{maxCount}</maxCount>
            <fieldName>{Esc(fieldName)}</fieldName>
        </ship:saveReturnShipmentCode>
    </soap:Body>
</soap:Envelope>";
        }

        #endregion

        #region SOAP Response Parsers

        private ShipmentResult ParseCreateShipmentResponse(string responseXml)
        {
            var result = new ShipmentResult();
            try
            {
                var doc = XDocument.Parse(responseXml);
                var body = doc.Descendants().FirstOrDefault(e => e.Name.LocalName == "createShipmentResponse");
                if (body == null) { result.OutFlag = 2; result.OutResult = "Unexpected response format"; return result; }

                var vo = body.Descendants().FirstOrDefault(e => e.Name.LocalName == "ShippingOrderResultVO") ?? body;
                result.OutFlag = IntVal(vo, "outFlag");
                result.OutResult = StrVal(vo, "outResult");
                result.JobId = LongVal(vo, "jobId");
                result.Count = IntVal(vo, "count");

                foreach (var d in vo.Descendants().Where(e => e.Name.LocalName == "ShippingOrderDetailVO"))
                {
                    result.Details.Add(new ShipmentDetail
                    {
                        CargoKey = StrVal(d, "cargoKey"),
                        InvoiceKey = StrVal(d, "invoiceKey"),
                        ErrCode = IntVal(d, "errCode"),
                        ErrMessage = StrVal(d, "errMessage")
                    });
                }
            }
            catch (Exception ex) { result.OutFlag = 2; result.OutResult = $"Parse error: {ex.Message}"; }
            return result;
        }

        private CancelResult ParseCancelShipmentResponse(string responseXml)
        {
            var result = new CancelResult();
            try
            {
                var doc = XDocument.Parse(responseXml);
                var body = doc.Descendants().FirstOrDefault(e => e.Name.LocalName == "cancelShipmentResponse");
                if (body == null) { result.OutFlag = 2; result.OutResult = "Unexpected response format"; return result; }

                var vo = body.Descendants().FirstOrDefault(e => e.Name.LocalName == "ShippingOrderResultVO") ?? body;
                result.OutFlag = IntVal(vo, "outFlag");
                result.OutResult = StrVal(vo, "outResult");
                result.SenderCustId = LongVal(vo, "senderCustId");
                result.Count = IntVal(vo, "count");

                foreach (var d in vo.Descendants().Where(e => e.Name.LocalName == "ShippingOrderDetailVO"))
                {
                    result.Details.Add(new CancelDetail
                    {
                        CargoKey = StrVal(d, "cargoKey"),
                        InvoiceKey = StrVal(d, "invoiceKey"),
                        JobId = LongVal(d, "jobId"),
                        DocId = StrVal(d, "docId"),
                        OperationCode = IntVal(d, "operationCode"),
                        OperationMessage = StrVal(d, "operationMessage"),
                        OperationStatus = StrVal(d, "operationStatus"),
                        ErrCode = IntVal(d, "errCode"),
                        ErrMessage = StrVal(d, "errMessage")
                    });
                }
            }
            catch (Exception ex) { result.OutFlag = 2; result.OutResult = $"Parse error: {ex.Message}"; }
            return result;
        }

        private QueryResult ParseQueryShipmentResponse(string responseXml)
        {
            var result = new QueryResult();
            try
            {
                var doc = XDocument.Parse(responseXml);
                var body = doc.Descendants().FirstOrDefault(e => e.Name.LocalName == "queryShipmentResponse");
                if (body == null) { result.OutFlag = 2; result.OutResult = "Unexpected response format"; return result; }

                var vo = body.Descendants().FirstOrDefault(e => e.Name.LocalName == "ShippingOrderResultVO") ?? body;
                result.OutFlag = IntVal(vo, "outFlag");
                result.OutResult = StrVal(vo, "outResult");
                result.SenderCustId = LongVal(vo, "senderCustId");
                result.Count = IntVal(vo, "count");

                foreach (var d in vo.Descendants().Where(e => e.Name.LocalName == "ShippingOrderDetailVO"))
                {
                    var queryDetail = new QueryDetail
                    {
                        CargoKey = StrVal(d, "cargoKey"),
                        InvoiceKey = StrVal(d, "invoiceKey"),
                        OperationStatus = StrVal(d, "operationStatus"),
                        OperationCode = IntVal(d, "operationCode"),
                        OperationMessage = StrVal(d, "operationMessage"),
                        ErrCode = IntVal(d, "errCode"),
                        ErrMessage = StrVal(d, "errMessage")
                    };

                    var itemEl = d.Descendants()
                        .FirstOrDefault(e => e.Name.LocalName == "itemDetail" || e.Name.LocalName == "ShippingOrderItemDetailVO");

                    if (itemEl != null)
                    {
                        queryDetail.ItemDetail = new ItemDetail
                        {
                            TrackingUrl = StrVal(itemEl, "trackingUrl"),
                            ReceiverCustName = StrVal(itemEl, "receiverCustName"),
                            DepartureUnitName = StrVal(itemEl, "departureUnitName"),
                            DeliveryDate = StrVal(itemEl, "deliveryDate"),
                            DeliveryTime = StrVal(itemEl, "deliveryTime")
                        };

                        foreach (var h in itemEl.Descendants()
                            .Where(e => e.Name.LocalName == "CargoEventVO" || e.Name.LocalName == "cargoEvent"))
                        {
                            queryDetail.ItemDetail.CargoHistory.Add(new CargoHistoryEvent
                            {
                                UnitName = StrVal(h, "unitName"),
                                EventName = StrVal(h, "eventName"),
                                ReasonName = StrVal(h, "reasonName"),
                                EventDate = StrVal(h, "eventDate"),
                                EventTime = StrVal(h, "eventTime"),
                                CityName = StrVal(h, "cityName"),
                                TownName = StrVal(h, "townName")
                            });
                        }
                    }
                    result.Details.Add(queryDetail);
                }
            }
            catch (Exception ex) { result.OutFlag = 2; result.OutResult = $"Parse error: {ex.Message}"; }
            return result;
        }

        private ReturnCodeResult ParseSaveReturnShipmentCodeResponse(string responseXml)
        {
            var result = new ReturnCodeResult();
            try
            {
                var doc = XDocument.Parse(responseXml);
                var body = doc.Descendants().FirstOrDefault(e => e.Name.LocalName == "saveReturnShipmentCodeResponse");
                if (body == null) { result.OutFlag = 2; result.OutResult = "Unexpected response format"; return result; }

                result.OutFlag = IntVal(body, "outFlag");
                result.OutResult = StrVal(body, "outResult");
                result.ErrCode = IntVal(body, "errCode");
            }
            catch (Exception ex) { result.OutFlag = 2; result.OutResult = $"Parse error: {ex.Message}"; }
            return result;
        }

        #endregion

        #region HTTP Transport

        private async Task<string> SendSoapRequestAsync(string soapXml, string soapAction)
        {
            _lastRequest = soapXml;

            var content = new StringContent(soapXml, Encoding.UTF8, "text/xml");
            content.Headers.ContentType = new MediaTypeHeaderValue("text/xml") { CharSet = "utf-8" };

            var request = new HttpRequestMessage(HttpMethod.Post, _endpointUrl)
            {
                Content = content
            };
            request.Headers.Add("SOAPAction", $"\"{SoapNamespace}/{soapAction}\"");

            var response = await _httpClient.SendAsync(request);
            _lastResponse = await response.Content.ReadAsStringAsync();

            return _lastResponse;
        }

        #endregion

        #region Helpers

        private static string StrVal(XElement parent, string localName) =>
            parent.Descendants().FirstOrDefault(e => e.Name.LocalName == localName)?.Value ?? string.Empty;

        private static int IntVal(XElement parent, string localName) =>
            int.TryParse(StrVal(parent, localName), out var v) ? v : 0;

        private static long LongVal(XElement parent, string localName) =>
            long.TryParse(StrVal(parent, localName), out var v) ? v : 0;

        private static string Esc(string value) =>
            value.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;")
                 .Replace("\"", "&quot;").Replace("'", "&apos;");

        #endregion

        public void Dispose()
        {
            _httpClient.Dispose();
            GC.SuppressFinalize(this);
        }
    }

    #endregion

    #region Demo / Test

    public static class Demo
    {
        /// <summary>
        /// Tek başına çalıştırmak için: Program.cs'deki kodu bu metoda yönlendirin
        /// veya bu dosyayı ayrı bir projede Main olarak kullanın.
        /// </summary>
        public static async Task RunDemoAsync(string[] args)
        {
            Console.WriteLine("╔══════════════════════════════════════════════════╗");
            Console.WriteLine("║  Yurtiçi Kargo .NET API Client - All In One     ║");
            Console.WriteLine("╚══════════════════════════════════════════════════╝\n");

            using var client = new YurticiKargoClient(
                username: "YKTEST",
                password: "YK",
                language: "TR",
                testMode: true
            );

            // --- 1. CreateShipment Test ---
            Console.WriteLine("--- 1. CreateShipment ---");
            var shipments = new List<Dictionary<string, string>>
            {
                new Dictionary<string, string>
                {
                    ["cargoKey"] = "TEST" + DateTime.Now.Ticks.ToString()[^8..],
                    ["invoiceKey"] = "INV" + DateTime.Now.Ticks.ToString()[^8..],
                    ["receiverCustName"] = "Mehmet Yılmaz",
                    ["receiverAddress"] = "Eski Büyükdere Cad. No:3 Maslak İstanbul",
                    ["receiverPhone1"] = "02123652426",
                    ["cityName"] = "İstanbul",
                    ["townName"] = "Maslak"
                }
            };

            var createResult = await client.CreateShipmentAsync(shipments);
            Console.WriteLine($"  OutFlag: {createResult.OutFlag}, Success: {createResult.IsSuccess()}");
            Console.WriteLine($"  OutResult: {createResult.OutResult}");
            Console.WriteLine($"  JobId: {createResult.JobId}, Count: {createResult.Count}");
            foreach (var d in createResult.Details)
                Console.WriteLine($"  Detail: {d.CargoKey} -> [{d.ErrCode}] {d.ErrMessage}");
            Console.WriteLine();

            // --- 2. CancelShipment Test ---
            Console.WriteLine("--- 2. CancelShipment ---");
            var cancelResult = await client.CancelShipmentAsync(new List<string> { "0000113" });
            Console.WriteLine($"  OutFlag: {cancelResult.OutFlag}, Success: {cancelResult.IsSuccess()}");
            Console.WriteLine($"  OutResult: {cancelResult.OutResult}");
            foreach (var d in cancelResult.Details)
                Console.WriteLine($"  Detail: {d.CargoKey} -> {d.OperationStatus} ({d.OperationMessage})");
            Console.WriteLine();

            // --- 3. QueryShipment Test ---
            Console.WriteLine("--- 3. QueryShipment ---");
            var queryResult = await client.QueryShipmentAsync(
                keys: new List<string> { "12520" },
                keyType: 0,
                addHistoricalData: true
            );
            Console.WriteLine($"  OutFlag: {queryResult.OutFlag}, Success: {queryResult.IsSuccess()}");
            Console.WriteLine($"  OutResult: {queryResult.OutResult}");
            foreach (var d in queryResult.Details)
            {
                Console.WriteLine($"  Detail: {d.CargoKey} -> {d.OperationStatus}");
                if (d.ItemDetail != null)
                {
                    Console.WriteLine($"    Tracking: {d.ItemDetail.TrackingUrl}");
                    Console.WriteLine($"    Receiver: {d.ItemDetail.ReceiverCustName}");
                    foreach (var h in d.ItemDetail.CargoHistory)
                        Console.WriteLine($"    → {h.EventDate} {h.EventTime} | {h.UnitName} | {h.EventName}");
                }
            }
            Console.WriteLine();

            // --- 4. SaveReturnShipmentCode Test ---
            Console.WriteLine("--- 4. SaveReturnShipmentCode ---");
            var returnResult = await client.SaveReturnShipmentCodeAsync(
                returnCode: "RMA-" + DateTime.Now.Ticks.ToString()[^6..],
                startDate: DateTime.Now.ToString("yyyyMMdd"),
                endDate: DateTime.Now.AddDays(30).ToString("yyyyMMdd"),
                maxCount: 1,
                fieldName: "53"
            );
            Console.WriteLine($"  OutFlag: {returnResult.OutFlag}, Success: {returnResult.IsSuccess()}");
            Console.WriteLine($"  OutResult: {returnResult.OutResult}");
            Console.WriteLine($"  ErrCode: {returnResult.ErrCode}");
            Console.WriteLine();

            // Debug: Last request/response
            Console.WriteLine("--- Debug: Last SOAP Request (truncated) ---");
            var req = client.GetLastRequest();
            Console.WriteLine(req[..Math.Min(300, req.Length)] + "...\n");

            Console.WriteLine("Done.");
        }
    }

    #endregion
}
