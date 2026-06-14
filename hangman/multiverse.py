"""Multiverse Hangman -- The Gunslinger saves innocents across parallel timelines."""

import random
from collections import Counter

from .colors import C
from .words import MAX_WRONG, EVIL_MODE, STAGES
from .engine import (
    clr, draw_gallows, draw_word, draw_alphabet,
    calc_score, show_word_analysis, evil_guess,
)
from .ui import HAS_RICH, console, mv_table, game_prompt, MV_COMPLETER


# Story flavor text keyed by difficulty
_DIFF_FLAVOR = {
    'easy':      "Wanderers and travelers.  Common words, 8 guesses.",
    'medium':    "Outcasts between worlds.  Uncommon words, 7 guesses.",
    'hard':      "The cursed and forgotten.  Rare words, 6 guesses.  The AI resists.",
    'nightmare': "The Tower's chosen sacrifices.  Very rare words, 5 guesses.  The AI fights hard.",
}

_DIFF_PRISONER = {
    'easy':      "a wanderer",
    'medium':    "an outcast",
    'hard':      "a cursed soul",
    'nightmare': "a chosen sacrifice",
}


class Timeline:
    """
    One parallel timeline -- a universe where the Gunslinger pursues
    a specific innocent's True Name.

    Easy/Medium: candidates holds a single fixed word (non-adversarial).
    Hard/Nightmare: candidates is the full adversarial pool; the word
    shifts on each guess until cornered.
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
        self.num, self.label = Timeline._alloc()
        self.candidates = list(candidates)
        self.max_wrong  = max_wrong
        self.history    = []
        self.echo_log   = set()
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
        self.history.append({
            'candidates': list(self.candidates),
            'revealed':   dict(self.revealed),
            'guessed':    set(self.guessed),
            'hits':       set(self.hits),
            'wrong':      self.wrong,
            'guess':      None,
            'hit':        None,
        })

    def record_guess(self, guess, hit):
        if self.history:
            self.history[-1]['guess'] = guess
            self.history[-1]['hit']   = hit

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


# -- Branch helpers ------------------------------------------------------------

def _make_branch_candidates(diff_pool, word_len, guessed, hits, revealed, evil,
                             current_word=''):
    """
    Build a candidate list for a new branched timeline.

    evil=True  -> returns full filtered pool (adversarial Hard/Nightmare)
    evil=False -> returns a list with ONE new word, different from current_word
                  (fixed-word Easy/Medium)
    """
    misses  = guessed - hits
    exclude = {current_word} if not evil and current_word else set()

    filtered = [
        (w, c) for w, c in diff_pool
        if len(w) == word_len
        and w not in exclude
        and all(w[pos] == letter for pos, letter in revealed.items())
        and not any(m in w for m in misses)
    ]
    if not filtered:
        filtered = [
            (w, c) for w, c in diff_pool
            if len(w) == word_len and w not in exclude
        ]
    if not filtered:
        filtered = [(w, c) for w, c in diff_pool if len(w) == word_len]

    if evil:
        return filtered
    return [random.choice(filtered)]


# -- Story intro ---------------------------------------------------------------

def _story_intro(diff):
    """Show the Dark Tower narrative intro screen."""
    clr()

    story_lines = [
        "The Dark Tower stands at the center of all existence,",
        "its beams threading through infinite parallel worlds.",
        "Something has gone wrong.",
        "",
        "Innocents have been condemned across the timelines --",
        "each sentenced to hang unless their True Name is spoken",
        "before the last breath is drawn.",
        "",
        "You are the last Gunslinger.",
        "",
        "You carry five Chronons -- shards of todash energy",
        "that let you walk between worlds, bend time backward,",
        "and branch into realities where the truth is different.",
        "",
        "Find the True Name.  Free the innocent.",
        "The Tower watches.  Ka wills it.",
    ]

    if HAS_RICH and console is not None:
        from rich.panel import Panel
        from rich.text import Text

        body = Text()
        for line in story_lines:
            if line:
                body.append(f"  {line}\n")
            else:
                body.append("\n")

        console.print()
        console.print(Panel(
            body,
            title='[bold magenta]THE GUNSLINGER[/bold magenta]',
            border_style='magenta',
            padding=(1, 2),
        ))
        console.print(
            f"\n  [dim]Mission: [bold]{diff.upper()}[/bold]  --  "
            f"{_DIFF_FLAVOR[diff]}[/dim]\n"
        )
    else:
        print(f"\n{C.MAG}{C.BLD}  THE GUNSLINGER{C.RST}")
        print(f"  {'=' * 52}")
        for line in story_lines:
            print(f"  {C.DIM}{line}{C.RST}" if line else "")
        print(f"  {'=' * 52}")
        print(f"\n  {C.DIM}Mission: {C.BLD}{diff.upper()}{C.RST}"
              f"  {C.DIM}--  {_DIFF_FLAVOR[diff]}{C.RST}\n")

    input(f"  {C.DIM}[Enter to step through the thinny]{C.RST}")


# -- Timeline overview ---------------------------------------------------------

def _mv_overview(timelines, active_idx, chronons, word_len, wins=0, played=0,
                 diff='nightmare'):
    avail  = sum(1 for t in timelines if t.alive)
    ch_col = C.CYN if chronons > 2 else C.YLW if chronons > 0 else C.RED
    ch_bar = ch_col + '*' * chronons + C.DIM + '.' * max(0, 5 - chronons) + C.RST

    print(f"\n{C.MAG}{C.BLD}  THE GUNSLINGER{C.RST}"
          f"  |  Chronons [{ch_bar}]"
          f"  |  Timelines: {len(timelines)}"
          f"  {C.DIM}(alive: {avail})  Saved: {wins}/{played}"
          f"  [{diff.upper()}]{C.RST}")

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
            status_col, status_txt = C.GRN + C.BLD, '  FREED '
        elif tl.dead:
            status_col, status_txt = C.RED + C.DIM, '  LOST  '
        elif i == active_idx:
            status_col, status_txt = C.CYN + C.BLD, '  ACTIVE'
        else:
            status_col, status_txt = C.DIM,          '        '

        lbl_col = (C.CYN + C.BLD if i == active_idx else
                   C.GRN         if tl.solved        else
                   C.RED + C.DIM if tl.dead          else C.WHT)

        print(f"  {lbl_col}TL-{tl.label}{C.RST}"
              f"  [{tl.progress_bar()}] {tl.wrong}/{tl.max_wrong}"
              f"  pool:{len(tl.candidates):3d}"
              f"  [{pattern}]"
              f"  {status_col}{status_txt}{C.RST}")

    print(f"  {'-' * 60}")


# -- History picker (Time Machine) ---------------------------------------------

def _history_picker(tl, word_len):
    """
    Visual gallery of all past states in a timeline.
    The Gunslinger walks the timestream and picks a moment to branch from.
    Returns the chosen snapshot dict, or None if cancelled.
    """
    clr()

    if not tl.history:
        print(f"\n  {C.YLW}The timestream of TL-{tl.label} holds no recorded moments yet.{C.RST}")
        input(f"  {C.DIM}[Enter]{C.RST}")
        return None

    print(f"\n  {C.MAG}{C.BLD}THE TIMESTREAM  --  TL-{tl.label}{C.RST}  "
          f"{C.DIM}({len(tl.history)} moments recorded){C.RST}")
    print(f"  {C.DIM}Walk the stream.  Pick a moment to branch from.{C.RST}\n")

    current_snap = {
        'candidates': list(tl.candidates),
        'revealed':   dict(tl.revealed),
        'guessed':    set(tl.guessed),
        'hits':       set(tl.hits),
        'wrong':      tl.wrong,
        'guess':      None,
        'hit':        None,
        '_current':   True,
    }
    all_states = tl.history + [current_snap]

    if HAS_RICH and console is not None:
        from rich.columns import Columns
        from rich.panel import Panel
        from rich.text import Text

        panels = []
        for i, snap in enumerate(all_states):
            is_current = snap.get('_current', False)
            stage      = min(round(snap['wrong'] / tl.max_wrong * 6), 6)
            wrong_pct  = snap['wrong'] / tl.max_wrong
            gal_style  = ('bold red'  if wrong_pct >= 1.0 else
                          'red'       if wrong_pct >= 0.6 else
                          'yellow'    if wrong_pct >= 0.3 else 'green')

            content = Text()
            content.append(STAGES[stage].rstrip(), style=gal_style)
            content.append('\n\n')

            for p in range(word_len):
                letter = snap['revealed'].get(p)
                content.append(letter if letter else '_',
                               style='bold white' if letter else 'dim')
                if p < word_len - 1:
                    content.append(' ')
            content.append(f"\nwrong: {snap['wrong']}/{tl.max_wrong}\n", style='dim')

            g, h = snap.get('guess'), snap.get('hit')
            if is_current:
                content.append('(present)', style='bold cyan')
            elif g and g.startswith('HINT:'):
                content.append(f"hint -> {g[5:]}", style='bold yellow')
            elif g:
                content.append(f"{g}: ", style='bold')
                content.append('TRUE' if h else 'VOID',
                               style='bold green' if h else 'bold red')
            else:
                content.append('origin', style='dim')

            label        = '[now]' if is_current else f'[{i}]'
            border_style = ('bold cyan' if is_current else
                            'cyan'      if i == 0     else 'white')
            panels.append(Panel(content, title=label, border_style=border_style,
                                expand=False))

        console.print(Columns(panels, equal=False, expand=False))

    else:
        col_w = word_len * 2 + 2
        print(f"  {C.DIM}{'Step':<6}{'Bar':<10}{'Wrong':<7}{'Pattern':<{col_w}}Guess{C.RST}")
        print(f"  {'-' * 55}")
        for i, snap in enumerate(all_states):
            is_current = snap.get('_current', False)
            pat    = ' '.join(snap['revealed'].get(p, '_') for p in range(word_len))
            filled = round(snap['wrong'] / tl.max_wrong * 6)
            bc     = C.RED if filled >= 4 else C.YLW if filled >= 2 else C.GRN
            bar    = f"[{bc}{'#'*filled}{C.DIM}{'-'*(6-filled)}{C.RST}]"
            g, h   = snap.get('guess'), snap.get('hit')

            if is_current:
                lbl   = f"{C.BLD}{C.CYN}[now]{C.RST}"
                g_str = f"{C.CYN}(present){C.RST}"
            else:
                lbl = f"{C.CYN}[{i}]{C.RST}"
                if g and g.startswith('HINT:'):
                    g_str = f"{C.YLW}hint->{g[5:]}{C.RST}"
                elif g:
                    g_str = (f"{C.GRN}{g}: TRUE{C.RST}" if h
                             else f"{C.RED}{g}: VOID{C.RST}")
                else:
                    g_str = f"{C.DIM}origin{C.RST}"

            print(f"  {lbl:<5}  {bar}  {snap['wrong']}/{tl.max_wrong}   "
                  f"{pat:<{col_w}}  {g_str}")
        print(f"  {'-' * 55}")

    n = len(tl.history)
    while True:
        raw = input(f"\n  Pick a moment [0-{n-1}] (Enter = step back to present): ").strip()
        if not raw:
            return None
        try:
            idx = int(raw)
            if 0 <= idx < n:
                return tl.history[idx]
            print(f"  {C.RED}Enter a number from 0 to {n-1}.{C.RST}")
        except ValueError:
            print(f"  {C.RED}Enter a number.{C.RST}")


# -- Help screen ---------------------------------------------------------------

def _mv_help():
    print(f"""
  {C.YLW}{C.BLD}Gunslinger Commands{C.RST}

  {C.WHT}[letter]      {C.RST}Guess a letter in the ACTIVE timeline
  {C.WHT}[word]        {C.RST}Guess the full True Name in the active timeline

  {C.MAG}>b            {C.RST}Branch -- step sideways through the thinny RIGHT NOW.
                  New timeline: same player state, DIFFERENT prisoner.
                  {C.DIM}(-2 chronons){C.RST}

  {C.CYN}>r            {C.RST}Time Machine -- walk the timestream of the active TL,
                  pick any recorded moment, then choose:
                    (s) same prisoner  /  (d) different prisoner
                  The active TL is never changed.  {C.DIM}(-2 chronons){C.RST}

  {C.WHT}>s N          {C.RST}Switch -- make timeline N the active one  (free)
  {C.WHT}>e L N        {C.RST}Echo   -- peer across the thinny: what would guessing
                  letter L do in timeline N?  HIT/MISS + pool change.
                  Once per letter per TL.  {C.DIM}(-1 chronon){C.RST}
  {C.WHT}>x            {C.RST}Collapse -- let this timeline fade into todash  (free)
  {C.WHT}>h            {C.RST}Hint    -- the Tower whispers a letter  (costs 1 wrong guess)
  {C.WHT}>?            {C.RST}Show this screen

  {C.DIM}Win : speak the True Name in ANY timeline.
  Loss: ALL timelines dead.
  Max 4 parallel timelines.  You start with 5 Chronons.{C.RST}
""")
    input(f"  {C.DIM}[Enter to continue]{C.RST}")


# -- Guess flavor text ---------------------------------------------------------

def _guess_flavor(remaining, max_wrong):
    """Short story beat based on guesses remaining."""
    if remaining == max_wrong:
        return ""
    fraction = remaining / max_wrong
    if fraction > 0.6:
        return f"  {C.DIM}The gallows creak in the wind.{C.RST}\n"
    if fraction > 0.3:
        return f"  {C.YLW}{C.DIM}Ka draws near, Gunslinger.{C.RST}\n"
    if remaining == 1:
        return f"  {C.RED}{C.BLD}Last chance.  The Tower grows impatient.{C.RST}\n"
    return f"  {C.RED}Time bleeds away.{C.RST}\n"


# -- Main game loop ------------------------------------------------------------

def play_multiverse(pool, model, session_score, wins, played, diff='nightmare'):
    """
    The Gunslinger hunts True Names across parallel timelines.

    All four difficulties are supported:
      Easy/Medium  -- fixed word per timeline (not adversarial)
      Hard/Nightmare -- adversarial AI per timeline
    """
    max_wrong = MAX_WRONG[diff]
    evil      = EVIL_MODE[diff]

    _story_intro(diff)
    clr()

    Timeline.reset()

    diff_pool = list(pool[diff])
    random.shuffle(diff_pool)

    # Pick a consistent word length across all timelines
    lc       = Counter(len(w) for w, _ in diff_pool)
    word_len = lc.most_common(1)[0][0]
    same_len = [(w, c) for w, c in diff_pool if len(w) == word_len]

    if evil:
        base = same_len                              # full adversarial pool
    else:
        base = [random.choice(same_len)]             # single fixed word

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
            _mv_overview(timelines, active_idx, chronons, word_len, wins, played, diff)
            draw_gallows(won_tl.wrong, max_wrong)
            print(f"  {C.DIM}True Name:{C.RST}")
            draw_word(won_tl.revealed, word_len)

            alive_bonus = sum(1 for t in timelines if not t.dead)
            tl_mult     = 1.0 + 0.5 * max(0, len(timelines) - 1)
            ch_mult     = 1.25 if chronons == 0 else 1.0
            base_pts    = calc_score(word_len, won_tl.wrong, max_wrong, diff)
            surv_pts    = 50 * max(0, alive_bonus - 1)
            ch_pts      = chronons * 20
            earned      = int(base_pts * tl_mult * ch_mult) + surv_pts + ch_pts
            session_score += earned

            print(f"\n{C.GRN}{C.BLD}  TRUE NAME FOUND.  TL-{won_tl.label} freed.{C.RST}"
                  f"  {C.GRN}Word: {final}{C.RST}")
            print(f"  {C.YLW}The innocent goes free.  Ka wills it, Gunslinger.{C.RST}")
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
            _mv_overview(timelines, active_idx, chronons, word_len, wins, played, diff)
            draw_gallows(max_wrong, max_wrong)
            print(f"  {C.DIM}True Name:{C.RST}")
            draw_word(timelines[0].revealed, word_len)
            print(f"{C.RED}{C.BLD}  ALL TIMELINES COLLAPSED."
                  f"  The Tower claims every soul.{C.RST}")
            print(f"  {C.RED}Ka is a wheel.  It always comes around.")
            print(f"  {C.DIM}(One possible True Name was: {rev_word}){C.RST}")
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
        _mv_overview(timelines, active_idx, chronons, word_len, wins, played, diff)
        print(f"\n  {C.BLD}Active: TL-{tl.label}{C.RST}  "
              f"{C.DIM}{diff.upper()} | True Name: {word_len} letters{C.RST}\n")

        draw_gallows(tl.wrong, max_wrong)

        rem = max_wrong - tl.wrong
        rc  = C.GRN if rem > max_wrong * 0.5 else C.YLW if rem > 1 else C.RED + C.BLD
        print(_guess_flavor(rem, max_wrong), end='')
        print(f"  Guesses left: {rc}{rem}{C.RST}\n")

        print(f"  {C.DIM}True Name:{C.RST}")
        draw_word(tl.revealed, word_len)
        draw_alphabet(tl.guessed, tl.hits)

        print(f"\n  {C.DIM}>b branch(-2)  >r timestream(-2)  >s N switch  "
              f">e L N echo(-1)  >x collapse  >h hint  >? help{C.RST}")

        ch_str = '*' * chronons + '.' * max(0, 5 - chronons)
        toolbar = (
            f'<b>Score:</b> {session_score}  |  '
            f'<b>Saved:</b> {wins}/{played}  |  '
            f'<b>TL-{tl.label}</b>  |  '
            f'<ansimagenta>{ch_str} ({chronons}ch)</ansimagenta>  |  '
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

            # >b -- step sideways: same state, different prisoner
            elif cmd == 'B':
                if chronons < 2:
                    flash(f"{C.RED}Not enough Chronons to cross (need 2, have {chronons}).{C.RST}")
                elif len(timelines) >= 4:
                    flash(f"{C.RED}The thinny is overloaded -- max 4 timelines.{C.RST}")
                else:
                    current = tl.candidates[0][0] if tl.candidates else ''
                    new_cands = _make_branch_candidates(
                        diff_pool, word_len,
                        tl.guessed, tl.hits, tl.revealed,
                        evil, current,
                    )
                    new_tl   = Timeline(new_cands, max_wrong, state=tl.state_dict())
                    timelines.append(new_tl)
                    chronons -= 2
                    flash(f"{C.MAG}You step sideways through the thinny.{C.RST}  "
                          f"TL-{new_tl.label} opens -- a parallel world.  "
                          f"Same moment, different {_DIFF_PRISONER[diff]}.  "
                          f"{C.DIM}Pool: {len(new_cands)}.  "
                          f"(-2 chronons -> {chronons} left){C.RST}")

            # >r -- Time Machine: pick any moment, same or different prisoner
            elif cmd == 'R':
                if chronons < 2:
                    flash(f"{C.RED}Not enough Chronons to walk the timestream "
                          f"(need 2, have {chronons}).{C.RST}")
                elif len(timelines) >= 4:
                    flash(f"{C.RED}The thinny is overloaded -- max 4 timelines.{C.RST}")
                elif not tl.history:
                    flash(f"{C.YLW}TL-{tl.label} has no recorded moments yet -- "
                          f"make at least one guess first.{C.RST}")
                else:
                    snap = _history_picker(tl, word_len)
                    if snap is not None:
                        step_idx = tl.history.index(snap)
                        print(f"\n  {C.CYN}You stand in moment {step_idx} of TL-{tl.label}.{C.RST}")
                        print(f"  {C.GRN}[s]{C.RST}  Same prisoner  -- the same soul, a new fate from this point")
                        print(f"  {C.MAG}[d]{C.RST}  Different prisoner  -- parallel world, new True Name")
                        bt = input(f"\n  [s/d] (Enter = return to present): ").strip().lower()
                        if bt in ('s', 'd'):
                            snap_state = {
                                'wrong':    snap['wrong'],
                                'revealed': dict(snap['revealed']),
                                'guessed':  set(snap['guessed']),
                                'hits':     set(snap['hits']),
                            }
                            if bt == 's':
                                new_cands = list(snap['candidates'])
                                fate_desc = "same prisoner"
                            else:
                                cur = (snap['candidates'][0][0]
                                       if snap.get('candidates') else '')
                                new_cands = _make_branch_candidates(
                                    diff_pool, word_len,
                                    snap['guessed'], snap['hits'],
                                    snap['revealed'], evil, cur,
                                )
                                fate_desc = "different prisoner"
                            new_tl   = Timeline(new_cands, max_wrong, state=snap_state)
                            timelines.append(new_tl)
                            chronons -= 2
                            flash(f"{C.CYN}You fold through time.{C.RST}  "
                                  f"TL-{new_tl.label} opens at moment {step_idx} "
                                  f"of TL-{tl.label}.  {fate_desc.capitalize()}, "
                                  f"pool: {len(new_cands)}.  "
                                  f"{C.DIM}(-2 chronons -> {chronons} left){C.RST}")

            # >s N -- switch active timeline
            elif cmd.startswith('S'):
                try:
                    n = int(cmd[1:].strip()) - 1
                    if 0 <= n < len(timelines) and timelines[n].alive:
                        active_idx = n
                    elif 0 <= n < len(timelines):
                        flash(f"{C.RED}TL-{timelines[n].label} has already been lost.{C.RST}")
                    else:
                        flash(f"{C.RED}No such timeline.{C.RST}")
                except ValueError:
                    flash(f"{C.RED}Usage: >s 2  (shift focus to timeline 2){C.RST}")

            # >e L N -- echo: peer across the thinny
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
                        flash(f"{C.RED}TL-{target.label} has been lost to the todash.{C.RST}")
                    elif el in target.guessed:
                        outcome = (f"{C.GRN}TRUE{C.RST}" if el in target.hits
                                   else f"{C.RED}VOID{C.RST}")
                        flash(f"The thinny echoes: {C.BLD}{el}{C.RST} in TL-{target.label} "
                              f"was {outcome}  (already spoken -- free knowledge)")
                    elif el in target.echo_log:
                        flash(f"{C.YLW}{el} was already echoed in TL-{target.label}.  "
                              f"The thinny remembers only once per letter.{C.RST}")
                    elif chronons < 1:
                        flash(f"{C.RED}Not enough Chronons to echo "
                              f"(need 1, have {chronons}).{C.RST}")
                    else:
                        target.echo_log.add(el)
                        chronons -= 1
                        positions, survivors = evil_guess(el, target.candidates,
                                                          target.revealed)
                        result = f"{C.GRN}TRUE{C.RST}" if positions else f"{C.RED}VOID{C.RST}"
                        delta  = f"{len(target.candidates)} -> {len(survivors)}"
                        flash(f"You peer through the thinny into TL-{target.label}.  "
                              f"{C.BLD}{el}{C.RST}: {result}  "
                              f"{C.DIM}(pool {delta})  "
                              f"(-1 chronon -> {chronons} left){C.RST}")
                except (ValueError, IndexError):
                    flash(f"{C.RED}Usage: >e A 2  or  >eA2  "
                          f"(echo letter A in timeline 2){C.RST}")

            # >x -- collapse timeline into the todash
            elif cmd == 'X':
                if sum(1 for t in timelines if t.alive) <= 1:
                    flash(f"{C.RED}You cannot let the last world fall.{C.RST}")
                else:
                    tl.alive = False
                    flash(f"{C.YLW}TL-{tl.label} fades into the todash darkness.{C.RST}")

            # >h -- hint: the Tower whispers
            elif cmd == 'H':
                if tl.num in hint_used:
                    flash(f"{C.YLW}The Tower has already whispered in TL-{tl.label}.  "
                          f"It will not speak again.{C.RST}")
                elif tl.candidates:
                    unrevealed = [i for i in range(word_len) if i not in tl.revealed]
                    if unrevealed:
                        tl.snapshot()
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
                        tl.record_guess(f'HINT:{letter}', True)
                        hint_used.add(tl.num)
                        flash(f"{C.YLW}The Tower whispers: '{letter}'.  "
                              f"Every whisper costs something.{C.RST}")

            else:
                flash(f"{C.RED}Unknown command '{raw}'.  Type >? for help.{C.RST}")

        # -- Full-word guess ---------------------------------------------------
        elif len(raw) > 1 and raw.isalpha():
            tl.snapshot()
            target_word = tl.candidates[0][0] if tl.candidates else ''
            matched     = (raw == target_word)
            if matched:
                for i, ch in enumerate(raw):
                    tl.revealed[i] = ch
                    tl.hits.add(ch)
            else:
                tl.wrong += 1
                filtered = [(w, c) for w, c in tl.candidates if w != raw]
                if filtered:
                    tl.candidates = filtered
            tl.record_guess(raw, matched)

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
                tl.record_guess(raw, True)
            else:
                tl.wrong += 1
                tl.record_guess(raw, False)

            # Reality fracture: same letter, different outcomes across TLs
            this_hit = raw in tl.hits
            diverged = [
                (t.label, raw in t.hits)
                for t in timelines
                if t is not tl and raw in t.guessed
                   and (raw in t.hits) != this_hit
            ]
            if diverged:
                here   = f"{C.GRN}TRUE{C.RST}"  if this_hit else f"{C.RED}VOID{C.RST}"
                others = ', '.join(
                    f"TL-{lbl}: {C.GRN}TRUE{C.RST}" if h
                    else f"TL-{lbl}: {C.RED}VOID{C.RST}"
                    for lbl, h in diverged
                )
                print(f"\n  {C.MAG}{C.BLD}REALITY FRACTURE!{C.RST}  "
                      f"{C.MAG}'{raw}' rings {here}{C.MAG} in TL-{tl.label}"
                      f" but {others}.{C.RST}")
                print(f"  {C.DIM}These worlds have diverged.  "
                      f"Different truths hold in different realities.{C.RST}")
                input(f"  {C.DIM}[Enter]{C.RST}")
