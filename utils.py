

import requests
from bs4 import BeautifulSoup

def clean_text(text):
    return " ".join(text.split())

def fetch_text_from_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    return soup.get_text(separator="\n")
