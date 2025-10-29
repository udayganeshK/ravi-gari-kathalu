import pandas as pd
import json
import os
from pathlib import Path

def process_mavaya_stories():
    # Read the CSV file
    csv_file = "Mavaya stories - detailed_story_analysis_20251012_235444.csv.csv"
    df = pd.read_csv(csv_file)
    
    # Filter only stories marked as "Story"
    story_df = df[df['classification'] == 'Story'].copy()
    
    # Read existing stories-data.json
    with open('stories-data.json', 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    
    # Get existing story filenames to avoid duplicates
    existing_files = set()
    if isinstance(existing_data, list):
        # If it's a list, convert to dict by year and collect filenames
        existing_files.update(story.get('filename', '') for story in existing_data)
        # Convert list to dict by year
        existing_data_by_year = {}
        for story in existing_data:
            year = str(story.get('year', 2024))
            if year not in existing_data_by_year:
                existing_data_by_year[year] = []
            existing_data_by_year[year].append(story)
        existing_data = existing_data_by_year
    else:
        # If it's already a dict, collect filenames
        for year_data in existing_data.values():
            existing_files.update(story.get('file', story.get('filename', '')) for story in year_data)
    
    # Process new stories
    new_stories_added = 0
    stories_by_year = {}
    
    for _, row in story_df.iterrows():
        filename = row['filename']
        year = str(row['year'])
        title = row['title']
        filepath = row['filepath']
        
        # Skip if already exists
        if filename in existing_files:
            continue
            
        # Check if the HTML file actually exists
        if not os.path.exists(filepath):
            print(f"Warning: File not found: {filepath}")
            continue
            
        # Clean up title - remove "- రవి గరి కథలు" suffix if present
        clean_title = title.replace(" - రవి గరి కథలు", "").strip()
        
        # Create story entry
        story_entry = {
            "title": clean_title,
            "file": filename,
            "confidence": row['confidence'],
            "reasons": row['reasons'],
            "text_length": row['text_length']
        }
        
        # Group by year
        if year not in stories_by_year:
            stories_by_year[year] = []
        stories_by_year[year].append(story_entry)
        new_stories_added += 1
    
    # Merge with existing data
    updated_data = existing_data.copy()
    
    for year, new_stories in stories_by_year.items():
        if year in updated_data:
            # Add new stories to existing year, avoiding duplicates
            existing_files_in_year = set(story.get('file', story.get('filename', '')) for story in updated_data[year])
            for story in new_stories:
                if story['file'] not in existing_files_in_year:
                    # Convert to match existing format
                    story_entry_formatted = {
                        "title": story['title'],
                        "excerpt": f"{story['title'][:100]}...",
                        "wordCount": story['text_length'],
                        "year": int(year),
                        "date": f"{year}-01-01",
                        "filename": f"stories/{year}/{story['file']}",
                        "categories": ["story"],
                        "tags": ["story"]
                    }
                    updated_data[year].append(story_entry_formatted)
        else:
            # Create new year entry with formatted stories
            formatted_stories = []
            for story in new_stories:
                story_entry_formatted = {
                    "title": story['title'],
                    "excerpt": f"{story['title'][:100]}...",
                    "wordCount": story['text_length'],
                    "year": int(year),
                    "date": f"{year}-01-01",
                    "filename": f"stories/{year}/{story['file']}",
                    "categories": ["story"],
                    "tags": ["story"]
                }
                formatted_stories.append(story_entry_formatted)
            updated_data[year] = formatted_stories
    
    # Sort stories within each year by title
    for year in updated_data:
        updated_data[year].sort(key=lambda x: x['title'])
    
    # Convert back to list format to match original structure
    final_data = []
    for year in sorted(updated_data.keys()):
        final_data.extend(updated_data[year])
    
    # Write updated data back to file
    with open('stories-data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print(f"✅ Processing complete!")
    print(f"📊 Total stories in CSV: {len(df)}")
    print(f"📚 Stories classified as 'Story': {len(story_df)}")
    print(f"➕ New stories added: {new_stories_added}")
    print(f"📋 Stories by year added:")
    
    for year, stories in stories_by_year.items():
        print(f"   {year}: {len(stories)} stories")
    
    return updated_data, new_stories_added

if __name__ == "__main__":
    process_mavaya_stories()
