import pandas as pd
import re
import json
import numpy as np
from natsort import natsorted

def fileType(input_file):
    """
    This functions check which type of file it is which then is cleaned based on the format.
    """
    with open(input_file, 'r', encoding='utf-8') as f: 
        text = f.read()
    pattern1 = '---------------'
    pattern2 = '_______________' 
    if pattern1 in text:
        format1(text)
    elif pattern2 in text:
        format2(text)
    else:
        print("No common pattern detected.")


def format1(text):
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
    with open('proposalsOnly.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    lines = [line for line in lines if line != '\n']
    proposalsList = []
    templist = []
    for i in range(0,len(lines)):
        p1 = re.search(r'(?P<Prop>[0-9][A-z]\.|[0-9]\.[0-9]|[0-9]\.[^\n])\s{2,}(?P<Proposal>.+?[^\n\w])\s{2,}(?P<Type>.+?)\s{2,}(?P<Vote>.+?)\s{2,}(?P<For_Against>\w{1,})',lines[i])
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
                "Proposal Vote":p1.group('Vote').strip() if p1 else '',
                "For/Against Management":p1.group('For_Against') if p1 else ''
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

    df = pd.DataFrame(proposalsList)
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
        elif indexChecker(props[i],props[i+1],sortedProps):
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
    output_file = input("What should the output file be called (add '.csv' at the end):")
    merged_df.to_csv(output_file)

def format2(text):
    pattern = r'(?s){50,}(.+?)(?={50,}|SIGNATURES)'
    company_sections = re.findall(pattern, text)
    """
    Data is now divided in different sections
    """
    detailsList = []

    for section in company_sections:
        company_name_match = re.search(r'(.{1,20})', section)                               # pattern to find Company Name
        company_name = company_name_match.group(1).strip() if company_name_match else ''

        details_match = re.search(r'\n(?P<Ticker>.{1,5})\s{2,}(?P<SecurityID>.{1,20})\s{2,}(?P<MeetingDate>.{1,10})\s{2,}(?P<MeetingStatus>.{1,15})', section)
        # based on the match, data is divided in different groups like:
        # {Ticker, SecurityID, Meeting ID etc}
        details_match2 = re.search(r'\n(?P<MeetingType>[A-z]+)\s{15,}(?P<Country>.{1,20})\n', section)
        
        # Note: 'propDetails' is initialized but never used.
        propDetails = []
        subsections = section.split('\n')

        for i in subsections:
            proposal_match = re.search(r'(?P<IssueNo>[0-9][A-Z]\.|[0-9]\.[0-9]|[0-9]\.|[0-9])\s{1,}(?P<Description>.{1,22}[^\s])\s{1,}(?P<Proponent>.{1,5}[^\s])\s{1,}(?P<Record>.{1,6}[^\s])\s{2,}(?P<Vote>.{1,5}[^\s])\s{2,}(?P<For_Against>.{1,8}[^\s])', i)

            if details_match:
                ticker = details_match.group('Ticker').strip() if details_match else ''
                securityID = details_match.group('SecurityID').strip() if details_match else ''
                meetingDate = details_match.group('MeetingDate').strip() if details_match else ''
                meetingStatus = details_match.group('MeetingStatus').strip() if details_match else ''
                meetingType = details_match2.group('MeetingType').strip() if details_match2 else ''
                country = details_match2.group('Country').strip() if details_match2 else ''

                number = proposal_match.group('IssueNo').strip() if proposal_match else ''
                description = proposal_match.group('Description').strip() if proposal_match else ''
                proponent = proposal_match.group('Proponent').strip() if proposal_match else ''
                record = proposal_match.group('Record').strip() if proposal_match else ''
                vote = proposal_match.group('Vote').strip() if proposal_match else ''
                forAgainst = proposal_match.group('For_Against').strip() if proposal_match else ''

                if description == '':
                    pass
                elif description != "" and number != "" and record != "":
                    details = {
                        "Company Name": company_name,
                        "Ticker": ticker,
                        "Security ID": securityID,
                        "Meeting Date": meetingDate,
                        "Meeting Status": meetingStatus,
                        "Meeting type": meetingType,
                        "Country of Trade": country,
                        'Issue Number': number,
                        'Description': description,
                        'Proponent': proponent,
                        'Management Record': record,
                        'Vote Cast': vote,
                        'For Against Management': forAgainst
                    }
                    detailsList.append(details)
                else:

                    stringTemp = i.strip()
                    if detailsList: # Avoids error if detailsList is empty
                        detailsList[-1]['Description'] = detailsList[-1]['Description'] + ' ' + stringTemp
        else:
            ''
        # data is now stored as List of Dictionaries, which will be helpful for Pandas library to interpret 
        df = pd.DataFrame(detailsList)      # Details List is converted to Data Frame
        output_file = input("What should the output file be called (add '.csv' at the end):")
        df.to_csv()                         # Converts Data Frame into csv file 

def indexChecker(in1,in2,sortedProps):
    """
    This function is made to do natural sorting of the elements, 
    as many of the Nasdaq files lack formatting when it comes to indexing the proposals
    """
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
        
inp= str(input("ENTER THE FILE PATH: "))
fileType(inp)

