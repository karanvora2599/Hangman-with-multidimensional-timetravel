"""CLI entry point: mode/difficulty menus and main game loop."""

import os

from .colors import C
from .engine import clr
from .model import load_word_pool
from .classic import play
from .multiverse import play_multiverse


def choose_mode():
    print(f"\n{C.CYN}  Select mode:{C.RST}")
    print(f"  {C.WHT}[1] Classic       {C.RST}Standard hangman  (Easy → Nightmare)")
    print(f"  {C.MAG}[2] Multiverse    {C.RST}Time-travel across parallel universes")
    print(f"\n  {C.DIM}Multiverse: branch timelines, rewind turns, echo letters across dimensions.")
    print(f"  Every timeline chases a DIFFERENT word — nightmare difficulty only.{C.RST}")
    while True:
        ch = input(f"\n  Mode [1-2]: ").strip()
        if ch in '12':
            return int(ch)
        print(f"  {C.RED}Enter 1 or 2.{C.RST}")


def choose_diff():
    print(f"\n{C.CYN}  Select difficulty:{C.RST}")
    print(f"  {C.GRN}[1] Easy       {C.RST}8 guesses | common words")
    print(f"  {C.YLW}[2] Medium     {C.RST}7 guesses | uncommon words")
    print(f"  {C.RED}[3] Hard       {C.RST}6 guesses | rare words    +  {C.MAG}Entropy AI{C.RST}")
    print(f"  {C.MAG}[4] Nightmare  {C.RST}5 guesses | very rare     +  {C.MAG}Entropy AI{C.RST}")
    print(f"\n  {C.DIM}Entropy AI: picks the partition that maximises pool_size x positional_entropy.{C.RST}")
    while True:
        ch = input(f"\n  Choice [1-4]: ").strip()
        if ch in '1234':
            return ['easy', 'medium', 'hard', 'nightmare'][int(ch) - 1]
        print(f"  {C.RED}Enter 1, 2, 3, or 4.{C.RST}")


def main():
    if os.name == 'nt':
        os.system('')   # enable ANSI escape codes on Windows

    clr()
    print(f"""
{C.RED}{C.BLD}  HANGMAN  --  The Smart & Difficult Edition{C.RST}
  {'-' * 46}
  {C.DIM}Linguistic enhancements:
    Character trigram model    perplexity-based difficulty scoring
    Entropy-weighted AI        maximises pool ambiguity, not just size
    wordfreq integration       100k-word pool (if installed){C.RST}
""")

    pool, model, _ = load_word_pool()

    session_score = 0
    wins          = 0
    played        = 0

    while True:
        mode = choose_mode()

        if mode == 1:
            diff = choose_diff()
            input(f"\n  {C.DIM}[Enter to start]{C.RST}")
            session_score, won = play(diff, pool, model, session_score, wins, played)
        else:
            input(f"\n  {C.DIM}[Enter to enter the multiverse]{C.RST}")
            session_score, won = play_multiverse(pool, model, session_score, wins, played)

        played += 1
        wins   += won

        print(f"\n  {C.CYN}Session: {wins}/{played} won  |  Score: {session_score}{C.RST}")
        if input(f"  Play again? (y/n): ").strip().lower() != 'y':
            break

    clr()
    print(f"\n{C.RED}{C.BLD}  HANGMAN  --  Game Over{C.RST}")
    print(f"  {'-' * 46}")
    print(f"\n  {C.YLW}{C.BLD}Final Score : {session_score}{C.RST}")
    print(f"  {C.CYN}Games Won   : {wins} / {played}{C.RST}")
    if played:
        pct     = wins / played * 100
        verdict = (f"{C.GRN}Word master."  if pct >= 70 else
                   f"{C.YLW}Good effort."  if pct >= 40 else
                   f"{C.RED}The AI wins.")
        print(f"\n  {verdict}{C.RST}")
    print(f"\n  {C.DIM}Thanks for playing.{C.RST}\n")
