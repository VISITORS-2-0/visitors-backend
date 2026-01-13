import pandas as pd
import json

def generate_interval_summary_all_values(input_csv_path, output_csv_path):
    """
    Aggregates normalized interval data.
    Ensures Value_Dict contains ALL possible values (including zeros).
    """
    
    print(f"Loading normalized data from {input_csv_path}...")
    df = pd.read_csv(input_csv_path)
    
    # 1. Identify all unique values present in the entire dataset
    # This ensures consistency across all rows
    all_possible_values = sorted(df['Value'].dropna().unique())
    
    # Ensure 'No Value' is in the list
    if 'No Value' not in all_possible_values:
        all_possible_values.append('No Value')
        
    print(f"Global set of values: {all_possible_values}")

    # 2. Group by time interval and concept
    grouped = df.groupby(['StartTime', 'EndTime', 'ConceptName'])

    results = []
    
    print(f"Processing {len(grouped)} intervals...")

    for (start, end, concept), group in grouped:
        # Get counts of each value currently in this group
        current_counts = group['Value'].value_counts().to_dict()
        
        # Initialize a dict with 0 for every possible global value
        complete_counts = {val: 0 for val in all_possible_values}
        
        # Update with the actual counts found
        complete_counts.update(current_counts)
        
        # Calculate total patients (sum of all counts)
        total_patients = sum(complete_counts.values())
        
        results.append({
            'StartTime': start,
            'EndTime': end,
            'ConceptName': concept,
            'Value_Dict': complete_counts, 
            'TotalPatientsWithData': total_patients
        })

    result_df = pd.DataFrame(results)
    
    # Save the result
    result_df.to_json(output_csv_path, index=False, orient='records', lines=False)
    print(f"Done! Saved to {output_csv_path}")

# Example Usage:
generate_interval_summary_all_values('./output_mountly.csv', 'summary_intervals_corrected.json')