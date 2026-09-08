import asyncio,json,os,sys,tempfile,unittest
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

class AgentProtocolTests(unittest.TestCase):
 def test_stdio_discovery_and_skill_application(self):
  async def check():
   with tempfile.TemporaryDirectory() as d:
    root=Path(__file__).resolve().parents[1]
    task=json.loads((root/'worker/example-task.json').read_text())
    task['skills']=[{'id':'test-story','name':'Test story','tags':'story','enabled':True,'version':3,'instructions':'Use a complete ending.'}]
    task['project'].update(autoSkills=True,style='story',sourceType='script',source='A finished story.',scenes=[])
    (Path(d)/'task.json').write_text(json.dumps(task))
    params=StdioServerParameters(command=sys.executable,args=[str(root/'worker/agent_server.py')],env={**os.environ,'CLIPFORGE_TASKS_DIR':d})
    async with stdio_client(params) as (read,write):
     async with ClientSession(read,write) as session:
      await session.initialize()
      names={t.name for t in (await session.list_tools()).tools}
      self.assertTrue({'discover_skills','write_script','list_local_models','list_tasks'}<=names)
      result=await session.call_tool('discover_skills',{'task_name':'task.json'})
      self.assertFalse(result.isError)
      self.assertIn('Use a complete ending',str(result))
      generated=await session.call_tool('write_script',{'task_name':'task.json'})
      self.assertFalse(generated.isError)
      self.assertIn('A finished story',str(generated))
      invalid=await session.call_tool('discover_skills',{'task_name':'../private.json'})
      self.assertTrue(invalid.isError)
  asyncio.run(check())
