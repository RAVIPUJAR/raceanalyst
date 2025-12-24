// Auto‑inject shared header & footer, highlight active menu, and enable mobile menu toggle

document.addEventListener("DOMContentLoaded", async () => {
    // Remove existing headers if they exist
    const existingHeaders = document.querySelectorAll('header');
    existingHeaders.forEach(header => header.remove());
    
    // Remove existing footers if they exist
    const existingFooters = document.querySelectorAll('footer');
    existingFooters.forEach(footer => footer.remove());
    
    // Remove any placeholder containers
    const headerContainer = document.getElementById('header');
    const footerContainer = document.getElementById('footer');
    if (headerContainer) headerContainer.remove();
    if (footerContainer) footerContainer.remove();

    try {
        // Inject Header
        const headerResponse = await fetch("shared/header.html");
        if (headerResponse.ok) {
            const headerHtml = await headerResponse.text();
            document.body.insertAdjacentHTML('afterbegin', headerHtml);
        } else {
            // Fallback header if file not found
            document.body.insertAdjacentHTML('afterbegin', `
                <header>
                    <div class="container header-content">
                        <div class="logo">
                            <div class="logo-icon">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <h1>Race<span>Analyst</span></h1>
                        </div>
                        
                        <button class="mobile-menu-btn" id="mobileMenuBtn">
                            <i class="fas fa-bars"></i>
                        </button>
                        
                        <nav class="nav-menu" id="navMenu">
                            <ul>
                                <li><a href="index.html" data-page="index"><i class="fas fa-home"></i> Home</a></li>
                                <li><a href="#" data-page="calendar"><i class="fas fa-calendar-alt"></i> Race Calendar</a></li>
                                <li><a href="chatcenter.html" data-page="chat"><i class="fas fa-comments"></i> Chat Center</a></li>
                            </ul>
                        </nav>
                    </div>
                </header>
            `);
        }

        // Inject Footer
        const footerResponse = await fetch("shared/footer.html");
        if (footerResponse.ok) {
            const footerHtml = await footerResponse.text();
            document.body.insertAdjacentHTML('beforeend', footerHtml);
        } else {
            // Fallback footer if file not found
            document.body.insertAdjacentHTML('beforeend', `
                <footer>
                    <div class="container">
                        <div class="footer-content">
                            <div class="footer-section">
                                <h4>About RaceAnalyst</h4>
                                <p>Professional analysis and selections for Indian horse racing. Data-driven insights combined with decades of turf experience.</p>
                                <div class="social-links">
                                    <a href="#"><i class="fab fa-twitter"></i></a>
                                    <a href="#"><i class="fab fa-telegram"></i></a>
                                    <a href="#"><i class="fab fa-whatsapp"></i></a>
                                    <a href="#"><i class="fab fa-youtube"></i></a>
                                </div>
                            </div>
                            
                            <div class="footer-section">
                                <h4>Quick Links</h4>
                                <ul style="list-style: none;">
                                    <li><a href="index.html" style="color: #ccc; text-decoration: none;">Today's Selections</a></li>
                                    <li><a href="#" style="color: #ccc; text-decoration: none;">Race Calendar</a></li>
                                    <li><a href="#" style="color: #ccc; text-decoration: none;">Contact</a></li>
                                </ul>
                            </div>
                            
                            <div class="footer-section">
                                <h4>Contact</h4>
                                <p><i class="fas fa-envelope"></i> selections@raceanalyst.in</p>
                                <p><i class="fas fa-phone"></i> +91 00000 00000</p>
                                <p><i class="fas fa-map-marker-alt"></i> Bengaluru, India</p>
                            </div>
                        </div>
                        
                        <div class="copyright">
                            <p>&copy; 2024 RaceAnalyst. Professional racing insights. Bet responsibly.</p>
                            <p style="font-size: 0.8rem; margin-top: 0.5rem;">For entertainment purposes only.</p>
                        </div>
                    </div>
                </footer>
            `);
        }

        // Signal that layout (header + footer) is ready
        window.dispatchEvent(new Event("layoutReady"));

        // Highlight Active Page
        const currentPage = location.pathname.split("/").pop().replace(".html", "");
        document.querySelectorAll("nav.nav-menu a").forEach(a => {
            if (a.dataset.page === currentPage) {
                a.style.color = "#d4af37";
                a.style.fontWeight = "600";
            }
        });

        // Mobile Menu Toggle
        const menuBtn = document.getElementById("mobileMenuBtn");
        const navMenu = document.getElementById("navMenu");

        if (menuBtn && navMenu) {
            menuBtn.addEventListener("click", () => {
                navMenu.classList.toggle("menu-open");
                const icon = menuBtn.querySelector('i');
                if (navMenu.classList.contains('menu-open')) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-times');
                } else {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            });
        }

    } catch (error) {
        console.error("Error loading shared components:", error);
    }
});
