import io
import yaml
import os
import json

# api part
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# mailing part
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class billGenerator():
    

    # def get_integer_input(self,prompt):
    #     while True:
    #         user_input = input(prompt)
    #         if user_input.strip() == "":  # Check if the input is empty
    #             print("No input provided. Please enter a number.")
    #             continue
    #         try:
    #             return int(user_input)  # Attempt to convert the input to an integer
    #         except ValueError:
    #             print("Invalid input. Please enter a valid integer.")

    def get_integer_input(self, prompt):
        while True:
            user_input = input(prompt)
            
            if user_input == "0": #ABORT CASE
                return 0
            
            if user_input.strip() == "":  # Check if the input is empty
                print("No input provided. Please enter a number.")
                continue
            try:
                value = int(user_input)  # Attempt to convert the input to an integer
                print(f"The input you entered is: {value}")
                
                while True:
                    print("What would you like to do next?")
                    print("1. Change input")
                    print("2. Proceed with this valid input")
                    print("3. Abort BILL")
                    
                    option = input("Enter your choice (1/2/3): ")
                    
                    if option == "1":
                        break  # Go back to the main input loop to get new input
                    elif option == "2":
                        return value  # Proceed with the valid input
                    elif option == "3":
                        return 0  # Return 0
                    else:
                        print("Invalid choice. Please select 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    def get_string_input(self, prompt):
        while True:
            user_input = input(prompt).strip()  # Remove leading/trailing whitespace
            
            if user_input == "0": #ABORT CASE
                return 0
            
            if user_input == "":  # Check if the input is empty
                print("No input provided. Please enter a non-empty string.")
                continue

            print(f"The input you entered is: '{user_input}'")
            while True:
                print("What would you like to do next?")
                print("1. Change input")
                print("2. Proceed with this valid input")
                print("3. Return 0")

                option = input("Enter your choice (1/2/3): ")
                if option == "1":
                    break  # Go back to the main input loop to re-enter the string
                elif option == "2":
                    return user_input  # Proceed with the valid input
                elif option == "3":
                    return 0  # Return 0
                else:
                    print("Invalid choice. Please select 1, 2, or 3.")
                    
    def get_float_input(self, prompt):
        while True:
            user_input = input(prompt).strip()  # Remove leading/trailing whitespace
            
            if user_input == "0": #ABORT CASE
                return 0
            
            if user_input == "":  # Check if the input is empty
                print("No input provided. Please enter a number.")
                continue

            try:
                value = float(user_input)  # Attempt to convert input to a float
                print(f"The input you entered is: {value}")
                while True:
                    print("What would you like to do next?")
                    print("1. Change input")
                    print("2. Proceed with this valid input")
                    print("3. Return 0")

                    option = input("Enter your choice (1/2/3): ")
                    if option == "1":
                        break  # Go back to the main input loop to re-enter the float
                    elif option == "2":
                        return value  # Proceed with the valid input
                    elif option == "3":
                        return 0  # Return 0
                    else:
                        print("Invalid choice. Please select 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a valid float.")


    # def get_string_input(self,prompt):
    #     while True:
    #         user_input = input(prompt).strip()  # Remove leading/trailing whitespace
    #         if user_input == "":  # Check if the input is empty
    #             print("No input provided. Please enter a non-empty string.")
    #             continue
    #         return user_input  # Return the valid, non-empty string
        
    # def get_float_input(self,prompt):
    #     while True:
    #         user_input = input(prompt).strip()  # Remove leading/trailing whitespace
    #         if user_input == "":  # Check if the input is empty
    #             print("No input provided. Please enter a number.")
    #             continue
    #         try:
    #             user_input = float(user_input)  # Attempt to convert input to a float
    #             return user_input  # Exit the loop if conversion is successful
    #         except ValueError:
    #             print("Invalid input. Please enter a valid float.")

    def __init__(self):
        print('BILL GENERATOR - CLOUD')
    
        # Path to the service account credentials JSON file
        self.service_account_file = 'credentials2.json'

        # Define the required scopes
        self.scopes = [
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive'
        ]

        # Initialize Google API services
        self.credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file, scopes=self.scopes
        )
        self.docs_service = build('docs', 'v1', credentials=self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)

    def copy_document(self, new_title):
        """Create a copy of the template document."""
        copied_file = self.drive_service.files().copy(
            fileId=self.template_document_id,
            body={'name': new_title}
        ).execute()
        print(f"Document copied with new ID: {copied_file['id']}")
        return copied_file['id']

    def replace_text_in_doc(self, document_id, replacements):
        """Replace text placeholders in the specified Google Docs document."""
        requests = [
            {
                'replaceAllText': {
                    'containsText': {
                        'text': placeholder,
                        'matchCase': True
                    },
                    'replaceText': new_text
                }
            }
            for placeholder, new_text in replacements.items()
        ]

        # Send batch update request to Google Docs API
        self.docs_service.documents().batchUpdate(
            documentId=document_id, body={'requests': requests}
        ).execute()
        print("Text replacement completed successfully.")

    def download_as_pdf(self, document_id, output_file_name):
        request = self.drive_service.files().export_media(
            fileId=document_id, mimeType='application/pdf'
        )
        with io.FileIO(output_file_name, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download progress: {int(status.progress() * 100)}%")
        
        print(f"File downloaded successfully as {output_file_name}")

    def delete_document(self, document_id):
        self.drive_service.files().delete(fileId=document_id).execute()
        print(f"Document with ID {document_id} deleted from Google Drive.")
    
    def get_gmail_password(self):
        with open(self.service_account_file,'r') as f:
            y = json.load(f)
        return y["gmail_password"]

    def mail_pdf(self, pdf_path, sender_email, fac_email):
        """Send the generated PDF via email."""
        if sender_email == 1:
            sender_email = "suchithreddy26@gmail.com"  
            sender_password = self.get_gmail_password()
        elif sender_email == 2:    
            sender_email = "csreddy276@gmail.com"  
        else:
            sender_email = "suryaprakshrdy@gmail.com"
        
        # sender_password = self.get_string_input(f"Enter mail Password to mail from {sender_email}")  # Use an app password for security
        subject = "pdf_path"

        recipient_list = ["suchithreddy26@gmail.com" , "csreddy276@gmail.com" , "suryaprakshreddy@gmail.com" ''',fac_email , "shambu.arvapally@gmail.com" , "shankerallakoti@gmail.com" ''']
        
        recipient_list.remove(sender_email)

        # if self.thr == 'Annapurna':
        #     recipient_list.remove("shambu.arvapally@gmail.com")
        # elif self.thr == 'Gayatri':
        #     recipient_list.remove("shankerallakoti@gmail.com")
        

        # Create the email
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = ", ".join(recipient_list)
        message['Subject'] = subject

        # Add email body
        body = "Please find the attached bill PDF."
        message.attach(MIMEText(body, 'plain'))

        # Attach the PDF
        with open(pdf_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(pdf_path)}'
            )
            message.attach(part)

        # Send the email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            print(f"Email sent successfully to {recipient_list}!")

        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            server.quit()


    def generate_bill(self):
        """
        Process the template: Copy the document, replace text, download as PDF, 
        and optionally delete the copied document.
        """

        bill_no = vehicle_no = date = bags = through = type = qtls = actual_rate = self.factory_number = sheet_no = -1
        print('billing from - ')
        sheet_dict = {1:'SRM', 2:'SST' , 0:'ABORT'}
        while sheet_no<0 or sheet_no>2:
            print(sheet_dict)
            sheet_no = self.get_integer_input("\nEnter the Firm number")

        if not sheet_no:
            print("\nAborting.....")
            return 0
        elif sheet_no == 1:
            self.template_document_id = '1rrIgNAXiTVNQThz-HQozpIJpuWkUjP62AdfqGEHs1-I'
            title_tail = 'SRM'
            print("\nBilling from MILL (SRM) \n")
        else:
            self.template_document_id = '1xKAGWHvRkgH2OWP-e4ucUv6r9LkZtCdrSAigcGnVu4A'
            title_tail = 'SST' 
            print("\nBilling from TRADERS (SST) \n")
        

        print("SELECT THE FACTORY NUMBER")
        with open('factory_config.yaml', 'r') as file:
            factory_names = yaml.safe_load(file)
        
        while self.factory_number<0 or self.factory_number>len(factory_names):
            for self.factory_number in factory_names:
                print(self.factory_number,factory_names[self.factory_number]['Name'])
            self.factory_number = self.get_integer_input('\nEnter factory NUMBER from above list \nOR Enter 0 to ABORT:-')

        if not self.factory_number:
            print("Aborting....")
            return 0
        
        fac_address = factory_names[self.factory_number]
        reciever_address = ''
        for key in fac_address:
            reciever_address = reciever_address + key + ':' + fac_address[key] + '\n'        

        bill_no = self.get_integer_input("enter BILL NO \nOR Enter 0 to ABORT:- ")
        if not bill_no:
            print("Aborting....")
            return 0
        
        vehicle_no = self.get_string_input("enter VEHICLE NO\nOR Enter 0 to ABORT:- ")
        if not vehicle_no:
            print("Aborting....")
            return 0
        
        date = self.get_string_input("\nEnter DATE\nOR Enter 0 to ABORT:- ")
        if not date:
            print("Aborting....")
            return 0

        bags = self.get_integer_input("\nEnter BAGS\nOR Enter 0 to ABORT:- ")
        if not bags:
            print("Aborting....")
            return 0

        qtls = self.get_float_input("\nEnter WEIGHT in qtls\nOR Enter 0 to ABORT:- ")  # Remove leading/trailing whitespace
        if not qtls:
            print("Aborting....")
            return 0
            

        actual_rate = self.get_integer_input("\nEnter RATE by CSR\nOR Enter 0 to ABORT:- ")
        if not actual_rate:
            print("Aborting....")
            return 0
        
        while through<0 or through>2:
            through = self.get_integer_input("\nThrough :   \n1.Annapurna      2.Gayatri \nOR Enter 0 to ABORT:- ")
            
        if not through:
            print("Aborting....")
            return 0
        
        if through == 1:
            self.thr = 'Annapurna'
        else:
            self.thr = 'Gayatri'    

      
        while type<1 or type>2:
            type = self.get_integer_input("Bag Type :   1.Plastic      2.Jute \nOR Enter 0 to ABORT:- ")
        
        if not type:
            print("Aborting....")
            return 0
        if type == 1:
            bag_type = 'Plastic'
        else:
            bag_type = 'Jute'

        # Rate calculations
        rate=(actual_rate*100)/105
        rate=round(rate,2)
        Amount=round(rate*qtls,2)
        Cgst = round(Amount*0.025,2)
        Sgst = round(Amount*0.025,2)
        Igst = round(Amount*0.05,2)
        ttl = round(Amount+Igst,2)


        context={"BIL":bill_no,
                "VNO":vehicle_no,
                "DATE":date,
                "THR":self.thr,
                "BAGS":bags,
                "TYPE":bag_type,
                "QTL":qtls,
                "RATE":rate,
                "ACTUAL RATE":actual_rate,
                "AMT":Amount,
                "TTL":ttl,
                "FAC":reciever_address,
                "factory_name":factory_names[self.factory_number]['Name'],
                "FIRM":title_tail }
        
                # Updated replacements dictionary to convert all values to strings
        replacements = {
            '{{BIL}}': str(bill_no),
            '{{VNO}}': str(vehicle_no),
            '{{DATE}}': str(date),
            '{{THR}}': str(self.thr),
            '{{BAGS}}': str(bags),
            '{{TYPE}}': str(bag_type),
            '{{QTL}}': str(qtls),
            '{{RATE}}': str(rate),
            '{{ACTUAL RATE}}': str(actual_rate),
            '{{AMT}}': str(Amount),
            '{{TTL}}': str(ttl),
            '{{FAC}}': str(reciever_address),
            '{{factory_name}}': str(factory_names[self.factory_number]['Name']),
            '{{FIRM}}': str(title_tail)
        }

        # Additional conditional replacements based on location
        state = fac_address['State'].lower()
        if state == 'telangana':
            replacements['{{SGST}}'] = str(Sgst)
            replacements['{{CGST}}'] = str(Cgst)
            replacements['{{IGST}}'] = '----'
        else:  # For in-state factories
            replacements['{{IGST}}'] = str(Igst)
            replacements['{{SGST}}'] = '----'
            replacements['{{CGST}}'] = '----'


        # save processing
        pdf_title = 'Bill no '+ str(bill_no) + title_tail +'.pdf'
        
        # Step 1: Copy the document
        copied_document_id = self.copy_document(new_title="Updated Document Copy")
        
        # Step 2: Perform text replacements on the copied document
        self.replace_text_in_doc(copied_document_id, replacements)
        


        if os.path.exists(pdf_title):#stopped here
            print('!!!---A bill with same name :   '+pdf_title+'  already exists , do you want to override it? \n---!!!')
            print('1.Yes , create new one   \n2.No , let the old one be there \n0. ENTER 0 to ABORT')
            decision = -1
            while decision<0 or decision>2:
                decision = self.get_integer_input('select 1 or 2 :-')
            if not decision:
                print("Aborting....")
                return 0
            if decision==1:
                print('\nreplacing the existing bill with new one\n')
                pass
            else:
                print("\nnew bill generation cancelled\n")
                self.delete_document(copied_document_id)
                return 0
        
        print("generating bill")
        self.download_as_pdf(copied_document_id, pdf_title)          
        print('bill saved as pdf... :)')
        self.delete_document(copied_document_id)
        
        mail = -1
        print("Mail BILL ?")
        while(mail<0 or mail>2):
            mail = self.get_integer_input("\n1.Yes, MAILL this BIll \n2.No , continue without Mailing \n0.ENTER 0 to ABORT")
        if "Mail" not in fac_address.keys():
            print(f'the factory{fac_address} doesnt have mail id')
            mail = 2
        if not mail:
            print("Aborting....")
            return 0
        if(mail == 1):
            sender_email = 0
            while sender_email<1 or sender_email>3:
                sender_email = self.get_integer_input("sending mail from:\n 1.Suchith\n 2.Sumith\n 3.Surya\n 0.ENTER 0 to ABORT\n")
            fac_email = fac_address['Mail']
            self.mail_pdf(pdf_title, sender_email , fac_email)
        else:
            print("continuing without mailing")

        return context

# Example usage of the class
if __name__ == "__main__":
    
    # Initialize the GoogleDocsTemplateProcessor
    processor = billGenerator()

    # Process the template to create a customized PDF
    context = processor.generate_bill()
