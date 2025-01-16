import pandas as pd
import folium

# Read the CSV file
csv_file = "Geoportal_visokoskolske_ustanove.csv"
data = pd.read_csv(csv_file)

# Calculate the average coordinates for centering the map
avg_lat = data["Y"].mean()
avg_lon = data["X"].mean()

# Create a map centered around the average coordinates
map = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

# Add markers for each location
for index, row in data.iterrows():
    folium.Marker(
        location=[row["Y"], row["X"]], popup=row["naziv"], tooltip=row["naziv"]
    ).add_to(map)

# Save the map to an HTML file
map.save("locations_map.html")
