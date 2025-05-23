import pandas as pd
import os

# Load the CSV data
root_dir = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)
csv_file = os.path.join(root_dir, "data", "ulicegz.csv")
data = pd.read_csv(csv_file, delimiter=";")


# Function to get street information
def get_street_info(street_name):
    street_info = data[
        data["Ime ulice/trga"].str.contains(street_name, case=False, na=False)
    ]
    if not street_info.empty:
        return street_info.to_dict(orient="records")
    else:
        return None
