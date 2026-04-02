import re


def convert_size_to_ml(size_str: str) -> float:
    """
    
    Convert product sizes to milliliters (ml).
        
    Convert size string to ml.
    Supports ml, oz, g, kg, fl oz.
    """
    if not size_str:
        return None

    try:
        size_str = size_str.lower().replace(" ", "")

        match = re.match(r'(\d+(\.\d+)?)(ml|oz|g|kg|fl)', size_str)
        if not match:
            return None

        value = float(match.group(1))
        unit = match.group(3)

        if unit == "ml":
            return value
        elif unit in ["oz", "fl"]:
            return value * 29.5735
        elif unit == "g":
            return value  # assume density ≈ water
        elif unit == "kg":
            return value * 1000

        return None

    except Exception:
        return None