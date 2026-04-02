
def sizes_match(size1: float, size2: float, tolerance: float = 2.0) -> bool:
    """
    Compare sizes with tolerance (ml).
    """
    if size1 is None or size2 is None:
        return False

    return abs(size1 - size2) <= tolerance