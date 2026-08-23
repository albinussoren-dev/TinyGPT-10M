'use client';

import { auth } from '@/lib/firebase-client';
import Link from 'next/link';
import { useState } from 'react';

type Purchase = { id: string; product: { title: string; exam: { name: string }; subject: { name: string }; category: { name: string } } };

export function LibraryClient() {
  const [items, setItems] = useState<Purchase[]>([]);
  const [status, setStatus] = useState('Sign in, then load your purchases.');
  async function load() {
    const token = await auth.currentUser?.getIdToken();
    if (!token) return setStatus('Please sign in with Google first.');
    const res = await fetch('/api/library', { headers: { authorization: `Bearer ${token}` } });
    const data = await res.json();
    if (!res.ok) return setStatus(data.error ?? 'Unable to load library');
    setItems(data);
    setStatus(data.length ? 'Loaded purchased documents.' : 'No purchases found yet.');
  }
  return <section className="card space-y-4"><button className="btn" onClick={load}>Load my library</button><p className="text-sm text-slate-600">{status}</p><div className="grid gap-3">{items.map((p) => <article className="rounded border p-3" key={p.id}><h2 className="font-semibold">{p.product.title}</h2><p className="text-sm text-slate-600">{p.product.exam.name} / {p.product.subject.name} / {p.product.category.name}</p><Link className="btn mt-3" href={`/reader/${p.id}`}>Open secure reader</Link></article>)}</div></section>;
}
