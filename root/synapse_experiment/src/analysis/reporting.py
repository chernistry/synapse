import pandas as pd
from datetime import datetime
from pathlib import Path

def generate_report(experiment_data: list, output_dir: str = "results"):
    """
    Generates a CSV report from the experiment data, flattening nested dictionaries.

    Args:
        experiment_data (list): A list of dictionaries from the experiment run.
        output_dir (str): The directory to save the output CSV file in.
    """
    if not experiment_data:
        print("No data to generate report.")
        return

    # --- Flatten the data structure ---
    flattened_data = []
    for row in experiment_data:
        flat_row = {
            'scenario_id': row.get('scenario_id'),
            'scenario_type': row.get('scenario_type'),
            'agent': row.get('agent'),
            'path_found': row.get('path_found'),
            'srs': row.get('srs'),
            'pps': row.get('pps'),
        }
        
        # Add raw performance data with a 'raw_' prefix
        raw_perf = row.get('raw_perf', {})
        for key, value in raw_perf.items():
            flat_row[f'raw_{key}'] = value
            
        # Add normalized performance data with a 'norm_' prefix
        norm_perf = row.get('normalized_perf', {})
        for key, value in norm_perf.items():
            flat_row[f'norm_{key}'] = value
            
        flattened_data.append(flat_row)
        
    df = pd.DataFrame(flattened_data)

    # --- Ensure directory exists and save the file ---
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_path / f"experiment_results_{timestamp}.csv"
    
    try:
        # Define the desired column order for clarity
        column_order = [
            'scenario_id', 'scenario_type', 'agent', 'pps', 'srs', 'path_found',
            'norm_time', 'norm_energy', 'norm_safety', 'norm_payload_integrity',
            'raw_time', 'raw_energy', 'raw_safety', 'raw_payload_integrity'
        ]
        # Filter to only include columns that actually exist in the dataframe
        final_columns = [col for col in column_order if col in df.columns]
        
        df[final_columns].to_csv(filename, index=False, float_format='%.4f')
        print(f"Report successfully generated: {filename}")
    except Exception as e:
        print(f"Failed to generate report: {e}")

# Example Usage (can be called from main.py)
def _example():
    # This example is now outdated due to the new data structure
    # but is kept for conceptual reference.
    pass

if __name__ == '__main__':
    _example() 