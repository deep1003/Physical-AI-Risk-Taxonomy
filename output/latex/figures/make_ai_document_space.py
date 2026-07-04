import csv, os, re, statistics, random
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
random.seed(7)
BASE="/sessions/eloquent-affectionate-heisenberg/mnt/data3"
FIG=BASE+"/Physical-AI-Risk-Taxonomy/output/latex/figures"
coordf=BASE+"/ai_knowledge_ecosystem_codex/25_m3_cross_domain_gap_v3/02_data_outputs/m3_reference_l3_common_2d_coordinates_v3.csv"
actf=BASE+"/ai_knowledge_ecosystem_codex/17_l3_activation_measurement/02_data_outputs/all_domains_document_l3_activation.csv"

def norm(s): return re.sub(r'\s+',' ',(s or '').strip().lower())
# L3 label -> (x,y); also L2 centroid fallback
c_l3={}; l2pts={}
for r in csv.DictReader(open(coordf,encoding='utf-8',errors='ignore')):
    try:x=float(r['x']);y=float(r['y'])
    except:continue
    lab=norm(r['l3_label_draft']); c_l3.setdefault(lab,(x,y))
    l2pts.setdefault(norm(r['l3_final_l2']),[]).append((x,y))
c_l2={k:(statistics.fmean([p[0] for p in v]),statistics.fmean([p[1] for p in v])) for k,v in l2pts.items()}

PAI=re.compile(r'robot|physical ai|embodied|autonom|drone|uav|humanoid|manipulat|navigat|cyber-?physical|\bcps\b|actuator|\bslam\b|digital twin|self-driving|vehicle|locomotion|industrial automation|smart factory|smart manufactur|sensor fusion|motion planning|teleoperat|quadruped|legged')
RISK=re.compile(r'risk|safety|safe\b|hazard|fail|unsafe|security|attack|adversar|accident|harm|threat|vulnerab|collision|robust|jailbreak|misuse|liabilit')

xs_all=[];ys_all=[]; xs_p=[];ys_p=[]; xs_r=[];ys_r=[]
n=0;miss=0
for r in csv.DictReader(open(actf,encoding='utf-8',errors='ignore')):
    lab=norm(r.get('l3_label')); code=norm(r.get('l3_code'))
    xy=c_l3.get(lab) or c_l3.get(code) or c_l2.get(norm(r.get('l2_label')))
    if not xy: miss+=1; continue
    x=xy[0]+random.gauss(0,0.18); y=xy[1]+random.gauss(0,0.18)
    text=' '.join(norm(r.get(k)) for k in ('l1_label','l2_label','l3_label','title','title_en'))
    is_p=bool(PAI.search(text)); is_r=is_p and bool(RISK.search(text))
    if is_r: xs_r.append(x);ys_r.append(y)
    elif is_p: xs_p.append(x);ys_p.append(y)
    else: xs_all.append(x);ys_all.append(y)
    n+=1
print("plotted",n,"docs; missing-coord",miss,"| PAI",len(xs_p)+len(xs_r),"| PAI-Risk",len(xs_r))

fig,ax=plt.subplots(figsize=(7.6,6.4))
ax.scatter(xs_all,ys_all,s=2,c='#c9ced6',alpha=0.35,edgecolors='none',label=f'All AI documents ({len(xs_all):,})',rasterized=True)
ax.scatter(xs_p,ys_p,s=5,c='#e08214',alpha=0.7,edgecolors='none',label=f'Physical AI ({len(xs_p)+len(xs_r):,})',rasterized=True)
ax.scatter(xs_r,ys_r,s=7,c='#b2182b',alpha=0.85,edgecolors='none',label=f'Physical AI Risk ({len(xs_r):,})',rasterized=True)
ax.set_xticks([]);ax.set_yticks([])
ax.set_title('AI knowledge space: 2D projection of %s documents\n(node = document; Physical AI and Physical AI Risk highlighted)'%f"{n:,}",fontsize=10.5)
ax.legend(frameon=False,fontsize=9,loc='upper left',markerscale=2.4)
for s in ('top','right','bottom','left'):ax.spines[s].set_visible(False)
for ext in ('pdf','png','jpg'):
    fig.savefig(f"{FIG}/fig_ai_document_space.{ext}",dpi=600,bbox_inches='tight',facecolor='white')
print("saved fig_ai_document_space (pdf/png/jpg @600dpi)")
