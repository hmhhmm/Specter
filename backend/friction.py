from typing import List
import math
import numpy as np
import os
import time
import threading
from collections import deque
import logging

# Module logger
logger = logging.getLogger(__name__)

# Optional dependencies
try:
    from scipy.stats import entropy as _scipy_entropy
except Exception:
    _scipy_entropy = None
    logger.warning('scipy not available; entropy calculations will use fallback method')

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_distances
    _st_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    _st_model = None
    logger.warning('sentence-transformers not available; semantic distance will use heuristic')


def _ensure_hf_token() -> str:
    token = os.getenv('HF_TOKEN')
    if token:
        return token
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k == 'HF_TOKEN' and v:
                        os.environ.setdefault('HF_TOKEN', v)
                        logger.debug('Loaded HF_TOKEN from %s (masked)', env_path)
                        return v
        except Exception:
            logger.exception('Failed reading .env for HF_TOKEN')
            return ''
    return ''


class SimpleRateLimiter:
    def __init__(self, max_calls_per_minute: int = 60, min_interval_ms: int = 50) -> None:
        self.max_calls = int(max_calls_per_minute)
        self.min_interval = float(min_interval_ms) / 1000.0
        self._calls = deque()
        self._lock = threading.Lock()

    def allow(self) -> bool:
        now = time.time()
        with self._lock:
            # drop calls older than 60s
            while self._calls and now - self._calls[0] > 60:
                self._calls.popleft()
            if self._calls and (now - self._calls[-1]) < self.min_interval:
                return False
            if len(self._calls) >= self.max_calls:
                return False
            self._calls.append(now)
            return True


# Load HF token and configure limiter
_hf_token = _ensure_hf_token()
_hf_token_present = bool(_hf_token)
_HF_MAX_CALLS = int(os.getenv('HF_MAX_CALLS', '60'))
_HF_MIN_INTERVAL_MS = int(os.getenv('HF_MIN_INTERVAL_MS', '50'))
_rate_limiter = SimpleRateLimiter(_HF_MAX_CALLS, _HF_MIN_INTERVAL_MS)


class FrictionMathematician:
    """Mathematical model for F-Score (friction) estimation.

    Responsibilities:
    - Compute entropy from action probabilities
    - Measure semantic distance between expected and actual UI summaries
    - Combine components into a single F-Score (0-100)
    """

    def __init__(self) -> None:
        # Tunable weights (kept consistent with "Pro" logic)
        self.weight_entropy = 0.20  # ~25 pts max
        self.weight_dwell = 0.40    # ~40 pts max
        self.weight_semantic = 0.35 # ~25 pts max

    def calculate_entropy(self, action_probabilities: List[float]) -> float:
        """Return Shannon entropy (bits) for the discrete distribution.

        Falls back to a simple calculation if scipy is not available.
        """
        try:
            probs = np.array(action_probabilities, dtype=float)
            if probs.size == 0:
                return 0.0
            probs_sum = probs.sum()
            if probs_sum <= 0:
                return 0.0
            probs = probs / probs_sum
            # Use scipy if present for numerical stability
            if _scipy_entropy is not None:
                return float(_scipy_entropy(probs, base=2))
            # Fallback: compute directly
            entropy = -float(np.sum([p * math.log2(p) for p in probs if p > 0]))
            return entropy
        except Exception:
            logger.exception('Error calculating entropy')
            return 0.0

    def calculate_semantic_distance(self, expected: str, actual: str) -> float:
        """Return semantic distance in range [0.0, 1.0].

        If sentence-transformers is available, compute embedding cosine distance.
        Otherwise use a conservative heuristic based on token overlap.
        This method logs whether embeddings or heuristic were used.
        """
        try:
            exp = (expected or "").strip()
            act = (actual or "").strip()
            if not exp and not act:
                return 0.0

            reasons = []
            if _st_model is None:
                reasons.append('no_model')
            if not _hf_token_present:
                reasons.append('no_token')

            # Prefer embeddings when available and allowed by rate limiter
            if not reasons:
                allowed = _rate_limiter.allow()
                logger.debug('Friction.calculate_semantic_distance: model_present=%s, hf_token_present=%s, rate_limiter_allowed=%s', _st_model is not None, _hf_token_present, allowed)
                if allowed:
                    try:
                        logger.debug('Friction: using embeddings for semantic distance')
                        if os.getenv('FRIC_DEBUG') == '1':
                            print('Friction: using embeddings for semantic distance')
                        emb = _st_model.encode([exp, act], convert_to_numpy=True)
                        dist = cosine_distances([emb[0]], [emb[1]])[0][0]
                        logger.debug('Friction: semantic distance (embeddings) = %s', dist)
                        if os.getenv('FRIC_DEBUG') == '1':
                            print(f'Friction: semantic distance (embeddings) = {dist}')
                        return float(max(0.0, min(1.0, dist)))
                    except Exception:
                        logger.exception('Friction: embedding call failed, falling back to heuristic')
                        if os.getenv('FRIC_DEBUG') == '1':
                            print('Friction: embedding call failed, falling back to heuristic')
                else:
                    logger.debug('Friction: embeddings rate-limited; falling back to heuristic')
                    if os.getenv('FRIC_DEBUG') == '1':
                        print('Friction: embeddings rate-limited; falling back to heuristic')
            else:
                logger.debug('Friction: embeddings unavailable; reasons=%s', reasons)
                if os.getenv('FRIC_DEBUG') == '1':
                    print('Friction: embeddings unavailable; reasons=', reasons)

            # Heuristic fallback: Jaccard-like token distance
            set_e = set(exp.lower().split())
            set_a = set(act.lower().split())
            if not set_e and not set_a:
                return 0.0
            inter = len(set_e & set_a)
            union = len(set_e | set_a)
            jaccard = inter / union if union > 0 else 0.0
            semantic = float(max(0.0, min(1.0, 1.0 - jaccard)))
            logger.debug('Friction: using heuristic jaccard=%s -> semantic_dist=%s', jaccard, semantic)
            return semantic
        except Exception:
            logger.exception('Friction: calculate_semantic_distance unexpected error')
            return 0.0

    def compute_f_score(self, entropy_val: float, dwell_time_ms: int, semantic_dist: float) -> int:
        """Combine entropy, dwell time and semantic distance into an integer F-Score (0-100).

        Expected inputs:
        - entropy_val: bits (e.g., 0..~3)
        - dwell_time_ms: milliseconds
        - semantic_dist: 0.0..1.0
        """
        try:
            # Entropy -> scale to 0-25
            entropy_score = min(25.0, entropy_val * 10.0)

            # Dwell time: only penalize excessive waiting (> 5s). Map to 0-40
            dwell_penalty = 0.0
            if dwell_time_ms and dwell_time_ms > 5000:
                dwell_penalty = min(40.0, (dwell_time_ms - 5000) / 150.0)

            # Semantic distance: 0.0..1.0 -> 0-25
            semantic_score = min(25.0, semantic_dist * 25.0)

            # Weighted sum (weights are for clarity; already scaled to component ranges)
            raw = entropy_score + dwell_penalty + semantic_score

            # Normalize to 0-100 and round
            score = int(max(0, min(100, round(raw))))
            return score
        except Exception:
            logger.exception('Friction: compute_f_score error')
            return 0


__all__ = ["FrictionMathematician"]
