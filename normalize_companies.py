import pandas as pd
import numpy as np
from thefuzz import fuzz
from urllib.parse import urlparse
import re
from collections import defaultdict

def clean_website(url):
    if not isinstance(url, str) or not url:
        return ""
    
    # Add https:// if no protocol specified
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Parse URL and get domain
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www.
        domain = re.sub(r'^www\.', '', domain)
        
        return domain
    except:
        return ""

def normalize_company_name(name):
    if not isinstance(name, str):
        return ""
    
    # Initial cleanup
    name = name.strip()
    
    # Define words that should remain uppercase
    uppercase_words = {
        'IBM', 'LLC', 'LLP', 'IT', 'UK', 'US', 'USA', 'NHS', 'PLC', 'LTD', 'GB', 'AI',
        'CEO', 'CTO', 'CFO', 'COO', 'HR', 'BBC', 'ABC', 'NBC', 'CBS', 'FBI', 'CIA',
        'NASA', 'NATO', 'HSBC', 'BMW', 'KPMG', 'PWC', 'HMRC', 'VAT', 'GST', 'R&D',
        'B2B', 'B2C', 'P2P', 'SaaS', 'PaaS', 'IaaS', 'IoT', 'AI', 'ML', 'API',
        'AWS', 'GCP', 'SQL', 'NoSQL', 'PHP', 'HTML', 'CSS', 'XML', 'JSON', 'YAML',
        'KSB', 'SJR', 'KF', 'KSA', 'CO'
    }
    
    # Define words that should remain lowercase
    lowercase_words = {
        'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 'of', 'on',
        'or', 'the', 'to', 'up', 'via', 'with'
    }
    
    # Standardize common abbreviations
    replacements = {
        ' And ': ' & ',
        ' LIMITED': ' Ltd.',
        ' CORPORATION': ' Corp.',
        ' INCORPORATED': ' Inc.',
        ' COMPANY': ' Co.',
        ' PRIVATE LIMITED': ' Pvt. Ltd.',
        ' PUBLIC LIMITED COMPANY': ' PLC',
        ' LIMITED LIABILITY PARTNERSHIP': ' LLP',
        ' LIMITED LIABILITY COMPANY': ' LLC',
        ' GMBH': ' GmbH',
        ' AG ': ' AG',
        ' SA ': ' SA',
        ' NV ': ' NV',
        'LTD.': 'Ltd.',
        'CORP.': 'Corp.',
        'INC.': 'Inc.',
        'CO.': 'Co.',
        'PVT. LTD.': 'Pvt. Ltd.',
    }
    
    # Convert to uppercase for processing
    name = name.upper()
    
    # Apply replacements
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    # Split into words
    words = name.split()
    
    # Process each word
    processed_words = []
    for i, word in enumerate(words):
        # Remove any trailing periods for checking
        word_no_period = word.rstrip('.')
        
        # Check if word should remain uppercase
        if word_no_period in uppercase_words:
            processed_words.append(word)  # Keep original with any periods
        # Check if word should be lowercase (not at start or after period)
        elif word_no_period.lower() in lowercase_words and i > 0 and not words[i-1].endswith('.'):
            processed_words.append(word.lower())
        # Handle numbers at start of word
        elif word[0].isdigit():
            # Keep numbers and capitalize rest
            match = re.match(r'(\d+)(.+)', word)
            if match:
                num, rest = match.groups()
                processed_words.append(f"{num}{rest.capitalize()}")
            else:
                processed_words.append(word)
        # Handle hyphenated words
        elif '-' in word:
            parts = word.split('-')
            processed_parts = [p.capitalize() for p in parts]
            processed_words.append('-'.join(processed_parts))
        # Handle standard words
        else:
            processed_words.append(word.capitalize())
    
    # Join words back together
    normalized = ' '.join(processed_words)
    
    # Fix specific patterns
    normalized = re.sub(r'(?<=\w)\.(?=\w)', '. ', normalized)  # Add space after periods between words
    normalized = re.sub(r'\s+', ' ', normalized)  # Remove multiple spaces
    normalized = normalized.strip()
    
    return normalized

def get_best_normalized_name(group):
    # If only one name, normalize and return it
    if len(group) == 1:
        return normalize_company_name(group.iloc[0]['normalized'])
    
    # Get all normalized names
    names = [normalize_company_name(name) for name in group['normalized'].unique() if isinstance(name, str) and name]
    
    if not names:
        return normalize_company_name(group.iloc[0]['original'])  # Fallback to original name if no normalized names
    
    # Score each name against others
    scores = defaultdict(int)
    
    for name1 in names:
        for name2 in names:
            if name1 != name2:
                score = fuzz.ratio(name1, name2)
                scores[name1] += score
    
    if not scores:
        return names[0]  # Return first name if no scores
        
    # Return name with highest total similarity score
    return max(scores.items(), key=lambda x: x[1])[0]

def get_best_website(group):
    # Get non-empty websites
    websites = [clean_website(url) for url in group['website'] if isinstance(url, str) and url]
    
    if not websites:
        return ""
    
    # Count frequency of each domain
    domain_counts = defaultdict(int)
    for website in websites:
        domain_counts[website] += 1
    
    # Return most frequent domain
    return max(domain_counts.items(), key=lambda x: x[1])[0]

def main():
    # Read CSV file
    df = pd.read_csv('data/out_boots.csv')
    
    # First, group by website URLs
    website_groups = defaultdict(list)
    for idx, row in df.iterrows():
        website = clean_website(row['website'])
        if website:  # Only group if website exists
            website_groups[website].append(idx)
    
    # Process each website group to get best normalized name
    website_results = {}
    for website, indices in website_groups.items():
        if len(indices) > 1:  # Only process groups with multiple entries
            group = df.iloc[indices]
            best_name = get_best_normalized_name(group)
            website_results[website] = best_name
    
    # Now group by similar company names using fuzzy matching
    groups = []
    processed = set()
    
    for idx, row in df.iterrows():
        if idx in processed:
            continue
            
        # Find similar company names
        group = [idx]
        name = row['original'].lower()
        
        for idx2, row2 in df.iterrows():
            if idx2 not in processed and idx != idx2:
                if fuzz.ratio(name, row2['original'].lower()) >= 85:
                    group.append(idx2)
        
        groups.append(df.iloc[group])
        processed.update(group)
    
    # Process each group to get best normalized name and website
    results = []
    
    for group in groups:
        best_name = get_best_normalized_name(group)
        best_website = get_best_website(group)
        
        # If this website has a preferred normalized name from website grouping,
        # use that instead
        if best_website in website_results:
            best_name = website_results[best_website]
        
        # Add result for each original name in group
        for _, row in group.iterrows():
            results.append({
                'original': row['original'],
                'normalized': best_name,
                'website': best_website
            })
    
    # Create output dataframe
    output_df = pd.DataFrame(results)
    
    # Sort by original name
    output_df = output_df.sort_values('original')
    
    # Save to CSV
    output_df.to_csv('data/normalized_companies.csv', index=False)

if __name__ == "__main__":
    main() 