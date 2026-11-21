"""How much an attack hurts.  One place, a few named numbers, no hidden brackets.

    damage = move power x 2.4 x stat factor x hit quality x affinity  (+/- 10%)

1. Stat factor: your ATK against their DEF, on a gentle curve.

       stat factor = sqrt(ATK / DEF), kept between 0.35 and 1.4

       ATK = DEF       -> 1.0   (a normal hit does about 2.4x the move's listed power)
       ATK = 2 x DEF   -> 1.4   (the most attack can add)
       ATK = DEF / 2   -> 0.71
       ATK = DEF / 8   -> 0.35  (the least: a weak card still scratches)

   The old formula clipped damage between 1/3 and 2x the move's power and then
   rolled one of five overlapping "engagement" brackets, so past a point ATK
   did nothing at all and small stat changes could jump a whole bracket.

2. Hit quality (the d20 roll, after speed and trait modifiers - unchanged):

       miss (below 1) -> 0 | glancing 1-6 -> x0.75 | normal 7-15 -> x1 | strong 16-19 -> x1.25 | critical 20 -> x2

3. Affinity: weakness x1.5, resistance x0.5, immunity 0, repel / absorb as before.

4. The cap: no single hit can take more than 45% of the target's max health.
   Multipliers stack (critical x weakness x traits x wind...), and before the
   cap 1 hit in 100 did more than the target's entire health bar (simulator).
   2.4 keeps fights about as long as before: the old formula ended many fights
   with those giant hits, the new one with steadier ones.  Big moves
   still feel big: they just can't end a fight from full health in one blow.

Every attack also does at least 10% of the move's power (before affinities), so
no hit lands for 0 unless it misses or the target is immune.
"""
import math
import random

DAMAGE_SCALE = 2.4
STAT_FACTOR_MIN = 0.35
STAT_FACTOR_MAX = 1.4
VARIANCE = 0.10
MIN_DAMAGE_SHARE = 0.10

GLANCING = 0.75
STRONG = 1.25
CRITICAL = 2.0
CRITICAL_BLOOD_AWAKENING = 3.0      # Crown Rift Awakening's trait (was x4 on top of the old x2.5 crit scale)

WEAKNESS = 1.5
RESISTANCE = 0.5

MAX_HIT_SHARE = 0.45


def stat_factor(attack, defense):
    try:
        ratio = max(float(attack), 1.0) / max(float(defense), 1.0)
    except (TypeError, ValueError):
        ratio = 1.0
    return min(STAT_FACTOR_MAX, max(STAT_FACTOR_MIN, math.sqrt(ratio)))


def base_damage(power, attack, defense, rng=random):
    """Damage before the hit roll and affinities."""
    try:
        power = max(float(power), 0.0)
    except (TypeError, ValueError):
        power = 0.0
    dmg = power * DAMAGE_SCALE * stat_factor(attack, defense) * rng.uniform(1 - VARIANCE, 1 + VARIANCE)
    return max(round(dmg), round(power * MIN_DAMAGE_SHARE), 1)


def max_hit(target):
    """Largest single hit ``target`` can take."""
    try:
        return max(1, round(float(target.max_health) * MAX_HIT_SHARE))
    except Exception:
        return 10 ** 9
