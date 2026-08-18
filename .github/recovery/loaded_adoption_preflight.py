#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib, importlib.metadata, json, pathlib, subprocess, time

def run(argv, timeout=12):
    try:
        p=subprocess.run(argv,text=True,capture_output=True,timeout=timeout,check=False)
        return {'rc':p.returncode,'out':p.stdout.strip()[-4000:],'err':p.stderr.strip()[-1000:]}
    except Exception as e: return {'error':f'{type(e).__name__}: {e}'}

def sha(path):
    try: return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    except Exception: return ''

def emit(name,value): print(name+'='+json.dumps(value,sort_keys=True,default=str),flush=True)

mods={}
for n in ('ecr_email','employee_runtime','human_operator_panel','daemon_manager'):
    try:
        m=importlib.import_module(n); p=str(pathlib.Path(m.__file__).resolve()); row={'file':p,'sha256':sha(p)}
        for d in (n,n.replace('_','-')):
            try: row['version']=importlib.metadata.version(d); break
            except Exception: pass
        mods[n]=row
    except Exception as e: mods[n]={'error':f'{type(e).__name__}: {e}'}
emit('LOADED_MODULES',mods)

repos=(
'/home/evan/Projects/everything',
'/home/evan/Projects/static_and_singular',
'/home/evan/Projects/static_and_singular/internal_sub_projects/daemon_manager',
'/home/evan/Projects/static_and_singular/internal_sub_projects/ecr_email',
'/home/evan/Projects/worlds/v1/cognilode/internal_sub_projects/autonomy_core/internal_sub_projects/employee',
'/home/evan/Projects/static_and_singular/internal_sub_projects/human_operator_panel',
)
rows={}
for r in repos:
    p=pathlib.Path(r); rows[r]={'exists':p.exists()}
    if not p.exists(): continue
    rows[r].update(head=run(['git','-C',r,'rev-parse','HEAD'])['out'],branch=run(['git','-C',r,'branch','--show-current'])['out'],dirty=run(['git','-C',r,'status','--porcelain'])['out'].splitlines()[:12])
emit('SOURCE_REPOS',rows)

svc=run(['systemctl','--user','show','daemon_manager.service','--property=ActiveState','--property=SubState','--property=MainPID','--property=ExecMainStartTimestampMonotonic'])
sup=run(['/home/evan/.local/share/live/worlds/v1/runtime/venv/bin/supervisorctl','-c','/home/evan/.local/share/live/daemon_manager/supervisor/supervisord.conf','status'])
emit('SERVICE',{'daemon_manager':svc,'supervisor_lines':sup.get('out','').splitlines()[:50],'venv':str(pathlib.Path('/home/evan/.local/share/live/worlds/v1/runtime/venv').resolve()),'observed_at_s':time.time()})

found=[]
for base in ('/home/evan/.local/share/live/daemon_manager','/home/evan/.local/share/live/worlds/v1'):
    for p in pathlib.Path(base).rglob('selected_world_adoption.json'):
        try:
            x=json.loads(p.read_text()); found.append({'path':str(p),'mtime_ns':p.stat().st_mtime_ns,'status':x.get('status'),'state':x.get('state'),'world_id':x.get('world_id'),'selected_fingerprint':x.get('selected_fingerprint'),'manager_reload_required':x.get('manager_reload_required'),'manager_restart_requested':x.get('manager_restart_requested'),'loaded_generation':x.get('loaded_generation'),'runtime_sync':{k:(x.get('runtime_sync') or {}).get(k) for k in ('status','world_id','all_canonical_root_consumers_pass','all_owner_python_projects_editable')}})
        except Exception as e: found.append({'path':str(p),'error':f'{type(e).__name__}: {e}'})
emit('ADOPTION_RECEIPTS',sorted(found,key=lambda x:x.get('mtime_ns',0),reverse=True)[:6])
