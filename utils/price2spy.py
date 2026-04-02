from utils.logger import get_logger
import pandas as pd
logger = get_logger(__name__)


def transform_high_confidence_to_price2spy(high_df: pd.DataFrame) -> pd.DataFrame:
    """
        Transform high confidence matches into Price2Spy format.

        - One row per Base SKU
        - Competitor URLs spread across columns

        Args:
            high_df (pd.DataFrame): High confidence matches

        Returns:
            pd.DataFrame: Transformed dataframe
    """

    logger.info("Transforming high confidence matches into Price2Spy format")

    # Keep only necessary columns
    df = high_df[['Base SKU', 'Base Title', 'Comp URL']].copy()

    # Remove rows with missing competitor URLs
    df = df[df['Comp URL'].notna()]

    # Remove duplicates (same SKU + same competitor URL)
    df = df.drop_duplicates(subset=['Base SKU', 'Comp URL'])

    logger.info(f"After cleaning: {len(df)} rows remaining")

    # Group by Base SKU and Base Title, aggregate competitor URLs into lists (products with multiple matches will have multiple URLs)
    grouped = df.groupby(['Base SKU', 'Base Title'])['Comp URL'].apply(list).reset_index()

    logger.info(f"Grouped into {len(grouped)} unique products")

    # Expand competitor URLs into separate columns (up to 9 URLs for Price2Spy format)
    max_urls = grouped['Comp URL'].apply(len).max()
    max_urls = min(max_urls, 9)  # cap at 9 (Price2Spy format)

    url_cols = [f'Competitor URL {i+1}' for i in range(max_urls)] # Create column names for competitor URLs

    expanded_urls = pd.DataFrame(
        grouped['Comp URL'].apply(lambda x: x[:max_urls]).tolist(),
        columns=url_cols
    )

    # Combine with base SKU and title
    final_df = pd.concat(
        [grouped[['Base SKU', 'Base Title']], expanded_urls],
        axis=1
    )

    # Rename columns to match Price2Spy format
    final_df.rename(columns={
            'Base SKU': 'SKU',
            'Base Title': 'Product Name'
        }, inplace=True)

    # Add BuyBetter URL column (if exists in original data)
    if 'URL' in high_df.columns:
        url_map = high_df.drop_duplicates('Base SKU').set_index('Base SKU')['URL']
        final_df['Your BuyBetter URL'] = final_df['SKU'].map(url_map)
    else:
        final_df['Your BuyBetter URL'] = ''

    # Reorder columns to match Price2Spy format
    cols = ['Product Name', 'SKU', 'Your BuyBetter URL'] + url_cols
    final_df = final_df[cols]

    logger.info("Price2Spy transformation completed successfully")

    return final_df