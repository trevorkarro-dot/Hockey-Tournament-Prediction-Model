
import pandas as pd
import numpy as np
from scipy.stats import poisson
import os
os.makedirs("output", exist_ok=True)

# ════════════════════════════════════════════════════════════════════════════
# DATA
# ════════════════════════════════════════════════════════════════════════════
all_teams_A = ["HC Panter Black","HS Riga Blue","Narva PSK 1","HC Vipers Red","IiHoo","HCK Salamat Blue","HJK Blue"]
all_teams_B = ["HS Riga White","HC Panter Red","HC Vipers White","Ice Team Raseborg","Narva PSK 2","HCK Salamat White","HJK White"]
all_teams   = all_teams_A + all_teams_B

completed = [
    ("HC Panter Black","Narva PSK 1",6,1,"A"),("HCK Salamat Blue","IiHoo",1,7,"A"),
    ("HS Riga Blue","HC Vipers Red",6,0,"A"),("HJK Blue","HC Panter Black",1,6,"A"),
    ("Narva PSK 1","HCK Salamat Blue",4,0,"A"),("IiHoo","HS Riga Blue",2,18,"A"),
    ("HC Vipers Red","HJK Blue",4,0,"A"),("HC Panter Black","HCK Salamat Blue",9,0,"A"),
    ("Narva PSK 1","IiHoo",5,1,"A"),("HS Riga Blue","HJK Blue",19,0,"A"),
    ("HC Panter Black","HC Vipers Red",1,0,"A"),("Narva PSK 1","HS Riga Blue",2,8,"A"),
    ("HCK Salamat Blue","HJK Blue",6,5,"A"),("HC Vipers Red","IiHoo",4,0,"A"),
    ("HC Panter Red","Narva PSK 2",9,0,"B"),("HCK Salamat White","Ice Team Raseborg",1,5,"B"),
    ("HS Riga White","HC Vipers White",2,0,"B"),("HJK White","HC Panter Red",2,0,"B"),
    ("Narva PSK 2","HCK Salamat White",1,2,"B"),("Ice Team Raseborg","HS Riga White",0,3,"B"),
    ("HC Vipers White","HJK White",8,0,"B"),("HC Panter Red","HCK Salamat White",5,1,"B"),
    ("Narva PSK 2","Ice Team Raseborg",1,0,"B"),("HS Riga White","HJK White",8,2,"B"),
    ("HC Panter Red","HC Vipers White",1,1,"B"),("Narva PSK 2","HS Riga White",0,11,"B"),
    ("HCK Salamat White","HJK White",1,7,"B"),("HC Vipers White","Ice Team Raseborg",2,1,"B"),
]

remaining = [
    (29,"Sun 09:00","HC Panter Black","HS Riga Blue","A"),
    (30,"Sun 09:00","HC Panter Red","HS Riga White","B"),
    (31,"Sun 09:35","Narva PSK 1","HC Vipers Red","A"),
    (32,"Sun 09:35","Narva PSK 2","HC Vipers White","B"),
    (33,"Sun 10:10","HJK Blue","IiHoo","A"),
    (34,"Sun 10:10","HJK White","Ice Team Raseborg","B"),
    (35,"Sun 11:00","HCK Salamat Blue","HS Riga Blue","A"),
    (36,"Sun 11:00","HCK Salamat White","HS Riga White","B"),
    (37,"Sun 11:35","HC Panter Black","IiHoo","A"),
    (38,"Sun 11:35","HC Panter Red","Ice Team Raseborg","B"),
    (39,"Sun 12:25","Narva PSK 1","HJK Blue","A"),
    (40,"Sun 12:25","Narva PSK 2","HJK White","B"),
    (41,"Sun 13:00","HCK Salamat Blue","HC Vipers Red","A"),
    (42,"Sun 13:00","HCK Salamat White","HC Vipers White","B"),
]

def compute_stats(teams, results):
    s = {t:{"G":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"Pts":0} for t in teams}
    for h,a,hg,ag,_ in results:
        if h not in s or a not in s: continue
        s[h]["GF"]+=hg; s[h]["GA"]+=ag; s[h]["G"]+=1
        s[a]["GF"]+=ag; s[a]["GA"]+=hg; s[a]["G"]+=1
        if hg>ag: s[h]["W"]+=1; s[h]["Pts"]+=2; s[a]["L"]+=1
        elif hg<ag: s[a]["W"]+=1; s[a]["Pts"]+=2; s[h]["L"]+=1
        else: s[h]["D"]+=1; s[h]["Pts"]+=1; s[a]["D"]+=1; s[a]["Pts"]+=1
    return s

statsA = compute_stats(all_teams_A, completed)
statsB = compute_stats(all_teams_B, completed)

def build_shrinkage_model(teams, results, k=5):
    subset = [(h,a,hg,ag) for h,a,hg,ag,_ in results if h in teams and a in teams]
    total_gf = sum(hg+ag for h,a,hg,ag in subset)
    total_g  = len(subset)*2
    avg = total_gf/max(total_g,1)
    raw_att={}; raw_def={}; alpha={}
    for t in teams:
        s_gf=s_ga=g=0
        for h,a,hg,ag in subset:
            if h==t: s_gf+=hg; s_ga+=ag; g+=1
            elif a==t: s_gf+=ag; s_ga+=hg; g+=1
        raw_att[t]=(s_gf/max(g,1))/avg if avg>0 else 1.0
        raw_def[t]=(s_ga/max(g,1))/avg if avg>0 else 1.0
        alpha[t]=g/(g+k)
    att  ={t:alpha[t]*raw_att[t]+(1-alpha[t])*1.0 for t in teams}
    defe ={t:alpha[t]*raw_def[t]+(1-alpha[t])*1.0 for t in teams}
    return att, defe, avg, raw_att, raw_def, alpha

attA, defA, avgA, rawattA, rawdefA, alphaA = build_shrinkage_model(all_teams_A, completed)
attB, defB, avgB, rawattB, rawdefB, alphaB = build_shrinkage_model(all_teams_B, completed)
avg_comb = (avgA+avgB)/2

def build_lookup(teams, results):
    lk={t:{} for t in teams}
    for h,a,hg,ag,_ in results:
        if h in lk and a in lk:
            lk[h][a]=(hg,ag); lk[a][h]=(ag,hg)
    return lk

lkA=build_lookup(all_teams_A,completed)
lkB=build_lookup(all_teams_B,completed)
lkAll=build_lookup(all_teams,completed)

print("Data + base models ready.")
print(f"avgA={avgA:.3f}  avgB={avgB:.3f}  avg_comb={avg_comb:.3f}")