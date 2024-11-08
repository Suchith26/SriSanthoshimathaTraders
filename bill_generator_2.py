import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import yaml
import os

class billGenerator():
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
        """Download the Google Docs document as a PDF."""
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
        """Delete the specified Google Docs document from Google Drive."""
        self.drive_service.files().delete(fileId=document_id).execute()
        print(f"Document with ID {document_id} deleted from Google Drive.")

    def generate_bill(self):
        """
        Process the template: Copy the document, replace text, download as PDF, 
        and optionally delete the copied document.
        """

        bill_no = vehicle_no = date = bags = through = type = qtls = actual_rate = factory_number = sheet_no = 0
        print('billing from - ')
        sheet_dict = {1:'SRM', 2:'SST'}
        while sheet_no<1 or sheet_no>2:
            print(sheet_dict)
            sheet_no = self.get_integer_input("\nEnter the Firm number")
        if sheet_no == 1: #hardcoded the paths
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
        
        while factory_number<1 or factory_number>len(factory_names):
            for factory_number in factory_names:
                print(factory_number,factory_names[factory_number]['Name'])
            factory_number = self.get_integer_input('\nEnter factory NUMBER from above list:-')

        fac_address = factory_names[factory_number]
        reciever_address = ''
        for key in fac_address:
            reciever_address = reciever_address + key + ':' + fac_address[key] + '\n'        

        bill_no = self.get_integer_input("enter BILL NO: ")
        vehicle_no = self.get_string_input("enter VEHICLE NO: ")
        date = self.get_string_input("enter DATE: ")
        bags = self.get_integer_input("enter BAGS: ")

        qtls = self.get_float_input("enter WEIGHT in qtls: ")  # Remove leading/trailing whitespace
            

        actual_rate = self.get_integer_input("enter RATE by CSR: ")

        
        while through<1 or through>2:
            through = self.get_integer_input("Through :   1.Annapurna      2.Gayatri : ")
            
        if through == 1:
            thr = 'Annapurna'
        else:
            thr = 'Gayatri'    

      
        while type<1 or type>2:
            type = self.get_integer_input("Bag Type :   1.Plastic      2.Jute : ")
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
                "THR":thr,
                "BAGS":bags,
                "TYPE":bag_type,
                "QTL":qtls,
                "RATE":rate,
                "ACTUAL RATE":actual_rate,
                "AMT":Amount,
                "TTL":ttl,
                "FAC":reciever_address,
                "factory_name":factory_names[factory_number]['Name'],
                "FIRM":title_tail }
        
                # Updated replacements dictionary to convert all values to strings
        replacements = {
            '{{BIL}}': str(bill_no),
            '{{VNO}}': str(vehicle_no),
            '{{DATE}}': str(date),
            '{{THR}}': str(thr),
            '{{BAGS}}': str(bags),
            '{{TYPE}}': str(bag_type),
            '{{QTL}}': str(qtls),
            '{{RATE}}': str(rate),
            '{{ACTUAL RATE}}': str(actual_rate),
            '{{AMT}}': str(Amount),
            '{{TTL}}': str(ttl),
            '{{FAC}}': str(reciever_address),
            '{{factory_name}}': str(factory_names[factory_number]['Name']),
            '{{FIRM}}': str(title_tail)
        }

        # Additional conditional replacements based on location
        if factory_number > 5:  # For out-of-state factories
            replacements['{{IGST}}'] = str(Igst)
            replacements['{{SGST}}'] = '----'
            replacements['{{CGST}}'] = '----'
        else:  # For in-state factories
            replacements['{{SGST}}'] = str(Sgst)
            replacements['{{CGST}}'] = str(Cgst)
            replacements['{{IGST}}'] = '----'


        # save processing
        pdf_title = 'Bill no '+ str(bill_no) + title_tail +'.pdf'
        
        # Step 1: Copy the document
        copied_document_id = self.copy_document(new_title="Updated Document Copy")
        
        # Step 2: Perform text replacements on the copied document
        self.replace_text_in_doc(copied_document_id, replacements)
        


        if os.path.exists(pdf_title):#stopped here
            print('!!!---A bill with same name :   '+pdf_title+'  already exists , do you want to override it? \n---!!!')
            print('1.Yes , create new one   \n2.No , let the old one be there')
            decision = 0
            while decision<1 or decision>2:
                decision = self.get_integer_input('select 1 or 2 :-')
            if decision==1:
                print('\nreplacing the existing bill with new one\n')
                pass
            else:
                print("\nnew bill generation cancelled\n")
                self.delete_document(copied_document_id)
                return 0
        
        print("generating bill")
        self.download_as_pdf(copied_document_id, pdf_title)          
        print('bill saved as pdf...:)')
        self.delete_document(copied_document_id)

        return context

# Example usage of the class
if __name__ == "__main__":
    
    # Initialize the GoogleDocsTemplateProcessor
    processor = billGenerator()

    # Process the template to create a customized PDF
    context = processor.generate_bill()
