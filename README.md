# Daily Bulletin Scrapers

This repository contains Python scripts that download, parse, and append “company news” items from daily bulletins published by various Turkish brokerage firms. Each script retrieves the PDF bulletin, extracts relevant text using `pdfminer`, performs matching of ticker symbols against a reference CSV of BIST-traded stocks, and appends the parsed news items to a master CSV file.

## Contents

- `oyak_yatirim.py`: Downloads and parses daily bulletins from Oyak Yatırım Menkul Değerler A.Ş..
- `piramit_yatirim.py`: Downloads and parses daily bulletins from Piramit Menkul Kıymetler A.Ş., using Selenium to navigate to their site.
- `tacirler_yatirim.py`: Downloads and parses daily bulletins from Tacirler Yatırım Menkul Kıymetler A.Ş., also using Selenium.
- `vakif_yatirim.py`: Downloads and parses daily bulletins from Vakıf Yatırım Menkul Değerler A.Ş., using Selenium.
- `ziraat_yatirim.py`: Downloads and parses daily bulletins from Ziraat Yatırım Menkul Değerler A.Ş..

Each script extracts the relevant “company news” section from the PDF, identifies the ticker symbols, and appends results into the shared CSV file.

## How It Works

1. **Script Execution:** Each script defines a function (e.g., `oyak_yatirim()`) which you can import or run directly. When run:
   - It attempts to download the day’s PDF from the brokerage’s website.
   - Uses `pdfminer` to convert the PDF to text.
   - Extracts “company news” subsections via regular expressions.
   - Splits out valid ticker symbols and uses fuzzy matching (via `fuzzywuzzy`) to ensure a valid BIST stock code.
   - Appends the results, including date, time, broker name, and the bulletin’s URL, to master CSV.
2. **Data Sources:** A CSV file containing valid BIST tickers. Each script uses fuzzy matching on this list to ensure correct identification of ticker symbols
3. **Error Handling:** If a PDF pattern or URL changes on a brokerage site, the script might fail to download (e.g., a `PDFSyntaxError` or a `NoSuchElementException` in Selenium-based scripts).
4. If no “company news” is found, each script logs that no news is available for the day.

## Requirements 

- Python 3.7+
- pip packages
  - requests
  - pdfminer
  - fuzzywuzzy
  - pandas
  - numpy
  - selenium
- Chromedriver

## Setup Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
```















  
