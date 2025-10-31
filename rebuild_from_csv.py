#!/usr/bin/env python3
"""
Rebuild Stories Data from CSV Classification
===========================================

This script rebuilds the stories-data.json file using ONLY entries 
that are classified as "Story" in the CSV file, fixing the count mismatch.

Usage:
    python rebuild_from_csv.py
"""

import pandas as pd
import json
import os
from datetime import datetime

def rebuild_stories_data():
    """Rebuild stories-data.json using only CSV-classified stories."""
    
    print("🔄 Rebuilding stories data from CSV classification...")
    
    # Find CSV file
    csv_files = [f for f in os.listdir('.') if 'Mavaya' in f and f.endswith('.csv')]
    if not csv_files:
        print("❌ No Mavaya CSV file found!")
        return
    
    csv_file = csv_files[0]
    print(f"📖 Reading: {csv_file}")
    
    # Read CSV
    df = pd.read_csv(csv_file)
    print(f"📊 Total entries in CSV: {len(df)}")
    
    # Show classification breakdown
    print("\n📋 Classification breakdown:")
    classification_counts = df['classification'].value_counts()
    for classification, count in classification_counts.items():
        print(f"   {classification}: {count}")
    
    # Filter only stories
    stories_df = df[df['classification'].str.lower() == 'story'].copy()
    print(f"\n✅ Entries classified as 'Story': {len(stories_df)}")
    
    # Group by year
    new_stories_data = {}
    
    for _, row in stories_df.iterrows():
        year = str(row['year'])
        title = row['title']
        
        # Remove redundant suffix if present
        title = title.replace(' - రవి కావూరు కథలు', '').replace(' - రవి గరి కథలు', '')
        filename = row['filepath']
        
        if year not in new_stories_data:
            new_stories_data[year] = []
        
        # Create story entry
        story_entry = {
            "title": title,
            "file": filename,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "category": "story",
            "classification": "Story",  # From CSV
            "confidence": row.get('confidence', 'N/A'),
            "text_length": row.get('text_length', 0)
        }
        
        new_stories_data[year].append(story_entry)
    
    # Sort years and stories within each year
    sorted_data = {}
    for year in sorted(new_stories_data.keys()):
        sorted_data[year] = sorted(new_stories_data[year], key=lambda x: x['title'])
    
    # Save new stories data
    with open('stories-data.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    
    # Show summary
    total_stories = sum(len(stories) for stories in sorted_data.values())
    print(f"\n🎉 Successfully rebuilt stories-data.json!")
    print(f"📝 Total stories: {total_stories}")
    print(f"\n📅 Stories by year:")
    for year, stories in sorted_data.items():
        print(f"   {year}: {len(stories)} stories")
    
    # Show what was excluded
    excluded_count = len(df) - len(stories_df)
    print(f"\n🚫 Excluded {excluded_count} entries (Documents, etc.)")
    
    print(f"\n✅ Your website will now show exactly {total_stories} stories!")
    print("📌 Next steps:")
    print("   1. git add stories-data.json")
    print("   2. git commit -m 'Fix story count - use only CSV-classified stories'")
    print("   3. git push")

if __name__ == "__main__":
    rebuild_stories_data()
