package com.yurticikargo.models;

import java.util.ArrayList;
import java.util.List;

/**
 * createShipment SOAP yanıt modeli.
 */
public class ShipmentResult {

    private int outFlag;
    private String outResult;
    private long jobId;
    private int count;
    private List<ShipmentDetail> details = new ArrayList<>();

    public int getOutFlag() { return outFlag; }
    public void setOutFlag(int outFlag) { this.outFlag = outFlag; }

    public String getOutResult() { return outResult; }
    public void setOutResult(String outResult) { this.outResult = outResult; }

    public long getJobId() { return jobId; }
    public void setJobId(long jobId) { this.jobId = jobId; }

    public int getCount() { return count; }
    public void setCount(int count) { this.count = count; }

    public List<ShipmentDetail> getDetails() { return details; }
    public void setDetails(List<ShipmentDetail> details) { this.details = details; }

    public boolean isSuccess() { return outFlag == 0; }

    public List<ShipmentDetail> getErrors() {
        List<ShipmentDetail> errors = new ArrayList<>();
        for (ShipmentDetail d : details) {
            if (d.getErrCode() != 0) errors.add(d);
        }
        return errors;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("ShipmentResult{outFlag=").append(outFlag)
          .append(", outResult='").append(outResult).append('\'')
          .append(", jobId=").append(jobId)
          .append(", count=").append(count)
          .append(", details=").append(details)
          .append('}');
        return sb.toString();
    }

    public static class ShipmentDetail {
        private String cargoKey;
        private String invoiceKey;
        private int errCode;
        private String errMessage;

        public String getCargoKey() { return cargoKey; }
        public void setCargoKey(String cargoKey) { this.cargoKey = cargoKey; }

        public String getInvoiceKey() { return invoiceKey; }
        public void setInvoiceKey(String invoiceKey) { this.invoiceKey = invoiceKey; }

        public int getErrCode() { return errCode; }
        public void setErrCode(int errCode) { this.errCode = errCode; }

        public String getErrMessage() { return errMessage; }
        public void setErrMessage(String errMessage) { this.errMessage = errMessage; }

        public boolean isSuccess() { return errCode == 0; }

        @Override
        public String toString() {
            return "ShipmentDetail{cargoKey='" + cargoKey + "', invoiceKey='" + invoiceKey +
                   "', errCode=" + errCode + ", errMessage='" + errMessage + "'}";
        }
    }
}
