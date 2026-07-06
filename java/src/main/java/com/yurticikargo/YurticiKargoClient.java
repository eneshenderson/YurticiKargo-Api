package com.yurticikargo;

import com.yurticikargo.functions.CancelShipment;
import com.yurticikargo.functions.CreateShipment;
import com.yurticikargo.functions.QueryShipment;
import com.yurticikargo.functions.SaveReturnShipmentCode;
import com.yurticikargo.models.CancelResult;
import com.yurticikargo.models.QueryResult;
import com.yurticikargo.models.ReturnCodeResult;
import com.yurticikargo.models.ShipmentResult;

import java.net.http.HttpClient;
import java.time.Duration;
import java.util.List;
import java.util.Map;

/**
 * Yurtiçi Kargo SOAP Web Service Java Client.
 * 
 * Java 11+ HttpClient kullanarak raw SOAP XML gönderir.
 * Harici bağımlılık gerektirmez.
 * 
 * Kullanım:
 * <pre>
 * YurticiKargoClient client = new YurticiKargoClient("YKTEST", "YK", "TR", true);
 * ShipmentResult result = client.createShipment(List.of(Map.of(
 *     "cargoKey", "001",
 *     "invoiceKey", "INV001",
 *     "receiverCustName", "Ali Veli",
 *     "receiverAddress", "Adres",
 *     "receiverPhone1", "05551234567"
 * )));
 * </pre>
 */
public class YurticiKargoClient {

    private static final String WSDL_TEST = "https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices";
    private static final String WSDL_LIVE = "https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices";

    private final String username;
    private final String password;
    private final String language;
    private final boolean testMode;
    private final String endpoint;
    private final HttpClient httpClient;

    private final CreateShipment createShipmentFn;
    private final CancelShipment cancelShipmentFn;
    private final QueryShipment queryShipmentFn;
    private final SaveReturnShipmentCode saveReturnShipmentCodeFn;

    /**
     * Yurtiçi Kargo API Client oluşturur.
     *
     * @param username YK kullanıcı adı
     * @param password YK şifre
     * @param language Dil (TR/EN)
     * @param testMode true=test ortamı, false=canlı ortam
     */
    public YurticiKargoClient(String username, String password, String language, boolean testMode) {
        this.username = username;
        this.password = password;
        this.language = language;
        this.testMode = testMode;
        this.endpoint = testMode ? WSDL_TEST : WSDL_LIVE;

        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(30))
                .build();

        this.createShipmentFn = new CreateShipment(endpoint, username, password, language, httpClient);
        this.cancelShipmentFn = new CancelShipment(endpoint, username, password, language, httpClient);
        this.queryShipmentFn = new QueryShipment(endpoint, username, password, language, httpClient);
        this.saveReturnShipmentCodeFn = new SaveReturnShipmentCode(endpoint, username, password, language, httpClient);
    }

    /**
     * Gönderi oluşturma.
     * 
     * @param shipments Gönderi bilgileri listesi.
     *                  Her eleman zorunlu olarak cargoKey, invoiceKey, receiverCustName, receiverAddress, receiverPhone1 içermelidir.
     * @return ShipmentResult
     */
    public ShipmentResult createShipment(List<Map<String, String>> shipments) throws Exception {
        return createShipmentFn.execute(shipments);
    }

    /**
     * Gönderi iptal.
     * Gönderi düzenlendikten sonra iptal yapılamaz.
     *
     * @param cargoKeys İptal edilecek kargo anahtarları
     * @return CancelResult
     */
    public CancelResult cancelShipment(String[] cargoKeys) throws Exception {
        return cancelShipmentFn.execute(cargoKeys);
    }

    /**
     * Gönderi sorgulama.
     *
     * @param keys              Sorgulanacak anahtarlar
     * @param keyType           0=CargoKey, 1=InvoiceKey
     * @param addHistoricalData Hareket geçmişi dahil mi?
     * @param onlyTracking      Sadece takip URL'si mi?
     * @return QueryResult
     */
    public QueryResult queryShipment(String[] keys, int keyType, boolean addHistoricalData, boolean onlyTracking) throws Exception {
        return queryShipmentFn.execute(keys, keyType, addHistoricalData, onlyTracking);
    }

    /**
     * İade kodu oluşturma.
     *
     * @param returnCode İade kodu
     * @param startDate  Başlangıç tarihi (YYYYMMDD)
     * @param endDate    Bitiş tarihi (YYYYMMDD)
     * @param maxCount   Kullanım adedi
     * @param fieldName  Özel alan (test: "53", canlı: "16")
     * @return ReturnCodeResult
     */
    public ReturnCodeResult saveReturnShipmentCode(String returnCode, String startDate, String endDate, int maxCount, String fieldName) throws Exception {
        return saveReturnShipmentCodeFn.execute(returnCode, startDate, endDate, maxCount, fieldName);
    }

    // --- Getter methods ---

    public String getUsername() { return username; }
    public String getLanguage() { return language; }
    public boolean isTestMode() { return testMode; }
    public String getEndpoint() { return endpoint; }

    // --- Debug methods ---

    /**
     * createShipment SOAP XML isteğini döndürür (debug).
     */
    public String getCreateShipmentRequestXml(List<Map<String, String>> shipments) {
        return createShipmentFn.getRequestXml(shipments);
    }

    /**
     * cancelShipment SOAP XML isteğini döndürür (debug).
     */
    public String getCancelShipmentRequestXml(String[] cargoKeys) {
        return cancelShipmentFn.getRequestXml(cargoKeys);
    }

    /**
     * queryShipment SOAP XML isteğini döndürür (debug).
     */
    public String getQueryShipmentRequestXml(String[] keys, int keyType, boolean addHistoricalData, boolean onlyTracking) {
        return queryShipmentFn.getRequestXml(keys, keyType, addHistoricalData, onlyTracking);
    }

    /**
     * saveReturnShipmentCode SOAP XML isteğini döndürür (debug).
     */
    public String getSaveReturnShipmentCodeRequestXml(String returnCode, String startDate, String endDate, int maxCount, String fieldName) {
        return saveReturnShipmentCodeFn.getRequestXml(returnCode, startDate, endDate, maxCount, fieldName);
    }
}
