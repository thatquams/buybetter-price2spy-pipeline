import pandas as pd

def filter_low_confidence_by_high_confidence_base_products(
    high_df: pd.DataFrame,
    low_df: pd.DataFrame,
    key_col: str = 'Base SKU'
    ) -> pd.DataFrame:
    """
        Remove records from low confidence dataframe where the base product
        already exists in high confidence dataframe.

        Args:
            high_df (pd.DataFrame): High confidence matches
            low_df (pd.DataFrame): Low confidence matches
            key_col (str): Column used to identify unique base product

        Returns:
            pd.DataFrame: Filtered low confidence dataframe
    """
    try:
        
        # Get unique base SKUs already matched confidently
        high_keys = set(high_df[key_col].dropna().unique())

        # Filter low confidence
        filtered_low_df = low_df[~low_df[key_col].isin(high_keys)].copy()

        return filtered_low_df

    except Exception as e:
        raise RuntimeError(f"Error removing existing high confidence records: {e}")
    
    
    
