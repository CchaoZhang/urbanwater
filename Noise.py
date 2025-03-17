import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
from tqdm import tqdm

EARTH_RADIUS = 6371
KILOMETERS_PER_METER = 0.001


excel_data = pd.read_excel()
unique_centers = excel_data.drop_duplicates().reset_index(drop=True)

population_df = pd.read_csv()

population_coords = np.deg2rad(population_df[['latitude', 'longitude']].values)


population_tree = BallTree(population_coords, metric='haversine')


population_mask = np.ones(len(population_df), dtype=bool)


results = []


unique_centers = unique_centers.sort_values(by='dis2', ascending=False).reset_index(drop=True)

population_df['affected'] = False

for idx, row in tqdm(unique_centers.iterrows(), total=len(unique_centers), desc="处理数据中心"):
    center_lat = row['125Latitude']
    center_lon = row['125Longitude']
    radius_meters = row['dis2']
    radius_radian = radius_meters * KILOMETERS_PER_METER / EARTH_RADIUS
    center_coord = np.deg2rad([[center_lat, center_lon]])

    
    indices = population_tree.query_radius(center_coord, r=radius_radian)[0]

    
    valid_indices = indices[population_mask[indices]]

    
    population_df.loc[valid_indices, 'affected'] = True

    
    total_population = population_df.iloc[valid_indices]['population'].sum()

   
    population_mask[valid_indices] = False

    results.append({
        '125Longitude': center_lon,
        '125Latitude': center_lat,
        'dis2': radius_meters,
        'dis2 Population': total_population
    })


final_result = excel_data.merge(
    pd.DataFrame(results),
    on=['125Longitude', '125Latitude', 'dis2'],
    how='left'
)


final_result_path = r''
final_result.to_excel(final_result_path, index=False)


affected_population_path = r''
population_df.to_csv(affected_population_path, index=False)

print(f"{final_result_path}")
print(f"{affected_population_path}")
