import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3'; import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
export const r2=new S3Client({region:'auto',endpoint:process.env.R2_ENDPOINT,credentials:{accessKeyId:process.env.R2_ACCESS_KEY_ID??'',secretAccessKey:process.env.R2_SECRET_ACCESS_KEY??''}});
export function signedReadUrl(key:string){return getSignedUrl(r2,new GetObjectCommand({Bucket:process.env.R2_BUCKET,Key:key,ResponseContentDisposition:'inline'}),{expiresIn:60});}
