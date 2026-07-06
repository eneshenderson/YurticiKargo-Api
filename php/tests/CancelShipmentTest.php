<?php
/**
 * CancelShipment Test
 * 
 * Yurtiçi Kargo test ortamına bağlanarak gönderi iptal testi yapar.
 * 
 * Çalıştırma: php tests/CancelShipmentTest.php
 */

require_once __DIR__ . '/../YurticiKargoClient.php';

echo "=== CancelShipment Test ===\n\n";

try {
    $client = new YurticiKargoClient(
        username: 'YKTEST',
        password: 'YK',
        language: 'TR',
        testMode: true
    );

    echo "[OK] SOAP bağlantısı kuruldu.\n";

    // Önce iptal edeceğimiz bir gönderi oluştur
    echo "\n--- Ön Hazırlık: Gönderi Oluşturma ---\n";

    $cargoKey = 'CNL' . time();
    $createResult = $client->createShipment([
        [
            'cargoKey'         => $cargoKey,
            'invoiceKey'       => 'CINV' . time(),
            'receiverCustName' => 'İptal Test Alıcı',
            'receiverAddress'  => 'Test Mahallesi Test Caddesi No:1',
            'receiverPhone1'   => '05551234567',
            'cityName'         => 'İstanbul',
            'townName'         => 'Kadıköy',
        ]
    ]);

    echo "Gönderi oluşturma - outFlag: {$createResult->outFlag}, outResult: {$createResult->outResult}\n";

    // Test 1: Gönderi iptali
    echo "\n--- Test 1: Gönderi İptali ---\n";

    $result = $client->cancelShipment([$cargoKey]);

    echo "outFlag: {$result->outFlag}\n";
    echo "outResult: {$result->outResult}\n";
    echo "senderCustId: {$result->senderCustId}\n";
    echo "count: {$result->count}\n";

    if (($result->isSuccess)()) {
        echo "[PASS] İptal işlemi başarılı.\n";
    } else {
        echo "[INFO] outFlag={$result->outFlag}: {$result->outResult}\n";
    }

    if (!empty($result->details)) {
        foreach ($result->details as $detail) {
            echo "  - cargoKey: {$detail->cargoKey}\n";
            echo "    operationStatus: {$detail->operationStatus}\n";
            echo "    operationCode: {$detail->operationCode}\n";
            echo "    operationMessage: {$detail->operationMessage}\n";
            echo "    Açıklama: " . CancelShipment::getStatusDescription($detail->operationCode) . "\n";
        }
    }

    // Test 2: Zaten iptal edilmiş gönderiyi tekrar iptal
    echo "\n--- Test 2: Tekrar İptal (Zaten İptal Edilmiş) ---\n";

    $result2 = $client->cancelShipment([$cargoKey]);

    echo "outFlag: {$result2->outFlag}\n";
    echo "outResult: {$result2->outResult}\n";

    if (!empty($result2->details)) {
        foreach ($result2->details as $detail) {
            echo "  - cargoKey: {$detail->cargoKey}, status: {$detail->operationStatus}\n";
        }
    }

    // Test 3: Mevcut olmayan kargo anahtarı
    echo "\n--- Test 3: Mevcut Olmayan Kargo Anahtarı ---\n";

    $result3 = $client->cancelShipment(['NONEXIST99999']);

    echo "outFlag: {$result3->outFlag}\n";
    echo "outResult: {$result3->outResult}\n";

    if (!empty($result3->details)) {
        foreach ($result3->details as $detail) {
            echo "  - cargoKey: {$detail->cargoKey}, errCode: {$detail->errCode}, errMessage: {$detail->errMessage}\n";
        }
    }

    // Test 4: Validasyon testi
    echo "\n--- Test 4: Validasyon (Boş Dizi) ---\n";

    try {
        $client->cancelShipment([]);
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
