"""
Handles title cleaning, brand extraction, and size extraction.
"""

import re
import pandas as pd
from utils.logger import get_logger
from utils.helpers import _extract_size, _remove_size, _remove_parentheses

logger = get_logger(__name__)

# SIZE_PATTERN = r'\b(\d+(?:\.\d+)?\s?(?:ml|oz|g|fl|kg))\b'
# SIZE_PATTERN = r'(\d+(?:\.\d+)?\s?(?:ml|oz|g|kg|fl))'

def process_title_column(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """
        Process product titles:
        - Normalize text
        - Extract brand
        - Extract size
        - Remove size
        - Remove parentheses
    """
    
    if col_name not in df.columns:
        raise ValueError(f"Column '{col_name}' not found")

    try:
        logger.info(f"Processing column: {col_name}")

        df[col_name] = (
            df[col_name]
            .astype(str)
            .str.replace(r'[–—−]', '-', regex=True)
            .str.replace(r'\s*-\s*', ' - ', regex=True)
            .str.replace("&amp;", "AND")
            .str.replace(r'0[zZ]', 'oz', regex=True)
            .str.replace(r'\s+', ' ', regex=True)
            .str.strip()
            .str.lower()
        )

        # df[f"{col_name}_brand"] = df[col_name].apply(_extract_brand)
        df[f"{col_name}_size"] = df[col_name].apply(_extract_size)
        # Chain size removal and parentheses removal to avoid issues with size patterns inside parentheses
        df[f"{col_name}_clean"] = df[col_name].apply(_remove_size).apply(_remove_parentheses) 
        
        # df[f"{col_name}_updated"] = df[col_name].apply(_remove_size)
        # df[f"{col_name}_clean"] = df[f"{col_name}_updated"].apply(_remove_parentheses)
        
        logger.info(f"Completed processing column: {col_name}\n")
        
        logger.info(f"Retuned Columns : {df.columns.tolist()}")

        return df

    except Exception as e:
        logger.error(f"Error processing {col_name}: {e}", exc_info=True)
        raise