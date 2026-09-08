import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('maker',Path(__file__).parents[1]/'worker'/'maker.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class MakerTests(unittest.TestCase):
 def setUp(self):
  self.p={'style':'story','duration':15,'source':'a horror story','autoSkills':True,'skillIds':[]}
  self.skills=[{'id':'a','name':'Story','tags':'story,horror','instructions':'Use a hook','enabled':True,'version':1},{'id':'b','name':'Other','tags':'quote','instructions':'Be brief','enabled':True,'version':1},{'id':'c','name':'Off','tags':'story,horror','instructions':'Do not use','enabled':False,'version':1}]
 def test_skill_discovery_excludes_disabled(self):
  self.assertEqual([s['id'] for s in m.choose_skills(self.skills,self.p)],['a'])
 def test_pinned_order_and_missing_skill(self):
  self.p.update(autoSkills=False,skillIds=['b','missing','a','c'])
  self.assertEqual([s['id'] for s in m.choose_skills(self.skills,self.p)],['b','a'])
 def test_prompt_reads_instructions_before_source(self):
  messages=m.messages(self.p,[self.skills[0]])
  self.assertIn('Use a hook',messages[0]['content']);self.assertEqual(messages[1]['content'],self.p['source'])
 def test_schema_rejects_missing_narration(self):
  with self.assertRaises(ValueError):m.validate_scenes([{'heading':'a'}])
 def test_ass_content_cannot_inject_override(self):
  self.assertEqual(m.ass_text('{\\pos(0,0)}'),'｛＼pos(0,0)｝')
 def test_caption_timeline_matches_audio(self):
  ass,srt=m.subtitles([{'heading':'Hello','narration':'One two three four five six seven eight nine'}],[9],'story')
  self.assertIn('0:00:08.00,0:00:09.00',ass);self.assertIn('00:00:09,000',srt)
 def test_skill_file_is_text_only(self):
  with tempfile.TemporaryDirectory() as d:
   Path(d,'custom.md').write_text('---\nname: Short story\ntags: story,fiction\nversion: 2\n---\nUse short sentences.')
   s=m.load_skills(d)[0];self.assertEqual(s['name'],'Short story');self.assertEqual(s['version'],2);self.assertEqual(s['instructions'],'Use short sentences.')
 def test_article_blocks_local(self):
  with self.assertRaises(ValueError):m.read_article('https://127.0.0.1/private')
 def test_finished_script_does_not_call_model(self):
  task={'project':dict(self.p,sourceType='script',source='Hello world.\n\nAnother scene.')}
  self.assertEqual(len(m.write_script(task,[])),2)
if __name__=='__main__':unittest.main()
