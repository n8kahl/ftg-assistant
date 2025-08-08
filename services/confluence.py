def score_from_signals(bias_ok: bool, momentum_ok: bool, level_ok: bool, vol_ok: bool, flow_align: int = 0, event_penalty: int = 0) -> float:
    score = 0.0
    score += 3.0 if bias_ok else 0.0
    score += 2.0 if momentum_ok else 0.0
    score += 2.0 if level_ok else 0.0
    score += 1.0 if vol_ok else 0.0
    score += 2.0 * max(0, min(1, flow_align))
    score -= 2.0 if event_penalty else 0.0
    return round(min(10.0, score), 1)
