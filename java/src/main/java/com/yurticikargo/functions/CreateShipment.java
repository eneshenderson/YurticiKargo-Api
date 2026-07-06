package com.yurticikargo.functions;

import com.yurticikargo.models.ShipmentResult;
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
import java.util.List;
import java.util.Map;

/**
 * createShipment SOAP fonksiyonu.
 * Müşterinin kargo bilgilerini Yurtiçi Kargo sistemine ileten servistir.
 */
public class CreateShipment {

    private static final String SOAP_NS = "http://yurticikargo.com.tr/ShippingOrderDispatcherServices";
    private static final String[] SHIPMENT_FIELDS = {
        "cargoKey", "invoiceKey", "receiverCustName", "receiverAddress",
        "cityName", "townName", "receiverPhone1", "receiverPhone2", "receiverPhone3",
        "emailAddress", "taxNumber", "taxOfficeName",
        "desi", "kg", "waybillNo",
        "specialField1", "specialField2", "specialField3",
        "ttCollectionType", "ttDocumentSaveType",
        "description", "orgGeoCode", "privilegeOrder", "custProdId", "orgReceiverCustId"
    };
    // Numeric fields that need special handling
    private static final String[] LONG_FIELDS = {"taxOfficeId", "ttDocumentId", "dcSelectedCredit", "dcCreditRule"};
    private static final String[] INT_FIELDS = {"cargoCount"};
    private static final String[] DOUBLE_FIELDS = {"ttInvoiceAmount"};

    private final String endpoint;
    private final String username;
    private final String password;
    private final String language;
    private final HttpClient httpClient;

    public CreateShipment(String endpoint, String username, String password, String language, HttpClient httpClient) {
        this.endpoint = endpoint;
        this.username = username;
        this.password = password;
        this.language = language;
        this.httpClient = httpClient;
    }

    /**
     * Gönderi oluşturma isteği gönderir.
     *
     * @param shipments Her eleman bir gönderi bilgisi Map'i.
     *                  Zorunlu anahtarlar: cargoKey, invoiceKey, receiverCustName, receiverAddress, receiverPhone1
     * @return ShipmentResult
     */
    public ShipmentResult execute(List<Map<String, String>> shipments) throws Exception {
        String soapXml = buildRequest(shipments);
        String responseXml = sendRequest(soapXml);
        return parseResponse(responseXml);
    }

    private String buildRequest(List<Map<String, String>> shipments) {
        StringBuilder sb = new StringBuilder();
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        sb.append("<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" ");
        sb.append("xmlns:ship=\"").append(SOAP_NS).append("\">\n");
        sb.append("  <soapenv:Header/>\n");
        sb.append("  <soapenv:Body>\n");
        sb.append("    <ship:createShipment>\n");
        sb.append("      <wsUserName>").append(escapeXml(username)).append("</wsUserName>\n");
        sb.append("      <wsPassword>").append(escapeXml(password)).append("</wsPassword>\n");
        sb.append("      <userLanguage>").append(escapeXml(language)).append("</userLanguage>\n");

        for (Map<String, String> shipment : shipments) {
            sb.append("      <ShippingOrderVO>\n");
            // String fields
            for (String field : SHIPMENT_FIELDS) {
                appendField(sb, field, shipment);
            }
            // Long fields (default 0 if not provided)
            for (String field : LONG_FIELDS) {
                String val = shipment.get(field);
                sb.append("        <").append(field).append(">");
                sb.append(val != null && !val.isEmpty() ? val : "0");
                sb.append("</").append(field).append(">\n");
            }
            // Int fields
            for (String field : INT_FIELDS) {
                String val = shipment.get(field);
                sb.append("        <").append(field).append(">");
                sb.append(val != null && !val.isEmpty() ? val : "1");
                sb.append("</").append(field).append(">\n");
            }
            // Double fields
            for (String field : DOUBLE_FIELDS) {
                String val = shipment.get(field);
                if (val != null && !val.isEmpty()) {
                    sb.append("        <").append(field).append(">").append(val).append("</").append(field).append(">\n");
                }
            }
            sb.append("      </ShippingOrderVO>\n");
        }

        sb.append("    </ship:createShipment>\n");
        sb.append("  </soapenv:Body>\n");
        sb.append("</soapenv:Envelope>");
        return sb.toString();
    }

    private void appendField(StringBuilder sb, String fieldName, Map<String, String> data) {
        String value = data.get(fieldName);
        if (value != null && !value.isEmpty()) {
            sb.append("        <").append(fieldName).append(">")
              .append(escapeXml(value))
              .append("</").append(fieldName).append(">\n");
        }
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

    public ShipmentResult parseResponse(String xml) throws Exception {
        ShipmentResult result = new ShipmentResult();

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
        result.setJobId(getLongValue(doc, "jobId", 0));
        result.setCount(getIntValue(doc, "count", 0));

        // shippingOrderDetailVO
        NodeList detailNodes = doc.getElementsByTagName("shippingOrderDetailVO");
        for (int i = 0; i < detailNodes.getLength(); i++) {
            Element detailEl = (Element) detailNodes.item(i);
            ShipmentResult.ShipmentDetail detail = new ShipmentResult.ShipmentDetail();
            detail.setCargoKey(getTextValue(detailEl, "cargoKey"));
            detail.setInvoiceKey(getTextValue(detailEl, "invoiceKey"));
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

    private long getLongValue(Document doc, String tagName, long defaultVal) {
        String val = getTextValue(doc, tagName);
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
    public String getRequestXml(List<Map<String, String>> shipments) {
        return buildRequest(shipments);
    }
}
