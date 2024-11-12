# sri santhoshimatha ricemill
# program to 
# generate bill
# append bill to excel
# update amounts in excel
# display mill details
# remittances
import os
import json
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import yaml
from pathlib import Path
from docxtpl import DocxTemplate
from docx2pdf import convert

from bill_generator_2 import billGenerator


#stopping here :- append detail to mill sheet completed , import get_int_inputs and apply to all inputs
#sort the mill , fac lists in alphabetical order

class update():
    def get_integer_input(self,prompt):
        while True:
            user_input = input(prompt)
            if user_input.strip() == "":  # Check if the input is empty
                print("No input provided. Please enter a number.")
                continue
            try:
                return int(user_input)  # Attempt to convert the input to an integer
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    def get_string_input(self,prompt):
        while True:
            user_input = input(prompt).strip()  # Remove leading/trailing whitespace
            if user_input == "":  # Check if the input is empty
                print("No input provided. Please enter a non-empty string.")
                continue
            return user_input  # Return the valid, non-empty string
        
    def get_float_input(self,prompt):
        while True:
            user_input = input(prompt).strip()  # Remove leading/trailing whitespace
            if user_input == "":  # Check if the input is empty
                print("No input provided. Please enter a number.")
                continue
            try:
                user_input = float(user_input)  # Attempt to convert input to a float
                return user_input  # Exit the loop if conversion is successful
            except ValueError:
                print("Invalid input. Please enter a valid float.")

    def __init__(self):
        print('-'*50)
        print("FY 2024-25")
        print('-'*50)
        self.spreadsheet_id = '1nvdutA1w3neqZ57rlE3PH2Fm6ACPr3dKPsnrkEioMJI'  # to fetch sheets
        self.credentials_file = 'credentials.json'
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive",'https://www.googleapis.com/auth/documents']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, self.scope)
        self.client = gspread.authorize(self.creds)

    def downcast(self,df): # CONVERTS THE INTEGER VALUES ,READ AS STR BY PANDAS ,INTO INT AGAIN
        if 'WEIGHT' in df.columns:
            df['WEIGHT'] = pd.to_numeric(df['WEIGHT'], errors='coerce', downcast='float')
        
        columns = ['BAGS','RATE','BILL NO','COST','PURCHASE TOTAL','AMOUNT PAID','PAID TOTAL','BALANCE']
        for column in columns:#for every name in above list
            if column in df.columns:#if that name exists in table
                df[column] = pd.to_numeric(df[column], errors='coerce', downcast='integer') #then converts ENTIRE COLUMN into integer

    # Load DataFrame from Google Sheets
    def load_dataframe_from_sheet(self,sheet_name):
        sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)
        data = sheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])  # Use first row as header
        self.downcast(df) 
        return df

    def save_dataframe_to_sheet(self,df, sheet_name):
    # Replace NaN and infinite values with None (or 0, or another appropriate value)
        df.replace([np.inf, -np.inf, np.nan], None, inplace=True)
        sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)

        # Update the sheet with cleaned data
        sheet.update([df.columns.values.tolist()] + df.values.tolist())

    def get_mills_list(self):
        
        with open('mills.yaml','r') as f:
            mill_list = yaml.safe_load(f)  
        mills_per_row = 3
        mills = list(mill_list.items())  # Convert dict items to a list for easier iteration

        key_width = 5  # Width for the key
        value_width = 30  # Width for the value
        print('\n\n MILLS LIST \n')
        for i in range(0, len(mills), mills_per_row):
                row_mills = []
                for j in range(mills_per_row):
                    if i + j < len(mills):  # Check if the index is within the bounds
                        key, value = mills[i + j]
                        row_mills.append(f"{key}: {value.ljust(value_width)}")  # Left justify values
                print("".join(row_mills))
        return mill_list

    def check_bill_redundancy(self,df,bill_no): #check if bill already exists in fac sheet
        exists = df[(df['BILL NO'] == bill_no)].shape[0] > 0
        return exists

    def append_bill_to_factory_sheet(self,bill_details):
        sheet_name = bill_details['FIRM']
        print('Appending bill-',bill_details['BIL'],'to factory sheet of -',sheet_name,'\n')
        df = self.load_dataframe_from_sheet(sheet_name) #getting the whole factory sheet of sst or srm into a df
        
        bill_exists = self.check_bill_redundancy(df,bill_details['BIL'])
        if bill_exists:
            row = df[(df['BILL NO'] == bill_details['BIL'])]
            print("The bill no already exist , so updating with new values")
            row_index = row.index[0] #index of that particular bill
            
            df.at[row_index, 'DATE'] = str(bill_details['DATE'])
            df.at[row_index,'VEHICLE NO'] = str(bill_details['VNO'])
            df.at[row_index,'BAGS'] = bill_details['BAGS']
            df.at[row_index,'SOLVEX'] = bill_details['factory_name']   
            df.at[row_index,'WEIGHT'] = str(bill_details['QTL'])
            df.at[row_index,'RATE'] = bill_details['ACTUAL RATE']
            df.at[row_index,'THROUGH'] = bill_details['THR']
        

        else:    
            new_row = pd.DataFrame([{
                'BILL NO': bill_details['BIL'],
                'DATE': bill_details['DATE'],
                'VEHICLE NO': bill_details['VNO'],
                'BAGS': bill_details['BAGS'],
                'SOLVEX': bill_details['factory_name'],
                'WEIGHT': bill_details['QTL'],
                'RATE': bill_details['ACTUAL RATE'],
                'THROUGH': bill_details['THR']
            }])

            # Concatenate the new row with the existing DataFrame
            df = pd.concat([df, new_row], ignore_index=True)
        
        self.save_dataframe_to_sheet(df,sheet_name)
        print(f"\nBill no -{bill_details['BIL']} Append Successfull to {bill_details['FIRM']} factory sheet")
        
    def append_detail_to_mill_table(self,firm,bill_no):
        i=1
        mills_updated='' #list of mills updated in this bill
        
        while i==1:
            mill_list = self.get_mills_list()

            j=0    
            while j<1 or j>len(mill_list):
                mill_number= j = self.get_integer_input('\n Enter the mill no from above list:-')
            
            mill_name = mill_list[mill_number]
            df = self.load_dataframe_from_sheet(mill_name)
            date = self.get_string_input('\nDate:-')
            bags = self.get_integer_input('\nBags:-')
            weight = self.get_float_input('\nWeight in quintals:-')
            rate = self.get_integer_input('\nMill_Rate:-')
            cost = rate*weight


            new_row = pd.DataFrame([{
            'BILL NO': bill_no,
            'FROM': firm,
            'DATE': date,
            'BAGS': bags,
            'WEIGHT': weight,
            'RATE': rate,
            'COST': cost,
            # 'VEHICLE NO': bill_details['VNO'],
            }])

            # Concatenate the new row with the existing DataFrame
            df = pd.concat([df, new_row], ignore_index=True)
            
            purchase_total = df['COST'].sum()
            df.at[0, 'PURCHASE TOTAL'] = purchase_total
            df.at[0,'BALANCE'] = purchase_total - df.at[0,'PAID TOTAL']
            
            self.save_dataframe_to_sheet(df,mill_name)

            print("Mill Append Successfull")
            mills_updated = mills_updated +','+ mill_name
            i = self.get_integer_input('1.update another mill in this bill detail \nOR PRESS ANY KEY TO SAVE AND EXIT')

        return mills_updated
            

    def check_bill_with_credentials(self,vno,unload_date,bags): #check if the bill is existing in factory sheet and add if exists   
        firms = {1:'SRM',2:'SST'}
        for firm in firms: #check in both factory sheets
            df = self.load_dataframe_from_sheet(firms[firm])
            result = df[(df['DATE'] == unload_date) & 
                (df['VEHICLE NO'] == vno) & 
                (df['BAGS'] == bags)]

            if not result.empty:
                print("The values exist in" , firms[firm])
                bill_no = result.iloc[0]['BILL NO']
                mills_updated = self.append_detail_to_mill_table(firms[firm] , bill_no) # add detail to mills tables
                extras = self.get_integer_input('\nEnter no of bags , if any EXTRAS :- ')

                row_index = result.index[0] #index of that particular bill
                
                df.at[row_index, 'MILLS'] = mills_updated
                df.at[row_index,'EXTRA'] = extras
                self.save_dataframe_to_sheet(df,firms[firm]) #updating the factory sheet by appending mills
                print("\nMills detail Append at factory sheet Successfull")
                return
            else:
                print("The values do not exist in -",firms[firm],"-")
        print(" !!!! The values did not tally , please check the factory tables :( ")        
        return

    def detail_update(self):
        print("update factory , mills after getting detail")
        unload_date = self.get_string_input("Enter the UNLOADING DATE of this vehicle:- ")
        vno = self.get_string_input("Enter this VEHICLE NUMBER:- ")
        bags = self.get_integer_input("Enter the TOTAL no of BAGS in this vehicle:- ")
        self.check_bill_with_credentials(vno,unload_date,bags)
         
    def amount_update(self): # update totals too, hardcode
        print("update amount to mills")
        while True:
            mill_list = self.get_mills_list()
            mill_number = self.get_integer_input("Enter the MILL Number:- ")
            if mill_number == 100:
                break
            df = self.load_dataframe_from_sheet(mill_list[mill_number])
            print(f'DISPLAYING {mill_list[mill_number]} TABLE :-',df)
            user_input = self.get_integer_input("->Enter 1 if you still want to update this mill OR \n->Enter 2 to EXIT back to MAIN MENU OR \n->Enter ANY KEY to see MILL LIST :-")
            
            if user_input == 2:
                break
            
            while user_input ==1:
                date = self.get_string_input("enter the DATE paid on:-")
                amount = self.get_integer_input("enter the AMOUNT paid:-")
                from_bank = self.get_string_input("enter the BANK ACCOUNT paid from:-")
                to_bank = self.get_string_input("enter the BANK ACCOUNT paid TO:-") # USE IF NECESSARY

                df.replace("", np.nan, inplace=True)
                target_columns = ['PAID ON','AMOUNT PAID','PAID FROM']
                new_values = [date,amount,from_bank]

                # Append new values to the first NaN cell in each target column

                for col, value in zip(target_columns, new_values):
                    first_empty_index = df[col].isna().idxmax()  # Finds the first index with NaN
                    df.at[first_empty_index, col] = value
                user_input = self.get_integer_input("Enter 1 if you still want to add another amount in SAME MILL\n OR enter ANY KEY to SAVE and EXIT this mill:-")    
            
            if user_input!=1:  
                paid_total = df['AMOUNT PAID'].sum()
                
                df.at[0, 'PAID TOTAL'] = paid_total
                df.at[0,'BALANCE'] = df.at[0, 'PURCHASE TOTAL'] - paid_total
                
                self.save_dataframe_to_sheet(df,mill_list[mill_number])
                print(f'updated table of {mill_list[mill_number]}:-\n',df)
            
    def cancel_bill(self,bill_no,sheet_name):
        df = self.load_dataframe_from_sheet(sheet_name)
        if bill_no in df['BILL NO'].values:
            row_index = df[df['BILL NO'] == bill_no].index[0]
            df.loc[row_index,'BAGS'] = 0
            df.loc[row_index,'RATE'] = 0
            df.loc[row_index,'WEIGHT'] = 0
            df.loc[row_index,'EXTRA'] = 0
            df.loc[row_index,'SOLVEX'] = 'cancelled'
            df.loc[row_index,'DATE'] = 'cancelled'
            df.loc[row_index,'VEHICLE NO'] = 'cancelled'
            df.loc[row_index,'THROUGH'] = 'cancelled'
            df.loc[row_index,'MILLS'] = 'cancelled'
            self.save_dataframe_to_sheet(df,sheet_name)
            print(f'Bill no {bill_no} , {sheet_name} Cancelled successfully in factory sheet')
        else:
            print(f'Bill no {bill_no} , {sheet_name} not found in factory sheet :( ')    
            


if __name__ == '__main__':
    print('='*50)
    print("\nJAI SANTHOSHIMATHA \n")
    print('='*50)
    print("WELCOME TO sunny gadi code \n")
    
    upc = update()
    while True:
        i=0
        while i<1 or i>7:
            print("\nMAIN MENU :\n1.Generate Bill \n2.Detail Update \n3.Amount Update \n4.Display Mill Data \n5.Display Factory Data \n6.Cancel bill in fac sheet \n7.EXIT")
            print('type a number in 1,2,3,4,5,6')
            i = upc.get_integer_input("Choose a operation:- \n")

        if i==1:
            print("\n \n Generating New Bill \n\n")
            bgc = billGenerator()
            bill_details = bgc.generate_bill()
            if bill_details:
                upc.append_bill_to_factory_sheet(bill_details)
            else:
                print('New bill not generated or Old bill is not overwrited :)')    
        elif i==2:
            print("\n \n Updating Detail \n\n")
            upc.detail_update()
        elif i==3:
            print("\n \n Updating Amount \n\n")
            upc.amount_update()
        elif i==4:# print mill sheet
            while True:
                mill_list = upc.get_mills_list()
                mill_number = upc.get_integer_input('\nEnter the MILL NUMBER to get mill details\n')
                print(f'TABLE OF {mill_list[mill_number]} :-')
                print(upc.load_dataframe_from_sheet(mill_list[mill_number]))
                print('-'*50)
                exit = upc.get_integer_input('\nPress 1 to see OTHER mills tables\n Press ANY KEY to EXIT')
                if exit!=1:
                    break
        elif i==5:# print factory sheet
            while True:
                sheet_no = 0
                sheet_dict = {1:'SRM',2:'SST'}
                while sheet_no<1 or sheet_no>2: 
                    print(sheet_dict)
                    sheet_no = upc.get_integer_input("\nEnter the Firm number:-")
                df = upc.load_dataframe_from_sheet(sheet_dict[sheet_no])
                print(f'FACTORY TABLE of {sheet_dict[sheet_no]}')
                print(df)
                exit = upc.get_integer_input('\nPress 1 to see OTHER Factory tables\n Press ANY KEY to EXIT')
                if exit!=1:
                    break
        elif i ==6:
            print('BILL CANCELLING in factory sheet')
            print('-'*50) 
            bill_no = upc.get_integer_input("\nEnter the BILL NO:-")
            sheet_no = 0
            sheet_dict = {1:'SRM',2:'SST'}
            while sheet_no<1 or sheet_no>2: 
                print(sheet_dict)
                sheet_no = upc.get_integer_input("\nEnter the Firm number:-")
            upc.cancel_bill(bill_no,sheet_dict[sheet_no])    
        else:
            break            


# print(type(df.iloc[-2]["BAGS"]), df.iloc[-2]['BAGS'] )  - GET A ITEM BY LOCATION
# print(df,df.dtypes)    - df , column types
            
