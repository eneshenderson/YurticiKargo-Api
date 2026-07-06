using System.Xml.Linq;
using YurticiKargo.Models;

namespace YurticiKargo.Functions;

public static class CancelShipmentFunction
{
    public static string BuildRequestXml(
        string username, string password, string language,
        List<string> cargoKeys)
    {
        var keysXml = string.Join(";", cargoKeys);

        return $@"<?xml version=""1.0"" encoding=""utf-8""?>
<soap:Envelope xmlns:soap=""http://schemas.xmlsoap.org/soap/envelope/""
               xmlns:ship=""http://yurticikargo.com.tr/ShippingOrderDispatcherServices"">
    <soap:Body>
        <ship:cancelShipment>
            <wsUserName>{EscapeXml(username)}</wsUserName>
            <wsPassword>{EscapeXml(password)}</wsPassword>
            <userLanguage>{EscapeXml(language)}</userLanguage>
            <cargoKeys>{EscapeXml(keysXml)}</cargoKeys>
        </ship:cancelShipment>
    </soap:Body>
</soap:Envelope>";
    }

    public static CancelResult ParseResponse(string responseXml)
    {
        var result = new CancelResult();

        try
        {
            var doc = XDocument.Parse(responseXml);

            var body = doc.Descendants()
                .FirstOrDefault(e => e.Name.LocalName == "cancelShipmentResponse");

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
                result.Details.Add(new CancelDetail
                {
                    CargoKey = GetStringValue(detail, "cargoKey"),
                    InvoiceKey = GetStringValue(detail, "invoiceKey"),
                    JobId = GetLongValue(detail, "jobId"),
                    DocId = GetStringValue(detail, "docId"),
                    OperationCode = GetIntValue(detail, "operationCode"),
                    OperationMessage = GetStringValue(detail, "operationMessage"),
                    OperationStatus = GetStringValue(detail, "operationStatus"),
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
