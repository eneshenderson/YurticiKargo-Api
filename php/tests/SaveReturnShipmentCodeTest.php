<?php
/**
 * SaveReturnShipmentCode Test
 * 
 * Yurtiçi Kargo test ortamına bağlanarak iade kodu oluşturma testi yapar.
 * 
 * Çalıştırma: php tests/SaveReturnShipmentCodeTest.php
 */

require_once __DIR__ . '/../YurticiKargoClient.php';

echo "=== SaveReturnShipmentCode Test ===\n\n";

try {
    $client = new YurticiKargoClient(
        username: 'YKTEST',
        password: 'YK',
        language: 'TR',
        testMode: true
    );

    echo "[OK] SOAP bağlantısı kuruldu.\n";

    // Test 1: İade kodu oluşturma
    echo "\n--- Test 1: İade Kodu Oluşturma ---\n";

    $returnCode = 'RMA-TEST-' . time();
    $startDate = date('Ymd');
    $endDate = date('Ymd', strtotime('+30 days'));

    $result = $client->saveReturnShipmentCode(
        returnCode: $returnCode,
        startDate: $startDate,
        endDate: $endDate,
        maxCount: 1,
        fieldName: '53' // Test ortamı
    );

    echo "outFlag: {$result->outFlag}\n";
    echo "outResult: {$result->outResult}\n";
    echo "errCode: {$result->errCode}\n";

    if (($result->isSuccess)()) {
        echo "[PASS] İade kodu başarıyla oluşturuldu: {$returnCode}\n";
    } else {
        echo "[INFO] outFlag={$result->outFlag}: {$result->outResult} (errCode: {$result->errCode})\n";
    }

    // Test 2: Aynı iade kodunu tekrar oluşturmayı dene (hata beklenir)
    echo "\n--- Test 2: Aynı İade Kodunu Tekrar Oluşturma ---\n";

    $result2 = $client->saveReturnShipmentCode(
        returnCode: $returnCode,
        startDate: $startDate,
        endDate: $endDate,
        maxCount: 1,
        fieldName: '53'
    );

    echo "outFlag: {$result2->outFlag}\n";
    echo "outResult: {$result2->outResult}\n";
    echo "errCode: {$result2->errCode}\n";

    if (!($result2->isSuccess)()) {
        echo "[PASS] Beklenen hata alındı (duplicate iade kodu).\n";
    } else {
        echo "[INFO] İşlem tekrar başarılı oldu (beklenmedik).\n";
    }

    // Test 3: fieldName otomatik atanma (testMode = true → '53')
    echo "\n--- Test 3: fieldName Otomatik Atanma ---\n";

    $returnCode3 = 'RMA-AUTO-' . time();

    $result3 = $client->saveReturnShipmentCode(
        returnCode: $returnCode3,
        startDate: $startDate,
        endDate: $endDate,
        maxCount: 2
        // fieldName belirtilmedi, otomatik '53' olacak
    );

    echo "outFlag: {$result3->outFlag}\n";
    echo "outResult: {$result3->outResult}\n";

    if (($result3->isSuccess)()) {
        echo "[PASS] Otomatik fieldName ile iade kodu oluşturuldu.\n";
    } else {
        echo "[INFO] outFlag={$result3->outFlag}: {$result3->outResult}\n";
    }

    // Test 4: Validasyon - boş returnCode
    echo "\n--- Test 4: Validasyon (Boş returnCode) ---\n";

    try {
        $client->saveReturnShipmentCode(
            returnCode: '',
            startDate: $startDate,
            endDate: $endDate,
            maxCount: 1
        );
        echo "[FAIL] Hata beklendi ama alınmadı.\n";
    } catch (\InvalidArgumentException $e) {
        echo "[PASS] Doğru hata yakalandı: {$e->getMessage()}\n";
    }

    // Test 5: Validasyon - geçersiz tarih formatı
    echo "\n--- Test 5: Validasyon (Geçersiz Tarih) ---\n";

    try {
        $client->saveReturnShipmentCode(
            returnCode: 'RMA-VAL-' . time(),
            startDate: '2024-01-01', // Yanlış format
            endDate: $endDate,
            maxCount: 1
        );
        echo "[FAIL] Hata beklendi ama alınmadı.\n";
    } catch (\InvalidArgumentException $e) {
        echo "[PASS] Doğru hata yakalandı: {$e->getMessage()}\n";
    }

    // Test 6: Validasyon - maxCount < 1
    echo "\n--- Test 6: Validasyon (maxCount < 1) ---\n";

    try {
        $client->saveReturnShipmentCode(
            returnCode: 'RMA-MC-' . time(),
            startDate: $startDate,
            endDate: $endDate,
            maxCount: 0
        );
        echo "[FAIL] Hata beklendi ama alınmadı.\n";
    } catch (\InvalidArgumentException $e) {
        echo "[PASS] Doğru hata yakalandı: {$e->getMessage()}\n";
    }

} catch (SoapFault $e) {
    echo "[ERROR] SOAP Hatası: {$e->getMessage()}\n";
} catch (\Exception $e) {
    echo "[ERROR] Genel Hata: {$e->getMessage()}\n";
}

echo "\n=== Test Tamamlandı ===\n";
