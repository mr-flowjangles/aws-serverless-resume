/**
 * Bot Factory — Navigation Module
 * 
 * Handles left nav active state and smooth scrolling.
 */

document.querySelectorAll('.site-nav a').forEach(link => {
    link.addEventListener('click', function(e) {
        // Update active state
        document.querySelectorAll('.site-nav a').forEach(a => a.classList.remove('active'));
        this.classList.add('active');

        // Smooth scroll if href points to an anchor
        const href = this.getAttribute('href');
        if (href && href.startsWith('#') && href.length > 1) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    });
});
