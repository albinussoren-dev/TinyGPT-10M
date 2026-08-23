import { BuyButton } from '@/components/AuthAction';
import { prisma } from '@/lib/prisma';

export default async function Home() {
  const products = await prisma.product.findMany({ where: { isPublished: true }, include: { exam: true, subject: true, category: true }, orderBy: { createdAt: 'desc' } });
  return <div className="space-y-6"><section className="card"><h1 className="text-3xl font-bold">ExamQ&A Marketplace</h1><p className="mt-2 text-slate-600">Buy verified exam PDFs and read them in a secured, watermarked reader with encrypted PWA offline-reading foundations.</p></section><div className="grid gap-4 md:grid-cols-3">{products.map((p) => <article className="card" key={p.id}><div className="text-sm text-slate-500">{p.exam.name} / {p.subject.name} / {p.category.name}</div><h2 className="mt-2 text-xl font-semibold">{p.title}</h2><p className="mt-2 line-clamp-3">{p.description}</p><div className="mt-4 flex items-start justify-between gap-3"><b>₹{(p.pricePaise / 100).toFixed(2)}</b><BuyButton productId={p.id} /></div></article>)}</div></div>;
}
