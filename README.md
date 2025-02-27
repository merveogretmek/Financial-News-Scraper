# Daily Bulletin Scrapers

This repository contains Python scripts that download, parse, and append “company news” items from daily bulletins published by various Turkish brokerage firms. Each script retrieves the PDF bulletin, extracts relevant text using pdfminer, performs matching of ticker symbols against a reference CSV of BIST-traded stocks, and appends the parsed news items to a master CSV file.
