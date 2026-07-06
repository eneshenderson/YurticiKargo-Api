package com.yurticikargo.models;

import java.util.ArrayList;
import java.util.List;

/**
 * cancelShipment SOAP yanıt modeli.
 */
public class CancelResult {

    private int outFlag;
    private String outResult;
    private String senderCustId;
    private int count;
    private List<CancelDetail> details = new ArrayList<>();

    public int getOutFlag() { return outFlag; }
    public void setOutFlag(int outFlag) { this.outFlag = outFlag; }

    public String getOutResult() { return outResult; }
    public void setOutResult(String outResult) { this.outResult = outResult; }

    public String getSenderCustId() { return senderCustId; }
    public void setSenderCustId(String senderCustId) { this.senderCustId = senderCustId; }

    public int getCount() { return count; }
    public void setCount(int count) { this.count = count; }

    public List<CancelDetail> getDetails() { return details; }
    public void setDetails(List<CancelDetail> details) { this.details = details; }

    public boolean isSuccess() { return outFlag == 0; }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("CancelResult{outFlag=").append(outFlag)
          .append(", outResult='").append(outResult).append('\'')
          .append(", senderCustId='").append(senderCustId).append('\'')
          .append(", count=").append(count)
          .append(", details=").append(details)
          .append('}');
        return sb.toString();
    }

    public static class CancelDetail {
        private String cargoKey;
        private String invoiceKey;
        private long jobId;
        private String docId;
        private int operationCode;
        private String operationMessage;
        private String operationStatus;
        private int errCode;
        private String errMessage;

        public String getCargoKey() { return cargoKey; }
        public void setCargoKey(String cargoKey) { this.cargoKey = cargoKey; }

        public String getInvoiceKey() { return invoiceKey; }
        public void setInvoiceKey(String invoiceKey) { this.invoiceKey = invoiceKey; }

        public long getJobId() { return jobId; }
        public void setJobId(long jobId) { this.jobId = jobId; }

        public String getDocId() { return docId; }
        public void setDocId(String docId) { this.docId = docId; }

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

        @Override
        public String toString() {
            return "CancelDetail{cargoKey='" + cargoKey + "', operationStatus='" + operationStatus +
                   "', operationMessage='" + operationMessage + "', errCode=" + errCode + "}";
        }
    }
}
