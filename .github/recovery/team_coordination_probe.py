#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, json, pathlib, re, subprocess, sys, time, urllib.request
COORD='TEAM-COORD-20260817T2220CT-V1'
for path in ('/home/evan/Projects/static_and_singular/internal_sub_projects/ecr_email/src','/home/evan/Projects/worlds/v1/cognilode/internal_sub_projects/autonomy_core/internal_sub_projects/employee/src','/home/evan/Projects/static_and_singular/internal_sub_projects/contracts_commands_and_tools/src','/home/evan/Projects/static_and_singular/internal_sub_projects/secretary/src','/home/evan/Projects/static_and_singular/internal_sub_projects/persona_sot/src','/home/evan/Projects/static_and_singular/src'):
    if path not in sys.path: sys.path.insert(0,path)
def emit(n,v): print(n+'='+json.dumps(v,sort_keys=True,default=str),flush=True)
def short(t,n=220): return ' '.join(str(t or '').split())[:n]
endpoint_personas={}
try:
    from persona_sot import list_invokable_personas, conversations
    for persona in list_invokable_personas():
        try: eps=conversations(persona,include_historical=False)
        except Exception: continue
        for ep in eps:
            u=str(getattr(ep,'url','') or '')
            if u: endpoint_personas.setdefault(hashlib.sha256(u.encode()).hexdigest(),[]).append(persona)
except Exception as exc: emit('PERSONA_SOT_ERROR',{'error':f'{type(exc).__name__}: {exc}'})
summary={'total_pages':0,'conversation_pages':0,'generating_pages':0,'coordination_pages':0,'signin_pages':0}
participants=[]; participant_personas=set()
try:
    import websocket
    with urllib.request.urlopen('http://127.0.0.1:9331/json/list',timeout=3) as response: pages=json.load(response)
    for page in pages:
        if page.get('type')!='page' or not page.get('webSocketDebuggerUrl'): continue
        summary['total_pages']+=1
        try:
            ws=websocket.create_connection(page['webSocketDebuggerUrl'],timeout=3,suppress_origin=True)
            expr="""JSON.stringify({t:document.title,u:location.href,g:!!document.querySelector('button[data-testid=\"stop-button\"],button[aria-label*=\"Stop\" i]'),m:Array.from(document.querySelectorAll('[data-message-author-role]')).map((e,i)=>({i,r:e.getAttribute('data-message-author-role'),id:e.getAttribute('data-message-id')||e.id||'',t:(e.innerText||'').trim()})).filter(x=>x.t),b:(document.body.innerText||'').slice(-1600)})"""
            ws.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':expr,'returnByValue':True}})); raw=None
            for _ in range(20):
                msg=json.loads(ws.recv())
                if msg.get('id')==1: raw=msg; break
            value=json.loads(((((raw or {}).get('result') or {}).get('result') or {}).get('value')) or '{}')
            messages=value.get('m') if isinstance(value.get('m'),list) else []
            coord=any(COORD in str(x.get('t') or '') for x in messages)
            generating=bool(value.get('g')); url=str(value.get('u') or ''); title=str(value.get('t') or '')
            if '/c/' in url: summary['conversation_pages']+=1
            if generating: summary['generating_pages']+=1
            if coord: summary['coordination_pages']+=1
            if 'accounts.google.com' in url or 'Sign in with Google' in str(value.get('b') or ''): summary['signin_pages']+=1
            if not (generating or coord): ws.close(); continue
            shot=''
            try:
                ws.send(json.dumps({'id':2,'method':'Page.captureScreenshot','params':{'format':'png','fromSurface':True}}))
                for _ in range(20):
                    msg=json.loads(ws.recv())
                    if msg.get('id')==2:
                        data=str((msg.get('result') or {}).get('data') or '')
                        if data: shot=hashlib.sha256(base64.b64decode(data)).hexdigest()
                        break
            except Exception: pass
            ws.close()
            last_user=next((x for x in reversed(messages) if x.get('r')=='user'),{})
            last_assistant=next((x for x in reversed(messages) if x.get('r')=='assistant'),{})
            ush=hashlib.sha256(url.encode()).hexdigest(); personas=sorted(set(endpoint_personas.get(ush,[]))); participant_personas.update(personas)
            participants.append({'page_id':page.get('id'),'title':title,'url_sha256':ush,'persona_ids':personas,'generating':generating,'coordination_visible':coord,'message_count':len(messages),'last_user_id':last_user.get('id'),'last_user_sha256':hashlib.sha256(str(last_user.get('t') or '').encode()).hexdigest() if last_user else None,'last_user_excerpt':short(last_user.get('t')),'last_assistant_id':last_assistant.get('id'),'last_assistant_sha256':hashlib.sha256(str(last_assistant.get('t') or '').encode()).hexdigest() if last_assistant else None,'last_assistant_excerpt':short(last_assistant.get('t')),'screenshot_sha256':shot,'screen_tail_excerpt':short(value.get('b'),300)})
        except Exception as exc: participants.append({'page_id':page.get('id'),'error':f'{type(exc).__name__}: {exc}'})
except Exception as exc: participants=[{'error':f'{type(exc).__name__}: {exc}'}]
emit('PROTECTED_BROWSER_SUMMARY',summary); emit('CURRENT_PROVIDER_PARTICIPANTS',participants)
# Read HOP presentation for non-protected/current human-browser evidence; presentation remains non-authoritative.
try:
    with urllib.request.urlopen('http://127.0.0.1:8765/evidence-neighborhood',timeout=5) as response: raw=response.read()
    text=re.sub(r'<[^>]+>',' ',raw.decode('utf-8','replace')); text=' '.join(text.split())
    chunks=[]
    for needle in ('generating=True','TEAM-COORD-20260817T2220CT-V1','In-turn:'):
        start=0
        while True:
            i=text.find(needle,start)
            if i<0: break
            chunks.append(text[max(0,i-180):i+360]); start=i+len(needle)
    emit('EVIDENCE_NEIGHBORHOOD_COORDINATION_VIEW',{'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'excerpts':chunks[:12]})
except Exception as exc: emit('EVIDENCE_NEIGHBORHOOD_COORDINATION_VIEW',{'error':f'{type(exc).__name__}: {exc}'})
# Only coordination-related/live custody.
root=pathlib.Path('/home/evan/.local/share/live/worlds/v1/cognilode/universe/employee_runtime/activation_requests'); rows=[]
for p in sorted(root.glob('employee_*.json')):
    try: x=json.loads(p.read_text())
    except Exception: continue
    if not isinstance(x,dict): continue
    persona=str(x.get('persona_id') or ''); corr=str(x.get('correlation_id') or '')
    if not (persona in participant_personas or COORD in corr or corr.startswith('coord-20260817-') or bool(x.get('response_started'))): continue
    rows.append({k:x.get(k) for k in ('persona_id','request_id','correlation_id','semantic_sender','state','attempts','submission_observed','response_started','transport_status','transport_attempt_state','last_error','next_attempt_at_s')})
emit('PARTICIPANT_CUSTODY',rows)
# Coordination-only ECR admission.
try:
    from ecr_email.daemon import _domain_root
    from ecr_email.poll import poll_all_once
    from ecr_email.material_delegation import stage_and_delegate
    root=_domain_root(); polled=poll_all_once(root=root,persist=True,limit=100); material=dict(polled.get('material_watch') or {}); emitted=[dict(v) for v in material.get('emitted') or () if isinstance(v,dict)]; delegated=stage_and_delegate(emitted,root=root)
    matched=[]
    for row in emitted:
        if COORD in json.dumps(row,sort_keys=True,default=str): matched.append({k:row.get(k) for k in ('event_id','message_id','thread_id','correlation_id','recipient','sender','priority','action_requested','state')})
    emit('ECR_COORDINATION',{'new_count':polled.get('new_count'),'inbox_new_count':(polled.get('inbox') or {}).get('new_count'),'sent_new_count':(polled.get('sent') or {}).get('new_count'),'material_emitted_count':len(emitted),'matched':matched,'delegation_status':delegated.get('status'),'delegation_state':delegated.get('state'),'delegated_count':delegated.get('delegated_count'),'pending_count':delegated.get('pending_count')})
except Exception as exc: emit('ECR_COORDINATION',{'error':f'{type(exc).__name__}: {exc}'})
try:
    from employee_runtime.daemon import poll_once
    value=poll_once(repo_root='/home/evan/Projects/worlds/v1/cognilode/internal_sub_projects/autonomy_core/internal_sub_projects/employee',daemon_name='employee_runtime-team-coordination')
    emit('EMPLOYEE_COORDINATION_POLL',{k:value.get(k) for k in ('status','activation_attempted_count','activation_succeeded_count','activation_failed_count','deferred_comms_triggered_count','deferred_comms_waiting_count')})
except Exception as exc: emit('EMPLOYEE_COORDINATION_POLL',{'error':f'{type(exc).__name__}: {exc}'})
