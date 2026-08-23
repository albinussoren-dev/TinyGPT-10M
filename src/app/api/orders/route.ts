import { createCashfreeOrder } from '@/lib/cashfree';
import { jsonError } from '@/lib/errors';
import { prisma } from '@/lib/prisma';
import { requireUser } from '@/lib/auth';
import { orderSchema } from '@/lib/validators';

export async function POST(req: Request) {
  try {
    const user = await requireUser(req);
    const { productId } = orderSchema.parse(await req.json());
    const product = await prisma.product.findFirstOrThrow({ where: { id: productId, isPublished: true } });
    const order = await prisma.order.create({
      data: { cashfreeOrderId: `st_${crypto.randomUUID()}`, amountPaise: product.pricePaise, userId: user.id, productId: product.id },
    });
    const payment = await createCashfreeOrder(order.cashfreeOrderId, order.amountPaise, { id: user.id, email: user.email, name: user.name });
    return Response.json({ orderId: order.id, cashfreeOrderId: order.cashfreeOrderId, paymentSessionId: payment.payment_session_id });
  } catch (error) {
    return jsonError(error);
  }
}
