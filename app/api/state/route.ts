import { owner,rows,skillsFor,modelsFor,fail } from '@/lib/server';
export async function GET(){try{const user=await owner();const [projects,skills,models]=await Promise.all([rows(user,'project'),skillsFor(user),modelsFor(user)]);return Response.json({projects,skills,models},{headers:{'Cache-Control':'no-store'}});}catch(e){return fail(e);}}
