import json
import csv
from pathlib import Path
import os
from bs4 import BeautifulSoup

json_file = Path('stories-data.json')
csv_file = Path('stories-data-export.csv')

fields = [
    'Year', 'Title', 'File', 'Date', 'Category', 'Classification', 'Confidence', 'Text length',
    'Created date', 'Modified date', 'Created display', 'Modified display', 'Story Text'
]

def extract_story_text(html_path):
    if not os.path.exists(html_path):
        return ''
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            body = soup.find(class_='story-body')
            if body:
                return body.get_text(separator='\n', strip=True)
            # fallback: get all text
            return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        return ''

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

rows = []
for year, stories in data.items():
    for story in stories:
        story_file = story.get('file', '')
        story_text = extract_story_text(story_file)
        rows.append({
            'Year': year,
            'Title': story.get('title', ''),
            'File': story_file,
            'Date': story.get('date', ''),
            'Category': story.get('category', ''),
            'Classification': story.get('classification', ''),
            'Confidence': story.get('confidence', ''),
            'Text length': story.get('text_length', ''),
            'Created date': story.get('created_date', ''),
            'Modified date': story.get('modified_date', ''),
            'Created display': story.get('created_display', ''),
            'Modified display': story.get('modified_display', ''),
            'Story Text': story_text
        })

with open(csv_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"Exported {len(rows)} stories to {csv_file} (with story text)")