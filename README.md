# Hangman with Multi-Dimensional Time-Travel: The Smart & Difficult Edition

A CLI hangman game with an entropy-weighted adversarial AI, a character-level language model for difficulty scoring, and a **Multiverse Mode** where you travel between parallel timelines, each chasing a different hidden word.

---

## Table of Contents

1. [Requirements & Installation](#requirements--installation)
2. [Running the Game](#running-the-game)
3. [Classic Mode](#classic-mode)
   - [Difficulty Tiers](#difficulty-tiers)
   - [Controls](#controls)
   - [What the Screen Shows](#what-the-classic-screen-shows)
   - [Scoring](#classic-scoring)
4. [Multiverse Mode](#multiverse-mode)
   - [Core Concept](#core-concept)
   - [Chronons](#chronons)
   - [Commands](#multiverse-commands)
   - [The Two Branch Types](#the-two-branch-types)
   - [What the Screen Shows](#what-the-multiverse-screen-shows)
   - [Win & Loss Conditions](#win--loss-conditions)
   - [Divergence](#divergence)
   - [Scoring](#multiverse-scoring)
5. [The AI System](#the-ai-system)
   - [Entropy-Weighted Adversarial AI](#entropy-weighted-adversarial-ai)
   - [Character N-gram Model](#character-n-gram-language-model)
6. [Word Pools](#word-pools)
7. [Project Structure](#project-structure)
8. [Strategy Guide](#strategy-guide)

---

## Requirements & Installation

**Python 3.9 or newer** is required.

The game runs with zero additional dependencies. All packages below are optional enhancements:

```bash
# Strongly recommended: expands the word pool from ~130 to 100 000 words
pip install wordfreq

# Enhanced terminal UI (Rich panels, tables, progress bars)
pip install rich

# Smart input prompts (tab-completion, toolbar, history)
pip install prompt_toolkit
```

Clone or download the project, then install optional packages in one shot:

```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
wordfreq
rich>=13.0
prompt_toolkit>=3.0
```

---

## Running the Game

```bash
# Option 1 — recommended
python run.py

# Option 2 — as a module
python -m hangman
```

The game detects which optional packages are installed and upgrades the experience automatically — no configuration needed.

---

## Classic Mode

### Difficulty Tiers

| Tier      | Wrong guesses allowed | Word pool source           | AI mode        |
|-----------|:---------------------:|----------------------------|----------------|
| Easy      | 8                     | Common everyday words      | Fixed word     |
| Medium    | 7                     | Uncommon words             | Fixed word     |
| Hard      | 6                     | Rare / unusual words       | Entropy AI     |
| Nightmare | 5                     | Very rare, unusual spellings | Entropy AI   |

**Fixed word** — the word is chosen before you start guessing and never changes.

**Entropy AI** — the word is NOT fixed at the start. The AI maintains a pool of candidate words and reveals the actual word as late as possible. See [The AI System](#the-ai-system).

### Controls

| Input | Effect |
|-------|--------|
| A single letter | Guess that letter |
| A full word | Attempt the whole word (costs 1 wrong guess if incorrect) |
| `H` | Hint — reveals one letter at a random unrevealed position (costs 1 wrong guess; one per game) |

All input is case-insensitive. Guessing an already-guessed letter is silently ignored.

### What the Classic Screen Shows

```
  HANGMAN  --  The Smart & Difficult Edition
  ----------------------------------------------
  Difficulty: NIGHTMARE    Score: 840    W/L: 2/3   [ENTROPY AI]
  Category: Astronomy  |  Letters: 6  |  [pool: 31 words | H=2.41]

  +---+
  |   |
  O   |
 /|   |
      |
      |
=========

  Guesses remaining: 4

  _ _ Y _ _ Y      ← revealed so far

  A  B  C  D  E  F  G  H  I  J  K  L  M
  N  O  P  Q  R  S  T  U  V  W  X  Y  Z
                                  ↑ green = hit, red/dim = miss, white = unguessed

  Guess (letter or full word): _
```

**Pool indicator** `[pool: 31 words | H=2.41]` — only shown in Entropy AI mode. Tells you how many candidate words remain and the current positional entropy (higher = harder).

**Char complexity** — shown after each game:
```
  Char complexity : ***--  (unusual, perplexity 26.3)
```
Five-star scale (`*----` easy → `*****` hardest) measuring how surprising the word's character sequences are compared to normal English.

### Classic Scoring

```
score = base × efficiency + perfect_bonus + length_bonus

base            = 100 (Easy) / 250 (Medium) / 500 (Hard) / 1000 (Nightmare)
efficiency      = max(0, (max_wrong − wrong_guesses) / max_wrong)
perfect_bonus   = +500 if zero wrong guesses
length_bonus    = word_length × 10
```

Example — solve SYZYGY (6 letters) on Nightmare with 2 wrong guesses:
```
efficiency  = (5 − 2) / 5 = 0.6
score       = 1000 × 0.6 + 0 + 60 = 660
```

---

## Multiverse Mode

### Core Concept

In Multiverse Mode every **timeline** is a completely independent parallel universe pursuing a **different hidden word**. When you time-travel — whether branching forward into a new universe or branching backward to an earlier moment — a **new timeline is always created**. Existing timelines are never mutated by travel commands.

Key rules:
- Always **Nightmare** difficulty (5 wrong guesses per timeline).
- Up to **4 parallel timelines** at any time.
- You start with **5 Chronons** — the time-travel energy resource.
- The hidden word length is the same across all timelines (determined randomly at the start).

### Chronons

Chronons are spent on time-travel actions. You begin each game with **5 Chronons**.

| Action | Cost |
|--------|:----:|
| `>b` branch (new word) | −2 |
| `>r` rewind-branch (same word, past state) | −2 |
| `>e` echo (peek at a letter) | −1 |
| `>s` switch, `>x` collapse, `>h` hint | free\* |

\* Hint costs 1 wrong guess in the active timeline, not chronons.

Running out of chronons locks out all travel actions, but the game continues — you keep playing the surviving timelines with normal guesses.

### Multiverse Commands

All commands begin with `>`. Normal letters and words are guesses in the active timeline.

| Command | Cost | What it does |
|---------|:----:|--------------|
| `A`–`Z` | — | Guess a letter in the active timeline |
| `WORD` | — | Full-word guess in the active timeline |
| `>b` | −2 ⌛ | **New-word branch** — fork from the current moment into a universe with a different word |
| `>r` | −2 ⌛ | **Past branch** — fork from 1 guess ago in the active TL; active TL stays unchanged |
| `>s N` | free | Switch active timeline to timeline number N |
| `>e L N` | −1 ⌛ | **Echo** — preview what letter L would do in timeline N without guessing it |
| `>x` | free | Collapse the active timeline (cannot collapse the last surviving one) |
| `>h` | −1 ❌ | Hint — force-reveal one letter (one per timeline, costs a wrong guess) |
| `>?` | free | Show the in-game help screen |

#### Echo compact form

`>e L N` and `>eL N` and `>eLN` are all accepted. For example, to peek at letter E in timeline 2: `>e E 2` or `>eE2`.

### The Two Branch Types

These are the two fundamentally different ways to create a new timeline:

#### `>b` — New-word branch

Creates a parallel universe **from this exact moment**, carrying forward:
- Your current wrong count
- All revealed letter positions
- All previously guessed letters

But chasing a **completely different hidden word**. The new timeline's candidate pool is rebuilt fresh from the nightmare word list, then filtered to be consistent with your guesses so far:
- Letters you revealed must appear at those positions in the new word.
- Letters that were misses cannot appear anywhere in the new word.

This means you get genuine divergence — the new word satisfies all the same constraints but is otherwise free to be entirely different.

**When to use**: When you've made progress (revealed some letters) and want to hedge your bets — the revealed letters are guaranteed to be in both words, but the rest of the word will differ.

#### `>r` — Past branch (rewind-branch)

Creates a new timeline forked from **1 guess ago** in the active timeline. The active TL is completely untouched. The new timeline inherits:
- The candidate pool as it was before the last guess (same word being chased)
- The game state as it was before the last guess (one fewer wrong, no last reveal)

This lets you explore "what if I had guessed differently 1 step ago" without losing your current progress in the active TL.

**When to use**: After a miss — spin off a branch at the earlier state and try a different letter there, while the active TL continues forward.

#### Comparison table

| | `>b` new-word branch | `>r` past branch |
|--|--|--|
| Word | Different (fresh pool) | Same (same candidates) |
| State | Current (as of right now) | 1 guess ago |
| Active TL | Unchanged | Unchanged |
| Best for | Hedging on a reveal | Recovering from a bad guess |

### What the Multiverse Screen Shows

```
  MULTIVERSE HANGMAN  |  Chronons [***..] |  Timelines: 3  (alive: 2)  W/L: 1/4

  ────────────────────────────────────────────────────────────
  TL-A  [######] 5/5  pool:  0  [S Y Z Y G Y]   DEAD
  TL-B  [##----] 2/5  pool: 12  [. . Z . . .]   ACTIVE
  TL-C  [#-----] 1/5  pool: 19  [. . . . . .]
  ────────────────────────────────────────────────────────────

  Active: TL-B  |  Nightmare | 6 letters

    +---+
    |   |
    O   |
   /|   |
        |
        |
  =========

  Guesses left: 3

  _ _ Z _ _ _

  A  B  C  D  E  F  G  H  I  J  K  L  M
  N  O  P  Q  R  S  T  U  V  W  X  Y  Z

  >b new-word-branch(-2)  >r past-branch(-2)  >s N switch  >e L N echo(-1)  >x collapse  >h hint  >?

  TL-B > _
```

**Overview table** (top section):
- `TL-X` — timeline label (A, B, C, D)
- `[######]` — wrong-guess progress bar (6 chars, green→yellow→red)
- `N/5` — wrong guesses / max wrong
- `pool: N` — number of candidate words remaining in this TL
- `[letters]` — revealed positions so far (`.` = unknown)
- Status: `ACTIVE` (current), `DEAD` (exhausted), `SOLVED` (won)

**Chronon bar** — `[***..] = 3 chronons remaining` (stars = available, dots = spent)

### Win & Loss Conditions

**Win**: Fully reveal the word in ANY timeline. The game ends immediately — you do not need to solve all timelines.

**Loss**: Every timeline reaches its wrong-guess limit (all timelines dead).

When all timelines die simultaneously, one possible word from the first timeline is revealed (the adversarial AI may have had multiple candidates, so the exact word was never fully determined).

### Divergence

When you guess the same letter in two timelines but get different outcomes — a HIT in one and a MISS in another — the game announces a **Divergence**:

```
  Divergence!  'E' is HIT in TL-B but TL-C: MISS
```

Divergences confirm that the hidden words are genuinely different between those two timelines. This is expected and intentional: it tells you something concrete about each universe's word.

Use divergence information strategically:
- A letter that is MISS in TL-C but HIT in TL-B means TL-C's word contains none of that letter.
- Echo (`>e`) the diverged letter in a third timeline before guessing it there.

### Multiverse Scoring

```
earned = int(base_pts × tl_mult × ch_mult) + surv_pts + ch_pts

base_pts   = standard Nightmare score for the solved TL
           = 1000 × efficiency + perfect_bonus + word_len × 10
             where efficiency = (5 − wrong) / 5

tl_mult    = 1.0 + 0.5 × (total_timelines − 1)
             1.0 for 1 TL,  1.5 for 2,  2.0 for 3,  2.5 for 4

ch_mult    = 1.25  if you spent all 5 chronons, else 1.0
             (reward for aggressive time-travel play)

surv_pts   = 50 × (alive_timelines − 1)
             bonus for each timeline still alive when you win

ch_pts     = 20 × remaining_chronons
             bonus for each unspent chronon
```

**Example**: Solve on TL-B (2 wrong, 6-letter word) with 3 timelines created, 1 chronon left, 2 TLs still alive:

```
base_pts = 1000 × (3/5) + 0 + 60 = 660
tl_mult  = 1.0 + 0.5 × 2 = 2.0
ch_mult  = 1.0  (1 chronon left)
surv_pts = 50 × 1 = 50
ch_pts   = 20 × 1 = 20
earned   = int(660 × 2.0 × 1.0) + 50 + 20 = 1390
```

---

## The AI System

### Entropy-Weighted Adversarial AI

On Hard and Nightmare (and always in Multiverse), the hidden word is **not fixed at the start**. Instead, the AI maintains a *candidate pool* — a list of all words that are still consistent with your guesses — and on each guess picks the partition that is hardest for you.

**How a guess is processed:**

1. Your guess letter divides the candidate pool into groups by position pattern.
   - Group `(0,3)` = words where your letter appears at positions 0 and 3.
   - Group `()` = words where your letter appears nowhere.
2. Each group is scored:
   ```
   score = pool_size × (1 + positional_entropy)
   ```
3. The AI picks the highest-scoring group. That group's pattern is what you get revealed (or nothing if the AI picked the miss group).
4. The candidate pool is replaced with just the words in the winning group.

**Positional entropy** is the average Shannon entropy of letter distributions at each unrevealed position. A large group where every unrevealed position has an evenly-spread letter distribution is maximally hard — your future guesses convey little information. A small group of near-identical words is easy even if it's large.

**Consequence**: Common vowels like E, A, O often result in misses on Hard/Nightmare because the largest, most ambiguous partition is usually the one that excludes them. Rare letters (X, Z, Y, W) sometimes hit more because the AI has fewer words to hide behind.

### Character N-gram Language Model

A character trigram model (Laplace-smoothed) assigns every word a **perplexity score** — a measure of how surprising its spelling is compared to normal English.

**Training**: The model is trained on ~300 common English words (or the top-5 000 by frequency if `wordfreq` is installed), **not** on the game word list. This separation is essential: if the model trained on SYZYGY it would learn that YZY is a normal sequence, which defeats the purpose.

**How perplexity works**: For each consecutive 3-character window (trigram) in the word, the model asks "how likely is this character given the previous two?" The perplexity is the geometric mean of the inverse probabilities. Low perplexity = predictable spelling = easier to guess. High perplexity = surprising transitions = harder.

| Perplexity range | Label | Examples |
|:---:|---|---|
| < 12 | very predictable | WATER, PLANT |
| 12–18 | predictable | DANCE, STORM |
| 18–24 | average | CRISP, OCEAN |
| 24–32 | unusual | SYZYGY, KVETCH |
| > 32 | very unusual | CRWTH, XYLYL, ZEPHYR |

**How it's used**:
- Post-game display: `Char complexity: ***-- (unusual, perplexity 26.3)`
- Pool pre-sorting: Hard/Nightmare pools are sorted by descending perplexity so the AI always starts from the hardest words.

---

## Word Pools

### Without `wordfreq`

Hand-curated fallback lists:

| Tier | Count | Examples |
|------|------:|---------|
| Easy | 20 | BANJO, FJORD, WALTZ |
| Medium | 28 | ECLIPSE, KERFUFFLE, SPHINX |
| Hard | 30 | DISCOMBOBULATE, GOBBLEDYGOOK, OBSTREPEROUS |
| Nightmare | 127 | CRWTH, SYZYGY, COCCYX, SCHMALTZ, XYLOPHONE |

### With `wordfreq` installed

Stratified from 100 000 most-common English words by Zipf frequency:

| Tier | Zipf range | Word count (approx.) |
|------|:---:|---:|
| Easy | ≥ 5.0 | ~2 000 |
| Medium | 4.0–5.0 | ~5 000 |
| Hard | 3.0–4.0 | ~15 000 |
| Nightmare | < 3.0 | ~50 000+ |

Zipf scale: 8 = most common (THE), 0 = rarest. Words at Zipf < 3 appear fewer than ~1 000 times per billion words of text — genuinely obscure.

Hard and Nightmare pools are re-sorted by perplexity descending after loading, so the most linguistically unusual words appear first in adversarial play.

---

## Project Structure

```
HangMan/
├── run.py                  ← entry point  (python run.py)
├── requirements.txt        ← optional dependencies
├── README.md
└── hangman/
    ├── __init__.py         ← package root, exports main()
    ├── __main__.py         ← enables  python -m hangman
    ├── colors.py           ← ANSI colour constants (class C)
    ├── words.py            ← FALLBACK word lists, COMMON_EN corpus, game constants
    ├── model.py            ← CharNgramModel, _train_model(), load_word_pool()
    ├── engine.py           ← adversarial AI, rendering helpers, scoring
    ├── classic.py          ← classic single-player game loop
    ├── multiverse.py       ← Timeline class, multiverse game loop
    └── cli.py              ← mode/difficulty menus, main()
```

**Module dependency order** (no circular imports):
```
colors  ←  words  ←  model
                  ←  engine  ←  classic
                             ←  multiverse
                                         ←  cli
```

---

## Strategy Guide

### Classic — Easy / Medium

The word is fixed. Use standard letter-frequency order:

```
E T A O I N S H R D L C U M W F G Y P B V K J X Q Z
```

Vowels first (E, A, O, I) since most words have several. Then high-frequency consonants (T, N, S, H, R).

### Classic — Hard / Nightmare (Entropy AI)

The AI reassigns the word on each guess. Counter-intuitive strategies:

- **Avoid E, A, O early** — the AI almost always has a large partition that excludes common vowels. You'll miss and waste a guess.
- **Start with rare consonants** — try W, Y, K, X, Z early. The AI has fewer candidates that lack these letters, so you sometimes force a hit or shrink the pool dramatically.
- **Watch the pool counter** — `[pool: N words]` tells you how close you are to the word being determined. When pool = 1, the word is fixed.
- **Full-word guess when pool is small** — if pool ≤ 3 and you can narrow it down by logic, a correct word guess wins immediately without spending more wrong-guess budget.
- **The hint trick** — `H` costs a wrong guess but reveals a letter the AI has to commit to. On Nightmare with 5 guesses, spend the hint on your second turn (when pool is still large) to lock in one letter position.

### Multiverse — Chronon Budget

You have 5 chronons. Optimal general budget:
```
Turn 1–2:  guess letters freely (observe the pool, look for divergence potential)
Turn 3:    use >e to echo promising letters across timelines (-1 each)
Turn 4–5:  branch or rewind-branch if a timeline looks hopeless (-2 each)
End-game:  collapse dead timelines with >x to keep the scoreboard clean
```

Spending all 5 chronons earns ×1.25 on your final score — don't hoard them.

### Multiverse — Branch vs. Rewind

**Branch (`>b`)** is best when:
- You've revealed several letters and want a second shot at a different word with those constraints baked in.
- You want to maximise the timeline count for the score multiplier.
- The active TL's pool has shrunk to a difficult set of words.

**Rewind-branch (`>r`)** is best when:
- You just got a miss on a letter you wish you hadn't guessed.
- You want to try a different letter from 1 step ago in a safe copy.
- The active TL still has many candidates — forking at an earlier state keeps more options open.

### Multiverse — Echo Strategy

Echo (`>e L N`) costs 1 chronon and tells you HIT/MISS + pool size change for letter L in timeline N without consuming a guess. Use it to:

1. **Check before branching** — echo the same letter in both the current TL and a prospective branch target to see if they diverge.
2. **Pre-scout a risky guess** — if you're about to guess a letter on your last wrong-guess slot, echo it first.
3. **Map diverged timelines** — after a divergence announcement, echo the diverged letter in a third TL to determine which pattern that universe follows.

Each letter can be echoed **once per timeline**. Already-guessed letters are free to check (no chronon cost) since the outcome is known.

### Multiverse — Collapse Timing

`>x` is free. Collapsing a dying timeline (1 guess remaining, unknown word) before it dies:
- Removes it from the "all timelines dead" loss condition.
- Does **not** earn the per-surviving-TL bonus (it's collapsed, not solved).
- Lets you focus on the remaining timelines without the distraction.

Collapse when a timeline is essentially hopeless and you want a cleaner end-state. Do **not** collapse your last timeline — that immediately ends the game as a loss.
