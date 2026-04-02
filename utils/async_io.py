import pandas as pd
import asyncio
from utils.logger import get_logger
from datetime import datetime
logger = get_logger(__name__)

# async def async_read_excel(path: str, sheet_name: str) -> pd.DataFrame:
#     """
#         Async file operations, especially for reading Excel files, can significantly improve performance by
#         allowing other tasks to run concurrently while waiting for I/O operations to complete.
#         This is particularly beneficial when dealing with large files or multiple file reads, 
#         as it prevents blocking the main thread and enhances overall responsiveness.
#     """
#     loop = asyncio.get_running_loop()
#     return await loop.run_in_executor(None, pd.read_excel, path, sheet_name)


# async def async_read_excel(uploaded_file, sheet_names: list) -> pd.DataFrame:
#     """
#     Read multiple sheets from an uploaded Excel file.
#     """
#     try:
#         loop = asyncio.get_running_loop()

#         def read():
#             all_sheets = pd.read_excel(uploaded_file, sheet_name=sheet_names)

#             dfs = []
#             for sheet, df in all_sheets.items():
#                 df['source_sheet'] = sheet
#                 dfs.append(df)

#             return pd.concat(dfs, ignore_index=True)

#         return await loop.run_in_executor(None, read)

#     except Exception as e:
#         raise RuntimeError(f"Failed to read uploaded file: {e}")





async def async_read_excel(uploaded_file, sheet_names: list) -> pd.DataFrame:
    """
        Read multiple sheets from an uploaded Excel file.

        Args:
            uploaded_file: Streamlit uploaded file (file-like object)
            sheet_names (list): List of sheet names to read

        Returns:
            pd.DataFrame: Combined dataframe from all sheets
    """
    try:
        logger.info("Starting Excel file read process")

        # Validate input
        if uploaded_file is None:
            logger.error("No file was uploaded")
            raise ValueError("Uploaded file is None")

        if not sheet_names:
            logger.error("No sheet names provided")
            raise ValueError("Sheet names list is empty")

        logger.info(f"Sheets requested: {sheet_names}")

        loop = asyncio.get_running_loop() # Get the current event loop

        def read(): # This function will run in a separate thread to avoid blocking the event loop
            try:
                logger.info("Reading Excel sheets into memory")

                # Reset pointer, just in case it was read before, to ensure we read from the beginning
                # uploaded_file.seek(0)

                selected_sheets = pd.read_excel(uploaded_file, sheet_name=sheet_names) # Read all specified sheets into a dictionary of dataframes
                buyBetterProducts = pd.read_excel(uploaded_file, sheet_name="BuyBetter Products")[["SKU", "URL"]] # Read BuyBetter Products sheet separately

                logger.info(f"Successfully read {len(selected_sheets)} sheets")

                dfs = []

                for sheet, df in selected_sheets.items(): # Iterate through each sheet and its corresponding dataframe
                    logger.info(f"Processing sheet: '{sheet}' | Rows: {len(df)}")

                    df['source_sheet'] = sheet # Add a new column to identify the source sheet for each row
                    dfs.append(df)

                combined_df = pd.concat(dfs, ignore_index=True)\
                                                .drop(columns=['source_sheet', "Confidence %", "Review Reason"])# Combine all dataframes into one, resetting the index
                             
                # Merge with BuyBetter Products to get the URL column (if it exists), using a left join to keep all records from the combined dataframe
                combined_df = combined_df.merge(buyBetterProducts, left_on='Base SKU', right_on='SKU', how='left').drop(columns=['SKU']) 
                
                logger.info(
                    f"Successfully combined sheets | Total rows: {len(combined_df)}, Returned columns: {combined_df.columns.tolist()}"
                )
                
                logger.info("Exporting competitor products to a separate Excel file for reference")
                combined_df[['Competitor','Comp Title', 'Comp URL', 'Comp Price']].to_excel(\
                                f"output/competitors/competitors_products{datetime.now().\
                                    strftime('%Y-%m-%d_%H-%M-%S')}.xlsx", index=False) # Save competitor products to a separate Excel file for reference
                

                logger.info("Excel file read and processing completed successfully")

                return combined_df

            except ValueError as ve:
                logger.error(f"Sheet name error: {ve}")
                raise

            except Exception as e:
                logger.error(
                    f"Error occurred while reading Excel file: {e}",
                    exc_info=True
                )
                raise

        result = await loop.run_in_executor(None, read) # Run the read function in a separate thread to avoid blocking the event loop

        logger.info("Excel file read process completed successfully")

        return result

    except Exception as e:
        logger.error(
            f"Failed to read uploaded Excel file: {e}",
            exc_info=True
        )
        raise RuntimeError(f"Failed to read uploaded file: {e}")
    