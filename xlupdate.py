import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np

# Authenticate and create the client
mill_list = {1:'Aravind',2:'Thummanpet'}
def append_paddhu():
    print("WELCOME TO add paddhu \n")
    
    for key in mill_list:
        print(key,".",mill_list[key])
    mill_no = int(input(print('Select Mill Name from the list above:-')))    

    while mill_no<1 or mill_no>len(mill_list):
        for key in mill_list:
            print(key,".",mill_list[key])
        mill_no = int(input(print('please enter a number from the list above:-')))    
        
    sheet_name = mill_list[mill_no]
    spreadsheet_id = '1nvdutA1w3neqZ57rlE3PH2Fm6ACPr3dKPsnrkEioMJI'  # Replace with your Google Sheets ID

    credentials_file = 'credentials.json'

    # Load DataFrame
    df = load_dataframe_from_sheet(spreadsheet_id, sheet_name, credentials_file)

    print("ENTER THE FOLLOWING DETAILS:-\n")
    date = input("date")
    bags = input("bags")
    quintals = input("quintals")
    rate = input("rate")
    through = input("billed from sst/srm") #stopped here

    # updating things
    df.loc[len(df), 'Date'] = date  
    df.loc[len(df), 'Bags'] = bags
    df.loc[len(df), 'Quintals'] = quintals
    df.loc[len(df), 'Rate'] = rate  
    df.loc[len(df), ' '] = new_value  





def append_payment(payment_dict): 


def authenticate_gspread(credentials_file):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    return client

# Load DataFrame from Google Sheets
def load_dataframe_from_sheet(spreadsheet_id, sheet_name, credentials_file):
    client = authenticate_gspread(credentials_file)
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])  # Use first row as header
    return df

# Append value to 'Bags' column
def append_to_bags(df, new_value):
    df.loc[len(df), 'Bags'] = new_value  # Appends to the next available row in 'Bags' column

# Save updated DataFrame back to Google Sheets with clean data
def save_dataframe_to_sheet(df, spreadsheet_id, sheet_name, credentials_file):
    # Replace NaN and infinite values with None (or 0, or another appropriate value)
    df.replace([np.inf, -np.inf, np.nan], None, inplace=True)

    client = authenticate_gspread(credentials_file)
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    
    # Update the sheet with cleaned data
    sheet.update([df.columns.values.tolist()] + df.values.tolist())  # Update with new data


print("JAI SANTHOSHIMATHA \n")
print("WELCOME TO XL UPDATE \n")
print("Choose a operation:- \n")
i = input(print("1.add_paddhu      2.add_payment       3.Exit"))
while i<1 or i>3:
    i=input(print('type a number in 1,2,3 as reply'))
    print("1.add_paddhu      2.add_payment       3.Exit")
if i==1:
    append_paddhu()
elif i==2:
    append_payment()
else:
    exit()            

# Usage
spreadsheet_id = '1nvdutA1w3neqZ57rlE3PH2Fm6ACPr3dKPsnrkEioMJI'  # Replace with your Google Sheets ID
sheet_name = 'test' 
credentials_file = 'credentials.json'

# Load DataFrame
df = load_dataframe_from_sheet(spreadsheet_id, sheet_name, credentials_file)

# Append a value to 'Bags' column
append_to_bags(df, 10)


# Save back to Google Sheets
save_dataframe_to_sheet(df, spreadsheet_id, sheet_name, credentials_file)
