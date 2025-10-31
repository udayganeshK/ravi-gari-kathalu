// Global variables
let allStories = [];
let filteredStories = [];
let displayedStories = [];
let storiesPerPage = 12;
let currentPage = 1;
let currentLanguage = 'te'; // Default to Telugu

// Translation mappings
const translations = {
    categories: {
        te: {
            'family': 'కుటుంబం',
            'travel': 'ప్రయాణం',
            'kids': 'పిల్లలు',
            'spiritual': 'ఆధ్యాత్మిక',
            'philosophical': 'తత్వం',
            'general': 'సాధారణ',
            'short': 'చిన్న',
            'long': 'పెద్ద'
        },
        en: {
            'family': 'Family',
            'travel': 'Travel',
            'kids': 'Kids',
            'spiritual': 'Spiritual',
            'philosophical': 'Philosophy',
            'general': 'General',
            'short': 'Short',
            'long': 'Long'
        }
    },
    categoryFilters: {
        te: {
            'family': 'కుటుంబ కధలు',
            'travel': 'ప్రయాణ వృత్తాంతాలు',
            'kids': 'పిల్లల కధలు',
            'spiritual': 'ఆధ్యాత్మిక కధలు',
            'philosophical': 'తత్వ చర్చలు',
            'general': 'సాధారణ కధలు'
        },
        en: {
            'family': 'Family Stories',
            'travel': 'Travel Stories',
            'kids': 'Children Stories',
            'spiritual': 'Spiritual Stories',
            'philosophical': 'Philosophical Stories',
            'general': 'General Stories'
        }
    },
    ui: {
        te: {
            'words': 'పదాలు',
            'readMore': 'ఇక కథ లోకి',
            'loadMore': 'మరిన్ని కథలు లోడ్ చేయండి ({count})',
            'loadMoreDefault': 'మరిన్ని కథలు లోడ్ చేయండి',
            'storyLoading': 'కథ లోడ్ చేస్తున్నాం...',
            'storyError': 'కథ లోడ్ చేయడంలో లోపం'
        },
        en: {
            'words': 'words',
            'readMore': 'Read More',
            'loadMore': 'Load More Stories ({count})',
            'loadMoreDefault': 'Load More Stories',
            'storyLoading': 'Loading story...',
            'storyError': 'Error loading story'
        }
    }
};

// DOM elements
const storiesGrid = document.getElementById('storiesGrid');
const loadMoreBtn = document.getElementById('loadMoreBtn');
const noResults = document.getElementById('noResults');
const yearFilter = document.getElementById('yearFilter');
const categoryFilter = document.getElementById('categoryFilter');
const lengthFilter = document.getElementById('lengthFilter');
const searchInput = document.getElementById('searchInput');
const modal = document.getElementById('storyModal');
const modalTitle = document.getElementById('modalTitle');
const modalContent = document.getElementById('modalContent');
const langToggle = document.getElementById('langToggle');

// Initialize the website
document.addEventListener('DOMContentLoaded', function() {
    loadStories();
    setupEventListeners();
    setupNavigation();
    setupLanguageToggle();
});

// Load stories from JSON file
async function loadStories() {
    try {
        const response = await fetch('stories-data.json');
        const storiesData = await response.json();
        
        // Convert object structure to flat array
        allStories = [];
        for (const year in storiesData) {
            storiesData[year].forEach(story => {
                story.year = year; // Add year property to each story
                allStories.push(story);
            });
        }
        
        filteredStories = [...allStories];
        
        populateFilters();
        displayStories();
        updateTotalStoriesCount();
        
        console.log(`Loaded ${allStories.length} stories`);
    } catch (error) {
        console.error('Error loading stories:', error);
        showError('కథలు లోడ్ చేయడంలో లోపం జరిగింది');
    }
}

// Populate filter dropdowns
function populateFilters() {
    // Clear existing options (except first default option)
    const yearOptions = yearFilter.querySelectorAll('option:not(:first-child)');
    yearOptions.forEach(option => option.remove());
    
    const categoryOptions = categoryFilter.querySelectorAll('option:not(:first-child)');
    categoryOptions.forEach(option => option.remove());

    // Year filter
    const years = [...new Set(allStories.map(story => story.year))].sort((a, b) => b - a);
    years.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearFilter.appendChild(option);
    });

    // Category filter - use auto-categorization
    const categories = new Set();
    allStories.forEach(story => {
        const autoCategory = categorizeStory(story);
        categories.add(autoCategory);
    });
    
    [...categories].sort().forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = translations.categoryFilters[currentLanguage][category] || category;
        categoryFilter.appendChild(option);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Filter event listeners
    yearFilter.addEventListener('change', applyFilters);
    categoryFilter.addEventListener('change', applyFilters);
    lengthFilter.addEventListener('change', applyFilters);
    searchInput.addEventListener('input', debounce(applyFilters, 300));

    // Load more button
    loadMoreBtn.addEventListener('click', loadMoreStories);

    // Modal event listeners
    const closeBtn = document.querySelector('.close');
    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Escape key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

// Setup language toggle
function setupLanguageToggle() {
    langToggle.addEventListener('click', toggleLanguage);
    
    // Set initial language from localStorage or default
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'te';
    currentLanguage = savedLanguage;
    
    // Update language button text
    const langText = langToggle.querySelector('.lang-text');
    langText.textContent = currentLanguage === 'te' ? 'EN' : 'తె';
    
    // Update UI with initial language
    updateUILanguage();
}

// Toggle between Telugu and English
function toggleLanguage() {
    currentLanguage = currentLanguage === 'te' ? 'en' : 'te';
    localStorage.setItem('preferredLanguage', currentLanguage);
    
    // Update language button
    const langText = langToggle.querySelector('.lang-text');
    langText.textContent = currentLanguage === 'te' ? 'EN' : 'తె';
    
    // Update all translatable elements
    updateUILanguage();
    
    // Re-populate filters with new language
    populateFilters();
    
    // Re-render stories with new language
    renderStories();
    updateLoadMoreButton();
}

// Update UI language
function updateUILanguage() {
    const elements = document.querySelectorAll('[data-te][data-en]');
    elements.forEach(element => {
        const teText = element.getAttribute('data-te');
        const enText = element.getAttribute('data-en');
        
        if (currentLanguage === 'te') {
            element.textContent = teText;
        } else {
            element.textContent = enText;
        }
    });
    
    // Update page title
    if (currentLanguage === 'te') {
        document.title = 'రవి కావూరు కథలు - Telugu Stories Collection';
    } else {
        document.title = 'Ravi\'s Stories - Telugu Stories Collection';
    }
    
    // Update placeholder for search input
    const searchInput = document.getElementById('searchInput');
    const tePlaceholder = searchInput.getAttribute('data-te-placeholder');
    const enPlaceholder = searchInput.getAttribute('data-en-placeholder');
    
    if (currentLanguage === 'te') {
        searchInput.placeholder = tePlaceholder;
    } else {
        searchInput.placeholder = enPlaceholder;
    }
}
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    // Smooth scrolling for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }

            // Update active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            // Close mobile menu
            navMenu.classList.remove('active');
        });
    });

    // Mobile hamburger menu
    hamburger.addEventListener('click', function() {
        navMenu.classList.toggle('active');
    });

    // Update active nav link on scroll
    window.addEventListener('scroll', updateActiveNavLink);
}

// Update active navigation link based on scroll position
function updateActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const scrollPos = window.scrollY + 100;

    sections.forEach(section => {
        const top = section.offsetTop;
        const height = section.offsetHeight;
        const id = section.getAttribute('id');
        const navLink = document.querySelector(`.nav-link[href="#${id}"]`);

        if (scrollPos >= top && scrollPos < top + height) {
            document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
            if (navLink) navLink.classList.add('active');
        }
    });
}

// Apply filters
function applyFilters() {
    const yearValue = yearFilter.value;
    const categoryValue = categoryFilter.value;
    const lengthValue = lengthFilter.value;
    const searchValue = searchInput.value.toLowerCase().trim();

    filteredStories = allStories.filter(story => {
        // Year filter
        if (yearValue && story.year.toString() !== yearValue) {
            return false;
        }

        // Category filter - use auto-categorization
        if (categoryValue && categorizeStory(story) !== categoryValue) {
            return false;
        }

        // Length filter (based on text_length)
        if (lengthValue) {
            const isShort = story.text_length < 1000;
            const isLong = story.text_length >= 1000;
            if ((lengthValue === 'short' && !isShort) || (lengthValue === 'long' && !isLong)) {
                return false;
            }
        }

        // Search filter
        if (searchValue) {
            const searchText = (story.title + ' ' + story.excerpt).toLowerCase();
            if (!searchText.includes(searchValue)) {
                return false;
            }
        }

        return true;
    });

    currentPage = 1;
    displayStories();
}

// Display stories
function displayStories() {
    const startIndex = 0;
    const endIndex = currentPage * storiesPerPage;
    displayedStories = filteredStories.slice(startIndex, endIndex);

    if (displayedStories.length === 0) {
        showNoResults();
        return;
    }

    hideNoResults();
    renderStories();
    updateLoadMoreButton();
}

// Render stories in the grid
function renderStories() {
    storiesGrid.innerHTML = '';

    displayedStories.forEach(story => {
        const storyCard = createStoryCard(story);
        storiesGrid.appendChild(storyCard);
    });
}

// Function to categorize story based on title and content
function categorizeStory(story) {
    const title = story.title.toLowerCase();
    
    // Family related keywords (highest priority)
    if (title.includes('అమ్మ') || title.includes('నాన్న') || title.includes('కుటుంబ') || 
        title.includes('పెళ్లి') || title.includes('వివాహ') || title.includes('అల్లుడు') ||
        title.includes('కోడలు') || title.includes('వదిన') || title.includes('family')) {
        return 'family';
    }
    
    // Spiritual/Religious (second priority)
    if (title.includes('దేవుడు') || title.includes('భగవాన్') || title.includes('పూజ') || 
        title.includes('మంత్ర') || title.includes('స్తోత్ర') || title.includes('spiritual') ||
        title.includes('శ్రీ') || title.includes('గణేశ') || title.includes('విష్ణు') ||
        title.includes('శివ') || title.includes('దేవ') || title.includes('దేవి')) {
        return 'spiritual';
    }
    
    // Travel related (third priority)
    if (title.includes('ప్రయాణ') || title.includes('యాత్ర') || title.includes('ట్రిప్') || 
        title.includes('travel') || title.includes('trip') || title.includes('విమాన') ||
        title.includes('రైలు') || title.includes('బస్')) {
        return 'travel';
    }
    
    // Kids/Children (fourth priority)
    if (title.includes('పిల్లల') || title.includes('చిన్న') || title.includes('బాల') || 
        title.includes('పాప') || title.includes('kids') || title.includes('children') ||
        title.includes('బుడ్డి') || title.includes('అబ్బాయి') || title.includes('అమ్మాయి')) {
        return 'kids';
    }
    
    // Philosophical/Life lessons (fifth priority)
    if (title.includes('జీవిత') || title.includes('తత్వ') || title.includes('జ్ఞాన') || 
        title.includes('విషయ') || title.includes('అనుభవ') || title.includes('lesson') ||
        title.includes('wisdom') || title.includes('philosophical')) {
        return 'philosophical';
    }
    
    // Default to general
    return 'general';
}

// Create a story card element
function createStoryCard(story) {
    const card = document.createElement('div');
    card.className = 'story-card';
    card.onclick = (e) => {
        e.preventDefault();
        openStoryModal(story);
        return false;
    };

    // Auto-categorize the story
    const autoCategory = categorizeStory(story);
    const categoryTag = `<span class="category-tag ${autoCategory}">${getCategoryDisplayName(autoCategory)}</span>`;

    // Determine length based on text_length
    const isShort = story.text_length < 1000;
    const lengthTag = isShort ? 
        `<span class="category-tag short">${getCategoryDisplayName('short')}</span>` : 
        `<span class="category-tag long">${getCategoryDisplayName('long')}</span>`;

    const wordsText = translations.ui[currentLanguage]['words'] || 'words';
    const readMoreText = translations.ui[currentLanguage]['readMore'] || 'Read More';
    const wordCount = Math.round(story.text_length / 5); // Estimate words from characters

    card.innerHTML = `
        <div class="story-card-header">
            <h3 class="story-card-title">${story.title}</h3>
            <div class="story-card-meta">
                <span><i class="fas fa-calendar"></i> ${story.year}</span>
                <span><i class="fas fa-file-word"></i> ${wordCount} ${wordsText}</span>
            </div>
        </div>
        <div class="story-card-content">
            <p class="story-card-excerpt">${story.title}</p>
            <div class="story-card-footer">
                <div class="story-categories">
                    ${categoryTag}
                    ${lengthTag}
                </div>
                <button class="read-more">
                    ${readMoreText} <i class="fas fa-arrow-right"></i>
                </button>
            </div>
        </div>
    `;

    // Add click handler for read more buttons
    const readMoreBtn = card.querySelector('.read-more');
    if (readMoreBtn) {
        readMoreBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            openStoryModal(story);
        });
    }

    return card;
}

// Get category display name in current language
function getCategoryDisplayName(category) {
    return translations.categories[currentLanguage][category] || category;
}

// Load more stories
function loadMoreStories() {
    currentPage++;
    displayStories();
}

// Update load more button state
function updateLoadMoreButton() {
    const hasMore = (currentPage * storiesPerPage) < filteredStories.length;
    loadMoreBtn.style.display = hasMore ? 'block' : 'none';
    
    if (hasMore) {
        const remaining = filteredStories.length - (currentPage * storiesPerPage);
        const buttonText = remaining > storiesPerPage ? 
            translations.ui[currentLanguage]['loadMore'].replace('{count}', Math.min(remaining, storiesPerPage)) :
            translations.ui[currentLanguage]['loadMoreDefault'];
            
        const btnSpan = loadMoreBtn.querySelector('span');
        if (btnSpan) {
            btnSpan.textContent = buttonText;
        }
    }
}

// Show no results message
function showNoResults() {
    storiesGrid.style.display = 'none';
    loadMoreBtn.style.display = 'none';
    noResults.style.display = 'block';
}

// Hide no results message
function hideNoResults() {
    storiesGrid.style.display = 'grid';
    noResults.style.display = 'none';
}

// Open story modal
async function openStoryModal(story) {
    console.log('Opening modal for story:', story.title);
    
    if (!story || !story.file) {
        console.error('Invalid story data:', story);
        return;
    }
    
    // Check if modal elements exist
    if (!modal || !modalTitle || !modalContent) {
        console.error('Modal elements not found');
        return;
    }
    // Check if modal elements exist
    if (!modal || !modalTitle || !modalContent) {
        console.error('Modal elements not found');
        return;
    }
    
    modalTitle.textContent = story.title;
    
    // Set story metadata
    const storyMeta = modal.querySelector('.story-meta');
    if (storyMeta) {
        const yearSpan = storyMeta.querySelector('.story-year');
        const wordCountSpan = storyMeta.querySelector('.story-wordcount');
        const categoriesDiv = storyMeta.querySelector('.story-categories');
        
        const wordsText = translations.ui[currentLanguage]['words'] || 'words';
        const wordCount = Math.round(story.text_length / 5); // Estimate words
        
        if (yearSpan) yearSpan.textContent = story.year;
        if (wordCountSpan) wordCountSpan.textContent = `${wordCount} ${wordsText}`;
        
        // Add auto-categorized tags
        if (categoriesDiv) {
            const autoCategory = categorizeStory(story);
            const isShort = story.text_length < 1000;
            const lengthTag = isShort ? 'short' : 'long';
            
            categoriesDiv.innerHTML = `
                <span class="category-tag ${autoCategory}">${getCategoryDisplayName(autoCategory)}</span>
                <span class="category-tag ${lengthTag}">${getCategoryDisplayName(lengthTag)}</span>
            `;
        }
    }

    // Load story content
    const loadingText = translations.ui[currentLanguage]['storyLoading'] || 'Loading story...';
    modalContent.innerHTML = `<div style="text-align: center; padding: 2rem;"><i class="fas fa-spinner fa-spin fa-2x"></i><br><br>${loadingText}</div>`;
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';

    try {
        console.log('Fetching story file:', story.file);
        const response = await fetch(story.file);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Extract story content from the story-body div specifically
        let storyBodyDiv = doc.querySelector('.story-body');
        if (!storyBodyDiv) {
            // Fallback: try to find the main content area
            storyBodyDiv = doc.querySelector('main .story-content .story-body') || 
                          doc.querySelector('.story-content') || 
                          doc.querySelector('article');
        }
        
        if (!storyBodyDiv) {
            modalContent.innerHTML = '<p>కథ కంటెంట్ లోడ్ చేయలేకపోయాము.</p>';
            return;
        }
        
        // Remove script tags, style tags, and unwanted elements
        const elementsToRemove = storyBodyDiv.querySelectorAll('script, style, .story-tags, .tag, nav, .nav, .navigation, .header, .footer');
        elementsToRemove.forEach(el => el.remove());
        
        // Get clean text content from story body only
        const textContent = storyBodyDiv.textContent || storyBodyDiv.innerText || '';
        if (!textContent || textContent.trim() === '') {
            modalContent.innerHTML = '<p>కథ కంటెంట్ లోడ్ చేయలేకపోయాము.</p>';
            return;
        }
        
        const paragraphs = textContent
            .split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0)
            .filter(line => !line.includes('రవి కావూరు కథలు'))
            .filter(line => !line.includes('మొదటి పేజీ'))
            .filter(line => !line.includes('కథలు గురించి'));

        if (paragraphs.length > 0) {
            modalContent.innerHTML = paragraphs
                .map(paragraph => `<p>${paragraph}</p>`)
                .join('');
        } else {
            modalContent.innerHTML = '<p>కథ కంటెంట్ లోడ్ చేయలేకపోయాము.</p>';
        }

    } catch (error) {
        console.error('Error loading story:', error);
        const errorText = translations.ui[currentLanguage]['storyError'] || 'Error loading story';
        modalContent.innerHTML = `<div style="text-align: center; padding: 2rem; color: #e74c3c;"><i class="fas fa-exclamation-triangle fa-2x"></i><br><br>${errorText}</div>`;
    }
}

// Close story modal
function closeModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Update total stories count
function updateTotalStoriesCount() {
    const totalStoriesElement = document.getElementById('totalStories');
    if (totalStoriesElement) {
        totalStoriesElement.textContent = allStories.length;
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
        position: fixed;
        top: 100px;
        left: 50%;
        transform: translateX(-50%);
        background: #e91e63;
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        z-index: 3000;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    `;
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);

    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Scroll to stories section
function scrollToStories() {
    const storiesSection = document.getElementById('stories');
    if (storiesSection) {
        storiesSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Add smooth scrolling to CTA button
document.addEventListener('DOMContentLoaded', function() {
    const ctaButton = document.querySelector('.cta-button');
    if (ctaButton) {
        ctaButton.addEventListener('click', scrollToStories);
    }
});

// Add loading animation for images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('load', function() {
            this.style.opacity = '1';
        });
    });
});

// Add intersection observer for animations
document.addEventListener('DOMContentLoaded', function() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
            }
        });
    }, observerOptions);

    // Observe animated elements
    const animatedElements = document.querySelectorAll('.story-card-float');
    animatedElements.forEach(el => {
        el.style.animationPlayState = 'paused';
        observer.observe(el);
    });
});
