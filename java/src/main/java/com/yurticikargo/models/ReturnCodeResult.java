package com.yurticikargo.models;

/**
 * saveReturnShipmentCode SOAP yanıt modeli.
 */
public class ReturnCodeResult {

    private int outFlag;
    private String outResult;
    private int errCode;

    public int getOutFlag() { return outFlag; }
    public void setOutFlag(int outFlag) { this.outFlag = outFlag; }

    public String getOutResult() { return outResult; }
    public void setOutResult(String outResult) { this.outResult = outResult; }

    public int getErrCode() { return errCode; }
    public void setErrCode(int errCode) { this.errCode = errCode; }

    public boolean isSuccess() { return outFlag == 0 && errCode == 0; }

    @Override
    public String toString() {
        return "ReturnCodeResult{outFlag=" + outFlag + ", outResult='" + outResult +
               "', errCode=" + errCode + "}";
    }
}
