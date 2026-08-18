#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, pathlib, sys, time, urllib.request

COORD='TEAM-COORD-20260817T2220CT-V1'
for path in (
'/home/evan/Projects/static_and_singular/internal_sub_projects/ecr_email/src',
'/home/evan/Projects/worlds/v1/cognilode/internal_sub_projects/autonomy_core/internal_sub_projects/employee/src',
'/home/evan/Projects/static_and_singular/internal_sub_projects/contracts_commands_and_tools/src',
'/home/evan/Projects/static_and_singular/internal_sub_projects/secretary/src',
'/home/evan/Projects/static_and_singular/internal_sub_projects/persona_sot/src',
'/home/evan/Projects/static_and_singular/src',
):
    if path not in sys.path: sys.path.insert(0,path)

def emit(name,value):print(name+'='+json.dumps(value,sort_keys=True,default=str),flush=True)

# Coordination-only ECR admission. No business, repair, data, or runtime mutation.
try:
    from ecr_email.daemon import _domain_root
    from ecr_email.poll import poll_all_once
    from ecr_email.material_delegation import stage_and_delegate
    root=_domain_root(); polled=poll_all_once(root=root,persist=True,limit=100)
    material=dict(polled.get('material_watch') or {})
    emitted=[dict(v) for v in material.get('emitted') or () if isinstance(v,dict)]
    delegated=stage_and_delegate(emitted,root=root)
    matched=[]
    for row in emitted:
        blob=json.dumps(row,sort_keys=True,default=str)
        if COORD in blob:
            matched.append({k:row.get(k) for k in ('event_id','message_id','thread_id','correlation_id','recipient','sender','priority','action_requested','state')})
    emit('ECR_COORDINATION',{'new_count':polled.get('new_count'),'inbox_new_count':(polled.get('inbox') or {}).get('new_count'),'sent_new_count':(polled.get('sent') or {}).get('new_count'),'material_emitted_count':len(emitted),'matched':matched,'delegation_status':delegated.get('status'),'delegation_state':delegated.get('state'),'delegated_count':delegated.get('delegated_count'),'pending_count':delegated.get('pending_count')})
except Exception as exc:emit('ECR_COORDINATION',{'error':f'{type(exc).__name__}: {exc}'})

# Read all current activation custody so the facilitator can include every in-turn agent.
root=pathlib.Path('/home/evan/.local/share/live/worlds/v1/cognilode/universe/employee_runtime/activation_requests')
rows=[]
for p in sorted(root.glob('employee_*.json')):
    try:x=json.loads(p.read_text())
    except Exception:continue
    if not isinstance(x,dict):continue
    if x.get('state') in {'completed','cancelled','failed','superseded'} and not x.get('response_started'):continue
    rows.append({k:x.get(k) for k in ('persona_id','request_id','correlation_id','semantic_sender','state','attempts','submission_observed','response_started','transport_status','transport_attempt_state','last_error','next_attempt_at_s')})
emit('ACTIVE_CUSTODY',rows)

# Read live protected provider pages without changing them.
try:
    import websocket
    with urllib.request.urlopen('http://127.0.0.1:9331/json/list',timeout=3) as response:pages=json.load(response)
    live=[]
    for page in pages:
        if page.get('type')!='page' or not page.get('webSocketDebuggerUrl'):continue
        try:
            ws=websocket.create_connection(page['webSocketDebuggerUrl'],timeout=3,suppress_origin=True)
            expr="""JSON.stringify({t:document.title,u:location.href,g:!!document.querySelector('button[data-testid=\"stop-button\"],button[aria-label*=\"Stop\" i]'),m:Array.from(document.querySelectorAll('[data-message-author-role]')).map((e,i)=>({i,r:e.getAttribute('data-message-author-role'),id:e.getAttribute('data-message-id')||e.id||'',t:(e.innerText||'').trim()})).filter(x=>x.t)})"""
            ws.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':expr,'returnByValue':True}}));raw=None
            for _ in range(20):
                msg=json.loads(ws.recv())
                if msg.get('id')==1:raw=msg;break
            ws.close(); value=json.loads(((((raw or {}).get('result') or {}).get('result') or {}).get('value')) or '{}')
            messages=value.get('m') if isinstance(value.get('m'),list) else []
            last_user=next((x for x in reversed(messages) if x.get('r')=='user'),{})
            last_assistant=next((x for x in reversed(messages) if x.get('r')=='assistant'),{})
            live.append({'page_id':page.get('id'),'title':value.get('t'),'url_sha256':hashlib.sha256(str(value.get('u') or '').encode()).hexdigest(),'generating':bool(value.get('g')),'message_count':len(messages),'last_user_id':last_user.get('id'),'last_user_sha256':hashlib.sha256(str(last_user.get('t') or '').encode()).hexdigest() if last_user else None,'last_assistant_id':last_assistant.get('id'),'last_assistant_sha256':hashlib.sha256(str(last_assistant.get('t') or '').encode()).hexdigest() if last_assistant else None,'coordination_visible':any(COORD in str(x.get('t') or '') for x in messages)})
        except Exception as exc:live.append({'page_id':page.get('id'),'error':f'{type(exc).__name__}: {exc}'})
    emit('LIVE_PROVIDER_PAGES',live)
except Exception as exc:emit('LIVE_PROVIDER_PAGES',{'error':f'{type(exc).__name__}: {exc}'})

try:
    from employee_runtime.daemon import poll_once
    value=poll_once(repo_root='/home/evan/Projects/worlds/v1/cognilode/internal_sub_projects/autonomy_core/internal_sub_projects/employee',daemon_name='employee_runtime-team-coordination')
    emit('EMPLOYEE_COORDINATION_POLL',{k:value.get(k) for k in ('status','activation_attempted_count','activation_succeeded_count','activation_failed_count','deferred_comms_triggered_count','deferred_comms_waiting_count')})
except Exception as exc:emit('EMPLOYEE_COORDINATION_POLL',{'error':f'{type(exc).__name__}: {exc}'})
