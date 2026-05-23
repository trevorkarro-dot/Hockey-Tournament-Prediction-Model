
# ════════════════════════════════════════════════════════════════════════════
# BRIDGE RSI — CROSS-GROUP COMMON OPPONENT STRENGTH INDEX
# ════════════════════════════════════════════════════════════════════════════
#
# IDEA: Teams from A and B have no direct common opponents.
# But we can build a "bridge" by finding cross-group POSITIONAL peers.
#
# Algorithm:
# 1. Compute a GLOBAL RATING for every team using their adj att/def,
#    normalised to a common scale (both groups unified).
#
# 2. For a cross-group matchup (H in A, A in B):
#    Find all opponents OH that H played (in group A).
#    Find all opponents OA that A played (in group B).
#    For each OH, find their "peer" in group B by closest global rating.
#    For each OA, find their "peer" in group A by closest global rating.
#
# 3. Bridge RSI_H = geometric mean of:
#      (gf_H vs OH) / (gf_A vs peer(OH))    ← how H performed vs equiv-quality opponents
#    Bridge RSI_A = geometric mean of:
#      (gf_A vs OA) / (gf_H vs peer(OA))
#
# 4. Blend with base (β=0.25 for bridge since it's one step removed)
#    λH_final = λH_base × bridge_RSI_H^β

# Step 1: Unified global ratings (normalize each group's ratings onto shared scale)
# We use att * (1/def) as a single "quality" metric, scaled by group avg
def global_quality(teams, att, defe, avg):
    """Higher = better team. att/def * avg gives goals/game expected vs avg opponent."""
    return {t: att[t]/max(defe[t],0.1) * avg for t in teams}

qualA = global_quality(all_teams_A, attA, defA, avgA)
qualB = global_quality(all_teams_B, attB, defB, avgB)
# Normalize both onto combined scale (ratio of group averages)
scale_AB = avgA/avgB  # Group A is higher scoring; normalize B quality up
qualB_norm = {t: qualB[t]*scale_AB for t in qualB}
all_quality = {**qualA, **qualB_norm}

print("=== GLOBAL QUALITY SCORES (higher = stronger) ===")
ranked = sorted(all_quality.items(), key=lambda x:-x[1])
for t,q in ranked:
    grp="A" if t in all_teams_A else "B"
    print(f"  [{grp}] {t:<26}  quality={q:.3f}")