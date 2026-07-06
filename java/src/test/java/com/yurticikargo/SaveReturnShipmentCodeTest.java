package com.yurticikargo;

import com.yurticikargo.models.ReturnCodeResult;

/**
 * SaveReturnShipmentCode test — YKTEST ortamına bağlanır.
 *
 * Çalıştırma: java -cp out com.yurticikargo.SaveReturnShipmentCodeTest
 */
public class SaveReturnShipmentCodeTest {

    public static void main(String[] args) {
        System.out.println("=== SaveReturnShipmentCode Test ===\n");

        YurticiKargoClient client = new YurticiKargoClient("YKTEST", "YK", "TR", true);

        // Benzersiz iade kodu oluştur
        String returnCode = "RMA-TEST-" + System.currentTimeMillis() % 100000;
        String startDate = "20260101";
        String endDate = "20260131";
        int maxCount = 1;
        String fieldName = "53"; // Test ortamı

        try {
            // Debug: SOAP XML'i görüntüle
            System.out.println("--- SOAP Request XML ---");
            System.out.println(client.getSaveReturnShipmentCodeRequestXml(returnCode, startDate, endDate, maxCount, fieldName));
            System.out.println();

            // İsteği gönder
            ReturnCodeResult result = client.saveReturnShipmentCode(returnCode, startDate, endDate, maxCount, fieldName);

            System.out.println("--- Sonuç ---");
            System.out.println("outFlag: " + result.getOutFlag());
            System.out.println("outResult: " + result.getOutResult());
            System.out.println("errCode: " + result.getErrCode());
            System.out.println("isSuccess: " + result.isSuccess());
            System.out.println();

            if (result.isSuccess()) {
                System.out.println("[PASS] saveReturnShipmentCode başarılı!");
            } else {
                System.out.println("[INFO] Yanıt alındı (outFlag=" + result.getOutFlag() + ", errCode=" + result.getErrCode() + ")");
                System.out.println("  " + result.getOutResult());
            }

        } catch (Exception e) {
            System.out.println("[FAIL] Exception: " + e.getMessage());
            e.printStackTrace();
        }

        System.out.println("\n=== Test Bitti ===");
    }
}
