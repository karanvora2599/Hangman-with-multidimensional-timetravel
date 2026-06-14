"""Core game engine: adversarial AI, rendering, scoring."""

import math
import os
from collections import Counter

from .colors import C
from .words import STAGES


# -- Adversarial AI ------------------------------------------------------------

def positional_entropy(candidates, revealed_pos):
    """
    Average Shannon entropy of letter distributions at unrevealed positions.

    High entropy -> player can't predict which letter comes next -> harder.
    Low entropy  -> one letter dominates most positions -> easy to guess.
    """
    n = len(candidates)
    if n <= 1:
        return 0.0
    word_len    = len(candidates[0][0])
    total_h, count = 0.0, 0
    for pos in range(word_len):
        if pos in revealed_pos:
            continue
        freq = Counter(w[pos] for w, _ in candidates)
        h    = -sum((c / n) * math.log2(c / n) for c in freq.values())
        total_h += h
        count   += 1
    return total_h / count if count else 0.0


def evil_guess(letter, candidates, revealed):
    """
    Entropy-weighted adversarial partition.

    For each partition produced by guessing `letter`, score:
        (pool_size x (1 + positional_entropy),   # primary
         pool_size,                                # secondary
         -reveals)                                 # tertiary (fewer = harder)

    Returns (winning_positions_tuple, surviving_candidates).
    """
    groups = {}
    for word, cat in candidates:
        pos = tuple(i for i, c in enumerate(word) if c == letter)
        groups.setdefault(pos, []).append((word, cat))

    def score(pos_tuple, group):
        if not group:
            return (0.0, 0, 0)
        new_rev = set(revealed.keys()) | set(pos_tuple)
        n = len(group)
        h = positional_entropy(group, new_rev)
        return (n * (1.0 + h), n, -len(pos_tuple))

    best = max(groups, key=lambda p: score(p, groups[p]))
    return best, groups[best]


# -- Rendering -----------------------------------------------------------------

def clr():
    os.system('cls' if os.name == 'nt' else 'clear')


def draw_gallows(wrong, max_wrong):
    stage = min(round(wrong / max_wrong * 6), 6)
    col   = (C.GRN               if wrong == 0              else
             C.YLW               if wrong <= max_wrong // 2 else
             C.RED               if wrong < max_wrong       else
             C.MAG + C.BLD)
    print(f"\n{col}{STAGES[stage]}{C.RST}")


def draw_word(revealed, length):
    parts = [
        f"{C.GRN}{C.BLD}{revealed[i]}{C.RST}" if i in revealed
        else f"{C.DIM}_{C.RST}"
        for i in range(length)
    ]
    print(f"\n  {' '.join(parts)}\n")
    return len(revealed) == length


def draw_alphabet(guessed, hits):
    row = []
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if ch in guessed:
            col = C.GRN if ch in hits else C.RED + C.DIM
        else:
            col = C.WHT
        row.append(f"{col}{ch}{C.RST}")
    print("  " + "  ".join(row[:13]))
    print("  " + "  ".join(row[13:]))


# -- Scoring -------------------------------------------------------------------

def calc_score(length, wrong, max_wrong, diff):
    base    = {'easy': 100, 'medium': 250, 'hard': 500, 'nightmare': 1000}[diff]
    perfect = 500 if wrong == 0 else 0
    eff     = max(0.0, (max_wrong - wrong) / max_wrong)
    return int(base * eff + perfect + length * 10)


def show_word_analysis(word, diff, pool, model):
    """Print n-gram perplexity analysis of the word after each game."""
    pool_words = [w for w, _ in pool[diff]]
    s   = model.stars(word, pool_words)
    p   = model.perplexity(word)
    lbl = model.label(word)
    print(f"  {C.DIM}Char complexity : {s}  ({lbl}, perplexity {p:.1f}){C.RST}")
