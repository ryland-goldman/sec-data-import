# MIT License
#
# Copyright (c) 2023 Ryland Goldman
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

### Import libraries
import json                     # JSON library     - used to decode JSON from data.sec.gov
import requests                 # Requests library - used to make GET requests to sec.gov
from pandas import DataFrame    # Pandas library   - used to export data to Excel
from datetime import datetime   # Datetime library - used to check if data is recent
import sys                      # Sys library      - used to get arguments if running from CLI
import os                       # OS library       - used to validate path of Excel file

### Load variables from config file, or prompt for new ones
# path = Path to save Excel file
# ua   = User agent for SEC crawl (name, email)
try: # Try to load settings from configuration file
    conf_file = open("dataimport-settings.conf","r")
    conf_data = conf_file.read()
    ua, path = conf_data.split("\n")
except: # Prompt for new info if file doesn't exist
    print("""This information will be saved in a config file.\nUser Agent:
        The SEC requires a user-agent string including your name and email.
        For more information, please see https://www.sec.gov/os/webmaster-faq#code-support.""")
    ua = input("\tName: ")
    ua = ua + input("\tEmail: ")
    path = os.path.normpath(input("Path:\n\tEnter the path to save the Excel file (~/Downloads/): "))
    if path=="": path="~/Downloads/"
    try:
        with open("dataimport-settings.conf","w") as cf: # Load file
            cf.write(ua+"\n"+path)                       # Save to file
    except Exception as e:
        print("Could not save configuration file:",e)    # Error
    print("================")

### If running from CLI, use arguments
try: ticker = sys.argv[1]                         # Get first argument
except Exception as e: ticker = ""                # Do nothing
if ticker == "": ticker = input("Enter ticker: ") # Prompt for ticker if none provided

### Convert ticker to CIK from SEC database
ticker_to_cik = requests.get('https://www.sec.gov/include/ticker.txt',headers={"User-Agent": ua}) # Fetch data from API
for company in iter(ticker_to_cik.text.splitlines()): # Iterate over each ticker, checking for a match
    if ticker.lower() in company:
        _, CIK = company.split("\t")      # If a match is found, grab the second column of the TSV file
        CIK = "CIK" + CIK.zfill(10)       # Add leading zeros (10 digits)
try:
    print("Found CIK for ",ticker.upper(),": ",CIK,sep='') # Ticker exists
except Exception as e:
    print("Invalid ticker.")              # Ticker does not exist, exit program
    exit(-1)

### Load financial data
data_file = requests.get('https://data.sec.gov/api/xbrl/companyfacts/'+CIK+'.json',headers={"User-Agent": ua}) # Fetch data from API
data_parsed = json.loads(data_file.text)   # Parse JSON file
data = dict()                              # Create empty dict
for cat in data_parsed["facts"]:           # Loop through all categories (usually dei and us-gaap)
    data.update(data_parsed["facts"][cat]) # Merge dicts
all_items = []                             # Empty array for storing items

### Set initial items: ticker, CIK, name
all_items = [{"key":"Ticker",     "name":"Ticker",            "value":ticker.upper(),            "unit":"--", "date":"--", "description":"Ticker symbol"},
             {"key":"EntityName", "name":"Entity Name",       "value":data_parsed["entityName"], "unit":"--", "date":"--", "description":"Name of company"},
             {"key":"CIK",        "name":"Central Index Key", "value":CIK,                       "unit":"--", "date":"--", "description":"Unique number assigned to an individual, company, filing agent or foreign government by the United States Securities and Exchange Commission"}]

### Sort through financial data
n = 0 # Counter for the number of successful items
for item in data:   # Loop through everything
    try:
        units = next(iter(data[item]["units"])) # Find units (usually USD, USD/shares, shares, etc)
        new_object = { # Create an object for this item
            "key"   :       item,                                  # Item key
            "name"  :       data[item]["label"],                   # Item name
            "value" :       data[item]["units"][units][-1]["val"], # Numerical value of item
            "unit"  :       units,                                 # Units
            "date"  :       data[item]["units"][units][-1]["end"], # Date of last update
            "description" : data[item]["description"]              # Item description
        }

        
        if int(new_object["date"][0:4]) < datetime.now().year - 2: # If data is more than two years old, it is most likely outdated
            print("LOAD FAILED (depriciated)\t",item)
            continue
        
        all_items.append(new_object)      # Add item to array
        print("LOAD SUCCESS\t\t\t", item) # Print success message
        n = n + 1                         # Increase success counter
        
    except Exception as e: # Could not parse item
        print("LOAD FAILED (invalid format)\t", item)

### Export data to Excel
print("Succesfully found ",n," items for ",ticker.upper()," ",data_parsed["entityName"]," (",CIK,")",sep='')
data_frame = DataFrame(all_items) # Load into Pandas data frame
data_frame.to_excel(path+ticker.lower()+"_financial_data.xlsx") # Send to Excel
