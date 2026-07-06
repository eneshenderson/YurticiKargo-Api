namespace YurticiKargo.Models;

public class ReturnCodeResult
{
    public int OutFlag { get; set; }
    public string OutResult { get; set; } = string.Empty;
    public int ErrCode { get; set; }

    public bool IsSuccess() => OutFlag == 0;
}
