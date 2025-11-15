
import json, os
from settings import SCORE_FILE, TOP_SCORES

def load_scores():
    if not os.path.exists(SCORE_FILE):
        return []
    try:
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_score(score):

    scores = load_scores()
    scores.append(score)
    scores = sorted(scores, reverse=True)[:TOP_SCORES]
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f)
    return scores
