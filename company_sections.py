import pandas as pd
import re

input_file = "appleton_npx 1 1.txt"
  
with open(input_file, 'r', encoding='utf-8') as f:
       text = f.read() 
#This is used to import file
     
#seperates the data on the basis of hyphens(----) which will further help us clean it and work around it
pattern = r'(?s)-{50,}(.+?)(?=-{50,}|SIGNATURES)' 
company_sections = re.findall(pattern, text)

common_data_list = []   #An empty list which will be later used to append data as we scan through each intex of the list 'company_section'.
for section in company_sections:     #Runs a loop in "company section" array.
    company_name_match = re.search(r'^\s*(.*?)\s{2,}Agenda Number:', section)       #RegEX to match "Company Name"
    agenda_number_match = re.search(r'Agenda Number:\s*(\S+)',section)              #RegEX to match "Agenda Number"
    security_match = re.search(r'Security:\s*(\S+)',section)                        #RegEX to match "Security"
    meeting_type_match = re.search(r'Meeting Type:\s*(\S+)',section)                #RegEX to match "Meeting Type"
    meeting_date_match = re.search(r'Meeting Date:\s*(.*?)\n',section)              #RegEX to match "Meeting Date"
    ticker_match = re.search(r'Ticker:\s*(\S+)',section)                            #RegEX to match "Ticker"
    isin_match = re.search(r'ISIN:\s*(\S+)',section)                                #RegEX to match "ISIN"
    common_data = {                                                                 #a dectionary in JSON Format wihich will help in data storing with its header.             
                "Company Name": company_name_match.group(1).strip() if company_name_match else None,        
                "Agenda Number": agenda_number_match.group(1).strip() if agenda_number_match else None,
                "Security": security_match.group(1).strip() if security_match else None,
                "Meeting Type": meeting_type_match.group(1).strip() if meeting_type_match else None,
                "Meeting Date": meeting_date_match.group(1).strip() if meeting_date_match else None,
                "Ticker": ticker_match.group(1).strip() if ticker_match else None,
                "ISIN": isin_match.group(1).strip() if isin_match else None,
        }
    common_data_list.append(common_data)                                             #Appendinng the dictionary after every iteration of the loop

companyInfo = pd.DataFrame(common_data_list)                                         #Converting into DataFrame using Pandas library

