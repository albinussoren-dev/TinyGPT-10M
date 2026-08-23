import { jsonError } from '@/lib/errors';
import { prisma } from '@/lib/prisma';
import { verifyCashfreeWebhook } from '@/lib/security';

export async function POST(req: Request) {
  try {
    const raw = await req.text();
    if (!verifyCashfreeWebhook(raw, req.headers.get('x-webhook-signature'), req.headers.get('x-webhook-timestamp'))) {
      return new Response('Invalid signature', { status: 401 });
    }
    const body = JSON.parse(raw);
    const cashfreeOrderId = body?.data?.order?.order_id;
    const status = body?.data?.payment?.payment_status;
    if (status === 'SUCCESS' && cashfreeOrderId) {
      const order = await prisma.order.update({ where: { cashfreeOrderId }, data: { status: 'PAID' } });
      await prisma.purchase.upsert({
        where: { userId_productId: { userId: order.userId, productId: order.productId } },
        update: {},
        create: { userId: order.userId, productId: order.productId, orderId: order.id },
      });
    }
    return Response.json({ ok: true });
  } catch (error) {
    return jsonError(error);
  }
}
