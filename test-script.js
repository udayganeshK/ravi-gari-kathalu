// Minimal test script
console.log('Script loaded successfully');

window.testFunction = function() {
    console.log('Test function works!');
    console.log('Elements:', {
        yearTabs: document.getElementById('yearTabs'),
        categoryFilters: document.getElementById('categoryFilters'),
        storiesGrid: document.getElementById('storiesGrid')
    });
};

console.log('Test function defined');
