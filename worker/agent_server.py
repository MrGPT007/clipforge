"""ClipForge MCP tools. Run from the repository root: python worker/agent_server.py.
No operating-system scheduler or shell-execution tool is exposed.
"""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from mcp.server.fastmcp import FastMCP
import maker

mcp = FastMCP('ClipForge')
ROOT = Path(os.environ.get('CLIPFORGE_TASKS_DIR', 'tasks')).resolve()
SKILLS = Path(os.environ.get('CLIPFORGE_SKILLS_DIR', 'skills')).resolve()


def task_path(name):
    path = (ROOT / name).resolve()
    if path.parent != ROOT or path.suffix != '.json':
        raise ValueError('Choose a JSON task directly inside the tasks folder.')
    return path


@mcp.tool()
def list_tasks() -> list[str]:
    """List tasks exported from the editor. Never reads arbitrary user files."""
    return sorted(p.name for p in ROOT.glob('*.json') if p.is_file())


@mcp.tool()
def discover_skills(task_name: str) -> dict:
    """Discover enabled instructions BEFORE generating a script; returns versions and text."""
    task = json.loads(task_path(task_name).read_text(encoding='utf-8'))
    maker.validate_task(task)
    skills = maker.choose_skills(task.get('skills', []) + maker.load_skills(SKILLS), task['project'])
    return {'skills': skills, 'selection': 'matching enabled skills, in priority order',
            'fallback': 'Concise source-grounded writing if no skills match.'}


@mcp.tool()
def list_local_models() -> list[str]:
    """Discover LM Studio text models at its usual local address. No key configuration needed."""
    req = Request('http://localhost:1234/v1/models')
    with urlopen(req, timeout=5) as response:
        data = json.loads(response.read(1_000_000))
    return [m['id'] for m in data['data'] if isinstance(m.get('id'), str) and 'embed' not in m['id'].lower()]


@mcp.tool()
def write_script(task_name: str, model_id: str = '') -> dict:
    """Discover and apply skills, write with the task's provider, validate and return scenes.
    Cloud generation uses CLIPFORGE_API_KEY and can spend credit. No hidden provider fallback.
    This returns a draft; it does not publish or render.
    """
    task = json.loads(task_path(task_name).read_text(encoding='utf-8'))
    maker.validate_task(task)
    skills = discover_skills(task_name)['skills']
    if model_id:
        task['model']['model'] = model_id
    if task['model']['provider'] == 'local' and task['model']['model'] == 'auto':
        models = list_local_models()
        if len(models) != 1:
            raise ValueError('Choose one of the detected LM Studio models and pass model_id.')
        task['model']['model'] = models[0]
    scenes = maker.write_script(task, skills)
    return {'scenes': scenes, 'skillSnapshot': skills, 'model': task['model']['model']}


if __name__ == '__main__':
    mcp.run(transport='stdio')
