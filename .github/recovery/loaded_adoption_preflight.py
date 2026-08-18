#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, subprocess, time

def run(argv,timeout=15):
    try:
        p=subprocess.run(argv,text=True,capture_output=True,timeout=timeout,check=False)
        return {'rc':p.returncode,'out':p.stdout.strip()[-6000:],'err':p.stderr.strip()[-3000:]}
    except Exception as e:return {'error':f'{type(e).__name__}: {e}'}

def emit(name,value):print(name+'='+json.dumps(value,sort_keys=True,default=str),flush=True)

p=pathlib.Path('/home/evan/.local/share/live/daemon_manager/supervisor/selected_world_adoption.json')
try:x=json.loads(p.read_text())
except Exception as e:x={'read_error':f'{type(e).__name__}: {e}'}
emit('ADOPTION_CURRENT',x)
emit('SERVICE_CURRENT',{'show':run(['systemctl','--user','show','daemon_manager.service','--property=ActiveState','--property=SubState','--property=MainPID','--property=ExecMainStartTimestampMonotonic']),'status':run(['systemctl','--user','status','daemon_manager.service','--no-pager','--lines=25']),'journal':run(['journalctl','--user-unit','daemon_manager.service','--no-pager','-n','40']) ,'observed_at_s':time.time()})
