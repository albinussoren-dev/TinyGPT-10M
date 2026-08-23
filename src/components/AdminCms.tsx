'use client';

import { auth } from '@/lib/firebase-client';
import { FormEvent, useState } from 'react';

export function AdminCms() {
  const [status, setStatus] = useState('Create taxonomy records and products. Requires ADMIN role.');
  async function createTaxonomy(kind: string, form: HTMLFormElement) {
    const token = await auth.currentUser?.getIdToken();
    const name = new FormData(form).get('name');
    const res = await fetch(`/api/admin/taxonomy?kind=${kind}`, { method: 'POST', headers: { 'content-type': 'application/json', authorization: `Bearer ${token}` }, body: JSON.stringify({ name }) });
    setStatus(res.ok ? `Saved ${kind}` : (await res.json()).error);
    if (res.ok) form.reset();
  }
  function onSubmit(kind: string) {
    return (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); void createTaxonomy(kind, event.currentTarget); };
  }
  return <div className="grid gap-4 md:grid-cols-3">{['exams', 'subjects', 'categories'].map((kind) => <form className="card space-y-3" onSubmit={onSubmit(kind)} key={kind}><h2 className="text-lg font-semibold capitalize">{kind}</h2><input className="w-full rounded border p-2" name="name" placeholder={`New ${kind}`} required /><button className="btn">Save</button></form>)}<p className="md:col-span-3 text-sm text-slate-600">{status}</p></div>;
}
