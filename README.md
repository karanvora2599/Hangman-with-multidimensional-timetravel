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
   - [The Time Machine (`>r`)](#the-time-machine-r)
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

### The Story

The Dark Tower stands at the center of all existence, its beams threading through infinite parallel worlds. Something has gone wrong.

Innocents have been condemned across the timelines — each sentenced to hang unless their **True Name** is spoken before time runs out. You are the last **Gunslinger**, carrying five **Chronons** — shards of todash energy that let you walk between worlds, bend time backward, and branch into realities where the truth is different.

Find the True Name. Free the innocent. The Tower watches. **Ka wills it.**

Every run opens with a narrative intro. Guesses remaining have story beats ("The gallows creak in the wind", "Ka draws near, Gunslinger", "Last chance. The Tower grows impatient."). Win messages call the word a "True Name" and announce the prisoner's freedom. Loss messages read: *"The Tower claims every soul. Ka is a wheel."* Divergences between timelines are announced as **Reality Fractures**.

### Core Concept

Every **timeline** is a completely independent parallel universe — a different reality where a different prisoner awaits judgment, each chasing a **different hidden word** (the prisoner's True Name). When you time-travel, a **new timeline is always created**. Existing timelines are never mutated by travel commands.

Key rules:
- All four difficulty tiers available (Easy → Nightmare).
- Easy/Medium: each timeline has a **fixed word** chosen at creation — the AI does not shift it.
- Hard/Nightmare: each timeline runs the full **adversarial Entropy AI** — the word shifts on every guess until cornered.
- Up to **4 parallel timelines** at any time.
- You start with **5 Chronons** — the time-travel energy resource.
- The word length is the same across all timelines (set at game start).

### Difficulty in Multiverse

| Tier | Guesses | Word type | Prisoners |
|------|:-------:|-----------|-----------|
| Easy | 8 | Fixed word, common | Wanderers and travelers |
| Medium | 7 | Fixed word, uncommon | Outcasts between worlds |
| Hard | 6 | Adversarial AI, rare | The cursed and forgotten |
| Nightmare | 5 | Adversarial AI, very rare | The Tower's chosen sacrifices |

### Chronons

Chronons are spent on time-travel actions. You begin each game with **5 Chronons**.

| Action | Cost |
|--------|:----:|
| `>b` branch from NOW (different prisoner) | −2 |
| `>r` Time Machine (any past moment, same or different prisoner) | −2 |
| `>e` echo (peer through the thinny) | −1 |
| `>s` switch, `>x` collapse | free |
| `>h` hint (the Tower whispers a letter) | 1 wrong guess |

Running out of chronons locks out all travel actions, but the game continues — you keep playing the surviving timelines with normal guesses.

### Multiverse Commands

All commands begin with `>`. Normal letters and words are guesses in the active timeline.

| Command | Cost | What it does |
|---------|:----:|--------------|
| `A`–`Z` | — | Guess a letter in the active timeline |
| `WORD` | — | Guess the full True Name in the active timeline |
| `>b` | −2 | **Branch** — step sideways through the thinny right now; same player state, different prisoner |
| `>r` | −2 | **Time Machine** — walk the timestream; pick any past moment, choose same or different prisoner |
| `>s N` | free | Shift focus to timeline N |
| `>e L N` | −1 | **Echo** — peer through the thinny; preview letter L in timeline N without committing |
| `>x` | free | Let this timeline fade into the todash (cannot collapse the last surviving one) |
| `>h` | 1 wrong guess | The Tower whispers a letter — force-reveals one unrevealed position (once per TL) |
| `>?` | free | Show the in-game help screen |

#### Echo compact form

`>e L N` and `>eL N` and `>eLN` are all accepted. For example, to peek at letter E in timeline 2: `>e E 2` or `>eE2`.

### The Two Branch Types

#### `>b` — Branch (step sideways through the thinny)

Instantly forks the active timeline from **the current moment** into a parallel world with a **different prisoner** — a different hidden word. The new timeline carries forward your current wrong count, all revealed positions, and all guessed letters, but the word pool is rebuilt so the new prisoner's True Name is different:

- Positions you've revealed must hold the same letters in the new word.
- Letters that were misses cannot appear in the new word.

For Easy/Medium (fixed-word mode) a new single word is picked. For Hard/Nightmare (adversarial mode) the full filtered pool is used.

**When to use**: When you want to hedge quickly — same progress state, different word to chase in parallel.

#### `>r` — The Time Machine

Opens a **visual gallery** showing every past state of the active timeline as a panel with the gallows drawing, the word pattern, wrong-guess count, and what was guessed at that step. The active timeline is never touched.

```
  TL-A  --  Time Machine  (4 past states | pick one to branch from)

  +------ [0] ------+  +------ [1] ------+  +------ [2] ------+  +------ [3] ------+
  |    +---+        |  |    +---+        |  |    +---+        |  |    +---+        |
  |    |   |        |  |    |   |        |  |    |   |        |  |    |   |        |
  |        |        |  |    O   |        |  |    O   |        |  |    O   |        |
  |        |        |  |        |        |  |    |   |        |  |   /|\  |        |
  |        |        |  |        |        |  |        |        |  |        |        |
  |    =========   |  |    =========   |  |    =========   |  |    =========   |
  |                 |  |                 |  |                 |  |                 |
  |  _ _ _ _ _ _   |  |  _ _ _ _ _ _   |  |  _ _ _ _ _ _   |  |  _ _ _ _ _ _   |
  |  wrong: 0/5     |  |  wrong: 1/5     |  |  wrong: 2/5     |  |  wrong: 3/5     |
  |  start          |  |  E: MISS        |  |  T: MISS        |  |  A: MISS        |
  +-----------------+  +-----------------+  +-----------------+  +-----------------+

  Pick step to branch from [0-3] (Enter = cancel): _
```

After picking a step you choose the branch type:

```
  Branch type for step 2:
  [s]  Same word   -- chase the same word from that past state
  [d]  New word    -- fresh candidate pool, same player state at step 2

  [s/d] (Enter = cancel): _
```

- **Same prisoner (`s`)**: The new timeline resumes from the chosen past moment with the same candidate pool. Use this to retry a different letter from an earlier point without losing your current TL's progress.
- **Different prisoner (`d`)**: The new timeline starts from the chosen past moment but with a freshly filtered pool — a different word (prisoner) that still satisfies all constraints known at that step.

**When to use `>r` over `>b`**: When you want control over *which* past moment to fork from, not just the present. After several misses, jump back to an early clean moment and try a completely different strategy — or fork with the same prisoner to explore an alternate path through the same word.

#### Comparison

| | `>b` branch | `>r` time machine |
|--|--|--|
| Branch point | Always right now | Any past moment you pick |
| Prisoner | Always different | Your choice: same or different |
| Active TL | Unchanged | Unchanged |
| Chronon cost | −2 | −2 |
| Best for | Fast hedging | Strategic replays, alternate letter paths |

### The Time Machine (`>r`)

The Time Machine is the most powerful tool in multiverse mode. Here is a step-by-step walkthrough:

1. Type `>r` in any active timeline that has at least one guess in its history.
2. The screen clears and shows every past state as a side-by-side panel gallery (or a compact table if Rich is not installed). Each panel shows the gallows at that moment, the word pattern, the wrong-guess count, and the letter that was guessed from that state.
3. Type a step number to select that state, or press Enter to cancel (no chronons are spent on a cancel).
4. Choose `s` (same word) or `d` (different word).
5. A new timeline is created. The active timeline is completely unchanged.

The gallery always includes a `[now]` panel showing the current live state, so you can compare it against historical states before deciding. You cannot branch from `[now]` via `>r` — use `>b` for that.

### What the Multiverse Screen Shows

```
  THE GUNSLINGER  |  Chronons [***..] |  Timelines: 3  (alive: 2)  Saved: 1/4  [NIGHTMARE]

  TL-A  [######]  5/5  pool:  0   S Y Z Y G Y    FREED
  TL-B  [##----]  2/5  pool: 12   . . Z . . .    ACTIVE
  TL-C  [#-----]  1/5  pool: 19   . . . . . .

  Active: TL-B  |  NIGHTMARE  |  True Name: 6 letters

  Ka draws near, Gunslinger.
  Guesses left: 3

  True Name:
  _ _ Z _ _ _

  A  B  C  D  E  F  G  H  I  J  K  L  M
  N  O  P  Q  R  S  T  U  V  W  X  Y  Z

  >b branch(-2)  >r timestream(-2)  >s N switch  >e L N echo(-1)  >x collapse  >h hint  >?

  TL-B > _
```

**Overview header**: `Saved: W/P` shows how many games you've won this session; `[DIFF]` shows the current mission difficulty.

**Overview table** rows:
- `TL-X` — timeline label (A, B, C, D)
- `[######]` — wrong-guess progress bar (6 chars, green → yellow → red)
- `N/M` — wrong guesses / max wrong (M varies by difficulty: 5, 6, 7, or 8)
- `pool: N` — candidate words remaining (1 = fixed word in Easy/Medium; shrinks with adversarial AI in Hard/Nightmare)
- Pattern — revealed letters (`.` = unknown)
- Status: `ACTIVE`, `FREED` (won), `LOST` (dead)

**Story beats** replace the plain "Guesses left" line with escalating tension:
- Full health → no message
- Past 40% → *"The gallows creak in the wind."*
- Past 70% → *"Ka draws near, Gunslinger."*
- 1 remaining → *"Last chance. The Tower grows impatient."*

**Chronon bar** — `[***..] = 3 chronons remaining` (stars = available, dots = spent)

### Win & Loss Conditions

**Win**: Speak the True Name in ANY timeline — fully reveal the word. The game ends immediately.

```
  TRUE NAME FOUND.  TL-B freed.  Word: SYZYGY
  The innocent goes free.  Ka wills it, Gunslinger.
```

**Loss**: Every timeline reaches its wrong-guess limit.

```
  ALL TIMELINES COLLAPSED.  The Tower claims every soul.
  Ka is a wheel.  It always comes around.
  (One possible True Name was: SYZYGY)
```

When all timelines collapse in adversarial mode, one candidate word is shown — the exact word was never locked in, so this is only one possibility of what the Tower had in mind.

### Reality Fractures

When you guess the same letter in two timelines and get opposite outcomes — TRUE in one, VOID in another — the game announces a **Reality Fracture**:

```
  REALITY FRACTURE!  'E' rings TRUE in TL-B but TL-C: VOID.
  These worlds have diverged.  Different truths hold in different realities.
```

Fractures confirm that the hidden words are genuinely different across those timelines. This is the multiverse working as intended — each universe has its own truth, and the Gunslinger must track them separately.

Use fracture information strategically:
- A letter that is VOID in TL-C but TRUE in TL-B means TL-C's word contains none of that letter.
- Echo (`>e`) the fractured letter in a third timeline before guessing it there.

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
    ├── multiverse.py       ← Timeline class, time machine, multiverse game loop
    ├── ui.py               ← optional Rich + prompt_toolkit layer
    └── cli.py              ← mode/difficulty menus, main()
```

**Module dependency order** (no circular imports):
```
colors  ←  words  ←  model
                  ←  engine  ←  classic   ←  cli
                             ←  ui
                             ←  multiverse ←  cli
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

### Multiverse — Choosing Your Mission

**Easy / Medium** (fixed-word): each timeline has a locked word from the start. Reality fractures are guaranteed when the same letter is absent in one word and present in another. You can use the Time Machine to replay from any moment with the same word — knowing exactly what you're returning to.

**Hard / Nightmare** (adversarial): the word shifts on each guess. Fractures can emerge from the AI making different choices in different timelines, not just from different underlying words. The pool counter in the overview tells you how many words remain — watch for it to shrink toward 1, which locks the word in.

### Multiverse — Chronon Budget

You start each mission with **5 Chronons**. Spending all of them earns a ×1.25 score multiplier — don't hoard.

```
Turn 1–2:  guess letters freely; note pool sizes and watch for reality fractures
Turn 3:    use >e to echo a promising letter across other timelines (-1 each)
Turn 4–5:  branch or time-travel if a timeline looks hopeless (-2 each)
End-game:  collapse lost timelines with >x to keep the board readable
```

### Multiverse — Branch vs. Time Machine

**Branch (`>b`)** is best when:
- You want to act quickly without reviewing history.
- You've made progress (some letters revealed) and want a fresh prisoner with those constraints baked in.
- You need a second timeline fast to hit the timeline multiplier.

**Time Machine (`>r`)** is best when:
- You want to replay from a specific past moment — not just 1 step back.
- You just had a string of misses and want to restart before they happened.
- You want to branch with the *same prisoner* to try a different letter path on the same word.
- You have time to inspect the gallery, weigh the options, and make a deliberate choice.

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
