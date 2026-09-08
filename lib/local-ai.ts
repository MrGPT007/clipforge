import {generationMessages,parseScenes,type Model,type Project,type Skill} from './core';
export const LM_STUDIO='http://localhost:1234/v1';
export const LOCAL_VOICE='http://localhost:8880/v1';
export async function localRequest(path:string,init?:RequestInit,voice=false){
 try{const r=await fetch((voice?LOCAL_VOICE:LM_STUDIO)+path,{...init,redirect:'error',signal:AbortSignal.timeout(init?.method==='POST'?180000:5000)});if(!r.ok)throw Error(`Local service returned ${r.status}.`);return r;}
 catch{throw Error(voice?'Start your OpenAI-compatible voice server on port 8880 and allow browser access. LM Studio does not provide speech generation.':'LM Studio is not reachable. Start its server on port 1234 and allow browser access (CORS) in LM Studio. Your browser may also ask for local-network permission.');}
}
export async function localModels(){const d=await (await localRequest('/models')).json() as {data:{id:string}[]};if(!Array.isArray(d.data))throw Error('LM Studio returned an unreadable model list.');return d.data.filter((m:{id?:unknown})=>typeof m.id==='string'&&!/embed/i.test(m.id)).map((m:{id:string})=>m.id) as string[];}
export async function localGenerate(p:Project,m:Model,skills:Skill[]){let id=m.model;if(id==='auto'){const list=await localModels();if(list.length!==1)throw Error('Choose your LM Studio model in Models & voices first.');id=list[0];}const d=await (await localRequest('/chat/completions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:id,messages:generationMessages(p.source,p.style,p.duration,skills),temperature:.6,max_tokens:3000,response_format:{type:'json_object'}})})).json() as {choices?:{message?:{content?:string}}[]};return parseScenes(d.choices?.[0]?.message?.content||'');}
