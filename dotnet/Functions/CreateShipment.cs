using System.Xml.Linq;
using YurticiKargo.Models;

namespace YurticiKargo.Functions;

public static class CreateShipmentFunction
{
    public static string BuildRequestXml(
        string username, string password, string language,
        List<Dictionary<string, string>> shipments)
    {
        var shippingOrdersXml = string.Join("\n", shipments.Select(s =>
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

            var elements = fields
                .Where(f => s.ContainsKey(f) && !string.IsNullOrEmpty(s[f]))
                .Select(f => $"<{f}>{EscapeXml(s[f])}</{f}>");

            return $"<ShippingOrderVO>\n{string.Join("\n", elements)}\n</ShippingOrderVO>";
        }));

        return $@"<?xml version=""1.0"" encoding=""utf-8""?>
<soap:Envelope xmlns:soap=""http://schemas.xmlsoap.org/soap/envelope/""
               xmlns:ship=""http://yurticikargo.com.tr/ShippingOrderDispatcherServices"">
    <soap:Body>
        <ship:createShipment>
            <wsUserName>{EscapeXml(username)}</wsUserName>
            <wsPassword>{EscapeXml(password)}</wsPassword>
            <userLanguage>{EscapeXml(language)}</userLanguage>
            {shippingOrdersXml}
        </ship:createShipment>
    </soap:Body>
</soap:Envelope>";
    }

    public static ShipmentResult ParseResponse(string responseXml)
    {
        var result = new ShipmentResult();

        try
        {
            var doc = XDocument.Parse(responseXml);
            var ns = doc.Root?.GetDefaultNamespace() ?? XNamespace.None;

            // Remove namespaces for easier parsing
            var body = doc.Descendants()
                .FirstOrDefault(e => e.Name.LocalName == "createShipmentResponse");

            if (body == null)
            {
                result.OutFlag = 2;
                result.OutResult = "Unexpected response format";
                return result;
            }

            var shippingOrderResult = body.Descendants()
                .FirstOrDefault(e => e.Name.LocalName == "ShippingOrderResultVO")
                ?? body;

            result.OutFlag = GetIntValue(shippingOrderResult, "outFlag");
            result.OutResult = GetStringValue(shippingOrderResult, "outResult");
            result.JobId = GetLongValue(shippingOrderResult, "jobId");
            result.Count = GetIntValue(shippingOrderResult, "count");

            var details = shippingOrderResult.Descendants()
                .Where(e => e.Name.LocalName == "ShippingOrderDetailVO");

            foreach (var detail in details)
            {
                result.Details.Add(new ShipmentDetail
                {
                    CargoKey = GetStringValue(detail, "cargoKey"),
                    InvoiceKey = GetStringValue(detail, "invoiceKey"),
                    ErrCode = GetIntValue(detail, "errCode"),
                    ErrMessage = GetStringValue(detail, "errMessage")
                });
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
