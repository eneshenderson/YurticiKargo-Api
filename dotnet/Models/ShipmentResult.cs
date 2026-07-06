namespace YurticiKargo.Models;

public class ShipmentDetail
{
    public string CargoKey { get; set; } = string.Empty;
    public string InvoiceKey { get; set; } = string.Empty;
    public int ErrCode { get; set; }
    public string ErrMessage { get; set; } = string.Empty;
}

public class ShipmentResult
{
    public int OutFlag { get; set; }
    public string OutResult { get; set; } = string.Empty;
    public long JobId { get; set; }
    public int Count { get; set; }
    public List<ShipmentDetail> Details { get; set; } = new();

    public bool IsSuccess() => OutFlag == 0;

    public List<ShipmentDetail> GetErrors() =>
        Details.Where(d => d.ErrCode != 0).ToList();
}
