import { createHmac, timingSafeEqual } from 'crypto';

export function verifyCashfreeWebhook(rawBody: string, signature: string | null, timestamp: string | null) {
  const secret = process.env.CASHFREE_WEBHOOK_SECRET;
  if (!secret || !signature || !timestamp) return false;
  const expected = createHmac('sha256', secret).update(timestamp + rawBody).digest('base64');
  return timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
}

export function securityHeaders() {
  return {
    'Cache-Control': 'no-store',
    'X-Robots-Tag': 'noindex, nofollow',
  };
}
