# SEC Data Import
For questions on fetching data from the SEC API, visit [https://www.sec.gov/os/webmaster-faq](https://www.sec.gov/os/webmaster-faq).

This Python script imports data from the United States Securities and Exchange Commission's (SEC) Electronic Data Gathering, Analysis, and Retrieval (EDGAR) system into a Microsoft Excel spreadsheet.

## Dependencies
- [json](https://docs.python.org/3/library/json.html) - builtin Python library
- [datetime](https://docs.python.org/3/library/datetime.html) - builtin Python library
- [sys](https://docs.python.org/3/library/sys.html) - builtin Python library
- [os](https://docs.python.org/3/library/os.html) - builtin Python library
- [requests](https://pypi.org/project/requests/) - Open-source library for web requests ([GitHub](https://github.com/psf/requests))
- [pandas](https://pypi.org/project/pandas/) - Open-source library for Python data frames ([GitHub](https://github.com/pandas-dev/pandas))

## Usage
This script is meant to be run from the command line, not IDLE. The only argument the script accepts is the ticker symbol of the entity. On the first run, you must enter your full name and email address in accordance with the SEC's [policies](https://www.sec.gov/os/webmaster-faq#code-support), as well as the path to store the Excel file. This information will be saved in a `dataimport-settings.conf` configuration file.

The script converts the ticker symbol to the Central Index Key (CIK), which is used to fetch SEC records. Available data from the past two years will be added to the Excel spreadsheet and saved in the directory given during setup.
