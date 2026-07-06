/**
 * createShipment Test
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

console.log('createShipment Tests');
console.log('====================\n');

// Test 1: Zorunlu alan kontrolü
await test('Zorunlu alan eksik olduğunda hata fırlatır', async () => {
  try {
    await client.createShipment([{ cargoKey: '123' }]);
    assert.fail('Hata fırlatmalıydı');
  } catch (err) {
    assert.ok(err.message.includes('Zorunlu alan eksik'));
  }
});

// Test 2: Boş dizi kontrolü
await test('Boş shipments dizisi ile hata fırlatır', async () => {
  try {
    await client.createShipment([]);
    assert.fail('Hata fırlatmalıydı');
  } catch (err) {
    assert.strictEqual(err.message, 'shipments parametresi boş olamaz');
  }
});

// Test 3: Geçersiz parametre tipi
await test('Array olmayan parametre ile hata fırlatır', async () => {
  try {
    await client.createShipment('invalid');
    assert.fail('Hata fırlatmalıydı');
  } catch (err) {
    assert.strictEqual(err.message, 'shipments parametresi boş olamaz');
  }
});

// Test 4: Gerçek API çağrısı (test ortamı)
await test('Test ortamında gönderi oluşturur', async () => {
  const uniqueKey = 'TST' + Date.now();
  const result = await client.createShipment([
    {
      cargoKey: uniqueKey,
      invoiceKey: 'INV' + uniqueKey,
      receiverCustName: 'Test Alıcı',
      receiverAddress: 'Test Mahallesi Test Sokak No:1 Kadıköy/İstanbul',
      receiverPhone1: '05551234567',
      cityName: 'İstanbul',
      townName: 'Kadıköy'
    }
  ]);

  assert.ok(result.outFlag !== undefined, 'outFlag mevcut olmalı');
  assert.ok(result.outResult !== undefined, 'outResult mevcut olmalı');
  assert.ok(typeof result.isSuccess === 'function', 'isSuccess fonksiyonu mevcut olmalı');

  console.log(`    → outFlag: ${result.outFlag}, outResult: ${result.outResult}`);
  if (result.details.length > 0) {
    console.log(`    → İlk detay: cargoKey=${result.details[0].cargoKey}, errCode=${result.details[0].errCode}`);
  }
});

// Test 5: Çoklu gönderi (kargo bazlı)
await test('Çoklu gönderi oluşturma (aynı invoiceKey)', async () => {
  const ts = Date.now();
  const result = await client.createShipment([
    {
      cargoKey: 'M1' + ts,
      invoiceKey: 'INV' + ts,
      receiverCustName: 'Ali Veli',
      receiverAddress: 'Atatürk Cad. No:5',
      receiverPhone1: '05321234567',
      cargoCount: 1
    },
    {
      cargoKey: 'M2' + ts,
      invoiceKey: 'INV' + ts,
      receiverCustName: 'Ali Veli',
      receiverAddress: 'Atatürk Cad. No:5',
      receiverPhone1: '05321234567',
      cargoCount: 1
    }
  ]);

  assert.ok(result.outFlag !== undefined, 'outFlag mevcut olmalı');
  console.log(`    → outFlag: ${result.outFlag}, count: ${result.count}`);
});

// Test 6: Tahsilatlı teslimat parametreleri
await test('Tahsilatlı teslimat parametreleri ile gönderi oluşturur', async () => {
  const ts = Date.now();
  const result = await client.createShipment([
    {
      cargoKey: 'TT' + ts,
      invoiceKey: 'TTINV' + ts,
      receiverCustName: 'Kapıda Ödeme Test',
      receiverAddress: 'Test Adresi Kapıda Ödeme',
      receiverPhone1: '05551112233',
      ttCollectionType: '0',
      ttInvoiceAmount: '150.50',
      ttDocumentId: 'DOC' + ts,
      ttDocumentSaveType: '0'
    }
  ]);

  assert.ok(result.outFlag !== undefined, 'outFlag mevcut olmalı');
  console.log(`    → outFlag: ${result.outFlag}, outResult: ${result.outResult}`);
});

console.log(`\n${'─'.repeat(40)}`);
console.log(`Sonuç: ${passed} başarılı, ${failed} başarısız`);
console.log('');

if (failed > 0) process.exit(1);
