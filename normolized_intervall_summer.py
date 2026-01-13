import pandas as pd
import json

def generate_interval_summary(input_csv_path, output_csv_path):
    """
    Aggregates normalized interval data to show the distribution of values 
    across all patients for each time step.
    
    Correction: TotalPatientsWithData now includes 'No Value' counts.
    """
    
    print(f"Loading normalized data from {input_csv_path}...")
    df = pd.read_csv(input_csv_path)
    
    # Group by the unique time interval and concept
    grouped = df.groupby(['StartTime', 'EndTime', 'ConceptName'])
    
    summary_rows = []
    
    print(f"Processing {len(grouped)} unique time intervals...")
    
    for (start, end, concept), group in grouped:
        # Calculate the distribution of values in this interval
        counts_obj = group['Value'].value_counts()
        
        # Convert to dictionary
        counts_dict = counts_obj.to_dict()
        
        # CORRECTION: Total patients is simply the sum of all counts 
        # (This includes 'No Value', 'Normal', 'High', etc.)
        total_patients = sum(counts_dict.values())
        
        # Create the summary row
        summary_rows.append({
            'StartTime': start,
            'EndTime': end,
            'ConceptName': concept,
            'Value_Dict': counts_dict, 
            'TotalPatientsWithData': total_patients
        })
        
    # Create DataFrame
    summary_df = pd.DataFrame(summary_rows)
    
    # Save to CSV
    summary_df.to_json(output_csv_path, index=False, orient='records', lines=False)
    print(f"Summary generated successfully! Saved to {output_csv_path}")

# Example Usage:
generate_interval_summary('./output_mountly.csv', 'summary_intervals_corrected.json')