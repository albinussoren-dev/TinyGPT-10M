import { prisma } from '@/lib/prisma'; import { requireUser } from '@/lib/auth';
export async function POST(req:Request){const user=await requireUser(req); const {type,payload}=await req.json(); const event=await prisma.event.create({data:{userId:user.id,type:String(type),payload:payload??{}}}); return Response.json(event,{status:201})}
