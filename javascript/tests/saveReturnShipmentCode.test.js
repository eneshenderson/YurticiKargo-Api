/**
 * saveReturnShipmentCode Test
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

console.log('saveReturnShipmentCode Tests');
console.log('============================\n');

// Test 1: returnCode zorunlu
await test('returnCode olmadan hata fırlatır', async () => {
  try {
    await client.saveReturnShipmentCode({
      returnCode: '',
      startDate: '20240101',
      endDate: '20240131',
      maxCount: 1,
      fieldName: '53'
    });
    assert.fail('Hata fırlatmalıydı');
  } catch (err) {
    assert.ok(err.message.includes('returnCode'));
  }
});

// Test 2: startDate zorunlu
await test('startDate olmadan hata fırlatır', async () => {
  try {
    await client.saveReturnShipmentCode({
      returnCode: 'RMA001',
      startDate: '',
      endDate: '20240131',
      maxCount: 1,
      fieldName: '53'
    });
    assert.fail('Hata fırlatmalıydı');
  } catch (err) {
    assert.ok(err.message.includes('startDate'));
  }
});

// Test 3: endDate zorunlu
await test('endDate olmadan hata fırlatır', async () => {
  try {
    await client.saveReturnShipmentCode({
      returnCode: 'RMA001',
      startDate: '20240101',
      endDate: '',
      maxCount: 1,
      fieldName: '53'
    });
    assert.fail('Hata fırlatmalıydı');
  } catch (err) {
    assert.ok(err.message.includes('endDate'));
  }
});

// Test 4: fieldName zorunlu
await test('fieldName olmadan hata fırlatır', async () => {
  try {
    await client.saveReturnShipmentCode({
      returnCode: 'RMA001',
      startDate: '20240101',
      endDate: '20240131',
      maxCount: 1,
      fieldName: ''
    });
    assert.fail('Hata fırlatmalıydı');
  } catch (err) {
    assert.ok(err.message.includes('fieldName'));
  }
});

// Test 5: Gerçek API çağrısı
await test('Test ortamında iade kodu oluşturma isteği gönderir', async () => {
  const uniqueCode = 'RMA-' + Date.now();
  const result = await client.saveReturnShipmentCode({
    returnCode: uniqueCode,
    startDate: '20260701',
    endDate: '20260731',
    maxCount: 1,
    fieldName: '53'
  });

  assert.ok(result.outFlag !== undefined, 'outFlag mevcut olmalı');
  assert.ok(result.outResult !== undefined, 'outResult mevcut olmalı');
  assert.ok(typeof result.isSuccess === 'function', 'isSuccess fonksiyonu mevcut olmalı');

  console.log(`    → outFlag: ${result.outFlag}, outResult: ${result.outResult}`);
  console.log(`    → errCode: ${result.errCode}`);
});

// Test 6: fieldName=3 ile test
await test('fieldName=3 ile iade kodu oluşturur', async () => {
  const uniqueCode = 'RMA3-' + Date.now();
  const result = await client.saveReturnShipmentCode({
    returnCode: uniqueCode,
    startDate: '20260701',
    endDate: '20260731',
    maxCount: 5,
    fieldName: '3'
  });

  assert.ok(result.outFlag !== undefined, 'outFlag mevcut olmalı');
  console.log(`    → outFlag: ${result.outFlag}, outResult: ${result.outResult}`);
});

console.log(`\n${'─'.repeat(40)}`);
console.log(`Sonuç: ${passed} başarılı, ${failed} başarısız`);
console.log('');

if (failed > 0) process.exit(1);
