import { AdminCms } from '@/components/AdminCms';

export default function Admin() {
  return <div className="space-y-4"><section className="card"><h1 className="text-2xl font-bold">Admin CMS</h1><p className="text-slate-600">Protected APIs enforce Firebase authentication and ADMIN role server-side.</p></section><AdminCms /></div>;
}
