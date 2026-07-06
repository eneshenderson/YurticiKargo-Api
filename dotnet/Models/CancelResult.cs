namespace YurticiKargo.Models;

public class CancelDetail
{
    public string CargoKey { get; set; } = string.Empty;
    public string InvoiceKey { get; set; } = string.Empty;
    public long JobId { get; set; }
    public string DocId { get; set; } = string.Empty;
    public int OperationCode { get; set; }
    public string OperationMessage { get; set; } = string.Empty;
    public string OperationStatus { get; set; } = string.Empty;
    public int ErrCode { get; set; }
    public string ErrMessage { get; set; } = string.Empty;
}

public class CancelResult
{
    public int OutFlag { get; set; }
    public string OutResult { get; set; } = string.Empty;
    public long SenderCustId { get; set; }
    public int Count { get; set; }
    public List<CancelDetail> Details { get; set; } = new();

    public bool IsSuccess() => OutFlag == 0;
}
