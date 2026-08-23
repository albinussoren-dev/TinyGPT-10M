# Study Time ExamQ&A

Study Time is a production-oriented paid-document marketplace for exam Q&A PDFs. It uses Next.js App Router, TypeScript, Tailwind CSS, Prisma/PostgreSQL, Firebase Google Authentication, Cashfree payments, private Cloudflare R2 storage, watermarked online reading, encrypted PWA offline-reading primitives, RBAC admin APIs, analytics events, CI, and Vercel-ready configuration.

## Security model

- Paid PDFs are referenced only by private `Product.r2Key` values, never by public URLs.
- Protected APIs verify Firebase ID tokens server-side and persist users in PostgreSQL.
- Admin APIs require the database `ADMIN` role in addition to a valid Firebase token.
- Cashfree webhooks require HMAC signature verification before creating purchases.
- Reader access verifies purchase ownership, logs access, fetches the PDF from R2 using a short-lived server-side URL, watermarks the PDF, and returns `no-store` bytes.
- Web/PWA screenshot prevention is not claimed as complete; a future native Android reader can add Android `FLAG_SECURE`.

## Run locally

```bash
npm install
cp .env.example .env
npx prisma generate
npx prisma migrate deploy
npm run dev
```

## Required checks before release

```bash
npm run typecheck
npm run lint
npm test
npm run build
```
