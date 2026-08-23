import { prisma } from '@/lib/prisma';
export async function GET(){const products=await prisma.product.findMany({where:{isPublished:true},include:{exam:true,subject:true,category:true}}); return Response.json(products)}
