
# ════════════════════════════════════════════════════════════════════════════
# MONTE CARLO WITH BRIDGE RSI
# ════════════════════════════════════════════════════════════════════════════
def rank_teams(teams, results_dict):
    pts={t:0 for t in teams}; gf={t:0 for t in teams}; ga={t:0 for t in teams}
    for (h,a),(hg,ag) in results_dict.items():
        if h not in pts or a not in pts: continue
        gf[h]+=hg; ga[h]+=ag; gf[a]+=ag; ga[a]+=hg
        if hg>ag: pts[h]+=2
        elif hg<ag: pts[a]+=2
        else: pts[h]+=1; pts[a]+=1
    gd={t:gf[t]-ga[t] for t in teams}
    def resolve(group):
        if len(group)<=1: return group
        h2h_p={t:0 for t in group}; h2h_gf={t:0 for t in group}; h2h_ga={t:0 for t in group}
        for (h,a),(hg,ag) in results_dict.items():
            if h in h2h_p and a in h2h_p:
                h2h_gf[h]+=hg; h2h_ga[h]+=ag; h2h_gf[a]+=ag; h2h_ga[a]+=hg
                if hg>ag: h2h_p[h]+=2
                elif hg<ag: h2h_p[a]+=2
                else: h2h_p[h]+=1; h2h_p[a]+=1
        h2h_gd={t:h2h_gf[t]-h2h_ga[t] for t in group}
        def key(t): return (h2h_p[t],h2h_gd[t],h2h_gf[t],gd[t],gf[t],np.random.random())
        s=sorted(group,key=key,reverse=True)
        result=[]; i=0
        while i<len(s):
            j=i+1
            while j<len(s) and h2h_p[s[j]]==h2h_p[s[i]] and h2h_gd[s[j]]==h2h_gd[s[i]] and \
                  h2h_gf[s[j]]==h2h_gf[s[i]] and gd[s[j]]==gd[s[i]] and gf[s[j]]==gf[s[i]]: j+=1
            sub=s[i:j]
            if len(sub)>1: np.random.shuffle(sub)
            result.extend(sub); i=j
        return result
    sorted_by_pts=sorted(teams,key=lambda t:pts[t],reverse=True)
    result=[]; i=0
    while i<len(sorted_by_pts):
        j=i+1
        while j<len(sorted_by_pts) and pts[sorted_by_pts[j]]==pts[sorted_by_pts[i]]: j+=1
        tied=sorted_by_pts[i:j]
        result.extend(resolve(tied) if len(tied)>1 else tied); i=j
    return result

N=100_000
rng=np.random.default_rng(42)
rem_A=[(n,d,h,a,g) for n,d,h,a,g in remaining if g=="A"]
rem_B=[(n,d,h,a,g) for n,d,h,a,g in remaining if g=="B"]

lam_A={}
for _,_,h,a,_ in rem_A:
    lh,la,*_=get_pred_full(h,a); lam_A[(h,a)]=(lh,la)
lam_B={}
for _,_,h,a,_ in rem_B:
    lh,la,*_=get_pred_full(h,a); lam_B[(h,a)]=(lh,la)

goals_A={(h,a):(rng.poisson(lam_A[(h,a)][0],N).astype(np.int16),
                rng.poisson(lam_A[(h,a)][1],N).astype(np.int16)) for _,_,h,a,_ in rem_A}
goals_B={(h,a):(rng.poisson(lam_B[(h,a)][0],N).astype(np.int16),
                rng.poisson(lam_B[(h,a)][1],N).astype(np.int16)) for _,_,h,a,_ in rem_B}
rand_ko=np.random.default_rng(99).random((N,9))

finish={t:np.zeros(14,dtype=np.int32) for t in all_teams}
pos_A_c=np.zeros((7,7),dtype=np.int32); pos_B_c=np.zeros((7,7),dtype=np.int32)

print(f"Running {N:,} simulations with Bridge RSI for cross-group KO...")
for i in range(N):
    res_A={(h,a):(hg,ag) for h,a,hg,ag,g in completed if g=="A"}
    res_B={(h,a):(hg,ag) for h,a,hg,ag,g in completed if g=="B"}
    for _,_,h,a,_ in rem_A: res_A[(h,a)]=(int(goals_A[(h,a)][0][i]),int(goals_A[(h,a)][1][i]))
    for _,_,h,a,_ in rem_B: res_B[(h,a)]=(int(goals_B[(h,a)][0][i]),int(goals_B[(h,a)][1][i]))
    rA=rank_teams(all_teams_A,res_A); rB=rank_teams(all_teams_B,res_B)
    for p,t in enumerate(rA): pos_A_c[all_teams_A.index(t),p]+=1
    for p,t in enumerate(rB): pos_B_c[all_teams_B.index(t),p]+=1
    A=rA; B=rB; r=rand_ko[i]
    sf1w=A[0] if r[0]<ko_p[(A[0],B[1])] else B[1]; sf1l=B[1] if sf1w==A[0] else A[0]
    sf2w=B[0] if r[1]<ko_p[(B[0],A[1])] else A[1]; sf2l=A[1] if sf2w==B[0] else B[0]
    finw=sf1w if r[2]<ko_p[(sf1w,sf2w)] else sf2w; finl=sf2w if finw==sf1w else sf1w
    brow=sf1l if r[3]<ko_p[(sf1l,sf2l)] else sf2l; brol=sf2l if brow==sf1l else sf1l
    finish[finw][0]+=1; finish[finl][1]+=1; finish[brow][2]+=1; finish[brol][3]+=1
    for idx,(tx,ty) in enumerate([(A[2],B[2]),(A[3],B[3]),(A[4],B[4]),(A[5],B[5]),(A[6],B[6])]):
        base=4+idx*2
        if r[4+idx]<ko_p[(tx,ty)]: finish[tx][base]+=1; finish[ty][base+1]+=1
        else: finish[ty][base]+=1; finish[tx][base+1]+=1
    if i%25000==0: print(f"  {i:,}...")

pos_A=pos_A_c/N; pos_B=pos_B_c/N
ok=all(abs(sum(finish[t][p] for t in all_teams)-N)<100 for p in range(14))
print(f"Done! Valid={ok}")
for t in sorted(all_teams,key=lambda t:finish[t][0],reverse=True)[:5]:
    print(f"  {t:<26}  Champ:{finish[t][0]/N*100:.1f}%  Final:{(finish[t][0]+finish[t][1])/N*100:.1f}%  Semi:{sum(finish[t][:4])/N*100:.1f}%")