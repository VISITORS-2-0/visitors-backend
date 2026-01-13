import pandas as pd
import random
from datetime import datetime, timedelta

# Parameters
num_patients = 20
values = ['Normal', 'High', 'Moderately_low']
concept_name = 'WBC_STATE_BMT'
start_year = 1991
end_year = 1994

# Helper to format datetime with timezone
def format_dt(dt):
    # Formats the date to match your requested format: YYYY-MM-DDTHH:MM:SS+02:00
    return dt.strftime('%Y-%m-%dT%H:%M:%S+02:00')

new_data = []

# Loop to generate data for each patient
for i in range(num_patients):
    patient_id = 1000 + i  # Generates PatientIDs like 1000, 1001, ..., 1019
    
    # Random start time in the first half of 1991
    current_time = datetime(start_year, 1, 1) + timedelta(days=random.randint(0, 180))
    
    # Generate events until the end of 1994
    while current_time.year <= end_year:
        # 20% chance of a "point event" (0 duration), otherwise duration is 1 minute to 5 days
        if random.random() < 0.2:
            duration_minutes = 0 
        else:
            duration_minutes = random.randint(1, 5 * 24 * 60) 
        
        end_time = current_time + timedelta(minutes=duration_minutes)
        
        # Randomly select a value
        val = random.choice(values)
        
        # Add the row to our list
        new_data.append({
            'StartTime': format_dt(current_time),
            'EndTime': format_dt(end_time),
            'Value': val,
            'PatientID': patient_id,
            'ConceptName': concept_name
        })
        
        # Add a random gap before the next state starts (to ensure no overlap)
        # Gap is between 1 hour and 30 days
        gap_minutes = random.randint(60, 30 * 24 * 60)
        
        # Update current_time for the next iteration
        current_time = end_time + timedelta(minutes=gap_minutes)

# Create the DataFrame
df = pd.DataFrame(new_data)

# Save to CSV
filename = '20_patients_WBC_STATE.csv'
df.to_csv(filename, index=False)

print(f"Successfully generated '{filename}' with {len(df)} rows.")