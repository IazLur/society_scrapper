# society_scrapper

This project demonstrates a small proof of concept for retrieving company information from the public `recherche-entreprises` API. Given a domain name the script tries to guess the organisation name from the website title, queries the API, computes a simple score and optionally exports the result to CSV.

## Requirements
- Python 3.10+
- `requests`
- `beautifulsoup4`

You can install the Python dependencies with:

```bash
pip install requests beautifulsoup4
```

## Usage

```bash
python search.py example.com --ape 62.01Z --export results.csv
```

The script prints the found companies with their score and creates a CSV file with basic details.
