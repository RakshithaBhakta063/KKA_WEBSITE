class CustomNavbar extends HTMLElement {
    constructor() {
        super();

        // Get Flask URLs from the HTML attributes
        const homeURL = this.dataset.home;
        const aboutURL = this.dataset.about;
        const newsURL = this.dataset.news;
        const pastEventsURL = this.dataset.pastEvents;
        const upcomingEventsURL = this.dataset.upcomingEvents;
        const galleryURL = this.dataset.gallery;
        const contactURL = this.dataset.contact;
        const logoURL = this.dataset.logo;
        const menuIconURL = this.dataset.menuIcon;

        this.innerHTML = `
            <header>
                <nav class="navbar">
                    <div class="logo">
                        <a href="${homeURL}">
                            <img src="${logoURL}" alt="Logo">
                        </a>
                    </div>
                    <div class="menu-toggle">
                        <img src="${menuIconURL}" alt="Menu">
                    </div>
                    <ul class="nav-links">
                        <li><a href="${homeURL}">Home</a></li>
                        <li><a href="${aboutURL}">About Us</a></li>
                        <li><a href="${newsURL}">News</a></li>
                        <li class="dropdown">
                            <button class="dropbtn">Events</button>
                            <ul class="dropdown-content">
                                <li><a href="${pastEventsURL}">Past Events</a></li>
                                <li><a href="${upcomingEventsURL}">Upcoming Events</a></li>
                            </ul>
                        </li>
                        <li><a href="${galleryURL}">Gallery</a></li>
                        <li><a href="${contactURL}">Contact</a></li>
                        <li><button class="join-button">Join</button></li>
                        <li><button class="close-menu">Close</button></li>
                        
                    </ul>
                </nav>
            </header>
        `;

        // Get necessary elements
        const menuToggle = this.querySelector('.menu-toggle');
        const navLinks = this.querySelector('.nav-links');
        const dropdown = this.querySelector('.dropdown-content');
        const joinButton = this.querySelector('.join-button');
        const closeMenuButton = this.querySelector('.close-menu');

        // Toggle menu in mobile view
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });

        // Close dropdown and mobile menu when "Join" button is clicked in mobile view
        joinButton.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                dropdown.style.visibility = "hidden";
                dropdown.style.opacity = "0";
                navLinks.classList.remove('active');
            }
        });

        // Close entire mobile menu when "Close" button is clicked
        closeMenuButton.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                navLinks.classList.remove('active');
            }
        });
    }
}

// Define the custom element
customElements.define('custom-navbar', CustomNavbar);
