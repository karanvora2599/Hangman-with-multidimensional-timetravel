"""Multiverse Hangman -- time-travel across parallel adversarial universes."""

import random
from collections import Counter

from .colors import C
from .words import MAX_WRONG
from .engine import (
    clr, draw_gallows, draw_word, draw_alphabet,
    calc_score, show_word_analysis, evil_guess,
)
from .ui import HAS_RICH, console, mv_table, game_prompt, MV_COMPLETER


class Timeline:
    """
    One parallel timeline with its own adversarial candidate pool.

    Each branch is an independent universe: the hidden word evolves separately
    via the evil AI, so guessing the same letter may HIT in one timeline and
    MISS in another (divergence).
    """

    _counter = 0

    @classmethod
    def reset(cls):
        cls._counter = 0

    @classmethod
    def _alloc(cls):
        n   = cls._counter + 1
        lbl = chr(ord('A') + cls._counter % 26)
        cls._counter += 1
        return n, lbl

    def __init__(self, candidates, max_wrong, state=None):
        """
        candidates : word pool for this timeline (already filtered if branching)
        max_wrong  : wrong-guess limit
        state      : optional dict {wrong, revealed, guessed, hits} to inherit
                     -- used when forking from an existing timeline's state
        """
        self.num, self.label = Timeline._alloc()
        self.candidates = list(candidates)
        self.max_wrong  = max_wrong
        self.history    = []       # undo stack -- each entry is a full state snapshot
        self.echo_log   = set()    # letters already echoed in this TL (one-shot)
        self.alive      = True

        if state is None:
            self.wrong    = 0
            self.revealed = {}
            self.guessed  = set()
            self.hits     = set()
        else:
            self.wrong    = state['wrong']
            self.revealed = dict(state['revealed'])
            self.guessed  = set(state['guessed'])
            self.hits     = set(state['hits'])

    @property
    def word_len(self):
        return len(self.candidates[0][0]) if self.candidates else 0

    @property
    def solved(self):
        return self.word_len > 0 and len(self.revealed) >= self.word_len

    @property
    def dead(self):
        return self.wrong >= self.max_wrong

    def snapshot(self):
        """Push current state onto the undo stack before each guess."""
        self.history.append({
            'candidates': list(self.candidates),
            'revealed':   dict(self.revealed),
            'guessed':    set(self.guessed),
            'hits':       set(self.hits),
            'wrong':      self.wrong,
        })

    def state_dict(self):
        return {
            'wrong':    self.wrong,
            'revealed': dict(self.revealed),
            'guessed':  set(self.guessed),
            'hits':     set(self.hits),
        }

    def progress_bar(self, width=6):
        filled = round(self.wrong / self.max_wrong * width)
        col    = (C.RED + C.BLD if self.dead else
                  C.RED         if filled >= 4 else
                  C.YLW         if filled >= 2 else C.GRN)
        return col + '#' * filled + C.DIM + '-' * (width - filled) + C.RST


# -- Helper functions ----------------------------------------------------------

def _branch_pool(nightmare_pool, word_len, parent):
    """
    Fresh candidate pool for a new branch (>b command).

    Filters nightmare_pool to words consistent with the player's current
    state: hits must appear at revealed positions, miss-letters must not
    appear anywhere.  Because the pool is rebuilt from scratch (not copied
    from parent.candidates), the resulting hidden word is almost certainly
    different -- a true parallel universe.
    """
    misses   = parent.guessed - parent.hits
    filtered = [
        (w, c) for w, c in nightmare_pool
        if len(w) == word_len
        and all(w[pos] == letter for pos, letter in parent.revealed.items())
        and not any(m in w for m in misses)
    ]
    if filtered:
        return filtered
    return [(w, c) for w, c in nightmare_pool if len(w) == word_len]


def _mv_overview(timelines, active_idx, chronons, word_len, wins=0, played=0):
    """Print the session header + one summary line per timeline."""
    avail  = sum(1 for t in timelines if t.alive)
    ch_col = C.CYN if chronons > 2 else C.YLW if chronons > 0 else C.RED
    ch_bar = ch_col + '*' * chronons + C.DIM + '.' * max(0, 5 - chronons) + C.RST

    print(f"\n{C.MAG}{C.BLD}  MULTIVERSE HANGMAN{C.RST}"
          f"  |  Chronons [{ch_bar}]  |  Timelines: {len(timelines)}"
          f"  {C.DIM}(alive: {avail})  W/L: {wins}/{played}{C.RST}")

    if HAS_RICH and console is not None:
        tbl = mv_table(timelines, active_idx, word_len)
        if tbl is not None:
            console.print(tbl)
            return

    # ANSI fallback
    print(f"  {'-' * 60}")
    for i, tl in enumerate(timelines):
        pattern = ''
        for p in range(word_len):
            if p in tl.revealed:
                pattern += f"{C.WHT}{tl.revealed[p]}{C.RST}"
            elif tl.dead:
                pattern += f"{C.RED}{C.DIM}?{C.RST}"
            else:
                pattern += f"{C.DIM}.{C.RST}"

        if tl.solved:
            status_col, status_txt = C.GRN + C.BLD, ' SOLVED'
        elif tl.dead:
            status_col, status_txt = C.RED + C.DIM, ' DEAD  '
        elif i == active_idx:
            status_col, status_txt = C.CYN + C.BLD, ' ACTIVE'
        else:
            status_col, status_txt = C.DIM,          '       '

        lbl_col = (C.CYN + C.BLD if i == active_idx else
                   C.GRN         if tl.solved        else
                   C.RED + C.DIM if tl.dead          else C.WHT)
        bar = tl.progress_bar()

        print(f"  {lbl_col}TL-{tl.label}{C.RST}"
              f"  [{bar}] {tl.wrong}/{tl.max_wrong}"
              f"  pool:{len(tl.candidates):3d}"
              f"  [{pattern}]"
              f"  {status_col}{status_txt}{C.RST}")

    print(f"  {'-' * 60}")


def _mv_help():
    print(f"""
  {C.YLW}{C.BLD}Multiverse Commands{C.RST}

  {C.WHT}[letter]      {C.RST}Guess a letter in the ACTIVE timeline
  {C.WHT}[word]        {C.RST}Full-word guess in the active timeline

  {C.MAG}>b            {C.RST}Branch  -- spawn a parallel universe RIGHT NOW.
                  New TL inherits your wrong-count and revealed
                  letters, but chases a DIFFERENT word.  {C.DIM}(-2 chronons){C.RST}

  {C.CYN}>r            {C.RST}Rewind  -- spawn a NEW timeline branched from 1 guess
                  ago in the active TL.  Active TL stays unchanged.
                  Same word pool, earlier state.  {C.DIM}(-2 chronons){C.RST}

  {C.WHT}>s N          {C.RST}Switch  -- make timeline N the active one  (free)
  {C.WHT}>e L N        {C.RST}Echo    -- peek: what would happen if you guessed letter
                  L in timeline N?  Reports HIT/MISS + pool change.
                  Each letter can only be echoed once per TL.  {C.DIM}(-1 chronon){C.RST}
  {C.WHT}>x            {C.RST}Collapse -- abandon the active timeline  (free)
  {C.WHT}>h            {C.RST}Hint    -- force-reveal one letter  (costs 1 wrong guess)
  {C.WHT}>?            {C.RST}Show this help screen

  {C.DIM}Win : solve ANY timeline.
  Loss: ALL timelines dead (wrong == max_wrong).
  Max 4 parallel timelines.{C.RST}
""")
    input(f"  {C.DIM}[Enter to continue]{C.RST}")


def play_multiverse(pool, model, session_score, wins, played):
    """
    Multidimensional time-travel hangman -- always Nightmare difficulty.

    Every time-travel action (>b or >r) creates a NEW branch; no timeline
    is ever mutated by a time-travel command.  Only forward guesses mutate
    the active timeline.
    """
    diff      = 'nightmare'
    max_wrong = MAX_WRONG[diff]

    Timeline.reset()

    nightmare_pool = list(pool[diff])
    random.shuffle(nightmare_pool)
    lc       = Counter(len(w) for w, _ in nightmare_pool)
    word_len = lc.most_common(1)[0][0]
    base     = [(w, c) for w, c in nightmare_pool if len(w) == word_len]

    timelines  = [Timeline(base, max_wrong)]
    active_idx = 0
    chronons   = 5
    hint_used  = set()

    def atl():
        return timelines[active_idx]

    def flash(msg):
        print(f"\n  {msg}")
        input(f"  {C.DIM}[Enter]{C.RST}")

    while True:
        clr()
        tl = atl()

        # -- Victory -----------------------------------------------------------
        won_tl = next((t for t in timelines if t.solved), None)
        if won_tl:
            final = ''.join(won_tl.revealed.get(i, '?') for i in range(word_len))
            _mv_overview(timelines, active_idx, chronons, word_len, wins, played)
            draw_gallows(won_tl.wrong, max_wrong)
            draw_word(won_tl.revealed, word_len)

            alive_bonus = sum(1 for t in timelines if not t.dead)
            tl_mult     = 1.0 + 0.5 * max(0, len(timelines) - 1)
            ch_mult     = 1.25 if chronons == 0 else 1.0
            base_pts    = calc_score(word_len, won_tl.wrong, max_wrong, diff)
            surv_pts    = 50 * max(0, alive_bonus - 1)
            ch_pts      = chronons * 20
            earned      = int(base_pts * tl_mult * ch_mult) + surv_pts + ch_pts
            session_score += earned

            print(f"\n{C.GRN}{C.BLD}  TL-{won_tl.label} SOLVED!   Word: {final}{C.RST}")
            print(f"  {C.YLW}+{earned} pts  "
                  f"(base {base_pts} x{tl_mult:.1f}tl x{ch_mult}ch "
                  f"+{surv_pts}surv +{ch_pts}ch){C.RST}")
            show_word_analysis(final, diff, pool, model)
            input(f"\n  {C.DIM}[Enter to continue]{C.RST}")
            return session_score, True

        # -- Mark dead ---------------------------------------------------------
        for t in timelines:
            if t.dead:
                t.alive = False

        # -- Loss --------------------------------------------------------------
        if all(not t.alive for t in timelines):
            rev_word = (timelines[0].candidates[0][0]
                        if timelines[0].candidates else '?' * word_len)
            for i, ch in enumerate(rev_word):
                timelines[0].revealed[i] = ch
            _mv_overview(timelines, active_idx, chronons, word_len, wins, played)
            draw_gallows(max_wrong, max_wrong)
            draw_word(timelines[0].revealed, word_len)
            print(f"{C.RED}{C.BLD}  ALL TIMELINES COLLAPSED.  "
                  f"(One possible word was: {rev_word}){C.RST}")
            show_word_analysis(rev_word, diff, pool, model)
            input(f"\n  {C.DIM}[Enter to continue]{C.RST}")
            return session_score, False

        # -- Auto-switch away from dead TL -------------------------------------
        if not tl.alive:
            for i, t in enumerate(timelines):
                if t.alive:
                    active_idx = i
                    tl = t
                    break

        # -- Render ------------------------------------------------------------
        _mv_overview(timelines, active_idx, chronons, word_len, wins, played)
        print(f"\n  {C.BLD}Active: TL-{tl.label}{C.RST}  "
              f"{C.DIM}Nightmare | {word_len} letters{C.RST}\n")
        draw_gallows(tl.wrong, max_wrong)
        rem = max_wrong - tl.wrong
        rc  = C.GRN if rem > 2 else C.YLW if rem > 1 else C.RED + C.BLD
        print(f"  Guesses left: {rc}{rem}{C.RST}\n")
        draw_word(tl.revealed, word_len)
        draw_alphabet(tl.guessed, tl.hits)
        print(f"\n  {C.DIM}>b new-word-branch(-2)  >r past-branch(-2)  >s N switch  "
              f">e L N echo(-1)  >x collapse  >h hint  >? help{C.RST}")

        ch_str = '*' * chronons + '.' * max(0, 5 - chronons)
        toolbar = (
            f'<b>Score:</b> {session_score}  |  '
            f'<b>W/L:</b> {wins}/{played}  |  '
            f'<b>TL-{tl.label}</b>  |  '
            f'<ansimagenta>&#8987; {ch_str} ({chronons})</ansimagenta>  |  '
            f'Tab: &gt;b &gt;r &gt;s &gt;e &gt;x &gt;h'
        )
        raw = game_prompt(
            f'\n  TL-{tl.label} > ',
            toolbar=toolbar,
            completer=MV_COMPLETER,
        ).strip().upper()
        if not raw:
            continue

        # -- > commands --------------------------------------------------------
        if raw.startswith('>'):
            cmd = raw[1:].strip()

            if cmd in ('?', 'HELP'):
                _mv_help()

            # >b -- new parallel universe: same state, fresh word
            elif cmd == 'B':
                if chronons < 2:
                    flash(f"{C.RED}Need 2 chronons to branch (have {chronons}).{C.RST}")
                elif len(timelines) >= 4:
                    flash(f"{C.RED}Multiverse at capacity -- max 4 timelines.{C.RST}")
                else:
                    new_pool = _branch_pool(nightmare_pool, word_len, tl)
                    new_tl   = Timeline(new_pool, max_wrong, state=tl.state_dict())
                    timelines.append(new_tl)
                    chronons -= 2
                    flash(f"{C.MAG}Branched!{C.RST}  "
                          f"TL-{new_tl.label} forked from TL-{tl.label}.  "
                          f"Same player state, DIFFERENT word.  "
                          f"{C.DIM}Pool: {len(new_pool)} candidates.  "
                          f"(-2 chronons -> {chronons} left){C.RST}")

            # >r -- time-branch from 1 guess ago: same word, earlier state
            elif cmd == 'R':
                if chronons < 2:
                    flash(f"{C.RED}Need 2 chronons to time-branch (have {chronons}).{C.RST}")
                elif len(timelines) >= 4:
                    flash(f"{C.RED}Multiverse at capacity -- max 4 timelines.{C.RST}")
                elif not tl.history:
                    flash(f"{C.YLW}TL-{tl.label} has no history yet.{C.RST}")
                else:
                    snap   = tl.history[-1]    # peek -- current TL stays unchanged
                    new_tl = Timeline(list(snap['candidates']), max_wrong, state={
                        'wrong':    snap['wrong'],
                        'revealed': dict(snap['revealed']),
                        'guessed':  set(snap['guessed']),
                        'hits':     set(snap['hits']),
                    })
                    timelines.append(new_tl)
                    chronons -= 2
                    flash(f"{C.CYN}Time-branch!{C.RST}  "
                          f"TL-{new_tl.label} forked from 1 guess ago in TL-{tl.label}.  "
                          f"Same word, earlier state -- TL-{tl.label} is untouched.  "
                          f"{C.DIM}(-2 chronons -> {chronons} left){C.RST}")

            # >s N -- switch active timeline
            elif cmd.startswith('S'):
                try:
                    n = int(cmd[1:].strip()) - 1
                    if 0 <= n < len(timelines) and timelines[n].alive:
                        active_idx = n
                    elif 0 <= n < len(timelines):
                        flash(f"{C.RED}TL-{timelines[n].label} is dead.{C.RST}")
                    else:
                        flash(f"{C.RED}No such timeline.{C.RST}")
                except ValueError:
                    flash(f"{C.RED}Usage: >s 2  (switch to timeline 2){C.RST}")

            # >e L N -- echo: peek at letter L in timeline N
            elif cmd.startswith('E'):
                parts = cmd[1:].split()
                try:
                    if len(parts) == 2:
                        el, en = parts[0], int(parts[1]) - 1
                    elif len(parts) == 1 and len(parts[0]) >= 2:
                        el, en = parts[0][0], int(parts[0][1:]) - 1
                    else:
                        raise ValueError
                    if not el.isalpha() or len(el) != 1:
                        raise ValueError
                    if not (0 <= en < len(timelines)):
                        raise ValueError

                    target = timelines[en]
                    if not target.alive:
                        flash(f"{C.RED}TL-{target.label} is dead.{C.RST}")
                    elif el in target.guessed:
                        outcome = (f"{C.GRN}HIT{C.RST}" if el in target.hits
                                   else f"{C.RED}MISS{C.RST}")
                        flash(f"Echo {C.BLD}{el}{C.RST} in TL-{target.label}: "
                              f"{outcome}  (already guessed -- free info)")
                    elif el in target.echo_log:
                        flash(f"{C.YLW}{el} already echoed in TL-{target.label}; "
                              f"each letter can only be echoed once per TL.{C.RST}")
                    elif chronons < 1:
                        flash(f"{C.RED}Need 1 chronon to echo (have {chronons}).{C.RST}")
                    else:
                        target.echo_log.add(el)
                        chronons -= 1
                        positions, survivors = evil_guess(el, target.candidates,
                                                          target.revealed)
                        result = f"{C.GRN}HIT{C.RST}" if positions else f"{C.RED}MISS{C.RST}"
                        delta  = f"{len(target.candidates)} -> {len(survivors)}"
                        flash(f"Echo {C.BLD}{el}{C.RST} in TL-{target.label}: "
                              f"{result}  {C.DIM}(pool {delta})  "
                              f"(-1 chronon -> {chronons} left){C.RST}")
                except (ValueError, IndexError):
                    flash(f"{C.RED}Usage: >e A 2  or  >eA2  "
                          f"(echo letter A in timeline 2){C.RST}")

            # >x -- collapse active timeline
            elif cmd == 'X':
                if sum(1 for t in timelines if t.alive) <= 1:
                    flash(f"{C.RED}Cannot collapse the last surviving timeline.{C.RST}")
                else:
                    tl.alive = False
                    flash(f"{C.YLW}TL-{tl.label} collapsed.{C.RST}")

            # >h -- hint (force-reveal one letter, costs 1 wrong guess)
            elif cmd == 'H':
                if tl.num in hint_used:
                    flash(f"{C.YLW}Hint already used in TL-{tl.label}.{C.RST}")
                elif tl.candidates:
                    unrevealed = [i for i in range(word_len) if i not in tl.revealed]
                    if unrevealed:
                        pos    = random.choice(unrevealed)
                        letter = Counter(
                            w[pos] for w, _ in tl.candidates
                        ).most_common(1)[0][0]
                        positions, tl.candidates = evil_guess(letter, tl.candidates,
                                                               tl.revealed)
                        for p in positions:
                            tl.revealed[p] = letter
                        tl.hits.add(letter)
                        tl.guessed.add(letter)
                        tl.wrong += 1
                        hint_used.add(tl.num)

            else:
                flash(f"{C.RED}Unknown command '{raw}'. Type >? for help.{C.RST}")

        # -- Full-word guess ---------------------------------------------------
        elif len(raw) > 1 and raw.isalpha():
            tl.snapshot()
            target_word = tl.candidates[0][0] if tl.candidates else ''
            if raw == target_word:
                for i, ch in enumerate(raw):
                    tl.revealed[i] = ch
                    tl.hits.add(ch)
            else:
                tl.wrong += 1
                filtered = [(w, c) for w, c in tl.candidates if w != raw]
                if filtered:
                    tl.candidates = filtered

        # -- Single letter guess -----------------------------------------------
        elif len(raw) == 1 and raw.isalpha():
            if raw in tl.guessed:
                continue
            tl.snapshot()
            tl.guessed.add(raw)
            positions, tl.candidates = evil_guess(raw, tl.candidates, tl.revealed)
            if positions:
                for p in positions:
                    tl.revealed[p] = raw
                tl.hits.add(raw)
            else:
                tl.wrong += 1

            # Divergence notice: same letter gave different outcomes across TLs
            this_hit = raw in tl.hits
            diverged = [
                (t.label, raw in t.hits)
                for t in timelines
                if t is not tl and raw in t.guessed
                   and (raw in t.hits) != this_hit
            ]
            if diverged:
                here   = f"{C.GRN}HIT{C.RST}"  if this_hit else f"{C.RED}MISS{C.RST}"
                others = ', '.join(
                    f"TL-{lbl}: {C.GRN}HIT{C.RST}" if h else f"TL-{lbl}: {C.RED}MISS{C.RST}"
                    for lbl, h in diverged
                )
                print(f"\n  {C.MAG}{C.BLD}Divergence!{C.RST}  "
                      f"{C.MAG}'{raw}' is {here}{C.MAG} in TL-{tl.label}"
                      f" but {others}{C.RST}")
                input(f"  {C.DIM}[Enter]{C.RST}")
