using YurticiKargo;
using YurticiKargo.Models;

namespace YurticiKargo.Tests;

public static class SaveReturnShipmentCodeTest
{
    public static async Task RunAsync()
    {
        Console.WriteLine("=== SaveReturnShipmentCode Test ===\n");

        using var client = new YurticiKargoClient(
            username: "YKTEST",
            password: "YK",
            language: "TR",
            testMode: true
        );

        try
        {
            var result = await client.SaveReturnShipmentCodeAsync(
                returnCode: "RMA-TEST-" + DateTime.Now.Ticks.ToString()[^6..],
                startDate: DateTime.Now.ToString("yyyyMMdd"),
                endDate: DateTime.Now.AddDays(30).ToString("yyyyMMdd"),
                maxCount: 1,
                fieldName: "53"  // Test ortamında 53 veya 3
            );

            Console.WriteLine($"OutFlag: {result.OutFlag}");
            Console.WriteLine($"OutResult: {result.OutResult}");
            Console.WriteLine($"ErrCode: {result.ErrCode}");
            Console.WriteLine($"Success: {result.IsSuccess()}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Exception: {ex.Message}");
        }

        Console.WriteLine();
    }
}
