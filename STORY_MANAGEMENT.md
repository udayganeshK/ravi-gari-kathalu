# 📚 Story Management Guide for రవి కావూరు కథలు

This guide explains how to add, edit, or delete stories from the Telugu stories website.

## 🎯 Quick Overview

The website uses a simple JSON file (`stories-data.json`) to store all story information. Stories are organized by year and each story has metadata like title, creation date, file path, etc.

## 📁 File Structure

```
ravigarikathalu/
├── stories-data.json          # Main story database
├── stories/                   # Story HTML files
│   ├── 2020/                 # Stories by year
│   ├── 2021/
│   ├── 2022/
│   ├── 2023/
│   └── 2024/
├── index.html                # Main website
├── script.js                 # Website logic
└── styles.css               # Website styling
```

## 🔧 Methods to Edit Stories

### Method 1: 🌐 GitHub Web Interface (Easiest for collaborators)

If you have write access to the repository, you can edit stories directly on GitHub:

1. **Go to the repository** on GitHub
2. **Navigate to `stories-data.json`**
3. **Click the pencil icon** (Edit this file)
4. **Make your changes** following the story format
5. **Scroll down** and add a commit message
6. **Click "Commit changes"** to save

**Advantages:**
- ✅ No need to install anything
- ✅ Works from any browser
- ✅ Automatic backup of previous version
- ✅ Easy to revert if something goes wrong

**Tips for GitHub Web Editing:**
- Use the **Preview** tab to check formatting
- Make **small changes** at a time
- Write **clear commit messages** like "Added new story: కథ పేరు"
- **Check the website** after committing to ensure it works

### Method 2: 🖥️ Direct JSON Editing (Recommended for developers)

1. **Open `stories-data.json`** in any text editor
2. **Find the story** you want to edit/delete
3. **Make changes** following the format below
4. **Save the file**
5. **Commit and push** changes to GitHub

### Method 3: 🐍 Python Scripts (For advanced operations)

Use the provided Python utilities for safer operations.

---

## 🚀 Quick Start for Collaborators

If you're a collaborator and want to add/edit stories:

1. **For simple edits**: Use **GitHub Web Interface** (Method 1 above)
2. **For complex operations**: Download and use **Python scripts** (Method 3 above)

**Most common tasks:**
- ✏️ **Edit existing story**: Use GitHub web interface
- ➕ **Add new story**: Use GitHub web interface or Python scripts
- 🗑️ **Delete story**: Use Python scripts (safer) or manual JSON editing

## 📝 Story Data Format

Each story in `stories-data.json` follows this structure:

```json
{
  "title": "కథ పేరు",
  "file": "stories/2024/story-filename.html",
  "date": "2024-03-15",
  "category": "story",
  "classification": "Story",
  "confidence": 90,
  "text_length": 1500,
  "created_date": "2024-03-15",
  "modified_date": "2024-03-15",
  "created_display": "March 15, 2024",
  "modified_display": "March 15, 2024"
}
```

## ✅ How to: Add a New Story

### Option A: Manual Addition

1. **Add story HTML file** to appropriate year folder in `stories/`
2. **Open `stories-data.json`**
3. **Find the correct year section** (e.g., "2024": [...])
4. **Add new story object** at the end of the year's array:

```json
{
  "title": "మీ కొత్త కథ పేరు",
  "file": "stories/2024/new-story.html",
  "date": "2024-10-31",
  "category": "story",
  "created_date": "2024-10-31",
  "created_display": "October 31, 2024"
}
```

### Option B: Using CSV Import

1. **Add story to Mavaya CSV** with classification "Story"
2. **Run update script**:
   ```bash
   python3 update_stories.py
   ```

## ❌ How to: Delete a Story

### ⚠️ Important: Always backup before deleting!

1. **Open `stories-data.json`**
2. **Find the story** to delete
3. **Remove the entire story object** (including { } and trailing comma)
4. **Optionally delete HTML file** from `stories/` folder
5. **Save and commit changes**

### Example:
```json
{
  "2024": [
    {
      "title": "కథ 1",
      "file": "stories/2024/story1.html"
    },
    {
      "title": "తొలగించాల్సిన కథ",  ← DELETE THIS ENTIRE BLOCK
      "file": "stories/2024/unwanted.html"
    },
    {
      "title": "కథ 3",
      "file": "stories/2024/story3.html"
    }
  ]
}
```

## ✏️ How to: Edit Story Details

### Common Edits:

1. **Change Title**:
   ```json
   "title": "పాత పేరు" → "కొత్త పేరు"
   ```

2. **Update Date**:
   ```json
   "date": "2024-01-01",
   "created_date": "2024-01-01",
   "created_display": "January 01, 2024"
   ```

3. **Move to Different Year**:
   - Cut entire story object from current year
   - Paste into target year's array
   - Update date fields accordingly

## 🛠️ Bulk Operations

For large-scale changes, you can create Python scripts:

### Delete Multiple Stories by Pattern:
```python
import json

# Load stories
with open('stories-data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Remove stories containing specific text
for year in data:
    data[year] = [s for s in data[year] if 'unwanted_text' not in s['title']]

# Save changes
with open('stories-data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

## 🔍 Quality Control

### Before Making Changes:

1. **Backup** `stories-data.json`:
   ```bash
   cp stories-data.json stories-data.json.backup
   ```

2. **Validate JSON** format:
   ```bash
   python3 -m json.tool stories-data.json > /dev/null
   ```

3. **Check story count**:
   ```bash
   python3 -c "
   import json
   with open('stories-data.json', 'r', encoding='utf-8') as f:
       data = json.load(f)
   print(f'Total stories: {sum(len(stories) for stories in data.values())}')
   "
   ```

### After Making Changes:

1. **Test locally**:
   ```bash
   python3 -m http.server 8000
   # Visit http://localhost:8000
   ```

2. **Commit changes**:
   ```bash
   git add stories-data.json
   git commit -m "Update stories: [describe changes]"
   git push
   ```

## 🚨 Common Mistakes to Avoid

1. **❌ Breaking JSON syntax** - Always validate JSON after editing
2. **❌ Forgetting commas** between objects
3. **❌ Wrong date format** - Use YYYY-MM-DD
4. **❌ Inconsistent file paths** - Match actual file locations
5. **❌ Duplicate titles** - Each story should have unique title
6. **❌ Not backing up** before major changes

## 🔄 Automation Options

### For Regular Contributors:

1. **Create a simple form** (HTML/JavaScript) to add/edit stories
2. **Use GitHub's web interface** to edit `stories-data.json` directly
3. **Set up GitHub Actions** for automated validation

### For Technical Users:

1. **Write custom scripts** for your specific needs
2. **Use the existing Python utilities** as templates
3. **Create database integration** for advanced management

## 📞 Getting Help

1. **Check JSON syntax** at jsonlint.com
2. **Test changes locally** before pushing
3. **Ask the original developer** for complex modifications
4. **Create issues** on GitHub for bugs or feature requests

## 🎯 Best Practices

- ✅ **Always backup** before making changes
- ✅ **Make small, incremental changes**
- ✅ **Test locally** before deploying
- ✅ **Use meaningful commit messages**
- ✅ **Keep file structure consistent**
- ✅ **Validate JSON** after every edit
- ✅ **Document your changes**

---

*This guide covers the main scenarios for story management. For complex operations or custom requirements, consider creating specialized scripts or consulting with a developer.*
