const fmt = (n) => n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const form = document.getElementById('invoice-form');
const banner = document.getElementById('banner');

async function load() {
  const [list, sum] = await Promise.all([
    fetch('/api/invoices').then((r) => r.json()),
    fetch('/api/summary').then((r) => r.json()),
  ]);
  document.getElementById('rows').innerHTML = list.map((i) => `
    <tr data-number="${i.number}">
      <td>${i.number}</td><td>${i.client}</td>
      <td class="num">${fmt(i.net)}</td><td class="num">${fmt(i.vat)}</td><td class="num">${fmt(i.gross)}</td>
      <td><button data-delete="${i.id}" aria-label="Delete ${i.number}">Delete</button></td>
    </tr>`).join('');
  document.getElementById('summary').textContent =
    `${sum.count} invoices · Net ${fmt(sum.net)} · VAT ${fmt(sum.vat)} · Gross ${fmt(sum.gross)}`;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  document.querySelectorAll('[data-error]').forEach((el) => (el.textContent = ''));
  banner.textContent = '';
  const data = Object.fromEntries(new FormData(form));
  const body = { ...data, net: data.net === '' ? NaN : Number(data.net), vatRate: Number(data.vatRate) };
  const button = form.querySelector('button');
  button.disabled = true; // prevents double submit
  try {
    const res = await fetch('/api/invoices', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    });
    if (!res.ok) {
      const { errors } = await res.json();
      Object.entries(errors).forEach(([k, v]) => {
        const el = document.querySelector(`[data-error="${k}"]`);
        if (el) el.textContent = v; else banner.textContent = v;
      });
      if (res.status === 409) banner.textContent = errors.number;
      return;
    }
    form.reset();
    await load();
  } finally {
    button.disabled = false;
  }
});

document.getElementById('rows').addEventListener('click', async (e) => {
  const id = e.target.dataset.delete;
  if (!id) return;
  await fetch(`/api/invoices/${id}`, { method: 'DELETE' });
  await load();
});

load();
