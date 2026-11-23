import { test, expect } from './fixtures';

test.describe('Invoices UI', () => {
  test('adds an invoice and shows VAT, gross and totals', async ({ invoices }) => {
    await invoices.add({ number: 'INV-0001', client: 'Acme Retail', net: '1000', vatRate: '20' });

    const row = invoices.row('INV-0001');
    await expect(row).toContainText('Acme Retail');
    await expect(row.locator('td').nth(3)).toHaveText('200.00');
    await expect(row.locator('td').nth(4)).toHaveText('1,200.00');
    await expect(invoices.summary).toHaveText('1 invoices · Net 1,000.00 · VAT 200.00 · Gross 1,200.00');
    await expect(invoices.number).toHaveValue(''); // form is cleared after success
  });

  test('rounds VAT to cents on awkward amounts', async ({ invoices }) => {
    await invoices.add({ number: 'INV-0002', client: 'Delta Foods', net: '19.99', vatRate: '5' });
    await expect(invoices.row('INV-0002').locator('td').nth(3)).toHaveText('1.00');
    await expect(invoices.row('INV-0002').locator('td').nth(4)).toHaveText('20.99');
  });

  test('shows field errors and saves nothing for invalid input', async ({ invoices }) => {
    await invoices.add({ number: '123', client: '', net: '-5' });

    await expect(invoices.fieldError('number')).toHaveText('Use the format INV-0001');
    await expect(invoices.fieldError('client')).toHaveText('Client is required');
    await expect(invoices.fieldError('net')).toHaveText('Net amount must be greater than 0');
    await expect(invoices.rows).toHaveCount(0);
  });

  test('rejects a duplicate invoice number', async ({ invoices }) => {
    await invoices.add({ number: 'INV-0003', client: 'Orion Clinics', net: '50' });
    await invoices.add({ number: 'INV-0003', client: 'Someone Else', net: '75' });

    await expect(invoices.banner).toHaveText('Invoice INV-0003 already exists');
    await expect(invoices.rows).toHaveCount(1);
    await expect(invoices.row('INV-0003')).toContainText('Orion Clinics');
  });

  test('deleting an invoice updates the totals', async ({ invoices }) => {
    await invoices.add({ number: 'INV-0004', client: 'Vega Motors', net: '100' });
    await invoices.add({ number: 'INV-0005', client: 'Lumen Studio', net: '50', vatRate: '0' });
    await expect(invoices.summary).toContainText('2 invoices · Net 150.00 · VAT 20.00 · Gross 170.00');

    await invoices.remove('INV-0004');
    await expect(invoices.rows).toHaveCount(1);
    await expect(invoices.summary).toHaveText('1 invoices · Net 50.00 · VAT 0.00 · Gross 50.00');
  });
});
