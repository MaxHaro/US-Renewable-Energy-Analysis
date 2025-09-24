"""
U.S. Renewable Energy Analysis & Visualization

This script fetches, cleans, and visualizes annual electricity generation data for
key renewable energy sources from the U.S. Energy Information Administration (EIA) API.

Author: Sergio Maximiliano Haro
Date: 2025-09-24
"""

import requests
import time
import pandas as pd
import matplotlib.pyplot as plt

def fetch_eia_data(series_to_fetch, api_key):
    """
    Fetches data for multiple EIA series IDs using the v2 API.

    Args: series_to_fetch (dict): A dictionary mapping friendly names to EIA series IDs.
          api_key (str): Your personal EIA API key.

    Returns: dict: A dictionary containing the raw JSON data for each series, or None if a request fails.
    """
    print("Starting Data Fetching:")
    all_data = {}
    for series_name, series_id in series_to_fetch.items():
        api_url = f'https://api.eia.gov/v2/seriesid/{series_id}?api_key={api_key}'
        print(f"Fetching data for: {series_name}...")

        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            all_data[series_name] = data['response']['data']
            print(f"Success: Found {len(all_data[series_name])} data points.")
        else:
            print(f"ERROR: Failed to fetch data for {series_name}. Status Code: {response.status_code}")
            # Stop the script if any API call fails
            return None

        time.sleep(0.5)
    
    print("\nData Fetching Complete\n")
    return all_data

def process_data_to_dataframe(raw_data):
    """
    Transforms the raw API data into a clean, structured Pandas DataFrame.

    Args: raw_data (dict): The raw data dictionary returned from fetch_eia_data.

    Returns: pandas.DataFrame: A cleaned DataFrame with years as the index and energy sources as columns.
    """
    print("Processing Data into a DataFrame")
    processed_series_list = []
    for series_name, data_list in raw_data.items():
        if not data_list:
            print(f"Note: No data returned for {series_name}. Skipping.")
            continue
        
        temp_df = pd.DataFrame(data_list)
        temp_df = temp_df[['period', 'generation']]
        temp_df = temp_df.set_index('period')
        temp_df = temp_df.rename(columns={'generation': series_name})
        processed_series_list.append(temp_df)

    # Combining all the individual DataFrames into one.
    final_df = pd.concat(processed_series_list, axis=1)

    final_df = final_df.sort_index()

    # The EIA dataset starts in different years for different sources.
    # We fill any resulting NaN (Not a Number) values with 0, assuming negligible
    # generation in those early years.
    final_df.fillna(0, inplace=True)
    
    print("Data cleaning and structuring complete.\n")
    return final_df

def plot_generation_trends(df, output_filename='renewable_energy_chart.png'):
    """
    Generates and saves a line chart of energy generation trends.

    Args: df (pandas.DataFrame): The final DataFrame to be plotted.
          output_filename (str): The name of the file to save the plot image.
    """
    print("Generating and Saving Plot")
    
    fig, ax = plt.subplots(figsize=(12, 8))

    df.plot(kind='line', ax=ax, linewidth=2.5)

    ax.set_title('U.S. Annual Renewable Energy Generation (2001-2024)', fontsize=16, pad=15)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Generation (Thousand Megawatthours)', fontsize=12)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(title='Energy Source', fontsize=10)
    
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ','))
    )

    plt.tight_layout()

    plt.savefig(output_filename, dpi=300)
    print(f"Plot saved successfully as '{output_filename}'.")
    
    plt.show()


if __name__ == "__main__":

    API_KEY = '[YOUR_API_KEY_HERE]'

    SERIES_TO_FETCH = {
        'Solar': 'ELEC.GEN.SPV-US-99.A',
        'Wind': 'ELEC.GEN.WND-US-99.A',
        'Hydroelectric': 'ELEC.GEN.HYC-US-99.A',
        'Geothermal': 'ELEC.GEN.GEO-US-99.A',
        'Biomass': 'ELEC.GEN.BIO-US-99.A'
    }

    raw_energy_data = fetch_eia_data(SERIES_TO_FETCH, API_KEY)

    if raw_energy_data:
        final_dataframe = process_data_to_dataframe(raw_energy_data)
        
        print("Final Cleaned DataFrame (First 5 Rows)")
        print(final_dataframe.head())
        print("\nDataFrame Info")
        final_dataframe.info()
        print("\n")
        
        plot_generation_trends(final_dataframe)
