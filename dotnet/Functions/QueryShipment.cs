using System.Xml.Linq;
using YurticiKargo.Models;

namespace YurticiKargo.Functions;

public static class QueryShipmentFunction
{
    public static string BuildRequestXml(
        string username, string password, string language,
        List<string> keys, int keyType, bool addHistoricalData = false, bool onlyTracking = false)
    {
        var keysXml = string.Join(",", keys);

        return $@"<?xml version=""1.0"" encoding=""utf-8""?>
<soap:Envelope xmlns:soap=""http://schemas.xmlsoap.org/soap/envelope/""
               xmlns:ship=""http://yurticikargo.com.tr/ShippingOrderDispatcherServices"">
    <soap:Body>
        <ship:queryShipment>
            <wsUserName>{EscapeXml(username)}</wsUserName>
            <wsPassword>{EscapeXml(password)}</wsPassword>
            <wsLanguage>{EscapeXml(language)}</wsLanguage>
            <keys>{EscapeXml(keysXml)}</keys>
            <keyType>{keyType}</keyType>
            <addHistoricalData>{(addHistoricalData ? "true" : "false")}</addHistoricalData>
            <onlyTracking>{(onlyTracking ? "true" : "false")}</onlyTracking>
        </ship:queryShipment>
    </soap:Body>
</soap:Envelope>";
    }

    public static QueryResult ParseResponse(string responseXml)
    {
        var result = new QueryResult();

        try
        {
            var doc = XDocument.Parse(responseXml);

            var body = doc.Descendants()
                .FirstOrDefault(e => e.Name.LocalName == "queryShipmentResponse");

            if (body == null)
            {
                result.OutFlag = 2;
                result.OutResult = "Unexpected response format";
                return result;
            }

            var resultVo = body.Descendants()
                .FirstOrDefault(e => e.Name.LocalName == "ShippingOrderResultVO")
                ?? body;

            result.OutFlag = GetIntValue(resultVo, "outFlag");
            result.OutResult = GetStringValue(resultVo, "outResult");
            result.SenderCustId = GetLongValue(resultVo, "senderCustId");
            result.Count = GetIntValue(resultVo, "count");

            var details = resultVo.Descendants()
                .Where(e => e.Name.LocalName == "ShippingOrderDetailVO");

            foreach (var detail in details)
            {
                var queryDetail = new QueryDetail
                {
                    CargoKey = GetStringValue(detail, "cargoKey"),
                    InvoiceKey = GetStringValue(detail, "invoiceKey"),
                    OperationStatus = GetStringValue(detail, "operationStatus"),
                    OperationCode = GetIntValue(detail, "operationCode"),
                    OperationMessage = GetStringValue(detail, "operationMessage"),
                    ErrCode = GetIntValue(detail, "errCode"),
                    ErrMessage = GetStringValue(detail, "errMessage")
                };

                // Parse item detail
                var itemDetailEl = detail.Descendants()
                    .FirstOrDefault(e => e.Name.LocalName == "itemDetail"
                        || e.Name.LocalName == "ShippingOrderItemDetailVO");

                if (itemDetailEl != null)
                {
                    queryDetail.ItemDetail = new ItemDetail
                    {
                        TrackingUrl = GetStringValue(itemDetailEl, "trackingUrl"),
                        ReceiverCustName = GetStringValue(itemDetailEl, "receiverCustName"),
                        DepartureUnitName = GetStringValue(itemDetailEl, "departureUnitName"),
                        DeliveryDate = GetStringValue(itemDetailEl, "deliveryDate"),
                        DeliveryTime = GetStringValue(itemDetailEl, "deliveryTime")
                    };

                    // Parse cargo history
                    var historyElements = itemDetailEl.Descendants()
                        .Where(e => e.Name.LocalName == "CargoEventVO"
                            || e.Name.LocalName == "cargoEvent");

                    foreach (var histEl in historyElements)
                    {
                        queryDetail.ItemDetail.CargoHistory.Add(new CargoHistoryEvent
                        {
                            UnitName = GetStringValue(histEl, "unitName"),
                            EventName = GetStringValue(histEl, "eventName"),
                            ReasonName = GetStringValue(histEl, "reasonName"),
                            EventDate = GetStringValue(histEl, "eventDate"),
                            EventTime = GetStringValue(histEl, "eventTime"),
                            CityName = GetStringValue(histEl, "cityName"),
                            TownName = GetStringValue(histEl, "townName")
                        });
                    }
                }

                result.Details.Add(queryDetail);
            }
        }
        catch (Exception ex)
        {
            result.OutFlag = 2;
            result.OutResult = $"Parse error: {ex.Message}";
        }

        return result;
    }

    private static string GetStringValue(XElement parent, string localName) =>
        parent.Descendants().FirstOrDefault(e => e.Name.LocalName == localName)?.Value ?? string.Empty;

    private static int GetIntValue(XElement parent, string localName) =>
        int.TryParse(GetStringValue(parent, localName), out var v) ? v : 0;

    private static long GetLongValue(XElement parent, string localName) =>
        long.TryParse(GetStringValue(parent, localName), out var v) ? v : 0;

    private static string EscapeXml(string value) =>
        value.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;")
             .Replace("\"", "&quot;").Replace("'", "&apos;");
}
