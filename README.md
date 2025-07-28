## Overview
This project provides a Python script to parse, extract, and structure corporate voting and proposal data from semi-structured text files. The script then intelligently links and merges this data, exporting the final, clean dataset as a CSV file.

This tool is designed to handle inconsistencies in text formatting, including multi-line proposal descriptions, and correctly associates proposals with their respective companies.

## Features
__Company Data Extraction:__ Parses company name, agenda number, security, meeting type, meeting date, ticker, and ISIN from a text file.

__Proposal Data Extraction:__ Extracts detailed proposal information, including proposal number, description, type (Management or Shareholder), and vote recommendation.

__Handles Complex Formatting:__ Correctly parses multi-line proposal descriptions and various proposal numbering schemes (e.g., 1.A, 2.1, 3).

__Intelligent Merging:__ Assigns a unique ID to each company and its corresponding set of proposals, allowing for an accurate merge of the two data sources.

__Natural Sorting:__ Uses natsort to correctly order proposal numbers that may be alphanumeric.

__CSV Export:__ Outputs the final, structured data into a single, easy-to-use CSV file.

## Requirements
To run this script, you will need Python 3 and the following libraries:

`pandas`

`natsort`

You can install them using pip:

`pip install pandas natsort`

## How to Use
1. Place your input files in the same directory as the script, or provide the correct file paths. The script is configured to look for:

`appleton_npx 1 1.txt`

2. Run the script from your terminal:

`python your_script_name.py`

Find the output in a file named `appleton_npx1.csv` in the same directory.

Input File Formats
Company Data File (appleton_npx 1 1.txt)
The script expects company data to be separated by long lines of hyphens (-). Each company's information is expected to be laid out with clear labels like "Agenda Number:", "Security:", etc.
```
Example Snippet:

--------------------------------------------------
APPLE INC.                                          Agenda Number: 000000001
--------------------------------------------------
Security: 123456789      Meeting Type: Annual      Meeting Date: 01-JAN-2023
Ticker: AAPL           ISIN: US0378331005
--------------------------------------------------
```
Proposal:
Example Snippet:
```
Prop.# Proposal                                                  Type          Vote         For/Against
1.A    TO ELECT DIRECTOR:
       John Doe                                                  Mgmt          For          For
1.B    TO ELECT DIRECTOR:
       Jane Smith                                                Mgmt          For          For
2.     TO RATIFY THE APPOINTMENT OF THE INDEPENDENT
       AUDITORS                                                  Mgmt          For          For
3.1    SHAREHOLDER PROPOSAL REGARDING LOBBYING                   Shr           Against      Against
```
Output File (`appleton_npx1.csv`)
The script generates a CSV file with the following columns, merging the data from the input files:

- `Company Name`

- `Agenda Number`  

- `Security`

- `Meeting Type`

- `Meeting Date`

- `Ticker`

- `ISIN`

- `Prop (Proposal Number)`

- `Proposal (Proposal Description)`
  
- `Proposal Type`

- `Proposal Vote`

- `Vote Cast`

- `For/Against Management`
