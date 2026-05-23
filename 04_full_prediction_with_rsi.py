
# ════════════════════════════════════════════════════════════════════════════
# UNIFIED PREDICTION FUNCTION (same-group = direct RSI, cross-group = bridge RSI)
# ════════════════════════════════════════════════════════════════════════════
all_att  = {**attA, **defA}   # bug-fix: should be att/def separately
all_att  = {**attA, **attB}
all_def  = {**defA, **defB}

def get_pred_full(h, a, beta_same=0.3, beta_bridge=0.25):
    """Full prediction with correct RSI routing."""
    h_in_A = h in all_teams_A
    a_in_A = a in all_teams_A
    same_group = (h_in_A == a_in_A)

    att  = all_att
    defe = all_def
    avg  = avgA if same_group and h_in_A else (avgB if same_group and not h_in_A else avg_comb)

    lh_base = max(att[h] * defe[a] * avg, 0.05)
    la_base = max(att[a] * defe[h] * avg, 0.05)

    if same_group:
        lk = lkA if h_in_A else lkB
        # Direct common opponent RSI
        h_games = lk.get(h, {}); a_games = lk.get(a, {})
        common = set(h_games.keys()) & set(a_games.keys())
        if common:
            logs_h=[]; logs_a=[]
            for c in common:
                logs_h.append(np.log(max(h_games[c][0]/max(a_games[c][0],0.5),0.05)))
                logs_a.append(np.log(max(a_games[c][0]/max(h_games[c][0],0.5),0.05)))
            rsi_h = np.exp(np.mean(logs_h))**beta_same
            rsi_a = np.exp(np.mean(logs_a))**beta_same
        else:
            rsi_h = rsi_a = 1.0
        rsi_type = "Direct"
    else:
        # Cross-group: use bridge RSI
        if h_in_A:
            rsi_h, rsi_a = bridge_rsi(h,a,lkA,lkB,all_quality,all_teams_A,all_teams_B,beta=beta_bridge)
        else:
            rsi_a, rsi_h = bridge_rsi(a,h,lkA,lkB,all_quality,all_teams_A,all_teams_B,beta=beta_bridge)
        rsi_type = "Bridge"

    lh = max(lh_base * rsi_h, 0.05)
    la = max(la_base * rsi_a, 0.05)

    ph=pd_=pa=0.0; best_p=-1; ml_h=ml_a=0
    for hg in range(20):
        pmf_h=poisson.pmf(hg,lh)
        for ag in range(20):
            p=pmf_h*poisson.pmf(ag,la)
            if hg>ag: ph+=p
            elif hg==ag: pd_+=p
            else: pa+=p
            if p>best_p: best_p=p; ml_h=hg; ml_a=ag

    return lh, la, ml_h, ml_a, ph, pd_, pa, rsi_h, rsi_a, rsi_type

# Precompute KO win probs with bridge RSI
ko_p={}
for t1 in all_teams:
    for t2 in all_teams:
        if t1!=t2:
            lh,la,_,_,ph,pd_,pa,*_=get_pred_full(t1,t2)
            tot=ph+pa; ko_p[(t1,t2)]=ph/tot if tot>0 else 0.5

print("=== REMAINING GROUP GAMES ===")
match_rows=[]
for num,dt,h,a,grp in remaining:
    lh,la,ml_h,ml_a,ph,pd_,pa,rh,ra,rt=get_pred_full(h,a)
    match_rows.append({"#":num,"When":dt,"Grp":grp,"Home":h,"Away":a,
                       "λH":round(lh,2),"λA":round(la,2),
                       "Most Likely Score":f"{ml_h}–{ml_a}",
                       "P(Home Win)%":round(ph*100,1),"P(Draw)%":round(pd_*100,1),"P(Away Win)%":round(pa*100,1),
                       "RSI_H":round(rh,3),"RSI_A":round(ra,3),"RSI Type":rt})
    star="⭐" if num in(29,30) else ""
    print(f"#{num} {h} vs {a}: {ml_h}–{ml_a}  P(H)={ph*100:.0f}% P(D)={pd_*100:.0f}% P(A)={pa*100:.0f}%  RSI_H={rh:.3f} RSI_A={ra:.3f} [{rt}] {star}")
df_matches=pd.DataFrame(match_rows)
