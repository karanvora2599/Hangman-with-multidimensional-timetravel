"""
Optional enhanced UI layer.

Imports Rich and prompt_toolkit at module load; sets HAS_RICH / HAS_PT flags
so callers can branch without try/except scattered through game code.
Falls back silently to plain ANSI + input() when either package is missing.
"""

HAS_RICH = False
HAS_PT   = False
console  = None       # Rich Console, or None
MV_COMPLETER = None   # prompt_toolkit completer for multiverse commands

# -- Rich ---------------------------------------------------------------------
try:
    from rich.console import Console
    HAS_RICH = True
    console  = Console(highlight=False)
except ImportError:
    pass

# -- prompt_toolkit ------------------------------------------------------------
_pt_prompt   = None
_history     = None
_HTML        = None

try:
    from prompt_toolkit import prompt as _pt_prompt        # type: ignore[assignment]
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.formatted_text import HTML as _HTML  # type: ignore[assignment]
    HAS_PT   = True
    _history = InMemoryHistory()
    MV_COMPLETER = WordCompleter(
        ['>b', '>r', '>s 1', '>s 2', '>s 3', '>s 4',
         '>x', '>h', '>?', '>e '],
        ignore_case=True,
        sentence=True,
    )
except ImportError:
    pass


def game_prompt(label, *, toolbar=None, completer=None):
    """
    Thin input wrapper.

    With prompt_toolkit: renders a bottom toolbar with live game state,
    enables tab-completion (multiverse >commands), and keeps arrow-key history
    across turns.
    Without prompt_toolkit: falls back to plain input().
    """
    if HAS_PT and _pt_prompt is not None:
        kwargs: dict = {'history': _history}
        if toolbar and _HTML is not None:
            kwargs['bottom_toolbar'] = _HTML(toolbar)
        if completer:
            kwargs['completer'] = completer
        try:
            return _pt_prompt(label, **kwargs)
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt
        except Exception:
            pass        # unexpected terminal issue -> fall through to input()
    return input(label)


# -- Rich helpers --------------------------------------------------------------

def mv_table(timelines, active_idx, word_len):
    """
    Build a Rich Table for the multiverse TL overview.
    Returns a Table object; caller prints it via console.print().
    """
    if not HAS_RICH:
        return None

    from rich.table import Table
    from rich.text import Text
    import rich.box as rbox

    table = Table(
        show_header=False,
        box=rbox.SIMPLE,
        padding=(0, 1),
        show_edge=False,
        show_lines=False,
    )
    table.add_column(width=6)                  # TL label
    table.add_column(width=10)                 # [######] bar
    table.add_column(width=5)                  # wrong/max
    table.add_column(width=9)                  # pool: N
    table.add_column(width=max(word_len * 2, 8))  # revealed pattern
    table.add_column(width=8)                  # status

    for i, tl in enumerate(timelines):
        # -- Pattern ----------------------------------------------------------
        pattern = Text()
        for p in range(word_len):
            if p in tl.revealed:
                pattern.append(tl.revealed[p], style='bold white')
            elif tl.dead:
                pattern.append('?', style='red dim')
            else:
                pattern.append('.', style='dim')
            if p < word_len - 1:
                pattern.append(' ')

        # -- Status ------------------------------------------------------------
        if tl.solved:
            status, st_style = 'SOLVED', 'bold green'
        elif tl.dead:
            status, st_style = 'DEAD  ', 'red dim'
        elif i == active_idx:
            status, st_style = 'ACTIVE', 'bold cyan'
        else:
            status, st_style = '', 'dim'

        # -- Label -------------------------------------------------------------
        tl_style = ('bold cyan' if i == active_idx else
                    'green'     if tl.solved        else
                    'red dim'   if tl.dead          else 'white')

        # -- Progress bar ------------------------------------------------------
        filled    = round(tl.wrong / tl.max_wrong * 6)
        bar_inner = ('bold red' if tl.dead else
                     'red'       if filled >= 4 else
                     'yellow'    if filled >= 2 else 'green')
        bar = Text('[')
        bar.append('#' * filled,          style=bar_inner)
        bar.append('-' * (6 - filled),    style='dim')
        bar.append(']')

        table.add_row(
            Text(f'TL-{tl.label}', style=tl_style),
            bar,
            f'{tl.wrong}/{tl.max_wrong}',
            f'pool:{len(tl.candidates):3d}',
            pattern,
            Text(status, style=st_style),
        )

    return table
