import { jsonError } from '@/lib/errors';
import { prisma } from '@/lib/prisma';
import { requireAdmin } from '@/lib/auth';
import { productSchema } from '@/lib/validators';

export async function POST(req: Request) {
  try {
    await requireAdmin(req);
    const data = productSchema.parse(await req.json());
    return Response.json(await prisma.product.create({ data }), { status: 201 });
  } catch (error) {
    return jsonError(error);
  }
}

export async function GET(req: Request) {
  try {
    await requireAdmin(req);
    return Response.json(await prisma.product.findMany({ include: { exam: true, subject: true, category: true }, orderBy: { createdAt: 'desc' } }));
  } catch (error) {
    return jsonError(error);
  }
}
