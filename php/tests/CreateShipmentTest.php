<?php
/**
 * CreateShipment Test
 * 
 * Yurtiçi Kargo test ortamına bağlanarak gönderi oluşturma testi yapar.
 * 
 * Çalıştırma: php tests/CreateShipmentTest.php
 */

require_once __DIR__ . '/../YurticiKargoClient.php';

echo "=== CreateShipment Test ===\n\n";

try {
    $client = new YurticiKargoClient(
        username: 'YKTEST',
        password: 'YK',
        language: 'TR',
        testMode: true
    );

    echo "[OK] SOAP bağlantısı kuruldu.\n";

    // Test 1: Tek gönderi oluşturma
    echo "\n--- Test 1: Tek Gönderi Oluşturma ---\n";

    $cargoKey = 'TEST' . time(); // Benzersiz anahtar

    $result = $client->createShipment([
        [
            'cargoKey'         => $cargoKey,
            'invoiceKey'       => 'INV' . time(),
            'receiverCustName' => 'Test Alıcı',
            'receiverAddress'  => 'Eski Büyükdere Cad. No:3 Maslak İstanbul',
            'receiverPhone1'   => '02123652426',
            'cityName'         => 'İstanbul',
            'townName'         => 'Maslak',
        ]
    ]);

    echo "outFlag: {$result->outFlag}\n";
    echo "outResult: {$result->outResult}\n";
    echo "jobId: {$result->jobId}\n";
    echo "count: {$result->count}\n";

    if (($result->isSuccess)()) {
        echo "[PASS] Gönderi başarıyla oluşturuldu.\n";
    } else {
        echo "[INFO] outFlag={$result->outFlag}: {$result->outResult}\n";
    }

    if (!empty($result->details)) {
        foreach ($result->details as $detail) {
            echo "  - cargoKey: {$detail->cargoKey}, errCode: {$detail->errCode}, errMessage: {$detail->errMessage}\n";
        }
    }

    // Test 2: Çoklu gönderi (kargo bazlı)
    echo "\n--- Test 2: Çoklu Gönderi (Kargo Bazlı) ---\n";

    $invoiceKey = 'MINV' . time();
    $result2 = $client->createShipment([
        [
            'cargoKey'         => 'MK1' . time(),
            'invoiceKey'       => $invoiceKey,
            'receiverCustName' => 'Çoklu Test Alıcı',
            'receiverAddress'  => 'Test Adres 1',
            'receiverPhone1'   => '05551234567',
            'cargoCount'       => 1,
        ],
        [
            'cargoKey'         => 'MK2' . time(),
            'invoiceKey'       => $invoiceKey,
            'receiverCustName' => 'Çoklu Test Alıcı',
            'receiverAddress'  => 'Test Adres 1',
            'receiverPhone1'   => '05551234567',
            'cargoCount'       => 1,
        ],
    ]);

    echo "outFlag: {$result2->outFlag}\n";
    echo "outResult: {$result2->outResult}\n";

    if (($result2->isSuccess)()) {
        echo "[PASS] Çoklu gönderi başarıyla oluşturuldu.\n";
    } else {
        echo "[INFO] outFlag={$result2->outFlag}: {$result2->outResult}\n";
    }

    if (!empty($result2->details)) {
        foreach ($result2->details as $detail) {
            echo "  - cargoKey: {$detail->cargoKey}, errCode: {$detail->errCode}, errMessage: {$detail->errMessage}\n";
        }
    }

    // Test 3: Validasyon testi (eksik zorunlu alan)
    echo "\n--- Test 3: Validasyon (Eksik Alan) ---\n";

    try {
        $client->createShipment([
            [
                'cargoKey' => 'VAL_TEST',
                // invoiceKey eksik
                'receiverCustName' => 'Test',
                'receiverAddress'  => 'Test Adres',
                'receiverPhone1'   => '05551234567',
            ]
        ]);
        echo "[FAIL] Hata beklendi ama alınmadı.\n";
    } catch (\InvalidArgumentException $e) {
        echo "[PASS] Doğru hata yakalandı: {$e->getMessage()}\n";
    }

    // Debug bilgisi
    echo "\n--- Debug: Son SOAP Request ---\n";
    $lastReq = $client->getLastRequest();
    if ($lastReq) {
        echo substr($lastReq, 0, 500) . "...\n";
    }

} catch (SoapFault $e) {
    echo "[ERROR] SOAP Hatası: {$e->getMessage()}\n";
} catch (\Exception $e) {
    echo "[ERROR] Genel Hata: {$e->getMessage()}\n";
}

echo "\n=== Test Tamamlandı ===\n";
