package com.yurticikargo.functions;

import com.yurticikargo.models.QueryResult;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.ByteArrayInputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;

/**
 * queryShipment SOAP fonksiyonu.
 * Müşterinin kendi referans kodu ile gönderi geçmişini raporlayan servistir.
 */
public class QueryShipment {

    private static final String SOAP_NS = "http://yurticikargo.com.tr/ShippingOrderDispatcherServices";

    private final String endpoint;
    private final String username;
    private final String password;
    private final String language;
    private final HttpClient httpClient;

    public QueryShipment(String endpoint, String username, String password, String language, HttpClient httpClient) {
        this.endpoint = endpoint;
        this.username = username;
        this.password = password;
        this.language = language;
        this.httpClient = httpClient;
    }

    /**
     * Gönderi sorgulama isteği gönderir.
     *
     * @param keys              Sorgulanacak anahtarlar
     * @param keyType           0=CargoKey, 1=InvoiceKey
     * @param addHistoricalData Hareket geçmişi dahil mi?
     * @param onlyTracking      Sadece takip URL'si mi?
     * @return QueryResult
     */
    public QueryResult execute(String[] keys, int keyType, boolean addHistoricalData, boolean onlyTracking) throws Exception {
        String soapXml = buildRequest(keys, keyType, addHistoricalData, onlyTracking);
        String responseXml = sendRequest(soapXml);
        return parseResponse(responseXml);
    }

    private String buildRequest(String[] keys, int keyType, boolean addHistoricalData, boolean onlyTracking) {
        StringBuilder sb = new StringBuilder();
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        sb.append("<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" ");
        sb.append("xmlns:ship=\"").append(SOAP_NS).append("\">\n");
        sb.append("  <soapenv:Header/>\n");
        sb.append("  <soapenv:Body>\n");
        sb.append("    <ship:queryShipment>\n");
        sb.append("      <wsUserName>").append(escapeXml(username)).append("</wsUserName>\n");
        sb.append("      <wsPassword>").append(escapeXml(password)).append("</wsPassword>\n");
        sb.append("      <wsLanguage>").append(escapeXml(language)).append("</wsLanguage>\n");
        // WSDL: maxOccurs='unbounded' - each key as separate element
        for (String key : keys) {
            sb.append("      <keys>").append(escapeXml(key)).append("</keys>\n");
        }
        sb.append("      <keyType>").append(keyType).append("</keyType>\n");
        sb.append("      <addHistoricalData>").append(addHistoricalData).append("</addHistoricalData>\n");
        sb.append("      <onlyTracking>").append(onlyTracking).append("</onlyTracking>\n");
        sb.append("    </ship:queryShipment>\n");
        sb.append("  </soapenv:Body>\n");
        sb.append("</soapenv:Envelope>");
        return sb.toString();
    }

    private String sendRequest(String soapXml) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(endpoint))
                .header("Content-Type", "text/xml; charset=utf-8")
                .header("SOAPAction", "")
                .POST(HttpRequest.BodyPublishers.ofString(soapXml, StandardCharsets.UTF_8))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
        return response.body();
    }

    public QueryResult parseResponse(String xml) throws Exception {
        QueryResult result = new QueryResult();

        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(false);
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(new ByteArrayInputStream(xml.getBytes(StandardCharsets.UTF_8)));

        // Check for SOAP Fault
        NodeList faultNodes = doc.getElementsByTagName("faultstring");
        if (faultNodes.getLength() > 0) {
            result.setOutFlag(2);
            result.setOutResult(faultNodes.item(0).getTextContent().trim());
            return result;
        }

        result.setOutFlag(getIntValue(doc, "outFlag", 2));
        result.setOutResult(getTextValue(doc, "outResult"));

        // shippingDeliveryDetailVO
        NodeList detailNodes = doc.getElementsByTagName("shippingDeliveryDetailVO");
        for (int i = 0; i < detailNodes.getLength(); i++) {
            Element detailEl = (Element) detailNodes.item(i);
            QueryResult.QueryDetail detail = new QueryResult.QueryDetail();
            detail.setCargoKey(getTextValue(detailEl, "cargoKey"));
            detail.setInvoiceKey(getTextValue(detailEl, "invoiceKey"));
            detail.setOperationCode(getIntValue(detailEl, "operationCode", 0));
            detail.setOperationMessage(getTextValue(detailEl, "operationMessage"));
            detail.setOperationStatus(getTextValue(detailEl, "operationStatus"));
            detail.setErrCode(getIntValue(detailEl, "errCode", 0));
            detail.setErrMessage(getTextValue(detailEl, "errMessage"));

            // shippingDeliveryItemDetailVO
            NodeList itemNodes = detailEl.getElementsByTagName("shippingDeliveryItemDetailVO");
            if (itemNodes.getLength() > 0) {
                Element itemEl = (Element) itemNodes.item(0);
                QueryResult.QueryItemDetail itemDetail = new QueryResult.QueryItemDetail();
                itemDetail.setTrackingUrl(getTextValue(itemEl, "trackingUrl"));
                itemDetail.setReceiverCustName(getTextValue(itemEl, "receiverCustName"));
                itemDetail.setReceiverAddress(getTextValue(itemEl, "receiverAddressTxt"));
                itemDetail.setDepartureUnitName(getTextValue(itemEl, "departureUnitName"));
                itemDetail.setDeliveryDate(getTextValue(itemEl, "deliveryDate"));
                itemDetail.setDeliveryTime(getTextValue(itemEl, "deliveryTime"));

                // invDocCargoVOArray (cargo history)
                NodeList historyNodes = itemEl.getElementsByTagName("invDocCargoVOArray");
                for (int j = 0; j < historyNodes.getLength(); j++) {
                    Element histEl = (Element) historyNodes.item(j);
                    QueryResult.CargoEvent event = new QueryResult.CargoEvent();
                    event.setUnitName(getTextValue(histEl, "unitName"));
                    event.setEventName(getTextValue(histEl, "eventName"));
                    event.setEventDate(getTextValue(histEl, "eventDate"));
                    event.setEventTime(getTextValue(histEl, "eventTime"));
                    event.setReasonName(getTextValue(histEl, "reasonName"));
                    itemDetail.getCargoHistory().add(event);
                }

                detail.setItemDetail(itemDetail);
            }

            result.getDetails().add(detail);
        }

        return result;
    }

    private String getTextValue(Element parent, String tagName) {
        NodeList list = parent.getElementsByTagName(tagName);
        if (list.getLength() > 0 && list.item(0).getTextContent() != null) {
            return list.item(0).getTextContent().trim();
        }
        return "";
    }

    private String getTextValue(Document doc, String tagName) {
        NodeList list = doc.getElementsByTagName(tagName);
        if (list.getLength() > 0 && list.item(0).getTextContent() != null) {
            return list.item(0).getTextContent().trim();
        }
        return "";
    }

    private int getIntValue(Element parent, String tagName, int defaultVal) {
        String val = getTextValue(parent, tagName);
        if (!val.isEmpty()) {
            try { return Integer.parseInt(val); } catch (NumberFormatException e) { /* ignore */ }
        }
        return defaultVal;
    }

    private int getIntValue(Document doc, String tagName, int defaultVal) {
        String val = getTextValue(doc, tagName);
        if (!val.isEmpty()) {
            try { return Integer.parseInt(val); } catch (NumberFormatException e) { /* ignore */ }
        }
        return defaultVal;
    }

    private String escapeXml(String value) {
        if (value == null) return "";
        return value.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\"", "&quot;")
                    .replace("'", "&apos;");
    }

    /**
     * Debug: SOAP XML isteğini döndürür.
     */
    public String getRequestXml(String[] keys, int keyType, boolean addHistoricalData, boolean onlyTracking) {
        return buildRequest(keys, keyType, addHistoricalData, onlyTracking);
    }
}
