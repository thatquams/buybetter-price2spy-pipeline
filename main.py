"""
Main pipeline execution.
"""

import asyncio
from logger import get_logger
from config import THRESHOLD

from utils.async_io import async_read_excel
from processing.title_processor import process_title_column
from processing.size_converter import convert_size_to_ml
from scoring.similarity import compute_confidence
from scoring.confidence_filtering import filter_low_confidence_by_high_confidence_base_products
from scoring.confidence_results import export_confidence_results_to_excel
from utils.price2spy import transform_high_confidence_to_price2spy

logger = get_logger(__name__)


async def run_pipeline(file_path: str, sheet_names: list):
    """ 
        Main pipeline to:
        1. Read Excel file asynchronously
        2. Process Base and Comp title columns
        3. Convert sizes to ml
        4. Compute confidence scores
        5. Save results to separate Excel files based on confidence thresholds
        
        This pipeline is designed to be efficient and robust, leveraging asynchronous I/O for file reading and structured processing for data transformation and scoring.
    """
    
    try:

        df = await async_read_excel(file_path, sheet_names) # expects a file-like object from Streamlit upload
        

        df = process_title_column(df, 'Base Title')
        df = process_title_column(df, 'Comp Title')

        df['Base Title_size_ml'] = df['Base Title_size'].apply(convert_size_to_ml)
        df['Comp Title_size_ml'] = df['Comp Title_size'].apply(convert_size_to_ml)
        
        logger.info("Size conversion completed successfully, beginning confidence score computation.") # 

        df['Confidence Score %'] = df.apply(
            lambda row: compute_confidence(row, 'Base Title_clean', 'Comp Title_clean', 'Base Title_size_ml', 'Comp Title_size_ml'), axis=1)
        

        logger.info("Confidence scores computed successfully.")
        
        logger.info("Filtering results based on confidence score.")
        
        df.drop(columns=['Base Title_size_ml', 'Comp Title_size_ml', 'Base Title_size', 
                         'Comp Title_size', 'Base Title_clean', 'Comp Title_clean'], inplace=True) # drop columns that are not needed for output
        
        logger.info("Dropped intermediate processing columns, preparing final output.")
        
        # df = df[['Base SKU', 'Base Title', 'URL', 'Competitor', 'Comp Title', 'Comp Price', 'Comp URL', 'Confidence Score %']]
        
        # split results based on confidence score, save to separate Excel files
        high = df[df['Confidence Score %'] >= THRESHOLD] # high confidence matches
        low = df[df['Confidence Score %'] < THRESHOLD] # low confidence matches
        none = df[df['Confidence Score %'].isna()] # matches with no confidence score

        logger.info(f"High confidence matches: {len(high)} | Low confidence matches: {len(low)} | None confidence matches: {len(none)}")
        
        logger.info("Filtering low confidence matches to remove records where the base product already has a high confidence match.")
        
        filtered_low_df = filter_low_confidence_by_high_confidence_base_products(
                                high_df=high,
                                low_df=low,
                                key_col='Base SKU'
                            ) # Remove low confidence records where the base product already has a high confidence match
        
        logger.info("Pipeline completed successfully.")
        
        return high, filtered_low_df, none

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)


if __name__ == "__main__":
    
    high_df, low_df, none_df = asyncio.run(
        run_pipeline(
            'output/input/price2spy_export_20260320_235435.xlsx', # Replace with actual file path, when you run the pipeline. 
            ['Confirmed Matches', 'Manual Review']
        )
    )

    #  Export confidence results to Excel, including the new Price2Spy import sheet
    price2spy_df = transform_high_confidence_to_price2spy(high_df)

    export_confidence_results_to_excel(
        high_df=high_df,
        low_df=low_df,
        none_df=none_df,
        price2spy_df=price2spy_df   
    ) # Export all results to a single Excel file with separate sheets for high confidence, low confidence, none confidence, and Price2Spy import.