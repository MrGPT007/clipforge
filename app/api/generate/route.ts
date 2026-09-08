import {cloudBase,checkTask} from '@/lib/providers';
import { z } from 'zod';
import { owner,skillsFor,modelsFor,body,fail,ApiError } from '@/lib/server';
import { ProjectSchema,chooseSkills,generationMessages,parseScenes } from '@/lib/core';
export async function POST(request:Request){try{
 const user=await owner(request);const data=z.object({project:ProjectSchema,key:z.string().min(1).max(500)}).safeParse(await body(request));if(!data.success)throw new ApiError('Add your writing-service key and a story first.');
 const {project,key}=data.data;if(!project.source.trim())throw new ApiError('Add a story or idea first.');
 const models=await modelsFor(user);const model=models.find(m=>m.id===project.modelId);if(!model||model.provider==='local')throw new ApiError('For a model on your computer, download the task and run the local maker. Or choose an online writing service.');
 checkTask(model,'script');
 const skills=chooseSkills(await skillsFor(user),project);const endpoints={openrouter:'https://openrouter.ai/api/v1/chat/completions',groq:'https://api.groq.com/openai/v1/chat/completions'};
 const upstream=await fetch(cloudBase(model)+'/chat/completions',{method:'POST',redirect:'error',headers:{Authorization:`Bearer ${key}`,'Content-Type':'application/json'},body:JSON.stringify({model:model.model,messages:generationMessages(project.source,project.style,project.duration,skills),temperature:0.6,max_tokens:3000,response_format:{type:'json_object'}}),signal:AbortSignal.timeout(60000)});
 if(!upstream.ok)throw new ApiError(upstream.status===401?'Your writing-service key was not accepted. Check it and try again.':upstream.status===429?'Your writing service is busy or out of credit. Try later or choose another service.':'Your writing service could not make this script. Check the model name and try again.',502);
 const result=await upstream.json() as {choices?:{message?:{content?:string}}[]};let scenes;try{scenes=parseScenes(result.choices?.[0]?.message?.content||'');}catch{throw new ApiError('The writing service returned an incomplete script. Try again; the current script has been kept.',502);}
 return Response.json({scenes,skillSnapshot:skills,model:model.name},{headers:{'Cache-Control':'no-store'}});
 }catch(e){return fail(e);}}
