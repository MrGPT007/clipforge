import { env } from 'cloudflare:workers';
import { owner,db,fail,ApiError } from '@/lib/server';
const limit=20*1024*1024;
export async function POST(request:Request){try{
 const user=await owner(request);if(!env.BUCKET)throw new ApiError('Audio storage is unavailable. Try again later.',503);
 if(Number(request.headers.get('content-length'))>limit+10000)throw new ApiError('Choose an audio file smaller than 20 MB.',413);
 const data=await request.formData();const file=data.get('file');if(!(file instanceof File)||file.size>limit||!file.size)throw new ApiError('Choose an audio file smaller than 20 MB.');
 const allowed=['audio/mpeg','audio/mp3','audio/wav','audio/x-wav','audio/ogg','audio/webm','audio/mp4','audio/x-m4a'];if(!allowed.includes(file.type))throw new ApiError('Choose an MP3, WAV, OGG, M4A or WebM audio file.');
 const usage=await db().prepare('SELECT COALESCE(SUM(size),0) AS total FROM files WHERE owner=?').bind(user).first<{total:number}>();if((usage?.total||0)+file.size>100*1024*1024)throw new ApiError('Your audio storage is full. Remove an older recording first.');
 const id=crypto.randomUUID();await env.BUCKET.put('audio/'+id,file.stream(),{httpMetadata:{contentType:file.type}});
 try{await db().prepare('INSERT INTO files(id,owner,name,mime,size,created) VALUES(?,?,?,?,?,?)').bind(id,user,file.name.slice(0,160),file.type,file.size,new Date().toISOString()).run();}catch(e){await env.BUCKET.delete('audio/'+id);throw e;}
 return Response.json({id,name:file.name},{status:201});
 }catch(e){return fail(e);}}
export async function GET(request:Request){try{const user=await owner();const id=new URL(request.url).searchParams.get('id');const file=await db().prepare('SELECT mime FROM files WHERE id=? AND owner=?').bind(id,user).first<{mime:string}>();if(!file)throw new ApiError('This recording could not be found.',404);const object=await env.BUCKET?.get('audio/'+id);if(!object)throw new ApiError('This recording is unavailable.',404);return new Response(object.body,{headers:{'Content-Type':file.mime,'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'}});}catch(e){return fail(e);}}
export async function DELETE(request:Request){try{const user=await owner(request);const id=new URL(request.url).searchParams.get('id');const f=await db().prepare('SELECT id FROM files WHERE id=? AND owner=?').bind(id,user).first();if(!f)throw new ApiError('This recording was already removed.',404);await env.BUCKET?.delete('audio/'+id);await db().prepare('DELETE FROM files WHERE id=? AND owner=?').bind(id,user).run();return Response.json({ok:true});}catch(e){return fail(e);}}
