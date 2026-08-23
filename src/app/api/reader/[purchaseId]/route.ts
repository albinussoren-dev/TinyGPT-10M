import { jsonError } from '@/lib/errors';
import { prisma } from '@/lib/prisma';
import { requireUser } from '@/lib/auth';
import { signedReadUrl } from '@/lib/r2';
import { securityHeaders } from '@/lib/security';
import { watermarkPdf } from '@/lib/watermark';

export async function GET(req: Request, { params }: { params: { purchaseId: string } }) {
  try {
    const user = await requireUser(req);
    const purchase = await prisma.purchase.findFirst({ where: { id: params.purchaseId, userId: user.id }, include: { product: true } });
    if (!purchase) return new Response('Forbidden', { status: 403 });
    await prisma.accessLog.create({ data: { purchaseId: purchase.id, action: 'READ', ip: req.headers.get('x-forwarded-for'), userAgent: req.headers.get('user-agent') } });
    const source = await fetch(await signedReadUrl(purchase.product.r2Key));
    if (!source.ok) throw new Error('Unable to load private document');
    const bytes = await watermarkPdf(await source.arrayBuffer(), `${user.email} ${purchase.id}`);
    return new Response(bytes, { headers: { 'content-type': 'application/pdf', ...securityHeaders() } });
  } catch (error) {
    return jsonError(error);
  }
}
