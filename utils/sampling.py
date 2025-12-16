import random

EPSILON = 0.05  # plancher : une carte maîtrisée reste toujours réinterrogeable

def weighted_choice(cards):
    weights = []

    for c in cards:
        seen = max(1, c.get("times_seen", 0))
        correct = c.get("times_correct", 0)
        mastery = correct / seen

        weight = EPSILON + (1 - mastery) ** 2
        weights.append(weight)

    return random.choices(cards, weights=weights, k=1)[0]
