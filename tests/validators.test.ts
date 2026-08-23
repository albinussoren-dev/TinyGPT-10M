import { describe, expect, it } from 'vitest';
import { productSchema } from '../src/lib/validators';

const cuid = 'clwtx7kkj000008l5f0g7a9sp';

describe('product validation', () => {
  it('rejects invalid products', () => {
    expect(() => productSchema.parse({ title: 'x' })).toThrow();
  });

  it('rejects public paid-file URLs', () => {
    expect(() => productSchema.parse({ title: 'Algebra Q&A', description: 'Full solved paper set', pricePaise: 9900, examId: cuid, subjectId: cuid, categoryId: cuid, r2Key: 'https://cdn.example.com/a.pdf' })).toThrow();
  });

  it('accepts complete private-R2-key products', () => {
    expect(productSchema.parse({ title: 'Algebra Q&A', description: 'Full solved paper set', pricePaise: 9900, examId: cuid, subjectId: cuid, categoryId: cuid, r2Key: 'private/a.pdf' }).isPublished).toBe(false);
  });
});
