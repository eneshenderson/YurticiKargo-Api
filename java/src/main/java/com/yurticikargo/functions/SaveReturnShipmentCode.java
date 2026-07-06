package com.yurticikargo.functions;

import com.yurticikargo.models.ReturnCodeResult;
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
 * saveReturnShipmentCode SOAP fonksiyonu.
 * İade müşterilerinin YK birimine ileterek iade işlemini tamamlayacakları kodu oluşturur.
 */
public class SaveReturnShipmentCode {

    private final String endpoint;
    private final String username;
    private final String password;
    private final String language;
    private final HttpClient httpClient;

    public SaveReturnShipmentCode(String endpoint, String username, String password, String language, HttpClient httpClient) {
        this.endpoint = endpoint;
        this.username = username;
        this.password = password;
        this.language = language;
        this.httpClient = httpClient;
    }

    /**
     * İade kodu oluşturma isteği gönderir.
     *
     * @param returnCode İade kodu (benzersiz)
     * @param startDate  Geçerlilik başlangıç tarihi (YYYYMMDD)
     * @param endDate    Geçerlilik bitiş tarihi (YYYYMMDD)
     * @param maxCount   Kullanım adedi
     * @param fieldName  Özel alan bilgisi (test: 53 veya 3, canlı: 16)
     * @return ReturnCodeResult
     */
    public ReturnCodeResult execute(String returnCode, String startDate, String endDate, int maxCount, String fieldName) throws Exception {
        String soapXml = buildRequest(returnCode, startDate, endDate, maxCount, fieldName);
        String responseXml = sendRequest(soapXml);
        return parseResponse(responseXml);
    }

    private String buildRequest(String returnCode, String startDate, String endDate, int maxCount, String fieldName) {
        StringBuilder sb = new StringBuilder();
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        sb.append("<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" ");
        sb.append("xmlns:ship=\"http://yurticikargo.com.tr/ShippingOrderDispatcherServices\">\n");
        sb.append("  <soapenv:Header/>\n");
        sb.append("  <soapenv:Body>\n");
        sb.append("    <ship:saveReturnShipmentCode>\n");
        sb.append("      <wsUserName>").append(escapeXml(username)).append("</wsUserName>\n");
        sb.append("      <wsPassword>").append(escapeXml(password)).append("</wsPassword>\n");
        sb.append("      <wsLanguage>").append(escapeXml(language)).append("</wsLanguage>\n");
        sb.append("      <fieldName>").append(escapeXml(fieldName)).append("</fieldName>\n");
        sb.append("      <returnCode>").append(escapeXml(returnCode)).append("</returnCode>\n");
        sb.append("      <startDate>").append(escapeXml(startDate)).append("</startDate>\n");
        sb.append("      <endDate>").append(escapeXml(endDate)).append("</endDate>\n");
        sb.append("      <maxCount>").append(maxCount).append("</maxCount>\n");
        sb.append("    </ship:saveReturnShipmentCode>\n");
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

    public ReturnCodeResult parseResponse(String xml) throws Exception {
        ReturnCodeResult result = new ReturnCodeResult();

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

        // ExtendedBaseResultVO
        NodeList resultNodes = doc.getElementsByTagName("ExtendedBaseResultVO");
        if (resultNodes.getLength() > 0) {
            Element resultEl = (Element) resultNodes.item(0);
            result.setOutFlag(getIntValue(resultEl, "outFlag", 2));
            result.setOutResult(getTextValue(resultEl, "outResult"));
            result.setErrCode(getIntValue(resultEl, "errCode", 0));
        } else {
            result.setOutFlag(getIntValue(doc, "outFlag", 2));
            result.setOutResult(getTextValue(doc, "outResult"));
            result.setErrCode(getIntValue(doc, "errCode", 0));
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
    public String getRequestXml(String returnCode, String startDate, String endDate, int maxCount, String fieldName) {
        return buildRequest(returnCode, startDate, endDate, maxCount, fieldName);
    }
}
