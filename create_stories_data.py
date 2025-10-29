import csv
import json
import os
from bs4 import BeautifulSoup
import re
from datetime import datetime

def extract_story_data(file_path):
    """Extract story data from HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Get title (from title tag or first heading)
        title = ""
        if soup.title:
            title = soup.title.get_text().strip()
        elif soup.h1:
            title = soup.h1.get_text().strip()
        elif soup.h2:
            title = soup.h2.get_text().strip()
        
        # If no title found, use filename
        if not title:
            title = os.path.basename(file_path).replace('.html', '').replace('-', ' ')
        
        # Get text content for excerpt and word count
        text_content = soup.get_text()
        lines = [line.strip() for line in text_content.splitlines() if line.strip()]
        text_content = ' '.join(lines)
        
        # Create excerpt (first 200 characters)
        excerpt = text_content[:200] + "..." if len(text_content) > 200 else text_content
        
        # Count words
        word_count = len(text_content.split())
        
        # Extract year from file path
        path_parts = file_path.split(os.sep)
        year = None
        for part in path_parts:
            if part.isdigit() and len(part) == 4:
                year = int(part)
                break
        
        # Get file modification date as fallback
        file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        return {
            "title": title,
            "excerpt": excerpt,
            "wordCount": word_count,
            "year": year or file_date.year,
            "date": file_date.strftime("%Y-%m-%d"),
            "filename": file_path.replace(os.getcwd() + os.sep, "").replace(os.sep, "/"),
            "categories": [],  # Will be filled based on content analysis
            "tags": []  # Will be filled based on content analysis
        }
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def categorize_story(story_data):
    """Categorize story based on content"""
    title = story_data['title'].lower()
    excerpt = story_data['excerpt'].lower()
    content = (title + " " + excerpt).lower()
    
    categories = []
    tags = []
    
    # Family/Personal stories
    if any(word in content for word in ['అమ్మ', 'అప్ప', 'తల్లి', 'తండ్రి', 'కుటుంబ', 'family', 'mother', 'father']):
        categories.append('family')
        tags.append('family')
    
    # Spiritual/Religious stories
    if any(word in content for word in ['దేవుడు', 'భగవంతుడు', 'దేవ', 'పూజ', 'ప్రార్థన', 'temple', 'spiritual', 'prayer']):
        categories.append('spiritual')
        tags.append('spiritual')
    
    # Travel stories
    if any(word in content for word in ['యాత్र', 'ప్రయాణ', 'trip', 'travel', 'journey', 'వెళ్ళాం', 'వెళ్లాను']):
        categories.append('travel')
        tags.append('travel')
    
    # Philosophical stories
    if any(word in content for word in ['జీవితం', 'అర్థం', 'తత్వం', 'philosophy', 'life', 'meaning', 'విలువ']):
        categories.append('philosophical')
        tags.append('life')
    
    # Children/Kids stories
    if any(word in content for word in ['పిల్లవాడు', 'పిల్లలు', 'చిన్న', 'బాలుడు', 'child', 'kid', 'children']):
        categories.append('kids')
        tags.append('children')
    
    # Determine if short or long story based on word count
    if story_data['wordCount'] < 500:
        categories.append('short')
        tags.append('short')
    else:
        categories.append('long')
        tags.append('long')
    
    # If no specific category found, mark as general
    if len([cat for cat in categories if cat not in ['short', 'long']]) == 0:
        categories.append('general')
        tags.append('general')
    
    story_data['categories'] = categories
    story_data['tags'] = tags
    
    return story_data

def main():
    # Read the CSV file with classifications
    stories_data = []
    csv_file = 'detailed_story_analysis_20251012_235444.csv'
    
    if not os.path.exists(csv_file):
        print(f"CSV file {csv_file} not found!")
        return
    
    print("Processing stories from CSV classification...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        story_count = 0
        
        for row in reader:
            if row['classification'] == 'Story':
                file_path = row['filepath']
                
                if os.path.exists(file_path):
                    story_data = extract_story_data(file_path)
                    if story_data:
                        story_data = categorize_story(story_data)
                        stories_data.append(story_data)
                        story_count += 1
                        
                        if story_count % 50 == 0:
                            print(f"Processed {story_count} stories...")
                else:
                    print(f"File not found: {file_path}")
    
    print(f"\nTotal stories processed: {len(stories_data)}")
    
    # Sort stories by year (newest first) and then by title
    stories_data.sort(key=lambda x: (-x['year'], x['title']))
    
    # Save to JSON file for the website
    with open('stories-data.json', 'w', encoding='utf-8') as f:
        json.dump(stories_data, f, ensure_ascii=False, indent=2)
    
    print(f"Stories data saved to stories-data.json")
    
    # Print summary statistics
    print("\n=== SUMMARY ===")
    print(f"Total stories: {len(stories_data)}")
    
    # Year distribution
    years = {}
    for story in stories_data:
        year = story['year']
        years[year] = years.get(year, 0) + 1
    
    print("\nStories by year:")
    for year in sorted(years.keys(), reverse=True):
        print(f"  {year}: {years[year]} stories")
    
    # Category distribution
    categories = {}
    for story in stories_data:
        for cat in story['categories']:
            categories[cat] = categories.get(cat, 0) + 1
    
    print("\nStories by category:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count} stories")

if __name__ == "__main__":
    main()
