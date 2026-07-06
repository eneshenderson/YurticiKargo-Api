package com.yurticikargo.functions;

import com.yurticikargo.models.CancelResult;
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
 * cancelShipment SOAP fonksiyonu.
 * Sisteme gönderilmiş bilgilerin iptal edilmesini sağlar.
 * Gönderi düzenlendikten sonra iptal yapılamaz.
 */
public class CancelShipment {

    private static final String SOAP_NS = "http://yurticikargo.com.tr/ShippingOrderDispatcherServices";

    private final String endpoint;
    private final String username;
    private final String password;
    private final String language;
    private final HttpClient httpClient;

    public CancelShipment(String endpoint, String username, String password, String language, HttpClient httpClient) {
        this.endpoint = endpoint;
        this.username = username;
        this.password = password;
        this.language = language;
        this.httpClient = httpClient;
    }

    /**
     * Gönderi iptal isteği gönderir.
     *
     * @param cargoKeys İptal edilecek kargo anahtarları
     * @return CancelResult
     */
    public CancelResult execute(String[] cargoKeys) throws Exception {
        String soapXml = buildRequest(cargoKeys);
        String responseXml = sendRequest(soapXml);
        return parseResponse(responseXml);
    }

    private String buildRequest(String[] cargoKeys) {
        StringBuilder sb = new StringBuilder();
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        sb.append("<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" ");
        sb.append("xmlns:ship=\"").append(SOAP_NS).append("\">\n");
        sb.append("  <soapenv:Header/>\n");
        sb.append("  <soapenv:Body>\n");
        sb.append("    <ship:cancelShipment>\n");
        sb.append("      <wsUserName>").append(escapeXml(username)).append("</wsUserName>\n");
        sb.append("      <wsPassword>").append(escapeXml(password)).append("</wsPassword>\n");
        sb.append("      <userLanguage>").append(escapeXml(language)).append("</userLanguage>\n");
        // WSDL: maxOccurs='unbounded' - each cargoKey as separate element
        for (String key : cargoKeys) {
            sb.append("      <cargoKeys>").append(escapeXml(key)).append("</cargoKeys>\n");
        }
        sb.append("    </ship:cancelShipment>\n");
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

    public CancelResult parseResponse(String xml) throws Exception {
        CancelResult result = new CancelResult();

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
        result.setSenderCustId(getTextValue(doc, "senderCustId"));
        result.setCount(getIntValue(doc, "count", 0));

        // shippingCancelDetailVO
        NodeList detailNodes = doc.getElementsByTagName("shippingCancelDetailVO");
        for (int i = 0; i < detailNodes.getLength(); i++) {
            Element detailEl = (Element) detailNodes.item(i);
            CancelResult.CancelDetail detail = new CancelResult.CancelDetail();
            detail.setCargoKey(getTextValue(detailEl, "cargoKey"));
            detail.setInvoiceKey(getTextValue(detailEl, "invoiceKey"));
            detail.setJobId(getLongValue(detailEl, "jobId", 0));
            detail.setDocId(getTextValue(detailEl, "docId"));
            detail.setOperationCode(getIntValue(detailEl, "operationCode", 0));
            detail.setOperationMessage(getTextValue(detailEl, "operationMessage"));
            detail.setOperationStatus(getTextValue(detailEl, "operationStatus"));
            detail.setErrCode(getIntValue(detailEl, "errCode", 0));
            detail.setErrMessage(getTextValue(detailEl, "errMessage"));
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

    private long getLongValue(Element parent, String tagName, long defaultVal) {
        String val = getTextValue(parent, tagName);
        if (!val.isEmpty()) {
            try { return Long.parseLong(val); } catch (NumberFormatException e) { /* ignore */ }
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
    public String getRequestXml(String[] cargoKeys) {
        return buildRequest(cargoKeys);
    }
}
