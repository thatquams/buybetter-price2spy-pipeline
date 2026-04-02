"""
Hybrid similarity scoring using fuzzy + semantic.
"""

import pandas as pd
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util

from utils.config import FUZZ_SCORE_THRESHOLD, MODEL_NAME
from processing.size_matcher import sizes_match

model = SentenceTransformer(MODEL_NAME)


def compute_confidence(row, base_col, comp_col, base_size_col, comp_size_col):
    """
    Compute hybrid similarity score.
    """
    
    # access necessary variables
    base_title = row.get(base_col); comp_title = row.get(comp_col); base_size = row.get(base_size_col); comp_size = row.get(comp_size_col)

    # check if titles are valid
    if not base_title or not comp_title:
        return 0.0

    # check size mismatch
    base_missing = pd.isna(base_size)
    comp_missing = pd.isna(comp_size)

    # size mismatch
    if (not base_missing and not comp_missing) and not sizes_match(base_size, comp_size):
        return None

    # run semantic if any size missing
    if base_missing or comp_missing:
        return _semantic_score(base_title, comp_title)

    # run fuzzy if sizes match
    fuzz_score = fuzz.token_sort_ratio(base_title, comp_title)

    # check fuzzy threshold, and return if met, else fallback to semantic
    if fuzz_score >= FUZZ_SCORE_THRESHOLD:
        return fuzz_score

    return _semantic_score(base_title, comp_title)


def _semantic_score(t1: str, t2: str) -> float:
    # compute semantic similarity score, return None if any error
    try:
        
        emb1 = model.encode(t1, convert_to_tensor=True)
        emb2 = model.encode(t2, convert_to_tensor=True)
        return round(util.cos_sim(emb1, emb2).item() * 100, 2)
    
    except:
        return None