package com.yurticikargo.models;

import java.util.ArrayList;
import java.util.List;

/**
 * queryShipment SOAP yanıt modeli.
 */
public class QueryResult {

    private int outFlag;
    private String outResult;
    private List<QueryDetail> details = new ArrayList<>();

    public int getOutFlag() { return outFlag; }
    public void setOutFlag(int outFlag) { this.outFlag = outFlag; }

    public String getOutResult() { return outResult; }
    public void setOutResult(String outResult) { this.outResult = outResult; }

    public List<QueryDetail> getDetails() { return details; }
    public void setDetails(List<QueryDetail> details) { this.details = details; }

    public boolean isSuccess() { return outFlag == 0; }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("QueryResult{outFlag=").append(outFlag)
          .append(", outResult='").append(outResult).append('\'')
          .append(", details=").append(details)
          .append('}');
        return sb.toString();
    }

    public static class QueryDetail {
        private String cargoKey;
        private String invoiceKey;
        private int operationCode;
        private String operationMessage;
        private String operationStatus;
        private int errCode;
        private String errMessage;
        private QueryItemDetail itemDetail;

        public String getCargoKey() { return cargoKey; }
        public void setCargoKey(String cargoKey) { this.cargoKey = cargoKey; }

        public String getInvoiceKey() { return invoiceKey; }
        public void setInvoiceKey(String invoiceKey) { this.invoiceKey = invoiceKey; }

        public int getOperationCode() { return operationCode; }
        public void setOperationCode(int operationCode) { this.operationCode = operationCode; }

        public String getOperationMessage() { return operationMessage; }
        public void setOperationMessage(String operationMessage) { this.operationMessage = operationMessage; }

        public String getOperationStatus() { return operationStatus; }
        public void setOperationStatus(String operationStatus) { this.operationStatus = operationStatus; }

        public int getErrCode() { return errCode; }
        public void setErrCode(int errCode) { this.errCode = errCode; }

        public String getErrMessage() { return errMessage; }
        public void setErrMessage(String errMessage) { this.errMessage = errMessage; }

        public QueryItemDetail getItemDetail() { return itemDetail; }
        public void setItemDetail(QueryItemDetail itemDetail) { this.itemDetail = itemDetail; }

        public boolean isSuccess() { return errCode == 0; }

        @Override
        public String toString() {
            return "QueryDetail{cargoKey='" + cargoKey + "', operationStatus='" + operationStatus +
                   "', errCode=" + errCode + ", itemDetail=" + itemDetail + "}";
        }
    }

    public static class QueryItemDetail {
        private String trackingUrl;
        private String receiverCustName;
        private String receiverAddress;
        private String departureUnitName;
        private String deliveryDate;
        private String deliveryTime;
        private List<CargoEvent> cargoHistory = new ArrayList<>();

        public String getTrackingUrl() { return trackingUrl; }
        public void setTrackingUrl(String trackingUrl) { this.trackingUrl = trackingUrl; }

        public String getReceiverCustName() { return receiverCustName; }
        public void setReceiverCustName(String receiverCustName) { this.receiverCustName = receiverCustName; }

        public String getReceiverAddress() { return receiverAddress; }
        public void setReceiverAddress(String receiverAddress) { this.receiverAddress = receiverAddress; }

        public String getDepartureUnitName() { return departureUnitName; }
        public void setDepartureUnitName(String departureUnitName) { this.departureUnitName = departureUnitName; }

        public String getDeliveryDate() { return deliveryDate; }
        public void setDeliveryDate(String deliveryDate) { this.deliveryDate = deliveryDate; }

        public String getDeliveryTime() { return deliveryTime; }
        public void setDeliveryTime(String deliveryTime) { this.deliveryTime = deliveryTime; }

        public List<CargoEvent> getCargoHistory() { return cargoHistory; }
        public void setCargoHistory(List<CargoEvent> cargoHistory) { this.cargoHistory = cargoHistory; }

        @Override
        public String toString() {
            return "QueryItemDetail{trackingUrl='" + trackingUrl + "', receiverCustName='" + receiverCustName +
                   "', deliveryDate='" + deliveryDate + "', history=" + cargoHistory.size() + " events}";
        }
    }

    public static class CargoEvent {
        private String unitName;
        private String eventName;
        private String eventDate;
        private String eventTime;
        private String reasonName;

        public String getUnitName() { return unitName; }
        public void setUnitName(String unitName) { this.unitName = unitName; }

        public String getEventName() { return eventName; }
        public void setEventName(String eventName) { this.eventName = eventName; }

        public String getEventDate() { return eventDate; }
        public void setEventDate(String eventDate) { this.eventDate = eventDate; }

        public String getEventTime() { return eventTime; }
        public void setEventTime(String eventTime) { this.eventTime = eventTime; }

        public String getReasonName() { return reasonName; }
        public void setReasonName(String reasonName) { this.reasonName = reasonName; }

        @Override
        public String toString() {
            return "CargoEvent{" + eventDate + " " + eventTime + " | " + unitName + " | " + eventName + "}";
        }
    }
}
