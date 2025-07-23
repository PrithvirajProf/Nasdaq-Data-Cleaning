import pandas as pd
import re
import json
import numpy as np
from natsort import natsorted

def indexChecker(in1,in2):
    index1 = 0
    index2 = 0
    if in1 and in2 in sortedProps:
        for i in range(len(sortedProps)):
            if sortedProps[i] == in1:
                index1 = i
            elif sortedProps[i]==in2:
                index2 = i
        if index1 == 0 or index2 ==0:
            return False
        elif index1>index2:
            return True
        else:
            return False

with open('appleton_npx 1 1.txt', 'r', encoding='utf-8') as f:
       text = f.read()
pattern = r'(?s)-{50,}(.+?)(?=-{50,}|SIGNATURES)'
company_sections = re.findall(pattern, text)

"""Data is now divided into different sections based on hyphens"""

CNANList = []
for i in range(len(company_sections)):
    if (i==0 or (i%3==0)):
        company_name_match = re.search(r'^\s*(.*?)\s{2,}Agenda Number:', company_sections[i])
        agenda_number_match = re.search(r'Agenda Number:\s*(\S+)',company_sections[i])
        security_match = re.search(r'Security:\s*(\S+)',company_sections[i+1])
        meeting_type_match = re.search(r'Meeting Type:\s*(\S+)',company_sections[i+1])
        meeting_date_match = re.search(r'Meeting Date:\s*(.*?)\n',company_sections[i+1])
        ticker_match = re.search(r'Ticker:\s*(\S+)',company_sections[i+1])
        isin_match = re.search(r'ISIN:\s*(\S+)',company_sections[i+1])
        CNAN={    
        "Company Name": company_name_match.group(1).strip() if company_name_match else None,
        "Agenda Number": agenda_number_match.group(1).strip() if agenda_number_match else None,       
        "Security": security_match.group(1).strip() if security_match else None,
        "Meeting Type": meeting_type_match.group(1).strip() if meeting_type_match else None,
        "Meeting Date": meeting_date_match.group(1).strip() if meeting_date_match else None,
        "Ticker": ticker_match.group(1).strip() if ticker_match else None,
        "ISIN": isin_match.group(1).strip() if isin_match else None,
        }
        CNANList.append(CNAN)

        

"""Common_data_list array will conain list of all the companies with column headings:
                "Company Name",
                "Agenda Number",
                "Security",
                "Meeting Type",
                "Meeting Date",
                "Ticker",
                "ISIN"
"""

df1 = pd.DataFrame(CNANList)    #defining a data frame to store the above data
df1['IDs'] = [i for i in range(1,len(df1['Security'])+1)]
df1.set_index('IDs')            #Setting IDs for each company will later help us in merging the two DataFrames


input_file = "proposalsOnly.txt"
# Read the entire text file
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
lines = [line for line in lines if line != '\n']
proposalsList = []
templist = []
for i in range(0,len(lines)):
    p1 = re.search(r'(?P<Prop>[0-9][A-Z]\.|[0-9]\.[0-9]|[0-9]\.[^\n])\s{2,}(?P<Proposal>.+?[^\n\w])\s{2,}(?P<Type>.+?)\s{2,}(?P<Vote>.+?)\s{2,}(?P<For_Against>\w{1,})',lines[i])
    searchDirectors = re.search(r'(?P<Prop>[0-9][A-Z]\.|[0-9]\.[0-9]|[0-9]\.[^\n])\s{2,}(?P<Proposal>[A-Z]*)+?',lines[i])
    searchNameOfDirectors = re.search(r'\s{7,}(?P<Proposal>[^1-9][^\s].+?)\s{2,}(?P<Type>Mgmt|Shr|Non\-Voting)\s{2,}(?P<Vote>.+?)\s{2,}(?P<For_Against>For|Against)',lines[i])
    pattern_not_use1 = re.search(r'Prop.\# Proposal\s{2,}.+',lines[i])
    pattern_not_use2 = re.search(r'\s{2,}Type\s{2,}\w+',lines[i])
    if p1:
        #('pattern1 here')
        myDict = {
            "Prop":p1.group('Prop').strip(),
            "Proposal":p1.group('Proposal').strip(),
            "Proposal Type":p1.group('Type').strip(),
            "Proposal Vote":p1.group('Vote').strip(),
            "For/Against Management":p1.group('For_Against')
        }
        proposalsList.append(myDict)
    elif searchDirectors:
        #Search for "Director"
        myDict={
            "Prop":searchDirectors.group('Prop').strip(),
            "Proposal":searchDirectors.group('Proposal').strip()
        }
        proposalsList.append(myDict)
    elif searchNameOfDirectors:
        #Search for ("Name of Directors")
        myDict={
            "Proposal":searchNameOfDirectors.group('Proposal').strip(),
            "Proposal Type":searchNameOfDirectors.group('Type').strip(),
            "Proposal Vote":searchNameOfDirectors.group('Vote').strip(),
            "For/Against Management":searchNameOfDirectors.group('For_Against')            
        }
        proposalsList.append(myDict)
    elif pattern_not_use1:
        #Will not pick the pattern : " Prop.# Proposal                                                  Proposal      Proposal Vote                  For/Against"
        continue
    elif pattern_not_use2:
        #Will not pick the pattern : "  Type                                         Management"   
        continue
    else:
        #All the lines which needs to be merged are appended here
        stringTemp = lines[i].strip()
        proposalsList[-1]['Proposal'] = proposalsList[-1]['Proposal'] + ' ' + stringTemp

df = pd.DataFrame(proposalsList)                #Will store the information in a DataFrame 
props = df['Prop']                              #List of all Prop Numbers
sortedProps = natsorted(props.unique())         #Bulit in funtion in NatSort ised for natural sorting
"""
The following code will define IDs for propInfo dataframe which will be used to merge two documents.
"""
count = 1   
currentID = []
for i in range(0,len(props)-1):
    if i == 0:
        currentID.append(count)
    elif indexChecker(props[i],props[i+1]):
        currentID.append(count)
        count = count + 1
    else:
        currentID.append(count)
currentID.append(count)
df['IDs'] = currentID
df.set_index('IDs')                         #Correct ID set

# Merging two DataFrames based on IDs

merged_df = pd.merge(df1, df , on='IDs', how='inner')
columns_to_drop = ['Unnamed: 0_x', 'Unnamed: 0_y', 'IDs']
existing_columns = [col for col in columns_to_drop if col in merged_df.columns]
merged_df.drop(columns=existing_columns, inplace=True)


# Exporting to a CSV file
merged_df.to_csv("appleton_npx1.csv")