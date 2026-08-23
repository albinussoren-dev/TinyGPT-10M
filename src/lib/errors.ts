import { ZodError } from 'zod';

export function jsonError(error: unknown) {
  if (error instanceof Response) return error;
  if (error instanceof ZodError) {
    return Response.json({ error: 'Validation failed', issues: error.flatten() }, { status: 400 });
  }
  const message = error instanceof Error ? error.message : 'Unexpected error';
  const status = message.includes('not found') ? 404 : 500;
  return Response.json({ error: message }, { status });
}

export function assertEnv(name: string) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required environment variable ${name}`);
  return value;
}
