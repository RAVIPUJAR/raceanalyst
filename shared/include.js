

// Auto‑inject shared header & footer, highlight active menu, and enable mobile menu toggle

document.addEventListener("DOMContentLoaded", async () => {
    // Inject Header
    const headerContainer = document.createElement("div");
    headerContainer.id = "header";
    document.body.prepend(headerContainer);

    const headerHtml = await fetch("shared/header.html").then(r => r.text());
    headerContainer.innerHTML = headerHtml;

    // Inject Footer
    const footerContainer = document.createElement("div");
    footerContainer.id = "footer";
    document.body.append(footerContainer);

    const footerHtml = await fetch("shared/footer.html").then(r => r.text());
    footerContainer.innerHTML = footerHtml;
    // Signal that layout (header + footer) is ready
    window.dispatchEvent(new Event("layoutReady"));

    // Highlight Active Page
    const currentPage = location.pathname.split("/").pop().replace(".html", "");
    document.querySelectorAll("nav.nav-menu a").forEach(a => {
        if (a.dataset.page === currentPage) {
            a.classList.add("active-page");
        }
    });

    // Mobile Menu Toggle
    const menuBtn = document.getElementById("mobileMenuBtn");
    const navMenu = document.getElementById("navMenu");

    if (menuBtn && navMenu) {
        menuBtn.addEventListener("click", () => {
            navMenu.classList.toggle("menu-open");
        });
    }
});
