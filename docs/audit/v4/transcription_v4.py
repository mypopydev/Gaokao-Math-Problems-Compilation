#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'tmp/audit/v4'; REG=Path('/Users/barryjzhao/Sources/AI/gaokaomath/普通高考'); SPR=Path('/Users/barryjzhao/Sources/AI/gaokaomath/春季高考')
KEY=re.compile(r'参考答案|答案与评分|评分标准|答案解析|解答\s*$',re.S); ITEM=re.compile(r'(?:\(?\d{1,2}[.．、)）]|（\d{1,2}）)')
def map_pdf(y,stem):
 if stem=='shanghai_spring': base,names=SPR,(f'{y}春季上海.pdf',f'{y}上海春季.pdf')
 elif stem=='shanghai_liberal': base,names=REG,(f'{y}上海文.pdf',f'{y}上海试点教材文.pdf')
 elif stem=='shanghai_science': base,names=REG,(f'{y}上海理.pdf',f'{y}上海试点教材理.pdf')
 else: base,names=REG,(f'{y}上海.pdf',)
 for n in names:
  p=base/str(y)/n
  if p.exists():return p
def main():
 rows=[json.loads(x) for x in open(OUT/'problems.jsonl') if x.strip()]; group=defaultdict(list)
 for r in rows:group[(r['year'],r['stem'])].append(r)
 out=[]
 for (y,stem),rs in sorted(group.items()):
  p=map_pdf(y,stem); rec={'year':y,'stem':stem,'pdf':str(p) if p else None,'our_count':len(rs),'text_pdf':False,'coverage':None,'flag':None,'upstream_count':None}
  if not p:rec['flag']='NO_UPSTREAM';out.append(rec);continue
  try:t=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,text=True,timeout=120).stdout
  except Exception:t=''
  if len(t)<80:rec['flag']='SCANNED';out.append(rec);continue
  region=t[:KEY.search(t).start()] if KEY.search(t) else t; region=re.sub(r'\s+','',region); anchors=[r['anchor'] for r in rs if r['anchor']]; hits=sum(a in region for a in anchors); rec.update(text_pdf=True,coverage=round(hits/len(anchors),3) if anchors else 1,matched=hits,sampled=len(anchors),upstream_count=len(ITEM.findall(region))); rec['flag']='LOW_COVERAGE' if rec['coverage']<.7 else None;out.append(rec)
 (OUT/'transcription.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in out)); print(json.dumps({'files':len(out),'low':sum(r['flag']=='LOW_COVERAGE' for r in out),'scanned':sum(r['flag']=='SCANNED' for r in out),'missing':sum(r['flag']=='NO_UPSTREAM' for r in out)},ensure_ascii=False))
if __name__=='__main__':main()
