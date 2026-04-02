import pandas as pd
from utils.logger import get_logger
from scoring.confidence_filtering import filter_low_confidence_by_high_confidence_base_products
from datetime import datetime
logger = get_logger(__name__)

# def export_confidence_results_to_excel(
#     high_df: pd.DataFrame,
#     low_df: pd.DataFrame,
#     output_path: str = "confidence_results.xlsx"
# ):

#     try:
#         logger.info(f"Exporting confidence results to Excel → {output_path}")
#         with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
#             high_df.to_excel(writer, sheet_name='Confirmed Matches', index=False)
#             low_df.to_excel(writer, sheet_name='Manual Review', index=False)

#         logger.info(f"Export successful → {output_path}")

#     except Exception as e:
#         logger.error(f"Failed to export Excel file: {e}")
#         raise RuntimeError(f"Failed to export Excel file: {e}")
    
    
    
def export_confidence_results_to_excel(
    high_df: pd.DataFrame,
    low_df: pd.DataFrame,
    none_df: pd.DataFrame = None,
    price2spy_df: pd.DataFrame = None,
    output_path: str = f"output/BuyBetter/price2spy_export{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
):
    """
        Export high and low confidence dataframes into a single Excel file
        with separate sheets.

        Args:
            high_df (pd.DataFrame): High confidence matches
            low_df (pd.DataFrame): Low confidence matches (already filtered)
            none_df (pd.DataFrame): None confidence matches (optional)
            price2spy_df (pd.DataFrame): Transformed dataframe for Price2Spy import (optional)
            output_path (str): Output Excel file path
    """
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            high_df.to_excel(writer, sheet_name='Confirmed Matches', index=False)
            low_df.to_excel(writer, sheet_name='Manual Review', index=False)

            if none_df is not None:
                none_df.to_excel(writer, sheet_name='No Match', index=False)
                
            if price2spy_df is not None:
                price2spy_df.to_excel(writer, sheet_name='price2spy Import', index=False)

        logger.info(f"Export successful → {output_path}")

    except Exception as e:
        logger.error(f"Failed to export Excel file: {e}")
        raise RuntimeError(f"Failed to export Excel file: {e}")