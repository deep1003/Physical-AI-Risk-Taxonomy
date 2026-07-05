#!/usr/bin/env python3
"""Generate Technical Report data figures in a Nature-style layout (Arial, thin
spines, no in-panel titles; captions carry description). Outputs PDF/PNG/JPG."""
import csv, json, os, re
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict, Counter

DPI=600
D="/Users/deep1003/data3"
VMD="/sessions/eloquent-affectionate-heisenberg/mnt/data3"
BASE=VMD if os.path.isdir(VMD) else D
FIG=os.path.join(BASE,"Physical-AI-Risk-Taxonomy/output/latex/figures")

# ---- Nature-style rcParams ----
plt.rcParams.update({
    'font.family':'Arial','font.size':7.5,'axes.linewidth':0.6,
    'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,
    'xtick.major.width':0.6,'ytick.major.width':0.6,
    'xtick.major.size':2.5,'ytick.major.size':2.5,
    'axes.edgecolor':'#333333','axes.labelcolor':'#111111',
    'text.color':'#111111','xtick.color':'#333333','ytick.color':'#333333',
})
# muted, print-safe palette
C_PATENT,C_PAPER,C_POLICY='#5b7fa6','#6fa07a','#b5726a'
C_SYS,C_INT,C_SOC='#5b7fa6','#6fa07a','#8f7bb0'

def save(fig,name):
    for ext in ('pdf','png','jpg'):
        fig.savefig(os.path.join(FIG,f"{name}.{ext}"),dpi=DPI,bbox_inches='tight',facecolor='white')
    plt.close(fig); print("saved",name)

def strip(ax):
    for s in ('top','right'): ax.spines[s].set_visible(False)

# ---- Fig: Physical AI record volume by source family and year ----
try:
    rows=list(csv.DictReader(open(f"{BASE}/ai_knowledge_ecosystem_codex/50_physical_ai_dataset/03_audit/physical_ai_counts_by_domain_year.csv")))
    yr=defaultdict(lambda:defaultdict(int))
    for r in rows:
        try:y=int(float(r['year']))
        except:continue
        if 2010<=y<=2025: yr[r['domain']][y]+=int(float(r['records']))
    years=list(range(2010,2026))
    fig,ax=plt.subplots(figsize=(6.6,3.1)); bottom=[0]*len(years)
    for dm,lab,col in [('patent','Patents',C_PATENT),('science','Papers',C_PAPER),('policy','Policy reports',C_POLICY)]:
        v=[yr[dm].get(y,0) for y in years]
        ax.bar(years,v,bottom=bottom,color=col,edgecolor='white',linewidth=.3,label=lab)
        bottom=[b+x for b,x in zip(bottom,v)]
    ax.set_xlabel('Year'); ax.set_ylabel('Physical AI records')
    ax.legend(frameon=False,loc='upper left',handlelength=1.1)
    ax.grid(axis='y',color='#ededed',lw=.5); ax.set_axisbelow(True); strip(ax)
    save(fig,"fig_risk_trend")
except Exception as e: print("skip fig_risk_trend:",e)

# ---- Fig: AI patent taxonomy categories (not in report body; best-effort) ----
try:
    cats=list(csv.DictReader(open(f"{BASE}/webofscience_ai_global_export/bibtex/ai_policy_organized_20260619/patstat/classified/patstat_canonical_ai_taxonomy_20260622/canonical_ai_taxonomy_category_summary.csv", encoding="utf-8-sig")))
    cats=[(r['category'].replace('_',' ').title(),int(r['rows_unique_within_category'])) for r in cats][::-1]
    labels=[c for c,_ in cats]; vals=[v for _,v in cats]
    cols=[C_POLICY if 'Physical Ai' in l else C_PATENT for l in labels]
    fig,ax=plt.subplots(figsize=(6.6,4.0))
    ax.barh(range(len(labels)),vals,color=cols,edgecolor='white',linewidth=.4)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels)
    for i,v in enumerate(vals): ax.text(v+4000,i,f"{v:,}",va='center',fontsize=6.5)
    ax.set_xlabel('Unique AI patents within category'); strip(ax)
    save(fig,"fig_patent_ai_categories")
except Exception as e: print("skip fig_patent_ai_categories:",e)

# ---- Fig: taxonomy L2 + top L3 ----
try:
    def eng(s):
        m=re.search(r'\(([^)]*)\)\s*$',s); return (m.group(1) if m else s).strip()
    cr=list(csv.DictReader(open(f"{BASE}/Physical-AI-Risk-Taxonomy/data/l4_cards.csv")))
    l2=Counter(r['l2_id'] for r in cr)
    l3=Counter(f"{r['l3_id']} {eng(r['l3_name'])}" for r in cr)
    top=l3.most_common(12)[::-1]
    fig,(a1,a2)=plt.subplots(1,2,figsize=(8.6,3.6),gridspec_kw={'width_ratios':[1,1.55]})
    a1.bar(['P2\nSystem','I2\nInteraction','S2\nSocietal'],[l2['P2'],l2['I2'],l2['S2']],color=[C_SYS,C_INT,C_SOC],edgecolor='white',linewidth=.5)
    for i,v in enumerate([l2['P2'],l2['I2'],l2['S2']]): a1.text(i,v+1.5,str(v),ha='center',fontweight='bold',fontsize=8)
    a1.set_ylim(0,130); a1.set_ylabel('L4 cards'); strip(a1)
    a1.text(-0.18,1.02,'a',transform=a1.transAxes,fontsize=10,fontweight='bold')
    lab=[k for k,_ in top]; c=[v for _,v in top]
    lc=lambda k:C_SYS if k[0]=='P' else C_INT if k[0]=='I' else C_SOC
    a2.barh(range(len(lab)),c,color=[lc(k) for k in lab],edgecolor='white',linewidth=.4)
    a2.set_yticks(range(len(lab))); a2.set_yticklabels(lab)
    for i,v in enumerate(c): a2.text(v+0.4,i,str(v),va='center',fontsize=7)
    a2.set_xlabel('L4 cards'); strip(a2)
    a2.text(-0.02,1.02,'b',transform=a2.transAxes,fontsize=10,fontweight='bold')
    save(fig,"fig_taxonomy_levels")
except Exception as e: print("skip fig_taxonomy_levels:",e)

# ---- Fig: AI risk topic space (UMAP; best-effort) ----
try:
    pl=json.load(open(f"{BASE}/AI_Topic_Space.github.io/data/interactive_l1_l2_l3_payload.json"))
    nodes=pl['nodes']
    dcol={'Policy':C_POLICY,'Science':C_PATENT,'Technology':C_PAPER}
    fig,ax=plt.subplots(figsize=(6.4,5.3))
    for dm in ['Science','Technology','Policy']:
        xs=[n['x'] for n in nodes if n.get('domain')==dm and n.get('x') is not None]
        ys=[n['y'] for n in nodes if n.get('domain')==dm and n.get('y') is not None]
        ax.scatter(xs,ys,s=5,c=dcol[dm],alpha=0.55,edgecolors='none',label=f"{dm} ({len(xs)})")
    ax.set_xticks([]); ax.set_yticks([])
    ax.legend(frameon=False,loc='upper right',markerscale=2)
    for s in ('top','right','bottom','left'):ax.spines[s].set_visible(False)
    save(fig,"fig_risk_space")
except Exception as e: print("skip fig_risk_space:",e)

print("DONE ->",FIG)
