package com.yurticikargo;

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
import java.time.Duration;
import java.util.*;

/**
 * Yurtiçi Kargo SOAP API Client - Tek Dosya (All-In-One)
 * 
 * Java 11+ ile derlenir ve calistirilir. Harici bagimlilik gerektirmez.
 * 
 * Derleme: javac -d out YurticiKargoAllInOne.java
 * Calistirma: java -cp out com.yurticikargo.YurticiKargoAllInOne
 */
public class YurticiKargoAllInOne {

    // =====================================================================
    // CONFIGURATION
    // =====================================================================

    private static final String ENDPOINT_TEST = "https://testws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices";
    private static final String ENDPOINT_LIVE = "https://ws.yurticikargo.com/KOPSWebServices/ShippingOrderDispatcherServices";
    private static final String SOAP_NS = "http://yurticikargo.com.tr/ShippingOrderDispatcherServices";

    private final String endpoint;
    private final String username;
    private final String password;
    private final String language;
    private final HttpClient httpClient;

    public YurticiKargoAllInOne(String username, String password, String language, boolean testMode) {
        this.username = username;
        this.password = password;
        this.language = language;
        this.endpoint = testMode ? ENDPOINT_TEST : ENDPOINT_LIVE;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(30))
                .build();
    }

    // =====================================================================
    // MODEL CLASSES
    // =====================================================================

    public static class ShipmentResult {
        public int outFlag;
        public String outResult;
        public long jobId;
        public int count;
        public List<ShipmentDetail> details = new ArrayList<>();

        public boolean isSuccess() { return outFlag == 0; }

        @Override
        public String toString() {
            return "ShipmentResult{outFlag=" + outFlag + ", outResult='" + outResult +
                   "', jobId=" + jobId + ", count=" + count + ", details=" + details + "}";
        }
    }

    public static class ShipmentDetail {
        public String cargoKey;
        public String invoiceKey;
        public int errCode;
        public String errMessage;

        public boolean isSuccess() { return errCode == 0; }

        @Override
        public String toString() {
            return "ShipmentDetail{cargoKey='" + cargoKey + "', errCode=" + errCode +
                   ", errMessage='" + errMessage + "'}";
        }
    }

    public static class CancelResult {
        public int outFlag;
        public String outResult;
        public String senderCustId;
        public int count;
        public List<CancelDetail> details = new ArrayList<>();

        public boolean isSuccess() { return outFlag == 0; }

        @Override
        public String toString() {
            return "CancelResult{outFlag=" + outFlag + ", outResult='" + outResult +
                   "', count=" + count + ", details=" + details + "}";
        }
    }

    public static class CancelDetail {
        public String cargoKey;
        public String invoiceKey;
        public long jobId;
        public String docId;
        public int operationCode;
        public String operationMessage;
        public String operationStatus;
        public int errCode;
        public String errMessage;

        @Override
        public String toString() {
            return "CancelDetail{cargoKey='" + cargoKey + "', operationStatus='" + operationStatus +
                   "', operationMessage='" + operationMessage + "'}";
        }
    }

    public static class QueryResult {
        public int outFlag;
        public String outResult;
        public List<QueryDetail> details = new ArrayList<>();

        public boolean isSuccess() { return outFlag == 0; }

        @Override
        public String toString() {
            return "QueryResult{outFlag=" + outFlag + ", outResult='" + outResult +
                   "', details=" + details + "}";
        }
    }

    public static class QueryDetail {
        public String cargoKey;
        public String invoiceKey;
        public int operationCode;
        public String operationMessage;
        public String operationStatus;
        public int errCode;
        public String errMessage;
        public QueryItemDetail itemDetail;

        public boolean isSuccess() { return errCode == 0; }

        @Override
        public String toString() {
            return "QueryDetail{cargoKey='" + cargoKey + "', operationStatus='" + operationStatus + "'}";
        }
    }

    public static class QueryItemDetail {
        public String trackingUrl;
        public String receiverCustName;
        public String receiverAddress;
        public String departureUnitName;
        public String deliveryDate;
        public String deliveryTime;
        public List<CargoEvent> cargoHistory = new ArrayList<>();

        @Override
        public String toString() {
            return "QueryItemDetail{trackingUrl='" + trackingUrl + "', receiverCustName='" + receiverCustName +
                   "', deliveryDate='" + deliveryDate + "', history=" + cargoHistory.size() + " events}";
        }
    }

    public static class CargoEvent {
        public String unitName;
        public String eventName;
        public String eventDate;
        public String eventTime;
        public String reasonName;

        @Override
        public String toString() {
            return eventDate + " " + eventTime + " | " + unitName + " | " + eventName;
        }
    }

    public static class ReturnCodeResult {
        public int outFlag;
        public String outResult;
        public int errCode;

        public boolean isSuccess() { return outFlag == 0 && errCode == 0; }

        @Override
        public String toString() {
            return "ReturnCodeResult{outFlag=" + outFlag + ", outResult='" + outResult +
                   "', errCode=" + errCode + "}";
        }
    }

    // =====================================================================
    // 1. CREATE SHIPMENT
    // =====================================================================

    public ShipmentResult createShipment(List<Map<String, String>> shipments) throws Exception {
        String soapXml = buildCreateShipmentXml(shipments);
        String responseXml = sendSoapRequest(soapXml);
        return parseShipmentResponse(responseXml);
    }

    private String buildCreateShipmentXml(List<Map<String, String>> shipments) {
        String[] stringFields = {"cargoKey", "invoiceKey", "receiverCustName", "receiverAddress",
                "cityName", "townName", "receiverPhone1", "receiverPhone2", "receiverPhone3",
                "emailAddress", "taxNumber", "taxOfficeName",
                "desi", "kg", "waybillNo",
                "specialField1", "specialField2", "specialField3",
                "ttCollectionType", "ttDocumentSaveType",
                "description", "orgGeoCode", "privilegeOrder", "custProdId", "orgReceiverCustId"};

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
            for (String field : stringFields) {
                String val = shipment.get(field);
                if (val != null && !val.isEmpty()) {
                    sb.append("        <").append(field).append(">").append(escapeXml(val)).append("</").append(field).append(">\n");
                }
            }
            // Required numeric fields with defaults
            appendNumeric(sb, "taxOfficeId", shipment, "0");
            appendNumeric(sb, "ttDocumentId", shipment, "0");
            appendNumeric(sb, "dcSelectedCredit", shipment, "0");
            appendNumeric(sb, "dcCreditRule", shipment, "0");
            appendNumeric(sb, "cargoCount", shipment, "1");
            // Optional double
            String ttAmount = shipment.get("ttInvoiceAmount");
            if (ttAmount != null && !ttAmount.isEmpty()) {
                sb.append("        <ttInvoiceAmount>").append(ttAmount).append("</ttInvoiceAmount>\n");
            }
            sb.append("      </ShippingOrderVO>\n");
        }

        sb.append("    </ship:createShipment>\n");
        sb.append("  </soapenv:Body>\n");
        sb.append("</soapenv:Envelope>");
        return sb.toString();
    }

    private void appendNumeric(StringBuilder sb, String field, Map<String, String> data, String defaultVal) {
        String val = data.get(field);
        sb.append("        <").append(field).append(">")
          .append(val != null && !val.isEmpty() ? val : defaultVal)
          .append("</").append(field).append(">\n");
    }

    private ShipmentResult parseShipmentResponse(String xml) throws Exception {
        Document doc = parseXml(xml);
        ShipmentResult result = new ShipmentResult();

        // Check SOAP Fault
        NodeList faults = doc.getElementsByTagName("faultstring");
        if (faults.getLength() > 0) {
            result.outFlag = 2;
            result.outResult = faults.item(0).getTextContent().trim();
            return result;
        }

        result.outFlag = getInt(doc, "outFlag", 2);
        result.outResult = getText(doc, "outResult");
        result.jobId = getLong(doc, "jobId", 0);
        result.count = getInt(doc, "count", 0);

        NodeList detailNodes = doc.getElementsByTagName("shippingOrderDetailVO");
        for (int i = 0; i < detailNodes.getLength(); i++) {
            Element el = (Element) detailNodes.item(i);
            ShipmentDetail detail = new ShipmentDetail();
            detail.cargoKey = getTextEl(el, "cargoKey");
            detail.invoiceKey = getTextEl(el, "invoiceKey");
            detail.errCode = getIntEl(el, "errCode", 0);
            detail.errMessage = getTextEl(el, "errMessage");
            result.details.add(detail);
        }
        return result;
    }

    // =====================================================================
    // 2. CANCEL SHIPMENT
    // =====================================================================

    public CancelResult cancelShipment(String[] cargoKeys) throws Exception {
        String soapXml = buildCancelShipmentXml(cargoKeys);
        String responseXml = sendSoapRequest(soapXml);
        return parseCancelResponse(responseXml);
    }

    private String buildCancelShipmentXml(String[] cargoKeys) {
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
        for (String key : cargoKeys) {
            sb.append("      <cargoKeys>").append(escapeXml(key)).append("</cargoKeys>\n");
        }
        sb.append("    </ship:cancelShipment>\n");
        sb.append("  </soapenv:Body>\n");
        sb.append("</soapenv:Envelope>");
        return sb.toString();
    }

    private CancelResult parseCancelResponse(String xml) throws Exception {
        Document doc = parseXml(xml);
        CancelResult result = new CancelResult();

        NodeList faults = doc.getElementsByTagName("faultstring");
        if (faults.getLength() > 0) {
            result.outFlag = 2;
            result.outResult = faults.item(0).getTextContent().trim();
            return result;
        }

        result.outFlag = getInt(doc, "outFlag", 2);
        result.outResult = getText(doc, "outResult");
        result.senderCustId = getText(doc, "senderCustId");
        result.count = getInt(doc, "count", 0);

        NodeList detailNodes = doc.getElementsByTagName("shippingCancelDetailVO");
        for (int i = 0; i < detailNodes.getLength(); i++) {
            Element el = (Element) detailNodes.item(i);
            CancelDetail detail = new CancelDetail();
            detail.cargoKey = getTextEl(el, "cargoKey");
            detail.invoiceKey = getTextEl(el, "invoiceKey");
            detail.jobId = getLongEl(el, "jobId", 0);
            detail.docId = getTextEl(el, "docId");
            detail.operationCode = getIntEl(el, "operationCode", 0);
            detail.operationMessage = getTextEl(el, "operationMessage");
            detail.operationStatus = getTextEl(el, "operationStatus");
            detail.errCode = getIntEl(el, "errCode", 0);
            detail.errMessage = getTextEl(el, "errMessage");
            result.details.add(detail);
        }
        return result;
    }

    // =====================================================================
    // 3. QUERY SHIPMENT
    // =====================================================================

    public QueryResult queryShipment(String[] keys, int keyType, boolean addHistoricalData, boolean onlyTracking) throws Exception {
        String soapXml = buildQueryShipmentXml(keys, keyType, addHistoricalData, onlyTracking);
        String responseXml = sendSoapRequest(soapXml);
        return parseQueryResponse(responseXml);
    }

    private String buildQueryShipmentXml(String[] keys, int keyType, boolean addHistoricalData, boolean onlyTracking) {
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

    private QueryResult parseQueryResponse(String xml) throws Exception {
        Document doc = parseXml(xml);
        QueryResult result = new QueryResult();

        NodeList faults = doc.getElementsByTagName("faultstring");
        if (faults.getLength() > 0) {
            result.outFlag = 2;
            result.outResult = faults.item(0).getTextContent().trim();
            return result;
        }

        result.outFlag = getInt(doc, "outFlag", 2);
        result.outResult = getText(doc, "outResult");

        NodeList detailNodes = doc.getElementsByTagName("shippingDeliveryDetailVO");
        for (int i = 0; i < detailNodes.getLength(); i++) {
            Element el = (Element) detailNodes.item(i);
            QueryDetail detail = new QueryDetail();
            detail.cargoKey = getTextEl(el, "cargoKey");
            detail.invoiceKey = getTextEl(el, "invoiceKey");
            detail.operationCode = getIntEl(el, "operationCode", 0);
            detail.operationMessage = getTextEl(el, "operationMessage");
            detail.operationStatus = getTextEl(el, "operationStatus");
            detail.errCode = getIntEl(el, "errCode", 0);
            detail.errMessage = getTextEl(el, "errMessage");

            // Item detail
            NodeList itemNodes = el.getElementsByTagName("shippingDeliveryItemDetailVO");
            if (itemNodes.getLength() > 0) {
                Element itemEl = (Element) itemNodes.item(0);
                QueryItemDetail itemDetail = new QueryItemDetail();
                itemDetail.trackingUrl = getTextEl(itemEl, "trackingUrl");
                itemDetail.receiverCustName = getTextEl(itemEl, "receiverCustName");
                itemDetail.receiverAddress = getTextEl(itemEl, "receiverAddressTxt");
                itemDetail.departureUnitName = getTextEl(itemEl, "departureUnitName");
                itemDetail.deliveryDate = getTextEl(itemEl, "deliveryDate");
                itemDetail.deliveryTime = getTextEl(itemEl, "deliveryTime");

                // Cargo history
                NodeList histNodes = itemEl.getElementsByTagName("invDocCargoVOArray");
                for (int j = 0; j < histNodes.getLength(); j++) {
                    Element hEl = (Element) histNodes.item(j);
                    CargoEvent event = new CargoEvent();
                    event.unitName = getTextEl(hEl, "unitName");
                    event.eventName = getTextEl(hEl, "eventName");
                    event.eventDate = getTextEl(hEl, "eventDate");
                    event.eventTime = getTextEl(hEl, "eventTime");
                    event.reasonName = getTextEl(hEl, "reasonName");
                    itemDetail.cargoHistory.add(event);
                }
                detail.itemDetail = itemDetail;
            }

            result.details.add(detail);
        }
        return result;
    }

    // =====================================================================
    // 4. SAVE RETURN SHIPMENT CODE
    // =====================================================================

    public ReturnCodeResult saveReturnShipmentCode(String returnCode, String startDate, String endDate, int maxCount, String fieldName) throws Exception {
        String soapXml = buildReturnCodeXml(returnCode, startDate, endDate, maxCount, fieldName);
        String responseXml = sendSoapRequest(soapXml);
        return parseReturnCodeResponse(responseXml);
    }

    private String buildReturnCodeXml(String returnCode, String startDate, String endDate, int maxCount, String fieldName) {
        StringBuilder sb = new StringBuilder();
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        sb.append("<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" ");
        sb.append("xmlns:ship=\"").append(SOAP_NS).append("\">\n");
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

    private ReturnCodeResult parseReturnCodeResponse(String xml) throws Exception {
        Document doc = parseXml(xml);
        ReturnCodeResult result = new ReturnCodeResult();

        NodeList faults = doc.getElementsByTagName("faultstring");
        if (faults.getLength() > 0) {
            result.outFlag = 2;
            result.outResult = faults.item(0).getTextContent().trim();
            return result;
        }

        result.outFlag = getInt(doc, "outFlag", 2);
        result.outResult = getText(doc, "outResult");
        result.errCode = getInt(doc, "errCode", 0);
        return result;
    }

    // =====================================================================
    // HTTP & XML UTILITIES
    // =====================================================================

    private String sendSoapRequest(String soapXml) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(endpoint))
                .header("Content-Type", "text/xml; charset=utf-8")
                .header("SOAPAction", "")
                .POST(HttpRequest.BodyPublishers.ofString(soapXml, StandardCharsets.UTF_8))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
        return response.body();
    }

    private Document parseXml(String xml) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(false);
        DocumentBuilder builder = factory.newDocumentBuilder();
        return builder.parse(new ByteArrayInputStream(xml.getBytes(StandardCharsets.UTF_8)));
    }

    private String getText(Document doc, String tag) {
        NodeList list = doc.getElementsByTagName(tag);
        return (list.getLength() > 0 && list.item(0).getTextContent() != null)
                ? list.item(0).getTextContent().trim() : "";
    }

    private String getTextEl(Element el, String tag) {
        NodeList list = el.getElementsByTagName(tag);
        return (list.getLength() > 0 && list.item(0).getTextContent() != null)
                ? list.item(0).getTextContent().trim() : "";
    }

    private int getInt(Document doc, String tag, int def) {
        String v = getText(doc, tag);
        try { return v.isEmpty() ? def : Integer.parseInt(v); } catch (NumberFormatException e) { return def; }
    }

    private int getIntEl(Element el, String tag, int def) {
        String v = getTextEl(el, tag);
        try { return v.isEmpty() ? def : Integer.parseInt(v); } catch (NumberFormatException e) { return def; }
    }

    private long getLong(Document doc, String tag, long def) {
        String v = getText(doc, tag);
        try { return v.isEmpty() ? def : Long.parseLong(v); } catch (NumberFormatException e) { return def; }
    }

    private long getLongEl(Element el, String tag, long def) {
        String v = getTextEl(el, tag);
        try { return v.isEmpty() ? def : Long.parseLong(v); } catch (NumberFormatException e) { return def; }
    }

    private String escapeXml(String value) {
        if (value == null) return "";
        return value.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;");
    }

    // =====================================================================
    // MAIN - Demo / Test
    // =====================================================================

    public static void main(String[] args) {
        System.out.println("==============================================================");
        System.out.println("  Yurtici Kargo Java API Client - All-In-One Demo");
        System.out.println("==============================================================");
        System.out.println();

        YurticiKargoAllInOne client = new YurticiKargoAllInOne("YKTEST", "YK", "TR", true);
        String uniqueId = String.valueOf(System.currentTimeMillis() % 100000);

        // --- 1. CREATE SHIPMENT ---
        System.out.println("--- 1. createShipment ---");
        try {
            Map<String, String> shipment = new HashMap<>();
            shipment.put("cargoKey", "AIO" + uniqueId);
            shipment.put("invoiceKey", "INV" + uniqueId);
            shipment.put("receiverCustName", "Test Alici");
            shipment.put("receiverAddress", "Eski Buyukdere Cad. No:3 Maslak Istanbul");
            shipment.put("receiverPhone1", "02123652426");
            shipment.put("cityName", "Istanbul");
            shipment.put("townName", "Maslak");

            ShipmentResult result = client.createShipment(List.of(shipment));
            System.out.println("  outFlag: " + result.outFlag);
            System.out.println("  outResult: " + result.outResult);
            System.out.println("  jobId: " + result.jobId);
            System.out.println("  isSuccess: " + result.isSuccess());
            for (ShipmentDetail d : result.details) {
                System.out.println("    -> " + d.cargoKey + " [" + d.errCode + "] " + d.errMessage);
            }
        } catch (Exception e) {
            System.out.println("  HATA: " + e.getMessage());
        }

        System.out.println();

        // --- 2. CANCEL SHIPMENT ---
        System.out.println("--- 2. cancelShipment ---");
        try {
            CancelResult result = client.cancelShipment(new String[]{"AIO" + uniqueId});
            System.out.println("  outFlag: " + result.outFlag);
            System.out.println("  outResult: " + result.outResult);
            System.out.println("  isSuccess: " + result.isSuccess());
            for (CancelDetail d : result.details) {
                System.out.println("    -> " + d.cargoKey + " | " + d.operationStatus + " | " + d.operationMessage);
            }
        } catch (Exception e) {
            System.out.println("  HATA: " + e.getMessage());
        }

        System.out.println();

        // --- 3. QUERY SHIPMENT ---
        System.out.println("--- 3. queryShipment ---");
        try {
            QueryResult result = client.queryShipment(new String[]{"12520"}, 0, true, false);
            System.out.println("  outFlag: " + result.outFlag);
            System.out.println("  outResult: " + result.outResult);
            System.out.println("  isSuccess: " + result.isSuccess());
            for (QueryDetail d : result.details) {
                System.out.println("    -> " + d.cargoKey + " | " + d.operationStatus + " | errCode=" + d.errCode);
                if (d.itemDetail != null) {
                    System.out.println("      trackingUrl: " + d.itemDetail.trackingUrl);
                    System.out.println("      receiver: " + d.itemDetail.receiverCustName);
                    System.out.println("      deliveryDate: " + d.itemDetail.deliveryDate);
                    for (CargoEvent ev : d.itemDetail.cargoHistory) {
                        System.out.println("        " + ev.eventDate + " " + ev.eventTime +
                                         " | " + ev.unitName + " | " + ev.eventName);
                    }
                }
            }
        } catch (Exception e) {
            System.out.println("  HATA: " + e.getMessage());
        }

        System.out.println();

        // --- 4. SAVE RETURN SHIPMENT CODE ---
        System.out.println("--- 4. saveReturnShipmentCode ---");
        try {
            ReturnCodeResult result = client.saveReturnShipmentCode(
                    "RMA-AIO-" + uniqueId, "20260101", "20260131", 1, "53");
            System.out.println("  outFlag: " + result.outFlag);
            System.out.println("  outResult: " + result.outResult);
            System.out.println("  errCode: " + result.errCode);
            System.out.println("  isSuccess: " + result.isSuccess());
        } catch (Exception e) {
            System.out.println("  HATA: " + e.getMessage());
        }

        System.out.println();
        System.out.println("==============================================================");
        System.out.println("Demo tamamlandi.");
    }
}
