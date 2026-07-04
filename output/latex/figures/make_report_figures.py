#!/usr/bin/env python3
"""Generate Technical Report figures at 600 dpi in PDF/PNG/JPG (color).
Data-grounded: local reproducible snapshot + verified corpora + AI Topic Space payload."""
import csv, json, os, re
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict, Counter

DPI=600
D="/Users/deep1003/data3"
VMD="/sessions/eloquent-affectionate-heisenberg/mnt/data3"
BASE=VMD if os.path.isdir(VMD) else D
FIG=os.path.join(BASE,"Physical-AI-Risk-Taxonomy/output/latex/figures")
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.linewidth':0.8})

def save(fig,name):
    for ext in ('pdf','png','jpg'):
        fig.savefig(os.path.join(FIG,f"{name}.{ext}"),dpi=DPI,bbox_inches='tight',
                    facecolor='white')
    plt.close(fig); print("saved",name,"(pdf/png/jpg @600dpi)")

# ---- Fig A: risk landscape / corpus year trend (ch.2) ----
rows=list(csv.DictReader(open(f"{BASE}/ai_knowledge_ecosystem_codex/50_physical_ai_dataset/03_audit/physical_ai_counts_by_domain_year.csv")))
yr=defaultdict(lambda:defaultdict(int))
for r in rows:
    try:y=int(float(r['year']))
    except:continue
    if 2010<=y<=2025: yr[r['domain']][y]+=int(float(r['records']))
years=list(range(2010,2026))
fig,ax=plt.subplots(figsize=(7.4,3.6)); bottom=[0]*len(years)
for dm,lab,col in [('patent','Patents','#3b6fb0'),('science','Papers','#4c9a5b'),('policy','Policy reports','#c0603a')]:
    v=[yr[dm].get(y,0) for y in years]
    ax.bar(years,v,bottom=bottom,color=col,edgecolor='white',linewidth=.4,label=lab)
    bottom=[b+x for b,x in zip(bottom,v)]
ax.set_xlabel('Year'); ax.set_ylabel('Physical AI records')
ax.set_title('Physical AI record volume by source family and year\n(integrated local Physical AI set, N=383,149)',fontsize=10)
ax.legend(frameon=False,fontsize=9); ax.grid(axis='y',color='#e6e6e6',lw=.6); ax.set_axisbelow(True)
for s in ('top','right'):ax.spines[s].set_visible(False)
save(fig,"fig_risk_trend")

# ---- Fig B: AI patent taxonomy categories (ch.4) ----
cats=list(csv.DictReader(open(f"{BASE}/webofscience_ai_global_export/bibtex/ai_policy_organized_20260619/patstat/classified/patstat_canonical_ai_taxonomy_20260622/canonical_ai_taxonomy_category_summary.csv", encoding="utf-8-sig")))
cats=[(r['category'].replace('_',' ').title(),int(r['rows_unique_within_category'])) for r in cats][::-1]
labels=[c for c,_ in cats]; vals=[v for _,v in cats]
cols=['#c0603a' if 'Physical Ai' in l else '#3b6fb0' for l in labels]
fig,ax=plt.subplots(figsize=(7.4,4.6))
ax.barh(range(len(labels)),vals,color=cols,edgecolor='#333',linewidth=.4)
ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels,fontsize=8)
for i,v in enumerate(vals): ax.text(v+4000,i,f"{v:,}",va='center',fontsize=7.5)
ax.set_xlabel('Unique AI patents within category'); ax.set_title('AI patent taxonomy categories (PATSTAT AI corpus, 2,032,236)\nPhysical AI = 350,109 (highlighted)',fontsize=10)
for s in ('top','right'):ax.spines[s].set_visible(False)
save(fig,"fig_patent_ai_categories")

# ---- Fig C: taxonomy L2 + top L3 (ch.6) ----
def eng(s):
    m=re.search(r'\(([^)]*)\)\s*$',s); return (m.group(1) if m else s).strip()
cr=list(csv.DictReader(open(f"{BASE}/Physical-AI-Risk-Taxonomy/data/l4_cards.csv")))
l2=Counter(r['l2_id'] for r in cr)
l3=Counter(f"{r['l3_id']} {eng(r['l3_name'])}" for r in cr)
top=l3.most_common(12)[::-1]
fig,(a1,a2)=plt.subplots(1,2,figsize=(10,4.3),gridspec_kw={'width_ratios':[1,1.55]})
a1.bar(['P2\nSystem','I2\nInteraction','S2\nSocietal'],[l2['P2'],l2['I2'],l2['S2']],color=['#3b6fb0','#4c9a5b','#8a5aa8'],edgecolor='#333',linewidth=.5)
for i,v in enumerate([l2['P2'],l2['I2'],l2['S2']]): a1.text(i,v+1.5,str(v),ha='center',fontweight='bold',fontsize=10)
a1.set_ylim(0,130); a1.set_ylabel('L4 cards'); a1.set_title('L2 category distribution (182 L4 cards)',fontsize=10)
for s in ('top','right'):a1.spines[s].set_visible(False)
lab=[k for k,_ in top]; c=[v for _,v in top]
lc=lambda k:'#3b6fb0' if k[0]=='P' else '#4c9a5b' if k[0]=='I' else '#8a5aa8'
a2.barh(range(len(lab)),c,color=[lc(k) for k in lab],edgecolor='#333',linewidth=.4)
a2.set_yticks(range(len(lab))); a2.set_yticklabels(lab,fontsize=8)
for i,v in enumerate(c): a2.text(v+0.4,i,str(v),va='center',fontsize=8)
a2.set_xlabel('L4 cards'); a2.set_title('Top L3 sub-categories by L4 card count',fontsize=10)
for s in ('top','right'):a2.spines[s].set_visible(False)
save(fig,"fig_taxonomy_levels")

# ---- Fig D: AI risk topic space (UMAP) (ch.11) ----
pl=json.load(open(f"{BASE}/AI_Topic_Space.github.io/data/interactive_l1_l2_l3_payload.json"))
nodes=pl['nodes']
dcol={'Policy':'#c0603a','Science':'#3b6fb0','Technology':'#4c9a5b'}
fig,ax=plt.subplots(figsize=(7.2,6.0))
for dm in ['Science','Technology','Policy']:
    xs=[n['x'] for n in nodes if n.get('domain')==dm and n.get('x') is not None]
    ys=[n['y'] for n in nodes if n.get('domain')==dm and n.get('y') is not None]
    ax.scatter(xs,ys,s=6,c=dcol[dm],alpha=0.55,edgecolors='none',label=f"{dm} ({len(xs)})")
ax.set_xticks([]); ax.set_yticks([])
ax.set_title('AI risk topic space (shared UMAP embedding of L3 reference terms)\n%d L3 nodes; colour = source domain'%sum(1 for n in nodes if n.get('x') is not None),fontsize=10)
ax.legend(frameon=False,fontsize=9,loc='upper right',markerscale=2)
for s in ('top','right','bottom','left'):ax.spines[s].set_visible(False)
save(fig,"fig_risk_space")
print("ALL DONE ->",FIG)
