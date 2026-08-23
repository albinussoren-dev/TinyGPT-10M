'use client';

import { auth } from '@/lib/firebase-client';
import { useState } from 'react';

type Props = { productId: string; label?: string };

export function BuyButton({ productId, label = 'Buy securely' }: Props) {
  const [status, setStatus] = useState<string>();
  async function buy() {
    setStatus('Creating secure order...');
    const token = await auth.currentUser?.getIdToken();
    if (!token) {
      setStatus('Please sign in with Google first.');
      return;
    }
    const res = await fetch('/api/orders', { method: 'POST', headers: { 'content-type': 'application/json', authorization: `Bearer ${token}` }, body: JSON.stringify({ productId }) });
    const data = await res.json();
    if (!res.ok) {
      setStatus(data.error ?? 'Unable to create order');
      return;
    }
    setStatus(`Payment session created: ${data.paymentSessionId}. Connect Cashfree checkout SDK in production storefront.`);
  }
  return <div className="space-y-2"><button className="btn" onClick={buy}>{label}</button>{status ? <p className="text-xs text-slate-600">{status}</p> : null}</div>;
}
