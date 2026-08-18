#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, subprocess, sys, time

def emit(name,value): print(name+'='+json.dumps(value,sort_keys=True,default=str),flush=True)

def compact(x):
    if not isinstance(x,dict): return {'raw_type':type(x).__name__}
    runtime=x.get('runtime_sync') if isinstance(x.get('runtime_sync'),dict) else {}
    reload=x.get('manager_reload') if isinstance(x.get('manager_reload'),dict) else {}
    resource=x.get('resource_preflight') if isinstance(x.get('resource_preflight'),dict) else {}
    return {'status':x.get('status'),'state':x.get('state'),'world_id':x.get('world_id'),'selected_fingerprint':x.get('selected_fingerprint'),'selected_commits':x.get('selected_commits'),'manager_reload_required':x.get('manager_reload_required'),'manager_restart_requested':x.get('manager_restart_requested'),'manager_reload':{k:reload.get(k) for k in ('status','unit','scope','requested_at_s','verified_at_s','main_pid_before','main_pid_after','exec_main_start_monotonic_before','exec_main_start_monotonic_after','returncode','error')},'loaded_generation':x.get('loaded_generation'),'runtime_sync':{k:runtime.get(k) for k in ('status','world_id','selected_fingerprint','all_canonical_root_consumers_pass','all_owner_python_projects_editable','owner_project_count','editable_project_count','reconciled_at_s')},'resource_preflight':{k:resource.get(k) for k in ('status','admitted','reasons')}}

roots=[]
for base in ('/home/evan/.local/share/live/daemon_manager','/home/evan/.local/share/live/worlds/v1'):
    for p in pathlib.Path(base).rglob('selected_world_adoption.json'):
        roots.append(p)
roots=sorted(roots,key=lambda p:p.stat().st_mtime_ns,reverse=True)
state_root=roots[0].parent if roots else pathlib.Path('/home/evan/.local/share/live/daemon_manager/supervisor')
before={}
if roots:
    try: before=json.loads(roots[0].read_text())
    except Exception as e: before={'read_error':f'{type(e).__name__}: {e}'}
emit('ADOPTION_TARGET',{'state_root':str(state_root),'receipt_paths':[str(p) for p in roots[:4]],'before':compact(before)})

from daemon_manager.selected_world_adoption import poll_once
first=poll_once(state_root=state_root,world_id='v1',force=True,request_manager_restart=True)
emit('ADOPTION_FORCE',compact(dict(first)))

# Let systemd complete the same-service restart, then use a fresh interpreter so
# loaded-generation evidence cannot be inherited from this process.
time.sleep(14)
code=f'''import json\nfrom daemon_manager.selected_world_adoption import poll_once\nx=poll_once(state_root={str(state_root)!r},world_id="v1",force=False,request_manager_restart=True)\nprint(json.dumps(x,sort_keys=True,default=str))'''
proc=subprocess.run([sys.executable,'-c',code],text=True,capture_output=True,timeout=120,check=False)
verify={}
try: verify=json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
except Exception as e: verify={'parse_error':f'{type(e).__name__}: {e}','stdout':proc.stdout[-4000:]}
emit('ADOPTION_VERIFY',{'process_returncode':proc.returncode,'stderr':proc.stderr[-2000:],'result':compact(verify)})
