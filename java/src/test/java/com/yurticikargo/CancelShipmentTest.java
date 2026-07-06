package com.yurticikargo;

import com.yurticikargo.models.CancelResult;

/**
 * CancelShipment test — YKTEST ortamına bağlanır.
 *
 * Çalıştırma: java -cp out com.yurticikargo.CancelShipmentTest
 */
public class CancelShipmentTest {

    public static void main(String[] args) {
        System.out.println("=== CancelShipment Test ===\n");

        YurticiKargoClient client = new YurticiKargoClient("YKTEST", "YK", "TR", true);

        // Daha önce oluşturulmuş bir cargoKey ile test edin
        String[] cargoKeys = {"0000113", "0000114"};

        try {
            // Debug: SOAP XML'i görüntüle
            System.out.println("--- SOAP Request XML ---");
            System.out.println(client.getCancelShipmentRequestXml(cargoKeys));
            System.out.println();

            // İsteği gönder
            CancelResult result = client.cancelShipment(cargoKeys);

            System.out.println("--- Sonuç ---");
            System.out.println("outFlag: " + result.getOutFlag());
            System.out.println("outResult: " + result.getOutResult());
            System.out.println("senderCustId: " + result.getSenderCustId());
            System.out.println("count: " + result.getCount());
            System.out.println("isSuccess: " + result.isSuccess());
            System.out.println();

            if (result.isSuccess()) {
                System.out.println("[PASS] cancelShipment başarılı!");
            } else {
                System.out.println("[INFO] Yanıt alındı (outFlag=" + result.getOutFlag() + ")");
            }

            for (CancelResult.CancelDetail detail : result.getDetails()) {
                System.out.println("  cargoKey=" + detail.getCargoKey() +
                                 ", operationStatus=" + detail.getOperationStatus() +
                                 ", operationMessage=" + detail.getOperationMessage() +
                                 ", operationCode=" + detail.getOperationCode());
            }

        } catch (Exception e) {
            System.out.println("[FAIL] Exception: " + e.getMessage());
            e.printStackTrace();
        }

        System.out.println("\n=== Test Bitti ===");
    }
}
