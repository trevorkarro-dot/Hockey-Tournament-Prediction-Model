
path="output/HC_Panter_Spring_Cup_2026_v5.xlsx"

with pd.ExcelWriter(path,engine="openpyxl") as w:
    df_formulas.to_excel(w,sheet_name="📐 Formulas",          index=False)
    df_model.to_excel(w,   sheet_name="📊 Team Parameters",   index=False)
    df_qual.to_excel(w,    sheet_name="🌍 Global Rankings",   index=False)
    df_sA.to_excel(w,      sheet_name="🔵 Group A Standings", index=False)
    df_sB.to_excel(w,      sheet_name="🟠 Group B Standings", index=False)
    df_matches.to_excel(w, sheet_name="🎯 Match Predictions", index=False)
    df_bridge.to_excel(w,  sheet_name="🌉 Bridge RSI Matrix", index=False)
    df_ko.to_excel(w,      sheet_name="🥊 KO + Place Games",  index=False)
    df_pos.to_excel(w,     sheet_name="📍 Group Position %",  index=False)
    df_finish.to_excel(w,  sheet_name="🏅 Tournament Finish", index=False)

wb=load_workbook(path)

def hf(h): return PatternFill("solid",fgColor=h)
def style(ws,hx,top2=False,bot2=False,champ_col=None):
    thin=Side(style="thin",color="CCCCCC"); bdr=Border(left=thin,right=thin,top=thin,bottom=thin)
    for cell in ws[1]:
        cell.fill=hf(hx); cell.font=Font(color="FFFFFF",bold=True,size=11)
        cell.alignment=Alignment(horizontal="center",vertical="center"); cell.border=bdr
    for ri,row in enumerate(ws.iter_rows(min_row=2),2):
        bg=hf("EBF2FF") if ri%2==0 else hf("FFFFFF")
        for cell in row:
            cell.fill=bg; cell.font=Font(size=10)
            cell.alignment=Alignment(horizontal="center",vertical="center"); cell.border=bdr
    if top2:
        for ri in range(2,ws.max_row+1):
            if ws.cell(ri,1).value in(1,2):
                [setattr(c,'fill',hf("C6EFCE")) or setattr(c,'font',Font(bold=True,size=10)) for c in ws[ri]]
    if bot2:
        for ri in range(2,ws.max_row+1):
            if ws.cell(ri,1).value in(6,7):
                [setattr(c,'fill',hf("FFE0E0")) for c in ws[ri]]
    if champ_col:
        hdrs=[ws.cell(1,c).value for c in range(1,ws.max_column+1)]
        if champ_col in hdrs:
            cc=hdrs.index(champ_col)+1
            for ri in range(2,ws.max_row+1):
                v=ws.cell(ri,cc).value
                if v and float(v)>=20: [setattr(c,'fill',hf("C6EFCE")) or setattr(c,'font',Font(bold=True)) for c in ws[ri]]
                elif v and float(v)>=3: [setattr(c,'fill',hf("FFF2CC")) or setattr(c,'font',Font(bold=True)) for c in ws[ri]]
    for col in ws.columns:
        w_=max((len(str(c.value)) if c.value else 0) for c in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width=min(w_+3,34)
    ws.freeze_panes="A2"

style(wb["📐 Formulas"],         "2E4057")
style(wb["📊 Team Parameters"],  "1A6B3C")
style(wb["🌍 Global Rankings"],  "2C5F8A")
style(wb["🔵 Group A Standings"],"1F4E79",top2=True,bot2=True)
style(wb["🟠 Group B Standings"],"833C00",top2=True,bot2=True)
style(wb["🎯 Match Predictions"],"1A4A4A")
style(wb["🌉 Bridge RSI Matrix"],"4A1060")
style(wb["🥊 KO + Place Games"], "3B1F79")
style(wb["📍 Group Position %"], "1D5C2E")
style(wb["🏅 Tournament Finish"],"404040",champ_col="Champion%")

# Key matches
ws=wb["🎯 Match Predictions"]
for ri in range(2,ws.max_row+1):
    if ws.cell(ri,1).value in(29,30):
        for c in ws[ri]: c.fill=hf("FFF2CC"); c.font=Font(bold=True,size=11)

# RSI type column color
ws=wb["🎯 Match Predictions"]
hdrs=[ws.cell(1,c).value for c in range(1,ws.max_column+1)]
rt_col=hdrs.index("RSI Type")+1 if "RSI Type" in hdrs else None
if rt_col:
    for ri in range(2,ws.max_row+1):
        v=ws.cell(ri,rt_col).value
        if v=="Bridge":
            ws.cell(ri,rt_col).fill=hf("E8D5F5"); ws.cell(ri,rt_col).font=Font(bold=True,color="4A1060")
        elif v=="Direct":
            ws.cell(ri,rt_col).fill=hf("D5EAF5"); ws.cell(ri,rt_col).font=Font(bold=True,color="1A4A6A")

# RSI type in KO sheet
ws=wb["🥊 KO + Place Games"]
hdrs=[ws.cell(1,c).value for c in range(1,ws.max_column+1)]
rt_col=hdrs.index("RSI Type")+1 if "RSI Type" in hdrs else None
sc=hdrs.index("Stage")+1 if "Stage" in hdrs else None
for ri in range(2,ws.max_row+1):
    if sc:
        sv=str(ws.cell(ri,sc).value or "")
        if "Final" in sv: [setattr(c,'fill',hf("FFD700")) or setattr(c,'font',Font(bold=True)) for c in ws[ri]]
        elif "Bronze" in sv: [setattr(c,'fill',hf("D4956A")) or setattr(c,'font',Font(bold=True,color="FFFFFF")) for c in ws[ri]]
        elif "SF" in sv: [setattr(c,'fill',hf("BDD7EE")) or setattr(c,'font',Font(bold=True)) for c in ws[ri]]
    if rt_col:
        v=ws.cell(ri,rt_col).value
        if v=="Bridge": ws.cell(ri,rt_col).fill=hf("E8D5F5"); ws.cell(ri,rt_col).font=Font(bold=True,color="4A1060")

# Bridge RSI matrix: color cells
ws=wb["🌉 Bridge RSI Matrix"]
for ri in range(2,ws.max_row+1):
    for ci in range(2,ws.max_column+1):
        v=ws.cell(ri,ci).value
        if v and v!="—":
            try:
                fv=float(v)
                if fv>=1.3: ws.cell(ri,ci).fill=hf("C6EFCE"); ws.cell(ri,ci).font=Font(bold=True,color="1D5C2E")
                elif fv>=1.1: ws.cell(ri,ci).fill=hf("E2EFDA"); ws.cell(ri,ci).font=Font(color="375623")
                elif fv<=0.7: ws.cell(ri,ci).fill=hf("FFE0E0"); ws.cell(ri,ci).font=Font(bold=True,color="9C0006")
                elif fv<=0.9: ws.cell(ri,ci).fill=hf("FCE4D6"); ws.cell(ri,ci).font=Font(color="833C00")
            except: pass

# Global rankings: top team gold
ws=wb["🌍 Global Rankings"]
for ri in range(2,min(4,ws.max_row+1)):
    for c in ws[ri]: c.fill=hf("FFF2CC"); c.font=Font(bold=True)

# README
ws_i=wb.create_sheet("ℹ️ README",0)
thin=Side(style="thin",color="AAAAAA"); bdr=Border(left=thin,right=thin,top=thin,bottom=thin)
info=[
    ("HC PANTER SPRING CUP 2026 — v5: Bridge RSI Cross-Group Model","1F4E79",13,True),
    ("Data after game #28 | 100,000 Monte Carlo sims | Bridge RSI for KO cross-group matchups","2E4057",10,False),
    ("","","10",""),
    ("🆕 v5: BRIDGE RSI (cross-group KO fix)","1A6B3C",11,True),
    ("Problem: Teams from Grp A and Grp B share NO common opponents → RSI was always 1.0","","10",""),
    ("Fix: Find the closest quality-matched PEER in the opponent's group for each game played","","10",""),
    ("  H (A) beat OppH. A (B) beat Peer(OppH). Bridge RSI_H = gf_H_vs_OppH / gf_A_vs_Peer","","10",""),
    ("  Weights: exp(−ΔQuality/Q) → similar quality peers count more","","10",""),
    ("  β=0.25 (vs β=0.30 for direct) — more conservative since bridge has more uncertainty","","10",""),
    ("","","10",""),
    ("📐 MODEL PIPELINE","2E4057",11,True),
    ("1. avg = Σ(GF)/Σ(G) per group","","10",""),
    ("2. raw_att=(GF/G)/avg,  raw_def=(GA/G)/avg","","10",""),
    ("3. α=G/(G+5) → shrinkage toward mean (4 games → α=0.44)","","10",""),
    ("4. Quality Score Q = adj_att/adj_def × avg (normalized across groups)","","10",""),
    ("5. Same-group: λ = att×def×avg × DirectRSI^0.30","","10",""),
    ("6. Cross-group: λ = att×def×avg_comb × BridgeRSI^0.25","","10",""),
    ("7. Win/Draw/Loss from Poisson PMF summed over 20×20 grid","","10",""),
    ("8. KO: P(win) = P(H>A)/(P(H>A)+P(A>H))","","10",""),
    ("9. Tiebreaks: Pts→H2H Pts→H2H GD→H2H GF→GD→GF→Pen→Dice","","10",""),
    ("10. 100,000 Monte Carlo simulations","","10",""),
    ("","","10",""),
    ("📁 SHEET GUIDE","2E4057",11,True),
    ("📐 Formulas        — Full step-by-step math","","10",""),
    ("📊 Team Parameters — Raw/adj att+def, α, quality per team","","10",""),
    ("🌍 Global Rankings — Unified cross-group quality ranking","","10",""),
    ("🔵🟠 Standings     — Live table (green=top2, red=bottom2)","","10",""),
    ("🎯 Match Predictions — Group games with RSI Type (Direct/Bridge) label","","10",""),
    ("🌉 Bridge RSI Matrix — Grp A rows vs Grp B cols (green>1.3, red<0.7)","","10",""),
    ("🥊 KO + Place Games — All KO/place predictions, all with proper RSI Type","","10",""),
    ("📍 Group Position % — Sim prob of each group position per team","","10",""),
    ("🏅 Tournament Finish — 1st-14th% all teams (all cols sum to 100%)","","10",""),
    ("","","10",""),
    ("KEY RESULT: HS Riga Blue 81.8% champion (bridge RSI confirms dominance vs cross-group peers)","833C00",10,True),
]
for i,(txt,fh,sz,bd) in enumerate(info,1):
    c=ws_i.cell(i,1,txt)
    if fh: c.fill=hf(fh); c.font=Font(bold=True,size=int(sz),color="FFFFFF")
    else: c.font=Font(size=int(sz) if sz else 10,bold=bool(bd))
    c.alignment=Alignment(horizontal="left",vertical="center"); c.border=bdr
ws_i.column_dimensions["A"].width=95

wb.save(path)
print(f"✅ {path}")
print(f"Sheets: {wb.sheetnames}")
