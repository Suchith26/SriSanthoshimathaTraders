import yaml
from pathlib import Path
from docxtpl import DocxTemplate
from docx2pdf import convert


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



    def generate_bill(self):

        bill_no = vehicle_no = date = bags = through = type = qtls = actual_rate = factory_number = sheet_no = 0

        sheet_dict = {1:'SRM', 2:'SST'}
        while sheet_no<1 or sheet_no>2:
            print(sheet_dict)
            sheet_no = self.get_integer_input("\nEnter the Firm number")
        if sheet_no == 1: #hardcoded the paths
            document_path = Path(__file__).parent/"BILL SRM.docx"
            title_tail = 'SRM'
            print("\nBilling from TRADERS \n")
        else:
            document_path = Path(__file__).parent/"BILL SST.docx"   
            title_tail = 'SST' 
            print("\nBilling from RICEMILL \n")
        doc=DocxTemplate(document_path) 

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
            through = self.get_integer_input("Through :   1.Annapurna      2.Gayatri")
            
        if through == 1:
            thr = 'Annapurna'
        else:
            thr = 'Gayatri'    

      
        while type<1 or type>2:
            type = self.get_integer_input("Bag Type :   1.Plastic      2.Jute")
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


        #file content building and rendering
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
        
        if factory_number>5: #hardcode , if fac no in list is>5 ,then considered as out of ts factorys
            context["IGST"] = Igst
            context["SGST"] = '----'
            context["CGST"] = '----'
        else:
            context["SGST"] = Sgst
            context["CGST"] = Cgst
            context["IGST"] = '----'

        doc.render(context)#writing details into word doc



        # save processing
        title = 'Bill no '+ str(bill_no) + title_tail +'.docx'
        pdf_title = 'Bill no '+ str(bill_no) + title_tail +'.pdf'
        doc.save(Path(__file__).parent/title) #saving as the new word doc
        
        docx = Path(__file__).parent/title
        pdfx = Path(__file__).parent/pdf_title

        if pdfx.exists():
            print('!!!---A bill with same name :'+str(pdfx)+'already exists , do you want to override it? \n---!!!')
            print('1.Yes , create new one   \n2.No , let the old one be there')
            decision = 0
            exist_in_xl = 1
            while decision<1 or decision>2:
                decision = int(input('select 1 or 2 :-'))
            if decision==1:
                pass
            else:
                docx.unlink()
                return 0
        else:

            pass

        print("generating bill")
        convert(docx,pdfx)
        docx.unlink() #removing word doc after pdf generation
        print('bill saved as pdf...:)')

        return context

if __name__ == '__main__':
    bgc = billGenerator()
    bgc.generate_bill()