import { test as base, expect, APIRequestContext } from '@playwright/test';
import { InvoicesPage } from './pages/InvoicesPage';

export type Invoice = { number: string; client: string; net: number; vatRate: 0 | 5 | 20 };

export async function createInvoice(request: APIRequestContext, inv: Invoice) {
  const res = await request.post('/api/invoices', { data: inv });
  expect(res.status(), await res.text()).toBe(201);
  return res.json();
}

type Fixtures = { invoices: InvoicesPage; cleanBackend: void };

export const test = base.extend<Fixtures>({
  // Runs automatically before every test (UI and API): each test starts from an empty backend.
  cleanBackend: [
    async ({ request }, use) => {
      await request.post('/api/reset');
      await use();
    },
    { auto: true },
  ],
  invoices: async ({ page }, use) => {
    const p = new InvoicesPage(page);
    await p.goto();
    await use(p);
  },
});

export { expect };
