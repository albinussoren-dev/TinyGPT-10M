const DB='study-time-offline';
export async function deriveAesKey(passphrase:string,salt:Uint8Array){const material=await crypto.subtle.importKey('raw',new TextEncoder().encode(passphrase),'PBKDF2',false,['deriveKey']); return crypto.subtle.deriveKey({name:'PBKDF2',salt,iterations:210000,hash:'SHA-256'},material,{name:'AES-GCM',length:256},false,['encrypt','decrypt']);}
export async function encryptForOffline(bytes:ArrayBuffer, passphrase:string){const salt=crypto.getRandomValues(new Uint8Array(16)); const iv=crypto.getRandomValues(new Uint8Array(12)); const key=await deriveAesKey(passphrase,salt); const cipher=await crypto.subtle.encrypt({name:'AES-GCM',iv},key,bytes); return {salt,iv,cipher};}
export { DB };
