import { jsonError } from '@/lib/errors';
import { prisma } from '@/lib/prisma';
import { requireAdmin } from '@/lib/auth';
import { taxonomySchema } from '@/lib/validators';

type Kind = 'exams' | 'subjects' | 'categories';
function kindFromUrl(req: Request): Kind {
  const kind = new URL(req.url).searchParams.get('kind');
  if (kind !== 'exams' && kind !== 'subjects' && kind !== 'categories') throw new Error('Invalid taxonomy kind');
  return kind;
}
async function list(kind: Kind) {
  if (kind === 'exams') return prisma.exam.findMany({ orderBy: { name: 'asc' } });
  if (kind === 'subjects') return prisma.subject.findMany({ orderBy: { name: 'asc' } });
  return prisma.category.findMany({ orderBy: { name: 'asc' } });
}
async function create(kind: Kind, data: { name: string }) {
  if (kind === 'exams') return prisma.exam.create({ data });
  if (kind === 'subjects') return prisma.subject.create({ data });
  return prisma.category.create({ data });
}
export async function GET(req: Request) {
  try {
    await requireAdmin(req);
    return Response.json(await list(kindFromUrl(req)));
  } catch (error) {
    return jsonError(error);
  }
}
export async function POST(req: Request) {
  try {
    await requireAdmin(req);
    return Response.json(await create(kindFromUrl(req), taxonomySchema.parse(await req.json())), { status: 201 });
  } catch (error) {
    return jsonError(error);
  }
}
