import { Page, Locator, expect } from '@playwright/test';

export class InvoicesPage {
  readonly number: Locator;
  readonly client: Locator;
  readonly net: Locator;
  readonly vatRate: Locator;
  readonly submit: Locator;
  readonly rows: Locator;
  readonly summary: Locator;
  readonly banner: Locator;

  constructor(private readonly page: Page) {
    this.number = page.getByLabel('Invoice number');
    this.client = page.getByLabel('Client');
    this.net = page.getByLabel('Net amount');
    this.vatRate = page.getByLabel('VAT rate');
    this.submit = page.getByRole('button', { name: 'Add invoice' });
    this.rows = page.locator('#rows tr');
    this.summary = page.getByTestId('summary');
    this.banner = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/');
    await expect(this.summary).toContainText('invoices');
  }

  async add(inv: { number: string; client: string; net: string; vatRate?: '0' | '5' | '20' }) {
    await this.number.fill(inv.number);
    await this.client.fill(inv.client);
    await this.net.fill(inv.net);
    await this.vatRate.selectOption(inv.vatRate ?? '20');
    await this.submit.click();
  }

  row(number: string) {
    return this.page.locator(`#rows tr[data-number="${number}"]`);
  }

  fieldError(name: 'number' | 'client' | 'net' | 'vatRate') {
    return this.page.locator(`[data-error="${name}"]`);
  }

  async remove(number: string) {
    await this.page.getByRole('button', { name: `Delete ${number}` }).click();
  }
}
