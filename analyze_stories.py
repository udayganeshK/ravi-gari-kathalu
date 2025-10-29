import os
import csv
from bs4 import BeautifulSoup
import re

def analyze_html_file(file_path):
    """Analyze an HTML file to determine if it's a story or document"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Get title
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else os.path.basename(file_path)
        
        # Get text content
        text_content = soup.get_text()
        
        # Indicators for documents (not stories)
        document_indicators = [
            'application', 'proforma', 'registration', 'form',
            'tax', 'rules', 'agreement', 'rent',
            'log-', 'whatsapp-chat', 'copy-of-',
            'house-tax', 'my-pension', 'blood-bank',
            'greeting-to-', 'aadhaar', 'aadhar'
        ]
        
        # Check filename for document indicators
        filename = os.path.basename(file_path).lower()
        is_likely_document = any(indicator in filename for indicator in document_indicators)
        
        # Story indicators in title/content
        story_indicators = [
            'కథ', 'కధ', 'కథా', 'కదబ',  # Telugu words for story
            'story', 'tale',
            'అనుభవ', 'జరిగిన',  # experience, happened
            'చిన్న', 'పెద్ద',  # small, big (story descriptors)
        ]
        
        has_story_indicators = any(indicator in title.lower() or indicator in filename for indicator in story_indicators)
        
        # Check content length (stories are usually longer)
        content_length = len(text_content.strip())
        
        # Determine category
        if is_likely_document:
            category = "document"
        elif has_story_indicators or (content_length > 1000 and not is_likely_document):
            category = "story"
        elif content_length < 500:
            category = "short_text"
        else:
            category = "unknown"
        
        return {
            'filename': os.path.basename(file_path),
            'title': title.replace(' - రవి గరి కథలు', ''),
            'category': category,
            'content_length': content_length,
            'year': file_path.split('/')[-2],
            'path': file_path
        }
        
    except Exception as e:
        return {
            'filename': os.path.basename(file_path),
            'title': 'ERROR',
            'category': 'error',
            'content_length': 0,
            'year': file_path.split('/')[-2],
            'path': file_path,
            'error': str(e)
        }

def main():
    stories_base_path = '/Users/udaykanteti/Workspaces/ravigarikathalu/stories'
    results = []
    
    # Walk through all year directories
    for year in ['2021', '2022', '2023', '2024']:
        year_path = os.path.join(stories_base_path, year)
        if os.path.exists(year_path):
            for filename in os.listdir(year_path):
                if filename.endswith('.html'):
                    file_path = os.path.join(year_path, filename)
                    result = analyze_html_file(file_path)
                    results.append(result)
    
    # Sort by year and filename
    results.sort(key=lambda x: (x['year'], x['filename']))
    
    # Write to CSV
    csv_path = '/Users/udaykanteti/Workspaces/ravigarikathalu/story_analysis.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['filename', 'title', 'category', 'content_length', 'year', 'path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow({k: v for k, v in result.items() if k in fieldnames})
    
    # Print summary
    story_count = sum(1 for r in results if r['category'] == 'story')
    document_count = sum(1 for r in results if r['category'] == 'document')
    unknown_count = sum(1 for r in results if r['category'] == 'unknown')
    
    print(f"Analysis complete! Results saved to {csv_path}")
    print(f"Total files: {len(results)}")
    print(f"Stories: {story_count}")
    print(f"Documents: {document_count}")
    print(f"Unknown/Other: {unknown_count}")
    
    # Show some examples
    print("\nStory examples:")
    for result in results[:5]:
        if result['category'] == 'story':
            print(f"  {result['filename']} - {result['title']}")
    
    print("\nDocument examples:")
    for result in results[:5]:
        if result['category'] == 'document':
            print(f"  {result['filename']} - {result['title']}")

if __name__ == "__main__":
    main()
