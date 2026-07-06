/**
 * cancelShipment Test
 * Node.js assert modülü ile test.
 */

import assert from 'assert';
import { YurticiKargoClient } from '../YurticiKargoClient.js';

const client = new YurticiKargoClient({
  username: 'YKTEST',
  password: 'YK',
  language: 'TR',
  testMode: true
});

let passed = 0;
let failed = 0;

function test(name, fn) {
  return fn().then(() => {
    console.log(`  ✓ ${name}`);
    passed++;
  }).catch((err) => {
    console.log(`  ✗ ${name}`);
    console.log(`    ${err.message}`);
    failed++;
  });
}

console.log('cancelShipment Tests');
console.log('====================\n');

// Test 1: Boş dizi kontrolü
await test('Boş cargoKeys dizisi ile hata fırlatır', async () => {
  try {
    await client.cancelShipment([]);
    assert.fail('Hata fırlatmalıydı');
  } catch (err) {
    assert.strictEqual(err.message, 'cargoKeys parametresi boş olamaz');
  }
});

// Test 2: Geçersiz parametre tipi
await test('Array olmayan parametre ile hata fırlatır', async () => {
  try {
    await client.cancelShipment(null);
    assert.fail('Hata fırlatmalıydı');
  } catch (err) {
    assert.strictEqual(err.message, 'cargoKeys parametresi boş olamaz');
  }
});

// Test 3: Tek kargo iptal denemesi
await test('Tek kargo anahtarı ile iptal isteği gönderir', async () => {
  const result = await client.cancelShipment(['NONEXIST001']);

  assert.ok(result.outFlag !== undefined, 'outFlag mevcut olmalı');
  assert.ok(result.outResult !== undefined, 'outResult mevcut olmalı');
  assert.ok(typeof result.isSuccess === 'function', 'isSuccess fonksiyonu mevcut olmalı');

  console.log(`    → outFlag: ${result.outFlag}, outResult: ${result.outResult}`);
  if (result.details.length > 0) {
    const d = result.details[0];
    console.log(`    → cargoKey: ${d.cargoKey}, status: ${d.operationStatus}, msg: ${d.operationMessage}`);
  }
});

// Test 4: Çoklu kargo iptal denemesi
await test('Çoklu kargo anahtarı ile iptal isteği gönderir', async () => {
  const result = await client.cancelShipment(['NONEXIST001', 'NONEXIST002', 'NONEXIST003']);

  assert.ok(result.outFlag !== undefined, 'outFlag mevcut olmalı');
  console.log(`    → outFlag: ${result.outFlag}, detay sayısı: ${result.details.length}`);
});

// Test 5: Önce oluştur, sonra iptal et
await test('Oluşturulan gönderiyi iptal eder', async () => {
  const ts = Date.now();
  const cargoKey = 'CNC' + ts;

  // Önce gönderi oluştur
  const createResult = await client.createShipment([
    {
      cargoKey: cargoKey,
      invoiceKey: 'CINV' + ts,
      receiverCustName: 'İptal Test',
      receiverAddress: 'İptal Adresi No:1',
      receiverPhone1: '05559998877'
    }
  ]);

  console.log(`    → Oluşturma: outFlag=${createResult.outFlag}`);

  // Şimdi iptal et
  const cancelResult = await client.cancelShipment([cargoKey]);

  assert.ok(cancelResult.outFlag !== undefined, 'outFlag mevcut olmalı');
  console.log(`    → İptal: outFlag=${cancelResult.outFlag}, outResult=${cancelResult.outResult}`);
  if (cancelResult.details.length > 0) {
    console.log(`    → Status: ${cancelResult.details[0].operationStatus}`);
  }
});

console.log(`\n${'─'.repeat(40)}`);
console.log(`Sonuç: ${passed} başarılı, ${failed} başarısız`);
console.log('');

if (failed > 0) process.exit(1);
