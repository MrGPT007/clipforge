import { z } from 'zod';
import { owner,db,body,fail,ApiError } from '@/lib/server';
import { SkillSchema,ModelSchema,ProjectSchema } from '@/lib/core';
const input=z.object({id:z.string().regex(/^[a-zA-Z0-9_-]{1,100}$/),kind:z.enum(['project','skill','model']),revision:z.number().int().min(0).optional(),value:z.unknown()});
export async function POST(request:Request){try{
 const user=await owner(request);const raw=input.safeParse(await body(request));if(!raw.success)throw new ApiError('Some details are missing. Check your entries.');
 const p=raw.data;const schema=p.kind==='project'?ProjectSchema:p.kind==='skill'?SkillSchema:ModelSchema;const parsed=schema.safeParse(p.value);if(!parsed.success)throw new ApiError('Check the text length and required fields before saving.');
 const key=user+':'+p.kind+':'+p.id;const now=new Date().toISOString();const existing=await db().prepare('SELECT revision FROM records WHERE id=? AND owner=?').bind(key,user).first<{revision:number}>();
 if(existing){if(p.revision!==existing.revision)throw new ApiError('This was changed in another window. Reload it before saving again.',409);
 const result=await db().prepare('UPDATE records SET body=?,revision=revision+1,updated=? WHERE id=? AND owner=? AND revision=? RETURNING revision').bind(JSON.stringify(parsed.data),now,key,user,p.revision).first<{revision:number}>();if(!result)throw new ApiError('This changed while saving. Reload it and try again.',409);
 return Response.json({...parsed.data,id:p.id,revision:result.revision,updated:now});}
 const count=await db().prepare('SELECT COUNT(*) AS n FROM records WHERE owner=? AND kind=?').bind(user,p.kind).first<{n:number}>();if((count?.n||0)>=250)throw new ApiError('This workspace has reached its 250-item limit. Remove an older item first.');
 await db().prepare('INSERT INTO records(id,owner,kind,body,revision,updated) VALUES(?,?,?,?,1,?)').bind(key,user,p.kind,JSON.stringify(parsed.data),now).run();
 return Response.json({...parsed.data,id:p.id,revision:1,updated:now},{status:201});
 }catch(e){return fail(e);}}
export async function DELETE(request:Request){try{const user=await owner(request);const p=z.object({id:z.string().max(100),kind:z.enum(['project','skill','model']),revision:z.number().int()}).parse(await body(request));const r=await db().prepare('DELETE FROM records WHERE id=? AND owner=? AND revision=? RETURNING id').bind(user+':'+p.kind+':'+p.id,user,p.revision).first();if(!r)throw new ApiError('This item changed. Reload the page before removing it.',409);return Response.json({ok:true});}catch(e){return fail(e);}}
