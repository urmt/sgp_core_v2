import numpy as np, pandas as pd, json, zlib, warnings
warnings.filterwarnings('ignore')
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, SVC
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score
from sklearn.model_selection import cross_val_score, LeaveOneOut
from sklearn.covariance import MinCovDet, EmpiricalCovariance
from scipy.spatial.distance import mahalanobis
from scipy.stats import pearsonr, entropy
import os

os.chdir("/home/student/sgp_core_v2")

N=4096; t=np.linspace(0,1,N)
seeds=[11,23,37,51,79,101,149,211,307,401]
TV=["replay","stitch","reverse","swap"]
domains=["chirp","rw_trend","regime_switch","chaotic_logistic","coupled_osc"]

# ===== V2_079 FROZEN METRICS =====
def ordinal_sequence(x, d=3):
    seq=[np.argsort(x[i:i+d]) for i in range(len(x)-d)]
    uniq={tuple(p):i for i,p in enumerate(sorted(set(tuple(s) for s in seq)))}
    return np.array([uniq[tuple(s)] for s in seq])
def signed_ordinal_flow(x):
    seq=ordinal_sequence(x); n=len(np.unique(seq)); P=np.zeros((n,n))
    for a,b in zip(seq[:-1],seq[1:]): P[a,b]+=1
    P+=1e-9; P/=P.sum(axis=1,keepdims=True); F=P-P.T; w=0.0
    for i in range(n):
        for j in range(n): w+=F[i,j]*(j-i)
    return w
def half_corr(x):
    h=len(x)//2; return float(np.corrcoef(x[:h],x[h:])[0,1])
def signed_compress(x):
    xf=zlib.compress(np.asarray(x,dtype=np.float32).tobytes())
    xr=zlib.compress(np.asarray(x[::-1],dtype=np.float32).tobytes())
    return len(xf)-len(xr)
def amp_transition_asymmetry(x, k=5):
    bins=np.percentile(x,np.linspace(0,100,k+1)[1:-1]); states=np.digitize(x,bins); n=k+1
    C=np.zeros((n,n))
    for i in range(len(states)-1): C[states[i],states[i+1]]+=1
    C+=1e-9; F=C/C.sum(axis=1,keepdims=True); B=C.T/C.T.sum(axis=1,keepdims=True)
    asym=0.0
    for i in range(n):
        for j in range(n): asym+=(F[i,j]-B[i,j])*(j-i)
    return asym

def make_signals(seed):
    np.random.seed(seed); t=np.linspace(0,1,N)
    sigs={}
    sigs["chirp"]=np.sin(2*np.pi*(8*t+40*t**2))
    rw=np.cumsum(np.random.randn(N))
    sigs["rw_trend"]=rw+0.002*np.arange(N)
    x=np.zeros(N); ts=np.array_split(np.arange(N),3)
    i0,i1,i2=len(ts[0]),len(ts[1]),len(ts[2])
    x[:i0]=np.random.randn(i0); x[i0:i0+i1]=3+0.3*np.random.randn(i1)
    x[i0+i1:]=np.sin(np.linspace(0,30*np.pi,i2))
    sigs["regime_switch"]=x
    r=3.99; x=np.zeros(N); x[0]=0.2
    for i in range(N-1): x[i+1]=r*x[i]*(1-x[i])
    sigs["chaotic_logistic"]=x
    sigs["coupled_osc"]=np.sin(2*np.pi*7*t)+0.5*np.sin(2*np.pi*13*t+0.2*np.sin(2*np.pi*3*t))
    return sigs

def replay(x): return np.concatenate([x[:len(x)//2],x[:len(x)//2]])
def stitch(x):
    ts=np.array_split(x,3); return np.concatenate([ts[2],ts[0],ts[1]])
def rev(x): return x[::-1]
def swap_halves(x): return np.concatenate([x[len(x)//2:],x[:len(x)//2]])
TR={"base":lambda x:x,"replay":replay,"stitch":stitch,"reverse":rev,"swap":swap_halves}
MK=["m1","m2","m3","m4"]

all_keys = MK

# === BUILD EMBEDDING DATASET ===
print("="*80)
print("PHASE 1: GROUND TRUTH — V2_079 EMBEDDINGS FROZEN")
print("="*80)

def compute_embedding(seed):
    sigs=make_signals(seed)
    rows=[]
    for domain,sx in sigs.items():
        for variant,tf in TR.items():
            y=tf(sx.copy())
            rows.append({"seed":seed,"domain":domain,"variant":variant,
                "m1":signed_ordinal_flow(y),"m2":half_corr(y),
                "m3":signed_compress(y),"m4":amp_transition_asymmetry(y)})
    return pd.DataFrame(rows)

all_rows=[]
for s in seeds:
    all_rows.append(compute_embedding(s))
df_full=pd.concat(all_rows,ignore_index=True)
print(f"Embedding dataset: {len(df_full)} samples ({len(seeds)} seeds, {len(domains)} domains, 5 variants)")

# === Standardize ===
scaler=RobustScaler()
Xn=scaler.fit_transform(df_full[MK].values)
df_n=df_full.copy()
df_n[MK]=Xn

# === METADATA ===
print("\n=== METRIC RAW STATS (all seeds pooled) ===")
raw_stats={}
for mk in MK:
    vals=df_full[mk].values
    raw_stats[mk]={"min":float(np.min(vals)),"max":float(np.max(vals)),
        "mean":float(np.mean(vals)),"std":float(np.std(vals)),
        "n_unique":len(np.unique(vals))}
    print(f"  {mk}: range=[{raw_stats[mk]['min']:.4f},{raw_stats[mk]['max']:.4f}] "
          f"mean={raw_stats[mk]['mean']:.4f} std={raw_stats[mk]['std']:.4f} "
          f"unique={raw_stats[mk]['n_unique']}")

# === DEAD METRIC CHECK per domain ===
print("\n=== DEAD METRIC CHECK (per-domain, per-seed) ===")
dead_summary={domain:{mk:0 for mk in MK} for domain in domains}
for s in seeds:
    sub=df_n[df_n.seed==s]
    for domain in domains:
        sub2=sub[sub.domain==domain]
        for mk in MK:
            if np.std(sub2[mk].values)<1e-10:
                dead_summary[domain][mk]+=1
for domain in domains:
    dead_str=" ".join(f"{mk}:{dead_summary[domain][mk]}/{len(seeds)}" for mk in MK)
    print(f"  {domain:18s} {dead_str}")

# === PHASE 2: EMBEDDING INFORMATION ANALYSIS ===
print("\n\n"+"="*80)
print("PHASE 2: EMBEDDING INFORMATION ANALYSIS")
print("="*80)

# --- 2A: PCA Decomposition ---
print("\n--- 2A: PCA DECOMPOSITION ---")
pca=PCA()
pca.fit(df_n[MK].values)
print(f"  Explained variance: {pca.explained_variance_ratio_}")
print(f"  Cumulative: {np.cumsum(pca.explained_variance_ratio_)}")
print(f"  Dim for 95%: {np.searchsorted(np.cumsum(pca.explained_variance_ratio_),0.95)+1}")
print(f"  Components:\n    {np.round(pca.components_,3)}")

# Per-domain PCA
print("\n  Per-domain PCA:")
for domain in domains:
    sub=df_n[df_n.domain==domain]
    pca_d=PCA()
    pca_d.fit(sub[MK].values)
    print(f"  {domain:18s} var={np.round(pca_d.explained_variance_ratio_,3)} "
          f"dim95={np.searchsorted(np.cumsum(pca_d.explained_variance_ratio_),0.95)+1}")

# Per-seed PCA (pooled across domains within seed)
print("\n  Per-seed PCA (all domains pooled):")
for s in seeds:
    sub=df_n[df_n.seed==s]
    pca_s=PCA()
    pca_s.fit(sub[MK].values)
    print(f"    seed {s:3d}: var={np.round(pca_s.explained_variance_ratio_,3)} "
          f"dim95={np.searchsorted(np.cumsum(pca_s.explained_variance_ratio_),0.95)+1}")

# --- 2B: Within-domain covariance spectra ---
print("\n--- 2B: WITHIN-DOMAIN COVARIANCE SPECTRA ---")
print(f"{'Domain':18s} {'Seed':5s} {'eigvals':25s} {'eff_rank':8s} {'cond':8s} {'det':10s}")
for domain in domains:
    for s in seeds:
        sub=df_n[(df_n.seed==s)&(df_n.domain==domain)]
        c=np.corrcoef(sub[MK].values.T)
        try:
            eig=np.linalg.eigvalsh(c)
            er=float(np.sum(eig)/eig[-1]) if eig[-1]>1e-12 else 0
            cn=float(eig[-1]/eig[0]) if eig[0]>1e-12 else np.inf
            det=float(np.linalg.det(c))
        except:
            eig=np.array([0]*4); er=0; cn=np.inf; det=0
        eig_str=" ".join(f"{e:.3f}" for e in eig)
        print(f"  {domain:18s} {s:5d} {eig_str:25s} {er:8.2f} {cn:8.1f} {det:10.2e}")

# --- 2C: Between vs Within Variance ---
print("\n--- 2C: BETWEEN vs WITHIN VARIANCE DECOMPOSITION ---")
for mk in MK:
    vals=df_n[mk].values
    grand_mean=np.mean(vals)
    ss_total=np.sum((vals-grand_mean)**2)
    # between-seed
    ss_between_seed=0
    for s in seeds:
        sub=df_n[df_n.seed==s]
        ss_between_seed+=len(sub)*(np.mean(sub[mk].values)-grand_mean)**2
    # between-domain within seed
    ss_between_domain=0
    for s in seeds:
        for domain in domains:
            sub=df_n[(df_n.seed==s)&(df_n.domain==domain)]
            grp_mean=np.mean(sub[mk].values)
            ss_between_domain+=len(sub)*(grp_mean-np.mean(df_n[df_n.seed==s][mk].values))**2
    # between-variant within domain-seed
    ss_between_variant=0
    for s in seeds:
        for domain in domains:
            for v in ["base"]+TV:
                sub=df_n[(df_n.seed==s)&(df_n.domain==domain)&(df_n.variant==v)]
                if len(sub)==0: continue
                grp_v=np.mean(sub[mk].values)
                d_mean=np.mean(df_n[(df_n.seed==s)&(df_n.domain==domain)][mk].values)
                ss_between_variant+=len(sub)*(grp_v-d_mean)**2
    ss_within=ss_total-ss_between_seed-ss_between_domain-ss_between_variant
    print(f"  {mk}: total_var={ss_total:.2f} "
          f"between_seed={ss_between_seed/ss_total*100:.1f}% "
          f"between_domain={ss_between_domain/ss_total*100:.1f}% "
          f"between_variant={ss_between_variant/ss_total*100:.1f}% "
          f"within={ss_within/ss_total*100:.1f}%")

# --- 2D: Metric Correlation Matrix (global) ---
print("\n--- 2D: GLOBAL METRIC CORRELATION ---")
cg=np.corrcoef(df_n[MK].values.T)
print(f"  {'':6s} {'m1':8s} {'m2':8s} {'m3':8s} {'m4':8s}")
for i,mk in enumerate(MK):
    print(f"  {mk:6s} {cg[i,0]:8.3f} {cg[i,1]:8.3f} {cg[i,2]:8.3f} {cg[i,3]:8.3f}")
# Per-domain correlation
print(f"\n  Per-domain max |r| off-diagonal:")
for domain in domains:
    sub=df_n[df_n.domain==domain]
    sub_pooled=sub.groupby("variant").mean()[MK]
    c_d=np.corrcoef(sub_pooled.values.T)
    triu=np.triu_indices_from(c_d,k=1)
    max_r=np.max(np.abs(c_d[triu]))
    print(f"  {domain:18s} max|r|={max_r:.3f}")

# --- 2E: Separability metrics ---
print("\n--- 2E: TRANSFORM SEPARABILITY ---")
print(f"\n  Transform centroids (pooled across domains + seeds):")
centroids=df_n.groupby("variant")[MK].mean()
for v in ["base"]+TV:
    row=" ".join(f"{centroids.loc[v,mk]:.3f}" for mk in MK)
    print(f"    {v:8s} {row}")

print(f"\n  Between-centroid distances (pooled centroids):")
for i,v1 in enumerate(["base"]+TV):
    for v2 in TV[i:]:
        if v1==v2: continue
        d=np.linalg.norm(centroids.loc[v1].values-centroids.loc[v2].values)
        print(f"    {v1:8s} vs {v2:8s}: {d:.3f}")

print(f"\n  Transform confusion (1-NN, LOO per seed):")
knn=KNeighborsClassifier(n_neighbors=1)
for domain in domains:
    sub=df_n[df_n.domain==domain]
    preds,trues=[],[]
    for ts in seeds:
        tr=sub[sub.seed!=ts]; te=sub[sub.seed==ts]
        knn.fit(tr[MK].values,tr.variant.values)
        preds.extend(knn.predict(te[MK].values)); trues.extend(te.variant.values)
    cm=confusion_matrix(trues,preds,labels=["base"]+TV)
    acc=accuracy_score(trues,preds)
    diag=sum(cm[i,i] for i in range(5))
    print(f"  {domain:18s} acc={acc:.3f} diag={diag}/{len(trues)}")

print(f"\n  Pooled 1-NN (across domains + LOO seeds):")
preds,trues=[],[]
for ts in seeds:
    tr=df_n[df_n.seed!=ts]; te=df_n[df_n.seed==ts]
    knn.fit(tr[MK].values,tr.variant.values)
    preds.extend(knn.predict(te[MK].values)); trues.extend(te.variant.values)
cm=confusion_matrix(trues,preds,labels=["base"]+TV)
acc=accuracy_score(trues,preds)
print(f"    acc={acc:.3f}")
print(f"    {'':10s} {'base':6s} {'replay':6s} {'stitch':6s} {'reverse':6s} {'swap':6s}")
for i,lbl in enumerate(["base"]+TV):
    print(f"    {lbl:10s} {' '.join(f'{cm[i,j]:5d}' for j in range(5))}")

# --- 2F: Linear Discriminant Analysis ---
print("\n--- 2F: LDA SEPARABILITY ---")
print(f"  One-vs-base LDA (per domain, LOO):")
for domain in domains:
    sub=df_n[df_n.domain==domain]
    for vs_base in TV:
        sub2=sub[(sub.variant=="base")|(sub.variant==vs_base)]
        lda=LinearDiscriminantAnalysis()
        preds,trues=[],[]
        for ts in seeds:
            tr=sub2[sub2.seed!=ts]; te=sub2[sub2.seed==ts]
            tr_X=tr[MK].values; tr_y=(tr.variant==vs_base).astype(int)
            te_X=te[MK].values; te_y=(te.variant==vs_base).astype(int)
            if len(np.unique(tr_y))<2: continue
            lda.fit(tr_X,tr_y)
            preds.extend(lda.predict(te_X)); trues.extend(te_y)
        if trues:
            acc=accuracy_score(trues,preds)
            print(f"    {domain:18s} base vs {vs_base:8s}: acc={acc:.3f}")

print(f"\n  5-class LDA (per domain, LOO):")
for domain in domains:
    sub=df_n[df_n.domain==domain]
    lda=LinearDiscriminantAnalysis()
    preds,trues=[],[]
    for ts in seeds:
        tr=sub[sub.seed!=ts]; te=sub[sub.seed==ts]
        if len(np.unique(tr.variant.values))<5: continue
        lda.fit(tr[MK].values,tr.variant.values)
        preds.extend(lda.predict(te[MK].values)); trues.extend(te.variant.values)
    if trues:
        acc=accuracy_score(trues,preds)
        print(f"    {domain:18s} acc={acc:.3f}")

print(f"\n  Pooled 5-class LDA (all domains, LOO):")
preds,trues=[],[]
for ts in seeds:
    tr=df_n[df_n.seed!=ts]; te=df_n[df_n.seed==ts]
    lda=LinearDiscriminantAnalysis().fit(tr[MK].values,tr.variant.values)
    preds.extend(lda.predict(te[MK].values)); trues.extend(te.variant.values)
print(f"    acc={accuracy_score(trues,preds):.3f}")

# --- 2G: Mahalanobis separability ---
print("\n--- 2G: MAHALANOBIS SEPARABILITY ---")
for domain in domains:
    sub=df_n[df_n.domain==domain]
    for vs_base in TV:
        correct=0; total=0
        for ts in seeds:
            tr=sub[sub.seed!=ts]; te=sub[sub.seed==ts]
            base_vec=tr[tr.variant=="base"][MK].values[0]
            target_vec=tr[tr.variant==vs_base][MK].values[0] if len(tr[tr.variant==vs_base])>0 else None
            if target_vec is None: continue
            # Pooled covariance
            X_tr=tr[MK].values
            cov=np.cov(X_tr.T)
            try: icov=np.linalg.inv(cov)
            except: continue
            for _,te_row in te.iterrows():
                d_base=mahalanobis(te_row[MK].values,base_vec,icov)
                d_target=mahalanobis(te_row[MK].values,target_vec,icov)
                actual=te_row["variant"]
                predicted=vs_base if d_target<d_base else "base"
                if (actual==vs_base and predicted==vs_base) or (actual=="base" and predicted=="base"):
                    correct+=1
                total+=1
        acc=correct/max(total,1)
        print(f"    {domain:18s} base vs {vs_base:8s}: Mahal acc={acc:.3f}")

# --- 2H: Gate vs LDA comparison ---
print("\n--- 2H: GATE vs LINEAR READOUT COMPARISON ---")
print(f"{'Domain':18s} {'Metric':8s} {'Gate':8s} {'LDA(base_vs)':14s} {'1NN':6s} {'Mahal':6s}")
for domain in domains:
    sub=df_n[df_n.domain==domain]
    # Gate
    gate_passes=0
    for s in seeds:
        sub_s=df_n[(df_n.seed==s)&(df_n.domain==domain)]
        base=sub_s[sub_s.variant=="base"][MK].values[0]
        dists={v:float(np.linalg.norm(sub_s[sub_s.variant==v][MK].values[0]-base)) for v in TV}
        c=np.corrcoef(sub_s[MK].values.T)
        eye=np.eye(4); mask=np.isfinite(c)
        diff=np.abs(c[mask]-eye[mask])
        cs=float(np.max(diff)) if len(diff)>0 else 1.0
        gate=all(dists[v]>th for v,th in zip(TV,[0.2,0.25,0.4,0.2])) and cs<0.90
        if gate: gate_passes+=1
    # LDA
    lda=LinearDiscriminantAnalysis()
    l_preds,l_trues=[],[]
    for ts in seeds:
        tr=sub[sub.seed!=ts]; te=sub[sub.seed==ts]
        lda.fit(tr[MK].values,tr.variant.values)
        l_preds.extend(lda.predict(te[MK].values)); l_trues.extend(te.variant.values)
    lda_acc=accuracy_score(l_trues,l_preds)
    # 1NN
    knn=KNeighborsClassifier(n_neighbors=1)
    preds,trues=[],[]
    for ts in seeds:
        tr=sub[sub.seed!=ts]; te=sub[sub.seed==ts]
        knn.fit(tr[MK].values,tr.variant.values)
        preds.extend(knn.predict(te[MK].values)); trues.extend(te.variant.values)
    nn_acc=accuracy_score(trues,preds)
    # Mahalanobis (nearest-centroid)
    mah_correct=0; mah_total=0
    for ts in seeds:
        tr=sub[sub.seed!=ts]; te=sub[sub.seed==ts]
        cov=np.cov(tr[MK].values.T)
        try: icov=np.linalg.inv(cov)
        except: continue
        centroids={v:tr[tr.variant==v][MK].values.mean(axis=0) for v in ["base"]+TV}
        for _,r in te.iterrows():
            ds={v:mahalanobis(r[MK].values,centroids[v],icov) for v in ["base"]+TV}
            pred=min(ds,key=ds.get); actual=r["variant"]
            if pred==actual: mah_correct+=1
            mah_total+=1
    mah_acc=mah_correct/max(mah_total,1)
    print(f"  {domain:18s} gate={gate_passes}/10 lda={lda_acc:.3f} nn={nn_acc:.3f} mah={mah_acc:.3f}")

# --- 2I: Mutual Information ---
print("\n--- 2I: MUTUAL INFORMATION BETWEEN METRICS AND TRANSFORM ---")
from sklearn.feature_selection import mutual_info_classif
mi=mutual_info_classif(df_n[MK].values,df_n["variant"].values,random_state=0)
for i,mk in enumerate(MK):
    print(f"  MI({mk}, variant)={mi[i]:.4f}")

# --- 2J: Can gate be fixed by threshold adjustment? ---
print("\n--- 2J: CAN GATE BE FIXED BY THRESHOLD ADJUSTMENT? ---")
# Check: what if we replace corr<0.90 with eff_rank>2.5, or drop corr entirely?
print("  Replacements for corr<0.90 evaluated:")
for domain in domains:
    sub=df_n[df_n.domain==domain]
    for threshold_scheme in ["corr<0.90","eff_rank>2.5","no_corr","pca_dim95>2"]:
        passes=0
        for s in seeds:
            sub_s=df_n[(df_n.seed==s)&(df_n.domain==domain)]
            base=sub_s[sub_s.variant=="base"][MK].values[0]
            dists={v:float(np.linalg.norm(sub_s[sub_s.variant==v][MK].values[0]-base)) for v in TV}
            c=np.corrcoef(sub_s[MK].values.T)
            eye=np.eye(4); mask=np.isfinite(c)
            diff=np.abs(c[mask]-eye[mask])
            cs=float(np.max(diff)) if len(diff)>0 else 1.0
            try:
                eig=np.linalg.eigvalsh(c)
                er=float(np.sum(eig)/eig[-1]) if eig[-1]>1e-12 else 0
            except: er=0
            pca_s=PCA().fit(sub_s[MK].values); cum=np.cumsum(pca_s.explained_variance_ratio_)
            d95=int(np.searchsorted(cum,0.95)+1)
            if threshold_scheme=="corr<0.90": corr_ok=cs<0.90
            elif threshold_scheme=="eff_rank>2.5": corr_ok=er>2.5
            elif threshold_scheme=="no_corr": corr_ok=True
            elif threshold_scheme=="pca_dim95>2": corr_ok=d95>2
            else: corr_ok=True
            gate=all(dists[v]>th for v,th in zip(TV,[0.2,0.25,0.4,0.2])) and corr_ok
            if gate: passes+=1
        print(f"    {domain:18s} {threshold_scheme:15s}: {passes}/10")

print("\n--- 2K: CEILING ANALYSIS — why gate maxes at ~3.5/10 ---")
print("  For each seed-domain, count how many th conditions fail:")
for domain in domains:
    print(f"  {domain}:")
    fail_counts={"replay_th":0,"stitch_th":0,"reverse_th":0,"swap_th":0,"corr":0,"eff_rank":0}
    for s in seeds:
        sub_s=df_n[(df_n.seed==s)&(df_n.domain==domain)]
        base=sub_s[sub_s.variant=="base"][MK].values[0]
        for v in TV:
            vec=sub_s[sub_s.variant==v][MK].values[0]
            d=float(np.linalg.norm(base-vec))
            thresh={"replay":0.20,"stitch":0.25,"reverse":0.40,"swap":0.20}
            if d<=thresh[v]: fail_counts[f"{v}_th"]+=1
        c=np.corrcoef(sub_s[MK].values.T)
        eye=np.eye(4); mask=np.isfinite(c)
        diff=np.abs(c[mask]-eye[mask])
        cs=float(np.max(diff)) if len(diff)>0 else 1.0
        if cs>=0.90: fail_counts["corr"]+=1
        try: eig=np.linalg.eigvalsh(c); er=float(np.sum(eig)/eig[-1]) if eig[-1]>1e-12 else 0
        except: er=0
        if er<=2.5: fail_counts["eff_rank"]+=1
    for k,v in fail_counts.items():
        print(f"    {k}: {v}/50")

# Save all results
print("\n\nSaving results...")
summary={"n_samples":len(df_full),"n_seeds":len(seeds),"n_domains":len(domains),
    "dead_metrics":{domain:{mk:dead_summary[domain][mk] for mk in MK} for domain in domains},
    "pca_explained_var":pca.explained_variance_ratio_.tolist(),
    "pca_dim95":int(np.searchsorted(np.cumsum(pca.explained_variance_ratio_),0.95)+1),
    "global_corr":np.corrcoef(df_n[MK].values.T).tolist(),
    "mi_variant":{mk:float(mi[i]) for i,mk in enumerate(MK)}}
with open("phase1_2_embedding_analysis.json","w") as f:
    json.dump(summary,f,indent=2)
print("Saved: phase1_2_embedding_analysis.json")
