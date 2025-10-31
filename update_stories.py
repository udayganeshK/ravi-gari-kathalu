#!/usr/bin/env python3
"""
Telugu Stories Data Updater
===========================

This script reads the "Mavaya stories" CSV file and updates the stories-data.json 
with new stories that are marked as "Story" in the classification column.

Usage:
    python update_stories.py

Requirements:
    pip install pandas

Author: Your Name
Date: October 2025
"""

import pandas as pd
import json
import os
from datetime import datetime

def find_csv_file():
    """Find the Mavaya stories CSV file in the current directory."""
    csv_files = [f for f in os.listdir('.') if f.startswith('Mavaya stories') and f.endswith('.csv')]
    if not csv_files:
        print("❌ No 'Mavaya stories' CSV file found!")
        return None
    
    if len(csv_files) > 1:
        print(f"📁 Found multiple CSV files:")
        for i, file in enumerate(csv_files, 1):
            print(f"   {i}. {file}")
        choice = input("Enter the number of the file to use: ")
        try:
            return csv_files[int(choice) - 1]
        except (ValueError, IndexError):
            print("❌ Invalid choice!")
            return None
    
    return csv_files[0]

def load_stories_data():
    """Load existing stories data or create new structure."""
    if os.path.exists('stories-data.json'):
        with open('stories-data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {"2021": [], "2022": [], "2023": [], "2024": [], "2025": []}

def update_stories_from_csv():
    """Main function to update stories from CSV."""
    print("🔍 Looking for Mavaya stories CSV file...")
    
    csv_file = find_csv_file()
    if not csv_file:
        return
    
    print(f"📖 Reading CSV file: {csv_file}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        print(f"📊 Total entries in CSV: {len(df)}")
        
        # Filter only stories (case-insensitive)
        story_entries = df[df['Classification'].str.lower() == 'story']
        print(f"📚 Stories found: {len(story_entries)}")
        
        if len(story_entries) == 0:
            print("⚠️  No entries marked as 'Story' found!")
            return
        
        # Load existing stories data
        stories_data = load_stories_data()
        
        # Get existing story titles to avoid duplicates
        existing_titles = set()
        for year_stories in stories_data.values():
            for story in year_stories:
                existing_titles.add(story['title'])
        
        new_stories_count = 0
        
        # Process each story entry
        for _, row in story_entries.iterrows():
            title = str(row['Title']).strip()
            
            # Remove redundant suffix if present
            title = title.replace(' - రవి కావూరు కథలు', '').replace(' - రవి గరి కథలు', '')
            
            # Skip if title already exists
            if title in existing_titles:
                continue
            
            # Determine year (default to 2024 if not specified)
            year = "2024"  # You can modify this logic based on your needs
            if 'Year' in row and pd.notna(row['Year']):
                year = str(int(row['Year']))
            
            # Ensure year exists in data structure
            if year not in stories_data:
                stories_data[year] = []
            
            # Create story entry
            story_entry = {
                "title": title,
                "file": f"mavaya-{title.lower().replace(' ', '-').replace(',', '').replace('.', '')}.html",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "category": "mavaya-stories"
            }
            
            # Add description if available
            if 'Description' in row and pd.notna(row['Description']):
                story_entry["description"] = str(row['Description'])[:200] + "..."
            
            stories_data[year].append(story_entry)
            existing_titles.add(title)
            new_stories_count += 1
        
        # Save updated stories data
        with open('stories-data.json', 'w', encoding='utf-8') as f:
            json.dump(stories_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Successfully added {new_stories_count} new stories!")
        print(f"📝 Total stories now: {sum(len(stories) for stories in stories_data.values())}")
        
        # Show summary by year
        print("\n📅 Stories by year:")
        for year, stories in sorted(stories_data.items()):
            print(f"   {year}: {len(stories)} stories")
        
        if new_stories_count > 0:
            print(f"\n🎉 New stories added from CSV: {new_stories_count}")
            print("📌 Next steps:")
            print("   1. Run: git add stories-data.json")
            print("   2. Run: git commit -m 'Update stories from CSV'")
            print("   3. Run: git push")
        else:
            print("\n💡 No new stories to add (all stories already exist).")
            
    except Exception as e:
        print(f"❌ Error processing CSV file: {e}")

if __name__ == "__main__":
    print("🚀 Telugu Stories Data Updater")
    print("=" * 40)
    update_stories_from_csv()
