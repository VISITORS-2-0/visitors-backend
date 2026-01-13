import pandas as pd
import numpy as np

def transform_to_intervals(input_csv_path, output_csv_path, interval_str='W-MON', method='most_time_spent'):
    """
    Transforms event-based abstraction data into fixed-interval time series.
    
    Args:
    input_csv_path (str): Path to the input CSV file.
    output_csv_path (str): Path where the result CSV will be saved.
    interval_str (str): The frequency of intervals. 
                        Examples: 'W-MON' (Weekly starting Monday), 
                                  'M' (Month End), 'MS' (Month Start), 'D' (Daily).
    method (str): Logic to choose value. Currently supports 'most_time_spent'.
    """
    
    print(f"Loading data from {input_csv_path}...")
    df = pd.read_csv(input_csv_path)
    
    # 1. Preprocessing: Ensure datetime and consistent timezone (convert to UTC)
    df['StartTime'] = pd.to_datetime(df['StartTime'], utc=True)
    df['EndTime'] = pd.to_datetime(df['EndTime'], utc=True)
    
    # 2. Define Global Time Grid
    # We want a single grid that covers the entire range of the dataset.
    global_min = df['StartTime'].min().floor('D') # Floor to start of day
    global_max = df['EndTime'].max().ceil('D')   # Ceil to end of day
    
    print(f"Global Time Range: {global_min} to {global_max}")
    print(f"Generating intervals with frequency: {interval_str}")
    
    # Create the buckets (intervals)
    buckets = pd.date_range(start=global_min, end=global_max, freq=interval_str)
    
    # Ensure the last bucket covers the end of the data
    if buckets[-1] < global_max:
        buckets = buckets.union(pd.DatetimeIndex([buckets[-1] + pd.tseries.frequencies.to_offset(interval_str)]))
        
    new_rows = []
    
    # Group by Patient and Concept to process each entity separately
    grouped = df.groupby(['PatientID', 'ConceptName'])
    
    total_groups = len(grouped)
    print(f"Processing {total_groups} unique patient-concept pairs...")

    for (patient_id, concept_name), group in grouped:
        # Sorting helps slightly with logic flow, though we check all overlaps
        group = group.sort_values('StartTime')
        
        # Iterate through every time bucket
        for i in range(len(buckets) - 1):
            bucket_start = buckets[i]
            bucket_end = buckets[i+1]
            
            # Filter rows that physically overlap with the current bucket
            # Overlap logic: (Start_Event < End_Bucket) AND (End_Event > Start_Bucket)
            relevant_rows = group[
                (group['StartTime'] < bucket_end) & 
                (group['EndTime'] > bucket_start)
            ].copy()
            
            representative_value = 'No Value'
            
            if not relevant_rows.empty:
                # Calculate the exact duration of overlap for each row within this bucket
                
                # Clip start/end to stay within the bucket boundaries
                # e.g. if event starts before bucket, count duration only from bucket_start
                relevant_rows['clip_start'] = relevant_rows['StartTime'].apply(lambda x: max(x, bucket_start))
                relevant_rows['clip_end'] = relevant_rows['EndTime'].apply(lambda x: min(x, bucket_end))
                
                relevant_rows['duration'] = (relevant_rows['clip_end'] - relevant_rows['clip_start']).dt.total_seconds()
                
                # Sum duration per unique Value (e.g. how many seconds was 'Normal'?)
                durations = relevant_rows.groupby('Value')['duration'].sum()
                
                if method == 'most_time_spent':
                    # Pick the value with the highest total duration
                    if not durations.empty and durations.max() > 0:
                        representative_value = durations.idxmax()
            
            # Add the result for this bucket
            new_rows.append({
                'StartTime': bucket_start,
                'EndTime': bucket_end,
                'Value': representative_value,
                'PatientID': patient_id,
                'ConceptName': concept_name
            })
            
    # Create final DataFrame
    result_df = pd.DataFrame(new_rows)
    
    # Save to CSV
    result_df.to_csv(output_csv_path, index=False)
    print(f"Done! Saved {len(result_df)} rows to {output_csv_path}")

# Example Usage:
transform_to_intervals('20_patients_WBC_STATE.csv', 'output_mountly.csv', interval_str='MS')