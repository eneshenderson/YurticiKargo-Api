namespace YurticiKargo.Models;

public class CargoHistoryEvent
{
    public string UnitName { get; set; } = string.Empty;
    public string EventName { get; set; } = string.Empty;
    public string ReasonName { get; set; } = string.Empty;
    public string EventDate { get; set; } = string.Empty;
    public string EventTime { get; set; } = string.Empty;
    public string CityName { get; set; } = string.Empty;
    public string TownName { get; set; } = string.Empty;
}

public class ItemDetail
{
    public string TrackingUrl { get; set; } = string.Empty;
    public string ReceiverCustName { get; set; } = string.Empty;
    public string DepartureUnitName { get; set; } = string.Empty;
    public string DeliveryDate { get; set; } = string.Empty;
    public string DeliveryTime { get; set; } = string.Empty;
    public List<CargoHistoryEvent> CargoHistory { get; set; } = new();
}

public class QueryDetail
{
    public string CargoKey { get; set; } = string.Empty;
    public string InvoiceKey { get; set; } = string.Empty;
    public string OperationStatus { get; set; } = string.Empty;
    public int OperationCode { get; set; }
    public string OperationMessage { get; set; } = string.Empty;
    public int ErrCode { get; set; }
    public string ErrMessage { get; set; } = string.Empty;
    public ItemDetail? ItemDetail { get; set; }

    public bool IsSuccess() => ErrCode == 0;
}

public class QueryResult
{
    public int OutFlag { get; set; }
    public string OutResult { get; set; } = string.Empty;
    public long SenderCustId { get; set; }
    public int Count { get; set; }
    public List<QueryDetail> Details { get; set; } = new();

    public bool IsSuccess() => OutFlag == 0;
}
