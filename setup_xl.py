import yaml
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load mill names from mills.yaml
with open('mills.yaml', 'r') as file:
    mills_data = yaml.safe_load(file)
mills = list(mills_data.values())

# Authenticate and connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials2.json', scope)
client = gspread.authorize(credentials)

# Open the Google Sheets file
spreadsheet = client.open("FY 2024-2025 rice mill details latest")  # Replace "A" with the actual name of your spreadsheet

# Access the template sheet ('test') to copy data from
template_sheet = spreadsheet.worksheet("test")
template_data = template_sheet.get_all_values()

# Create a new worksheet for each mill
for mill in mills:
    rows = len(template_data) + 100  # Adding 100 more rows
    cols = len(template_data[0])
    # Add a new worksheet with the mill name
    new_worksheet = spreadsheet.add_worksheet(title=mill, rows=rows, cols=cols)

    # Prepare data by updating the first column with the mill name
    updated_data = template_data
    updated_data[1][0] = mill  # Assuming the "Customer Name" is in the second row, first column

    # Write data to the new worksheet
    new_worksheet.update(updated_data)

    print(f"created {mill}")
