using System.Xml.Linq;
using YurticiKargo.Models;

namespace YurticiKargo.Functions;

public static class SaveReturnShipmentCodeFunction
{
    public static string BuildRequestXml(
        string username, string password, string language,
        string returnCode, string startDate, string endDate, int maxCount, string fieldName)
    {
        return $@"<?xml version=""1.0"" encoding=""utf-8""?>
<soap:Envelope xmlns:soap=""http://schemas.xmlsoap.org/soap/envelope/""
               xmlns:ship=""http://yurticikargo.com.tr/ShippingOrderDispatcherServices"">
    <soap:Body>
        <ship:saveReturnShipmentCode>
            <wsUserName>{EscapeXml(username)}</wsUserName>
            <wsPassword>{EscapeXml(password)}</wsPassword>
            <wsLanguage>{EscapeXml(language)}</wsLanguage>
            <returnCode>{EscapeXml(returnCode)}</returnCode>
            <startDate>{EscapeXml(startDate)}</startDate>
            <endDate>{EscapeXml(endDate)}</endDate>
            <maxCount>{maxCount}</maxCount>
            <fieldName>{EscapeXml(fieldName)}</fieldName>
        </ship:saveReturnShipmentCode>
    </soap:Body>
</soap:Envelope>";
    }

    public static ReturnCodeResult ParseResponse(string responseXml)
    {
        var result = new ReturnCodeResult();

        try
        {
            var doc = XDocument.Parse(responseXml);

            var body = doc.Descendants()
                .FirstOrDefault(e => e.Name.LocalName == "saveReturnShipmentCodeResponse");

            if (body == null)
            {
                result.OutFlag = 2;
                result.OutResult = "Unexpected response format";
                return result;
            }

            result.OutFlag = GetIntValue(body, "outFlag");
            result.OutResult = GetStringValue(body, "outResult");
            result.ErrCode = GetIntValue(body, "errCode");
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

    private static string EscapeXml(string value) =>
        value.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;")
             .Replace("\"", "&quot;").Replace("'", "&apos;");
}
