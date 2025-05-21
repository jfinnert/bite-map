#!/usr/bin/env python
"""
Simple script to test link ingestion locally.
Usage: python ingest_test.py https://www.youtube.com/watch?v=example
"""
import sys
import os
import requests
import json
from urllib.parse import urlparse

def validate_url(url):
    """
    Basic URL validation
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def ingest_link(url):
    """
    Send a URL to the ingest API endpoint
    """
    if not validate_url(url):
        print(f"Error: '{url}' does not appear to be a valid URL")
        sys.exit(1)
        
    api_url = "http://localhost:8000/api/ingest/link"
    payload = {"url": url}
    
    try:
        print(f"Sending {url} to {api_url}...")
        response = requests.post(api_url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Response: {json.dumps(result, indent=2)}")
            return 0
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return 1
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    # Check for URL argument
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} URL")
        sys.exit(1)
    
    # Get the URL from command line
    url = sys.argv[1]
    exit_code = ingest_link(url)
    sys.exit(exit_code)
