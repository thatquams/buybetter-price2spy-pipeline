import re 
import os
from datetime import datetime



SIZE_PATTERN = r'(\d+(?:\.\d+)?\s?(?:ml|oz|g|kg|fl))' # matches size patterns.


def _extract_size(title: str) -> str:
    """
        Extract product size from messy strings.
        Handles cases like:
        - t200ml
        - 200 ml
        - 1.01oz
    """
    try:
        if not title:
            return None

        # Normalize tricky cases
        title = re.sub(r'([a-zA-Z])(\d+(?:\.\d+)?\s?(ml|oz|g|kg|fl))', r' \2', title)

        sizes = re.findall(r'(\d+(?:\.\d+)?\s?(?:ml|oz|g|kg|fl))', title)

        return sizes[-1].replace(" ", "").lower() if sizes else None

    except Exception:
        return None


def _remove_size(title: str) -> str:
    try:
        return re.sub(SIZE_PATTERN, '', title).strip()
    except:
        return title


def _remove_parentheses(title: str) -> str:
    try:
        return re.sub(r'\(.*?\)', '', title).strip()
    except:
        return title
    

# def generate_output_path(base_dir="output/BuyBetter") -> str:
#     """
#         Generate output path with date-based folder structure.

#         Example:
#         output/BuyBetter/2026-04-02/price2spy_export_18-45-12.xlsx
#     """

#     now = datetime.now()

#     date_folder = now.strftime("%Y-%m-%d")
#     time_stamp = now.strftime("%H-%M-%S")

#     # Create full directory path
#     full_dir = os.path.join(base_dir, date_folder)

#     # Ensure directory exists
#     os.makedirs(full_dir, exist_ok=True)

#     # Final file path
#     file_name = f"price2spy_export_{time_stamp}.xlsx"
#     output_path = os.path.join(full_dir, file_name)

#     return output_path