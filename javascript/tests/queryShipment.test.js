/**
 * queryShipment Test
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

console.log('queryShipment Tests');
console.log('===================\n');

// Test 1: Boş keys kontrolü
await test('Boş keys dizisi ile hata fırlatır', async () => {
  try {
    await client.queryShipment({ keys: [], keyType: 0 });
    assert.fail('Hata fırlatmalıydı');
  } catch (err) {
    assert.strictEqual(err.message, 'keys parametresi boş olamaz');
  }
});

// Test 2: CargoKey ile sorgulama
await test('CargoKey ile sorgulama yapar (keyType=0)', async () => {
  const result = await client.queryShipment({
    keys: ['12520'],
    keyType: 0,
    addHistoricalData: false,
    onlyTracking: false
  });

  assert.ok(result.outFlag !== undefined, 'outFlag mevcut olmalı');
  assert.ok(result.outResult !== undefined, 'outResult mevcut olmalı');
  assert.ok(typeof result.isSuccess === 'function', 'isSuccess fonksiyonu mevcut olmalı');

  console.log(`    → outFlag: ${result.outFlag}, outResult: ${result.outResult}`);
  console.log(`    → Detay sayısı: ${result.details.length}`);
});

// Test 3: Hareket geçmişi ile sorgulama
await test('Hareket geçmişi dahil sorgulama yapar', async () => {
  const result = await client.queryShipment({
    keys: ['12520'],
    keyType: 0,
    addHistoricalData: true,
    onlyTracking: false
  });

  assert.ok(result.outFlag !== undefined, 'outFlag mevcut olmalı');

  if (result.details.length > 0 && result.details[0].itemDetail) {
    const history = result.details[0].itemDetail.cargoHistory;
    console.log(`    → Hareket geçmişi: ${history.length} kayıt`);
    if (history.length > 0) {
      console.log(`    → İlk olay: ${history[0].eventName} - ${history[0].eventDate}`);
    }
  } else {
    console.log(`    → outFlag: ${result.outFlag}, itemDetail bulunamadı`);
  }
});

// Test 4: Çoklu key ile sorgulama
await test('Çoklu key ile sorgulama yapar', async () => {
  const result = await client.queryShipment({
    keys: ['12520', '12521'],
    keyType: 0
  });

  assert.ok(result.outFlag !== undefined, 'outFlag mevcut olmalı');
  console.log(`    → outFlag: ${result.outFlag}, detay: ${result.details.length}`);
});

// Test 5: InvoiceKey ile sorgulama
await test('InvoiceKey ile sorgulama yapar (keyType=1)', async () => {
  const result = await client.queryShipment({
    keys: ['A123456'],
    keyType: 1
  });

  assert.ok(result.outFlag !== undefined, 'outFlag mevcut olmalı');
  console.log(`    → outFlag: ${result.outFlag}, outResult: ${result.outResult}`);
});

// Test 6: Sadece tracking URL sorgulama
await test('Sadece tracking sorgulama yapar (onlyTracking=true)', async () => {
  const result = await client.queryShipment({
    keys: ['12520'],
    keyType: 0,
    addHistoricalData: false,
    onlyTracking: true
  });

  assert.ok(result.outFlag !== undefined, 'outFlag mevcut olmalı');
  console.log(`    → outFlag: ${result.outFlag}`);
  if (result.details.length > 0 && result.details[0].itemDetail) {
    console.log(`    → trackingUrl: ${result.details[0].itemDetail.trackingUrl}`);
  }
});

console.log(`\n${'─'.repeat(40)}`);
console.log(`Sonuç: ${passed} başarılı, ${failed} başarısız`);
console.log('');

if (failed > 0) process.exit(1);
