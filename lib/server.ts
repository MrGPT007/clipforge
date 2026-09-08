import { env } from 'cloudflare:workers';
import { headers } from 'next/headers';
import { defaultSkills, defaultModels, type Skill, type Model } from './core';
export class ApiError extends Error { constructor(message:string,public status=400){super(message);} }
export function db(){if(!env.DB)throw new ApiError('Your saved work is temporarily unavailable. Please try again.',503);return env.DB;}
export async function owner(request?:Request){
 const h=await headers();const id=h.get('oai-authenticated-user-id');
 if(!id)throw new ApiError('Please sign in to open your studio.',401);
 if(request&&request.method!=='GET'){const origin=request.headers.get('origin');if(origin&&origin!==new URL(request.url).origin)throw new ApiError('Please make this change from your studio.',403);}
 return id;
}
export async function rows(user:string,kind:string){const r=await db().prepare('SELECT id,body,revision,updated FROM records WHERE owner=? AND kind=? ORDER BY updated DESC LIMIT 300').bind(user,kind).all<{id:string,body:string,revision:number,updated:string}>();return r.results.map(r=>({...JSON.parse(r.body),id:r.id.slice((user+':'+kind+':').length),revision:r.revision,updated:r.updated}));}
export async function skillsFor(user:string):Promise<Skill[]>{const custom=await rows(user,'skill');return [...defaultSkills.filter(s=>!custom.some(c=>c.id===s.id)),...custom];}
export async function modelsFor(user:string):Promise<Model[]>{const custom=await rows(user,'model');return [...defaultModels.filter(s=>!custom.some(c=>c.id===s.id)),...custom];}
export function fail(e:unknown){if(e instanceof ApiError)return Response.json({error:e.message},{status:e.status});console.error('ClipForge request failed',e instanceof Error?e.message:'Unknown error');return Response.json({error:'This could not be completed. Your edits are still here; please try again.'},{status:500});}
export async function body(request:Request){const text=await request.text();if(text.length>100000)throw new ApiError('This is too much text. Please shorten it.',413);try{return JSON.parse(text);}catch{throw new ApiError('The saved details could not be read. Please try again.');}}
