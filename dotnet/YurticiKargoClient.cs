using System.Net.Http.Headers;
using System.Text;
using YurticiKargo.Functions;
using YurticiKargo.Models;

namespace YurticiKargo;

/// <summary>
/// Yurtiçi Kargo SOAP API Client - Raw SOAP XML over HttpClient
/// </summary>
public class YurticiKargoClient : IDisposable
{
    private readonly string _username;
    private readonly string _password;
    private readonly string _language;
    private readonly string _wsdlUrl;
    private readonly HttpClient _httpClient;

    private string _lastRequest = string.Empty;
    private string _lastResponse = string.Empty;

    private const string TestWsdl = "https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl";
    private const string LiveWsdl = "https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices?wsdl";

    /// <summary>
    /// YurticiKargoClient constructor
    /// </summary>
    /// <param name="username">API kullanıcı adı (Test: YKTEST)</param>
    /// <param name="password">API şifre (Test: YK)</param>
    /// <param name="language">Dil kodu (TR)</param>
    /// <param name="testMode">true=test ortamı, false=canlı ortam</param>
    /// <param name="httpClient">Opsiyonel özel HttpClient instance</param>
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
        _wsdlUrl = testMode ? TestWsdl : LiveWsdl;
        _httpClient = httpClient ?? new HttpClient();
    }

    /// <summary>
    /// Gönderi oluşturma
    /// </summary>
    public async Task<ShipmentResult> CreateShipmentAsync(List<Dictionary<string, string>> shipments)
    {
        var xml = CreateShipmentFunction.BuildRequestXml(_username, _password, _language, shipments);
        var responseXml = await SendSoapRequestAsync(xml, "createShipment");
        return CreateShipmentFunction.ParseResponse(responseXml);
    }

    /// <summary>
    /// Gönderi iptal
    /// </summary>
    public async Task<CancelResult> CancelShipmentAsync(List<string> cargoKeys)
    {
        var xml = CancelShipmentFunction.BuildRequestXml(_username, _password, _language, cargoKeys);
        var responseXml = await SendSoapRequestAsync(xml, "cancelShipment");
        return CancelShipmentFunction.ParseResponse(responseXml);
    }

    /// <summary>
    /// Gönderi sorgulama
    /// </summary>
    public async Task<QueryResult> QueryShipmentAsync(
        List<string> keys,
        int keyType = 0,
        bool addHistoricalData = false,
        bool onlyTracking = false)
    {
        var xml = QueryShipmentFunction.BuildRequestXml(
            _username, _password, _language, keys, keyType, addHistoricalData, onlyTracking);
        var responseXml = await SendSoapRequestAsync(xml, "queryShipment");
        return QueryShipmentFunction.ParseResponse(responseXml);
    }

    /// <summary>
    /// İade kodu oluşturma
    /// </summary>
    public async Task<ReturnCodeResult> SaveReturnShipmentCodeAsync(
        string returnCode,
        string startDate,
        string endDate,
        int maxCount,
        string fieldName)
    {
        var xml = SaveReturnShipmentCodeFunction.BuildRequestXml(
            _username, _password, _language, returnCode, startDate, endDate, maxCount, fieldName);
        var responseXml = await SendSoapRequestAsync(xml, "saveReturnShipmentCode");
        return SaveReturnShipmentCodeFunction.ParseResponse(responseXml);
    }

    /// <summary>
    /// Son gönderilen SOAP XML isteği
    /// </summary>
    public string GetLastRequest() => _lastRequest;

    /// <summary>
    /// Son alınan SOAP XML yanıtı
    /// </summary>
    public string GetLastResponse() => _lastResponse;

    private async Task<string> SendSoapRequestAsync(string soapXml, string soapAction)
    {
        _lastRequest = soapXml;

        // The endpoint URL (remove ?wsdl suffix for actual requests)
        var endpointUrl = _wsdlUrl.Replace("?wsdl", "");

        var content = new StringContent(soapXml, Encoding.UTF8, "text/xml");
        content.Headers.ContentType = new MediaTypeHeaderValue("text/xml") { CharSet = "utf-8" };

        var request = new HttpRequestMessage(HttpMethod.Post, endpointUrl)
        {
            Content = content
        };
        request.Headers.Add("SOAPAction", $"\"http://yurticikargo.com.tr/ShippingOrderDispatcherServices/{soapAction}\"");

        var response = await _httpClient.SendAsync(request);
        _lastResponse = await response.Content.ReadAsStringAsync();

        return _lastResponse;
    }

    public void Dispose()
    {
        _httpClient.Dispose();
        GC.SuppressFinalize(this);
    }
}
