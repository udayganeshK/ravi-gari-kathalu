#!/usr/bin/env python3
"""
Script to update the classification of the reviewed files and create the final stories data.
"""
import pandas as pd
import json
import os
from datetime import datetime

def update_classifications():
    # Read the CSV file
    csv_file = None
    for file in os.listdir('.'):
        if file.startswith('detailed_story_analysis_') and file.endswith('.csv'):
            csv_file = file
            break
    
    if not csv_file:
        print("Error: Could not find the analysis CSV file")
        return
    
    print(f"Reading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    # Update the three files that needed review
    files_to_update = [
        'untitled-document-25.html',
        'untitled-document-33.html', 
        'imp.html'
    ]
    
    for filename in files_to_update:
        mask = df['filename'] == filename
        if mask.any():
            df.loc[mask, 'classification'] = 'Document'
            df.loc[mask, 'confidence'] = 90
            df.loc[mask, 'reasons'] = 'Manual review: placeholder/incomplete content'
            print(f"Updated {filename} to Document")
    
    # Save updated CSV
    updated_csv = f"final_story_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(updated_csv, index=False)
    print(f"Saved updated analysis to {updated_csv}")
    
    # Create stories data JSON
    stories_df = df[df['classification'] == 'Story'].copy()
    print(f"\nFound {len(stories_df)} stories out of {len(df)} total files")
    
    # Create stories data structure
    stories_data = []
    
    for _, story in stories_df.iterrows():
        # Extract category from content patterns
        category = "general"  # default
        
        # Determine category based on filename/title patterns
        title = story['title'].lower()
        filename = story['filename'].lower()
        
        if any(x in title or x in filename for x in ['కథ', 'कथ', 'story', 'కధ']):
            if any(x in title or x in filename for x in ['కథ కదంబం', 'కథసగర', 'కథ సగర']):
                category = "collection"
            else:
                category = "story"
        elif any(x in title or x in filename for x in ['యాత్र', 'trip', 'పర్వతం', 'గుడి']):
            category = "travel"
        elif any(x in title or x in filename for x in ['కవిత', 'పద్య', 'స్తోత్రం', 'మంత్రం']):
            category = "poetry"
        elif any(x in title or x in filename for x in ['భక్తి', 'దేవుడు', 'గాయత్రి', 'శ్రీ', 'స్వామి']):
            category = "spiritual"
        elif any(x in title or x in filename for x in ['అనుభవం', 'జీవితం', 'వ్యక్తిగత']):
            category = "personal"
        elif story['text_length'] < 500:
            category = "short"
        
        story_data = {
            "id": story['filename'].replace('.html', ''),
            "title": story['title'].replace(' - రవి గరి కథలు', ''),
            "filename": story['filename'],
            "year": int(story['year']),
            "category": category,
            "textLength": int(story['text_length']),
            "confidence": int(story['confidence']),
            "path": story['filepath']
        }
        
        stories_data.append(story_data)
    
    # Sort by year (newest first) and then by title
    stories_data.sort(key=lambda x: (-x['year'], x['title']))
    
    # Save stories data JSON
    with open('stories-data.json', 'w', encoding='utf-8') as f:
        json.dump(stories_data, f, ensure_ascii=False, indent=2)
    
    print(f"Created stories-data.json with {len(stories_data)} stories")
    
    # Print summary by category
    categories = {}
    for story in stories_data:
        cat = story['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nStories by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    print(f"\nStories by year:")
    years = {}
    for story in stories_data:
        year = story['year']
        years[year] = years.get(year, 0) + 1
    
    for year in sorted(years.keys(), reverse=True):
        print(f"  {year}: {years[year]}")
    
    return updated_csv, stories_data

if __name__ == "__main__":
    update_classifications()
