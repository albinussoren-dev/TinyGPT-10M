import { z } from 'zod';

export const idSchema = z.string().cuid();
export const productSchema = z.object({
  title: z.string().trim().min(3).max(160),
  description: z.string().trim().min(10).max(4000),
  pricePaise: z.number().int().positive().max(10_00_000),
  examId: z.string().cuid(),
  subjectId: z.string().cuid(),
  categoryId: z.string().cuid(),
  r2Key: z.string().trim().min(3).max(512).refine((key) => !key.startsWith('http'), 'R2 key must not be a public URL'),
  isPublished: z.boolean().default(false),
});
export const taxonomySchema = z.object({ name: z.string().trim().min(2).max(80) });
export const orderSchema = z.object({ productId: idSchema });
export const eventSchema = z.object({ type: z.string().trim().min(2).max(80), payload: z.record(z.unknown()).default({}) });
