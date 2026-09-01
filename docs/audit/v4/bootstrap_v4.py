#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,platform,re,subprocess
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
CONTENT=ROOT/'content'; OUT=ROOT/'tmp/audit/v4'; REPORT=ROOT/'docs/audit/v4/shanghai_accuracy_v4.md'
PROB=re.compile(r'\\begin\{problem\}(.*?)\\end\{problem\}',re.S)
ANS=re.compile(r'\\begin\{answer\}(.*?)\\end\{answer\}',re.S)
SOL=re.compile(r'\\begin\{solution\}(.*?)\\end\{solution\}',re.S)
SEC=re.compile(r'\\section\{([^}]*)\}')
CJK=re.compile(r'[一-鿿]{4,}')
def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def typ(sec):
 sub=any(x in sec for x in ('解答','证明','应用','计算')) or sec.strip()=='附加题'
 return 'subjective' if sub else 'objective' if ('填空' in sec or '选择' in sec or '单选' in sec or '多选' in sec) else 'unknown'
def parse(year,stem,p):
 s=p.read_text(); secs=[(m.start(),m.group(1)) for m in SEC.finditer(s)]; out=[]
 for i,m in enumerate(PROB.finditer(s),1):
  sec='(未分节)'
  for pos,name in secs:
   if pos<m.start(): sec=name
   else: break
  end= list(PROB.finditer(s))[i].start() if i<len(list(PROB.finditer(s))) else len(s)
  start=m.end(); a=next((x.group(1).strip() for x in ANS.finditer(s) if start<=x.start()<end),''); so=next((x.group(1).strip() for x in SOL.finditer(s) if start<=x.start()<end),'')
  out.append({'id':f'{year}/{stem}#Q{i}','year':year,'stem':stem,'qidx':i,'section':sec,'type':typ(sec),'problem_text':m.group(1).strip(),'answer_text':a,'solution_text':so,'source':str(p.relative_to(ROOT)),'anchor':(CJK.findall(m.group(1)) or [''])[0][:6]})
 return out
def main():
 OUT.mkdir(parents=True,exist_ok=True); rows=[]; files=[]
 for yd in sorted(CONTENT.iterdir()):
  if not yd.is_dir() or not yd.name.isdigit(): continue
  for p in sorted(yd.glob('shanghai*.tex')):
   r=parse(int(yd.name),p.stem,p); rows+=r; files.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'problems':len(r)})
 with (OUT/'problems.jsonl').open('w') as f:
  for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 ids=[r['id'] for r in rows]; snap={'audit':'shanghai_accuracy_v4','created_at':datetime.now(timezone.utc).isoformat(),'commit':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),'python':platform.python_version(),'files':files,'file_count':len(files),'problem_count':len(rows),'type_counts':dict(Counter(r['type'] for r in rows)),'ids_sha256':hashlib.sha256('\n'.join(ids).encode()).hexdigest(),'source_root':'/Users/barryjzhao/Sources/AI/gaokaomath','content_unchanged':True}
 (OUT/'snapshot.json').write_text(json.dumps(snap,ensure_ascii=False,indent=2)+'\n')
 REPORT.write_text(REPORT.read_text()+'\n## 基线与结构\n\n'+f"- commit: `{snap['commit']}`\n- 文件: {len(files)}\n- 题目: {len(rows)}\n- 类型: {snap['type_counts']}\n- source: `/Users/barryjzhao/Sources/AI/gaokaomath`\n- 本阶段没有修改 `content/`。\n",encoding='utf-8')
 print(json.dumps({'files':len(files),'problems':len(rows),'types':snap['type_counts'],'commit':snap['commit']},ensure_ascii=False))
if __name__=='__main__':main()
