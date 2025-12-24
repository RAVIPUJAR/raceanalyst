document.addEventListener("DOMContentLoaded", function() {
    console.log("include.js loaded - injecting header/footer");
    
    // 1. FIRST remove any existing headers/footers
    const oldHeader = document.querySelector('header');
    if (oldHeader) {
        console.log("Removing old header");
        oldHeader.remove();
    }
    
    const oldFooter = document.querySelector('footer');
    if (oldFooter) {
        console.log("Removing old footer");
        oldFooter.remove();
    }
    
    // 2. CREATE and INSERT UNIFIED HEADER
    const headerHTML = `
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
                    <li><a href="index.html"><i class="fas fa-home"></i> Home</a></li>
                    <li><a href="#"><i class="fas fa-calendar-alt"></i> Race Calendar</a></li>
                    <li><a href="chatcenter.html"><i class="fas fa-comments"></i> Chat Center</a></li>
                </ul>
            </nav>
        </div>
    </header>`;
    
    // Insert at the VERY beginning of body
    document.body.insertAdjacentHTML('afterbegin', headerHTML);
    console.log("New header inserted");
    
    // 3. CREATE and INSERT UNIFIED FOOTER
    const footerHTML = `
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
    </footer>`;
    
    // Insert at the VERY end of body
    document.body.insertAdjacentHTML('beforeend', footerHTML);
    console.log("New footer inserted");
    
    // 4. ADD Mobile Menu Functionality
    setupMobileMenu();
});

function setupMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navMenu = document.getElementById('navMenu');
    
    if (mobileMenuBtn && navMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            const icon = mobileMenuBtn.querySelector('i');
            if (navMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }
}
