'use client'; import { googleSignIn } from '@/lib/firebase-client';
export default function Login(){return <div className="card max-w-md"><h1 className="text-2xl font-bold">Sign in</h1><p className="my-4">Use Google to access purchases and admin tools.</p><button className="btn" onClick={()=>googleSignIn()}>Continue with Google</button></div>}
