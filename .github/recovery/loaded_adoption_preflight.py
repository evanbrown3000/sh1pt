#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, subprocess, time

def run(argv, timeout=12):
    try:
        p=subprocess.run(argv,text=True,capture_output=True,timeout=timeout,check=False)
        return {'rc':p.returncode,'out':p.stdout.strip()[-3000:],'err':p.stderr.strip()[-800:]}
    except Exception as e: return {'error':f'{type(e).__name__}: {e}'}

def emit(name,value): print(name+'='+json.dumps(value,sort_keys=True,default=str),flush=True)

repos=(
'/home/evan/Projects/static_and_singular',
'/home/evan/Projects/static_and_singular/internal_sub_projects/daemon_manager',
'/home/evan/Projects/static_and_singular/internal_sub_projects/ecr_email',
'/home/evan/Projects/worlds/v1/cognilode/internal_sub_projects/autonomy_core/internal_sub_projects/employee',
'/home/evan/Projects/static_and_singular/internal_sub_projects/human_operator_panel',
'/home/evan/Projects/static_and_singular/internal_sub_projects/shared_venv_manager',
'/home/evan/Projects/static_and_singular/internal_sub_projects/project_initializer',
)
rows={}
for r in repos:
    p=pathlib.Path(r); rows[r]={'exists':p.exists()}
    if not p.exists(): continue
    rows[r].update(head=run(['git','-C',r,'rev-parse','HEAD'])['out'],branch=run(['git','-C',r,'branch','--show-current'])['out'],origin_main=run(['git','-C',r,'rev-parse','origin/main'])['out'],dirty_count=len(run(['git','-C',r,'status','--porcelain'])['out'].splitlines()))
emit('REPOS',rows)

svc=run(['systemctl','--user','show','daemon_manager.service','--property=ActiveState','--property=SubState','--property=MainPID','--property=ExecMainStartTimestampMonotonic'])
sup=run(['/home/evan/.local/share/live/worlds/v1/runtime/venv/bin/supervisorctl','-c','/home/evan/.local/share/live/daemon_manager/supervisor/supervisord.conf','status'])
emit('SERVICE',{'daemon_manager':svc,'supervisor':sup,'observed_at_s':time.time()})

found=[]
for base in ('/home/evan/.local/share/live/daemon_manager','/home/evan/.local/share/live/worlds/v1'):
    for p in pathlib.Path(base).rglob('selected_world_adoption.json'):
        try:
            x=json.loads(p.read_text()); found.append({'path':str(p),'mtime_ns':p.stat().st_mtime_ns,'status':x.get('status'),'state':x.get('state'),'world_id':x.get('world_id'),'selected_fingerprint':x.get('selected_fingerprint'),'selected_commits':x.get('selected_commits'),'manager_reload_required':x.get('manager_reload_required'),'manager_restart_requested':x.get('manager_restart_requested'),'manager_reload':x.get('manager_reload'),'loaded_generation':x.get('loaded_generation'),'runtime_sync':x.get('runtime_sync')})
        except Exception as e: found.append({'path':str(p),'error':f'{type(e).__name__}: {e}'})
emit('ADOPTION',sorted(found,key=lambda x:x.get('mtime_ns',0),reverse=True)[:3])

loc=run(['bash','-lc',"find /home/evan/Projects /home/evan/.local/share/live/worlds/v1 -maxdepth 5 -type d -name everything -print 2>/dev/null | head -20"])
emit('EVERYTHING_LOCATIONS',loc)
