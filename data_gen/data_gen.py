import pandas as pd
import os

all_data = []


directory = 'real_missions'

for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        filepath = os.path.join(directory, filename)
        data = pd.read_csv(filepath)
        all_data.append(data)


combined_data = pd.concat(all_data, ignore_index=True)
combined_data.to_csv('real_data.csv', index=False)

print(combined_data.head(200))