import math
from collections import Counter

from .colors import C
from .words import COMMON_EN, FALLBACK


class CharNgramModel:
    """
    Character trigram language model (Laplace-smoothed).

    Assigns a per-word log-probability based on character n-gram transitions.
    Used two ways:
      - Perplexity score: how surprising is this word's spelling? (post-game display)
      - Word pool ranking: sort nightmare/hard pools by descending perplexity so
        the adversarial AI always draws from the hardest words first.

    Trained on COMMON_EN (or wordfreq top-5k), NOT on the game word list.
    This separation ensures rare words like SYZYGY score high perplexity rather
    than appearing "expected" to the model.
    """

    def __init__(self, n=3):
        self.n      = n
        self.ngrams = Counter()
        self.ctxs   = Counter()
        self.alpha  = 0

    def train(self, words):
        """words: iterable of uppercase strings."""
        PAD      = '\x00' * (self.n - 1)
        char_set = set()
        for word in words:
            seq = PAD + word + '\x00'
            for i in range(len(seq) - self.n + 1):
                ng  = seq[i : i + self.n]
                ctx = seq[i : i + self.n - 1]
                self.ngrams[ng]  += 1
                self.ctxs[ctx]   += 1
                char_set.update(ng)
        self.alpha = len(char_set) + 1

    def _avg_log_prob(self, word):
        """Average log2 probability per n-gram step. Higher = more expected."""
        if self.alpha == 0:
            return 0.0
        PAD   = '\x00' * (self.n - 1)
        seq   = PAD + word + '\x00'
        total = 0.0
        steps = 0
        for i in range(len(seq) - self.n + 1):
            ng  = seq[i : i + self.n]
            ctx = seq[i : i + self.n - 1]
            num = self.ngrams[ng] + 1
            den = self.ctxs[ctx]  + self.alpha
            total += math.log2(num / den)
            steps += 1
        return total / steps if steps else 0.0

    def perplexity(self, word):
        """
        Character-level perplexity.
        Lower  → predictable spelling → easier to guess.
        Higher → surprising spelling  → harder to guess.
        """
        return 2 ** (-self._avg_log_prob(word))

    def stars(self, word, all_words):
        """1-5 star difficulty string normalised against the pool. Uses ASCII * and -."""
        if not all_words:
            return '***--'
        perps = [self.perplexity(w) for w in all_words]
        lo, hi = min(perps), max(perps)
        p      = self.perplexity(word)
        rank   = (p - lo) / (hi - lo) if hi > lo else 0.5
        n      = min(5, round(rank * 4) + 1)
        return '*' * n + '-' * (5 - n)

    def label(self, word):
        p = self.perplexity(word)
        if   p < 12: return 'very predictable'
        elif p < 18: return 'predictable'
        elif p < 24: return 'average'
        elif p < 32: return 'unusual'
        else:        return 'very unusual'


def _train_model(words):
    model = CharNgramModel(n=3)
    model.train(words)
    return model


def load_word_pool():
    """
    Build the word pool and train the n-gram model.

    With wordfreq installed (pip install wordfreq):
      Pulls 100 000 English words, stratifies by Zipf frequency into four tiers,
      merges with FALLBACK, and re-sorts hard/nightmare by perplexity descending.

    Without wordfreq:
      Falls back to the hand-curated FALLBACK list.

    Returns (pool, CharNgramModel, used_wordfreq).
    pool: {tier: [(word, category), ...]}
    """
    pool = {k: list(v) for k, v in FALLBACK.items()}

    try:
        from wordfreq import top_n_list, zipf_frequency
    except ImportError:
        print(f"\n  {C.DIM}Tip: pip install wordfreq  for a 100k-word pool with "
              f"frequency-calibrated difficulty.{C.RST}")
        model = _train_model(COMMON_EN)
        return pool, model, False

    print(f"\n  {C.DIM}Loading wordfreq pool ... {C.RST}", end='', flush=True)

    tier_bounds = {
        'easy':      (5.0, 99.0),
        'medium':    (4.0,  5.0),
        'hard':      (3.0,  4.0),
        'nightmare': (0.0,  3.0),
    }
    cat_label = {
        'easy': 'Common English', 'medium': 'Uncommon English',
        'hard': 'Rare English',   'nightmare': 'Very Rare English',
    }

    existing = {w for tier in pool.values() for w, _ in tier}

    try:
        raw = top_n_list('en', 100_000)
    except Exception:
        raw = []

    for w in raw:
        if not w.isalpha() or not (4 <= len(w) <= 13):
            continue
        wu = w.upper()
        if wu in existing:
            continue
        freq = zipf_frequency(w, 'en')
        for tier, (lo, hi) in tier_bounds.items():
            if lo <= freq < hi:
                pool[tier].append((wu, cat_label[tier]))
                existing.add(wu)
                break

    common_training = [w.upper() for w in raw[:5000] if w.isalpha()]
    model = _train_model(common_training or COMMON_EN)

    for tier in ('hard', 'nightmare'):
        pool[tier].sort(key=lambda x: -model.perplexity(x[0]))

    counts = ', '.join(f'{t}: {len(pool[t])}' for t in pool)
    print(f"{C.GRN}done{C.RST} ({counts})")

    return pool, model, True
