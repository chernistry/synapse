import pandas as pd
from datetime import datetime
from pathlib import Path

def generate_report(experiment_data: list, output_dir: str = "results"):
    """
    Generates a flexible CSV report from the experiment data.
    It automatically determines columns from the data provided.

    Args:
        experiment_data (list): A list of flat dictionaries from the experiment run.
        output_dir (str): The directory to save the output CSV file in.
    """
    if not experiment_data:
        print("No data to generate report.")
        return

    # The data is already flat, so we can create the DataFrame directly.
    df = pd.DataFrame(experiment_data)

    # --- Ensure directory exists and save the file ---
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_path / f"experiment_results_{timestamp}.csv"
    
    try:
        # Dynamically determine column order for better readability
        # Basic columns first, then any raw performance metrics
        base_cols = ['scenario_id', 'scenario_type', 'agent', 'path_found']
        raw_cols = sorted([col for col in df.columns if col.startswith('raw_')])
        
        final_columns = [col for col in base_cols if col in df.columns] + raw_cols
        
        # Ensure all columns are included, even if not in the preferred order
        for col in df.columns:
            if col not in final_columns:
                final_columns.append(col)
        
        df[final_columns].to_csv(filename, index=False, float_format='%.4f')
        print(f"Report successfully generated: {filename}")
    except Exception as e:
        print(f"Failed to generate report: {e}")

# Example Usage is now handled by main.py
def _example():
    pass

if __name__ == '__main__':
    _example() 