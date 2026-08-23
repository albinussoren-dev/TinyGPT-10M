import { jsonError } from '@/lib/errors';
import { prisma } from '@/lib/prisma';
import { requireUser } from '@/lib/auth';

export async function GET(req: Request) {
  try {
    const user = await requireUser(req);
    const purchases = await prisma.purchase.findMany({
      where: { userId: user.id },
      include: { product: { include: { exam: true, subject: true, category: true } } },
      orderBy: { createdAt: 'desc' },
    });
    return Response.json(purchases);
  } catch (error) {
    return jsonError(error);
  }
}
