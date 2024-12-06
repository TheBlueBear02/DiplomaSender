const toggleButton = document.getElementById('dark-mode-toggle');
const imageElement = document.getElementById('style-mode-icon');

// Define the function to toggle dark mode
function styleModeToggle() {
    // Apply the system preference on initial load
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.body.classList.add('dark-mode');
        imageElement.src = 'static/icons/dark-mode-icon.svg';
    }

    // Add event listener to toggle dark mode on button click
    toggleButton.addEventListener('click', () => {
        const isDarkMode = document.body.classList.toggle('dark-mode'); // Toggle the dark-mode class
        if (isDarkMode) {
            imageElement.src = 'static/icons/dark-mode-icon.svg'; // Set icon for light mode toggle
        } else {
            imageElement.src = 'static/icons/light-mode-icon.svg'; // Set icon for dark mode toggle
        }
});
}
