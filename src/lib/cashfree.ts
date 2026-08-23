import { assertEnv } from './errors';

export async function createCashfreeOrder(orderId: string, amountPaise: number, customer: { id: string; email: string; name?: string | null }) {
  const res = await fetch(`${process.env.CASHFREE_API_URL ?? 'https://sandbox.cashfree.com/pg'}/orders`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-version': '2023-08-01',
      'x-client-id': assertEnv('CASHFREE_APP_ID'),
      'x-client-secret': assertEnv('CASHFREE_SECRET_KEY'),
    },
    body: JSON.stringify({
      order_id: orderId,
      order_amount: amountPaise / 100,
      order_currency: 'INR',
      customer_details: { customer_id: customer.id, customer_email: customer.email, customer_name: customer.name ?? undefined },
      order_meta: { return_url: `${process.env.NEXT_PUBLIC_APP_URL ?? ''}/library?order_id=${orderId}` },
    }),
  });
  if (!res.ok) throw new Error(`Cashfree order failed with HTTP ${res.status}`);
  return res.json() as Promise<{ payment_session_id: string; order_id: string }>;
}
