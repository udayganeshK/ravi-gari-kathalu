import os
import csv
from bs4 import BeautifulSoup
import re
from datetime import datetime

def extract_text_content(html_content):
    """Extract clean text content from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()
    # Clean up text
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    return text

def analyze_content_type(text, title, filename):
    """Comprehensive analysis to determine if content is a story or document"""
    
    text_lower = text.lower()
    title_lower = title.lower()
    
    # Strong indicators this is NOT a story (documents/forms/bills etc.)
    document_indicators = [
        # Bills and invoices
        'invoice', 'bill', 'payment', 'amount', 'tax', 'gst', 'total', 'due date',
        'account number', 'customer id', 'billing', 'charges', 'subscription',
        'fibernet', 'broadband', 'internet', 'plan', 'rental',
        
        # Official documents
        'application', 'form', 'registration', 'certificate', 'license',
        'government', 'office', 'department', 'ministry', 'authority',
        'proforma', 'annexure', 'schedule', 'rules', 'regulation',
        
        # Legal/Property documents
        'agreement', 'contract', 'deed', 'lease', 'rent', 'property',
        'house tax', 'municipal', 'survey number', 'plot',
        
        # Personal documents
        'passport', 'aadhaar', 'pan card', 'voter id', 'driving license',
        'bank statement', 'cheque', 'transaction',
        
        # Logs and records
        'log', 'record', 'entry', 'date:', 'time:', 'status:',
        'whatsapp chat', 'conversation', 'message',
        
        # Greetings/Announcements
        'greeting', 'congratulations', 'birthday', 'anniversary',
        'wishes', 'celebration', 'invitation',
        
        # Technical/Administrative
        'config', 'setup', 'installation', 'manual', 'guide',
        'specification', 'requirement', 'procedure'
    ]
    
    # Strong indicators this IS a story
    story_indicators = [
        # Narrative elements
        'కథ', 'కధ', 'అనుభవం', 'జరిగిన', 'జరిగింది', 'చెప్పాలని',
        'గుర్తుకు వచ్చింది', 'జ్ఞాపకం', 'జరిగిన విషయం',
        
        # Story beginnings
        'ఒకసారి', 'ఒకప్పుడు', 'అనగనగా', 'ఒక రోజు',
        'ముందు రోజు', 'గత వారం', 'చిన్న వయసులో',
        
        # Dialogue indicators
        'అన్నాడు', 'అంది', 'చెప్పాడు', 'చెప్పింది', 'అడిగాడు', 'అడిగింది',
        
        # Emotional/Reflective content
        'అనిపించింది', 'భావించాను', 'అర్థమైంది', 'తెలిసింది',
        'ఆలోచించాను', 'గుర్తుకు వచ్చింది'
    ]
    
    # Check for document indicators
    document_score = 0
    document_reasons = []
    
    for indicator in document_indicators:
        if indicator in text_lower or indicator in title_lower:
            document_score += 1
            document_reasons.append(f"Contains '{indicator}'")
    
    # Check filename patterns for documents
    doc_filename_patterns = [
        'application', 'form', 'proforma', 'bill', 'invoice', 'agreement',
        'log', 'chat', 'greeting', 'fibernet', 'tax', 'eci', 'minutes'
    ]
    
    for pattern in doc_filename_patterns:
        if pattern in filename.lower():
            document_score += 2
            document_reasons.append(f"Filename contains '{pattern}'")
    
    # Check for story indicators
    story_score = 0
    story_reasons = []
    
    for indicator in story_indicators:
        if indicator in text:
            story_score += 1
            story_reasons.append(f"Contains story element '{indicator}'")
    
    # Additional story checks
    if len(text) > 200:  # Stories are usually longer
        story_score += 1
        story_reasons.append("Substantial content length")
    
    # Check for narrative structure (paragraphs, dialogue)
    if text.count('\n') > 3 or text.count('।') > 2:
        story_score += 1
        story_reasons.append("Has narrative structure")
    
    # Decision logic
    if document_score >= 2:
        classification = "Document"
        confidence = min(90, 60 + document_score * 10)
        reasons = document_reasons[:3]  # Top 3 reasons
    elif story_score >= 2:
        classification = "Story"
        confidence = min(90, 60 + story_score * 10)
        reasons = story_reasons[:3]
    elif len(text) < 50:
        classification = "Document"
        confidence = 70
        reasons = ["Very short content, likely metadata or form"]
    else:
        # Ambiguous case - need manual review
        classification = "Needs Review"
        confidence = 30
        reasons = ["Unclear content type, needs manual review"]
    
    return classification, confidence, "; ".join(reasons)

def analyze_all_stories():
    """Analyze all HTML files in the stories directory"""
    
    results = []
    total_files = 0
    
    # Walk through all story directories
    for year in ['2021', '2022', '2023', '2024']:
        year_path = f'stories/{year}'
        if not os.path.exists(year_path):
            continue
            
        print(f"Analyzing {year}...")
        
        for filename in os.listdir(year_path):
            if not filename.endswith('.html'):
                continue
                
            total_files += 1
            filepath = os.path.join(year_path, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Extract title from HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else filename.replace('.html', '')
                
                # Extract text content
                text_content = extract_text_content(html_content)
                
                # Analyze content
                classification, confidence, reasons = analyze_content_type(text_content, title, filename)
                
                results.append({
                    'filename': filename,
                    'year': year,
                    'title': title,
                    'classification': classification,
                    'confidence': confidence,
                    'reasons': reasons,
                    'text_length': len(text_content),
                    'filepath': filepath
                })
                
                print(f"  {filename} -> {classification} ({confidence}%)")
                
            except Exception as e:
                print(f"  Error processing {filename}: {e}")
                results.append({
                    'filename': filename,
                    'year': year,
                    'title': 'ERROR',
                    'classification': 'Error',
                    'confidence': 0,
                    'reasons': f'Error reading file: {e}',
                    'text_length': 0,
                    'filepath': filepath
                })
    
    return results, total_files

def save_detailed_analysis(results):
    """Save detailed analysis to CSV"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f'detailed_story_analysis_{timestamp}.csv'
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['filename', 'year', 'title', 'classification', 'confidence', 
                     'reasons', 'text_length', 'filepath']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"\nDetailed analysis saved to: {csv_filename}")
    return csv_filename

def print_summary(results):
    """Print summary statistics"""
    
    total = len(results)
    stories = len([r for r in results if r['classification'] == 'Story'])
    documents = len([r for r in results if r['classification'] == 'Document'])
    needs_review = len([r for r in results if r['classification'] == 'Needs Review'])
    errors = len([r for r in results if r['classification'] == 'Error'])
    
    print(f"\n=== COMPREHENSIVE ANALYSIS SUMMARY ===")
    print(f"Total files analyzed: {total}")
    print(f"Stories: {stories}")
    print(f"Documents: {documents}")
    print(f"Needs Review: {needs_review}")
    print(f"Errors: {errors}")
    
    # By year breakdown
    print(f"\n=== BY YEAR ===")
    for year in ['2021', '2022', '2023', '2024']:
        year_results = [r for r in results if r['year'] == year]
        year_stories = len([r for r in year_results if r['classification'] == 'Story'])
        year_docs = len([r for r in year_results if r['classification'] == 'Document'])
        year_review = len([r for r in year_results if r['classification'] == 'Needs Review'])
        print(f"{year}: {len(year_results)} total ({year_stories} stories, {year_docs} documents, {year_review} review)")
    
    # High confidence classifications
    high_conf_stories = len([r for r in results if r['classification'] == 'Story' and r['confidence'] >= 80])
    high_conf_docs = len([r for r in results if r['classification'] == 'Document' and r['confidence'] >= 80])
    
    print(f"\n=== CONFIDENCE LEVELS ===")
    print(f"High confidence stories (≥80%): {high_conf_stories}")
    print(f"High confidence documents (≥80%): {high_conf_docs}")
    
    # Files that need manual review
    review_files = [r for r in results if r['classification'] == 'Needs Review' or r['confidence'] < 60]
    if review_files:
        print(f"\n=== FILES NEEDING MANUAL REVIEW ===")
        for file in review_files[:10]:  # Show first 10
            print(f"  {file['filename']} ({file['year']}) - {file['reasons']}")
        if len(review_files) > 10:
            print(f"  ... and {len(review_files) - 10} more")

if __name__ == "__main__":
    print("Starting comprehensive story analysis...")
    print("This will take a few minutes as I read through all 467 files...")
    
    results, total_files = analyze_all_stories()
    csv_file = save_detailed_analysis(results)
    print_summary(results)
    
    print(f"\nAnalysis complete! Check {csv_file} for detailed results.")
