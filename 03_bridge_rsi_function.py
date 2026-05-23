
# ════════════════════════════════════════════════════════════════════════════
# BRIDGE RSI FUNCTION
# ════════════════════════════════════════════════════════════════════════════
def find_peer(team_to_match, candidate_pool, quality_dict):
    """Find closest quality peer of team_to_match from candidate_pool."""
    q_target = quality_dict[team_to_match]
    return min(candidate_pool, key=lambda t: abs(quality_dict[t] - q_target))

def bridge_rsi(h, a, lk_h_group, lk_a_group, quality_dict,
               h_group_teams, a_group_teams, beta=0.25):
    """
    h: home team (cross-group)
    a: away team (cross-group)
    lk_h_group: lookup for h's group {team: {opp: (gf,ga)}}
    lk_a_group: lookup for a's group
    quality_dict: unified quality scores for all teams
    h_group_teams: teams in h's group (peer pool for a's opponents)
    a_group_teams: teams in a's group (peer pool for h's opponents)
    """
    h_games = lk_h_group.get(h, {})  # opponents h has faced
    a_games = lk_a_group.get(a, {})  # opponents a has faced

    # Bridge RSI for H:
    # For each opponent OH that H played, find peer(OH) in A's group
    # Compare: (gf_H vs OH) / (gf_A vs peer(OH))
    rsi_h_ratios = []
    for oh, (gf_h, _) in h_games.items():
        # Find closest quality peer of OH in a's group
        peer = find_peer(oh, [t for t in a_group_teams if t in a_games], quality_dict)
        if peer in a_games:
            gf_a_vs_peer = a_games[peer][0]
            ratio = gf_h / max(gf_a_vs_peer, 0.5)
            # Weight by similarity of quality (closer peer = higher weight)
            q_diff = abs(quality_dict[oh] - quality_dict[peer])
            q_sim  = np.exp(-q_diff / max(quality_dict[oh], 0.1))  # similarity weight
            rsi_h_ratios.append((np.log(max(ratio, 0.05)), q_sim))

    # Bridge RSI for A:
    rsi_a_ratios = []
    for oa, (gf_a, _) in a_games.items():
        peer = find_peer(oa, [t for t in h_group_teams if t in h_games], quality_dict)
        if peer in h_games:
            gf_h_vs_peer = h_games[peer][0]
            ratio = gf_a / max(gf_h_vs_peer, 0.5)
            q_diff = abs(quality_dict[oa] - quality_dict[peer])
            q_sim  = np.exp(-q_diff / max(quality_dict[oa], 0.1))
            rsi_a_ratios.append((np.log(max(ratio, 0.05)), q_sim))

    # Weighted geometric mean
    if rsi_h_ratios:
        logs, weights = zip(*rsi_h_ratios)
        w_sum = sum(weights)
        rsi_h = np.exp(sum(l*w for l,w in zip(logs,weights))/max(w_sum,1e-9))
    else:
        rsi_h = 1.0

    if rsi_a_ratios:
        logs, weights = zip(*rsi_a_ratios)
        w_sum = sum(weights)
        rsi_a = np.exp(sum(l*w for l,w in zip(logs,weights))/max(w_sum,1e-9))
    else:
        rsi_a = 1.0

    return rsi_h**beta, rsi_a**beta

# Test: HS Riga Blue (A) vs HS Riga White (B)
rh, ra = bridge_rsi("HS Riga Blue","HS Riga White",lkA,lkB,all_quality,all_teams_A,all_teams_B)
print(f"HS Riga Blue vs HS Riga White → Bridge RSI_H={rh:.3f}  RSI_A={ra:.3f}")

rh, ra = bridge_rsi("HC Panter Black","HS Riga White",lkA,lkB,all_quality,all_teams_A,all_teams_B)
print(f"HC Panter Black vs HS Riga White → Bridge RSI_H={rh:.3f}  RSI_A={ra:.3f}")

rh, ra = bridge_rsi("HS Riga Blue","HC Vipers White",lkA,lkB,all_quality,all_teams_A,all_teams_B)
print(f"HS Riga Blue vs HC Vipers White → Bridge RSI_H={rh:.3f}  RSI_A={ra:.3f}")

rh, ra = bridge_rsi("HS Riga Blue","HC Panter Red",lkA,lkB,all_quality,all_teams_A,all_teams_B)
print(f"HS Riga Blue vs HC Panter Red   → Bridge RSI_H={rh:.3f}  RSI_A={ra:.3f}")
