"""Classic single-player hangman game loop."""

import random
from collections import Counter

from .colors import C
from .words import MAX_WRONG, EVIL_MODE
from .engine import (
    clr, draw_gallows, draw_word, draw_alphabet,
    calc_score, show_word_analysis, evil_guess, positional_entropy,
)
from .ui import game_prompt


def play(diff, pool, model, session_score, wins, played):
    max_wrong  = MAX_WRONG[diff]
    evil       = EVIL_MODE[diff]
    candidates = list(pool[diff])
    random.shuffle(candidates)

    if evil:
        word_len   = len(candidates[0][0])
        candidates = [(w, c) for w, c in candidates if len(w) == word_len]
        if not candidates:
            candidates = list(pool[diff])
            word_len   = len(candidates[0][0])
        category   = Counter(c for _, c in candidates).most_common(1)[0][0]
        fixed_word = ""
    else:
        fixed_word, category = candidates[0]
        word_len   = len(fixed_word)
        candidates = [(fixed_word, category)]

    revealed  = {}
    guessed   = set()
    hits      = set()
    wrong     = 0
    hint_used = False

    if fixed_word:
        for i, ch in enumerate(fixed_word):
            if not ch.isalpha():
                revealed[i] = ch

    while True:
        clr()

        evil_tag = f"  {C.MAG}[ENTROPY AI]{C.RST}" if evil else ""
        pool_tag = (
            f"  {C.DIM}[pool: {len(candidates)} words | "
            f"H={positional_entropy(candidates, set(revealed.keys())):.2f}]{C.RST}"
            if evil else ""
        )

        print(f"\n{C.YLW}{C.BLD}  HANGMAN  --  The Smart & Difficult Edition{C.RST}")
        print(f"  {'-' * 46}")
        print(
            f"  {C.CYN}Difficulty: {C.BLD}{diff.upper()}{C.RST}"
            f"  {C.YLW}Score: {C.BLD}{session_score}{C.RST}"
            f"  {C.GRN}W/L: {wins}/{played}{C.RST}"
            f"{evil_tag}"
        )
        if evil:
            print(f"  {C.DIM}Category: {category}  |  Letters: {word_len}{pool_tag}{C.RST}")
        else:
            print(f"  {C.DIM}Category: {category}  |  Letters: {word_len}{C.RST}")

        draw_gallows(wrong, max_wrong)

        rem = max_wrong - wrong
        rc  = (C.GRN if rem > max_wrong * 0.5 else
               C.YLW if rem > 1 else C.RED + C.BLD)
        print(f"  Guesses remaining: {rc}{rem}{C.RST}\n")

        won = draw_word(revealed, word_len)

        if won:
            final  = candidates[0][0]
            earned = calc_score(word_len, wrong, max_wrong, diff)
            session_score += earned
            print(f"{C.GRN}{C.BLD}  CORRECT! The word was: {final}{C.RST}")
            if wrong == 0:
                print(f"  {C.YLW}+{earned} pts  *** PERFECT!{C.RST}")
            else:
                print(f"  {C.YLW}+{earned} pts{C.RST}")
            show_word_analysis(final, diff, pool, model)
            input(f"\n  {C.DIM}[Enter to continue]{C.RST}")
            return session_score, True

        if wrong >= max_wrong:
            final = candidates[0][0]
            for i, ch in enumerate(final):
                revealed[i] = ch
            draw_word(revealed, word_len)
            print(f"{C.RED}{C.BLD}  GAME OVER. The word was: {final}{C.RST}")
            show_word_analysis(final, diff, pool, model)
            input(f"\n  {C.DIM}[Enter to continue]{C.RST}")
            return session_score, False

        draw_alphabet(guessed, hits)

        if not hint_used:
            print(f"\n  {C.DIM}[H] Hint - reveal one letter (costs 1 guess){C.RST}")

        pool_info = (f'Pool: {len(candidates)} words | '
                     if evil else '')
        toolbar = (
            f'<b>Score:</b> {session_score} &nbsp;|&nbsp; '
            f'<b>W/L:</b> {wins}/{played} &nbsp;|&nbsp; '
            f'{pool_info}'
            f'<b>{diff.upper()}</b>'
            + ('&nbsp; [ENTROPY AI]' if evil else '')
        )
        raw = game_prompt(
            '\n  Guess (letter or full word): ',
            toolbar=toolbar,
        ).strip().upper()

        if not raw:
            continue

        if len(raw) > 1 and raw.isalpha():
            target = candidates[0][0]
            if raw == target:
                for i, ch in enumerate(target):
                    revealed[i] = ch
                    hits.add(ch)
            else:
                wrong += 1
                if evil:
                    filtered = [(w, c) for w, c in candidates if w != raw]
                    if filtered:
                        candidates = filtered
            continue

        if raw == 'H' and not hint_used:
            hint_used  = True
            unrevealed = [i for i in range(word_len) if i not in revealed]
            if unrevealed:
                pos = random.choice(unrevealed)
                if evil:
                    letter     = Counter(w[pos] for w, _ in candidates).most_common(1)[0][0]
                    candidates = [(w, c) for w, c in candidates if w[pos] == letter]
                    revealed[pos] = letter
                    hits.add(letter)
                    guessed.add(letter)
                else:
                    letter = fixed_word[pos]
                    for i, ch in enumerate(fixed_word):
                        if ch == letter:
                            revealed[i] = ch
                    hits.add(letter)
                    guessed.add(letter)
                wrong += 1
            continue

        if len(raw) != 1 or not raw.isalpha():
            continue
        if raw in guessed:
            continue

        guessed.add(raw)

        if evil:
            positions, candidates = evil_guess(raw, candidates, revealed)
            if positions:
                for p in positions:
                    revealed[p] = raw
                hits.add(raw)
            else:
                wrong += 1
        else:
            if raw in fixed_word:
                for i, ch in enumerate(fixed_word):
                    if ch == raw:
                        revealed[i] = ch
                hits.add(raw)
            else:
                wrong += 1
