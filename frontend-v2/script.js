window.onload = () => {
    let navItemElements = document.querySelectorAll(".nav-item");
    let navbar = document.querySelector(".navbar");
    for (let i = 0; i < navItemElements.length; i++) {
        navItemElements[i].onclick = () => {
            let ul = navItemElements[i].querySelector("ul");
            if (ul != null) {
                ul.style.display = ul.style.display == "none" ? "block" : "none";
            }
        }
    }

    navbar.onmouseleave = () => {
        document.querySelector(".navbar-nav-menu").style.display = "none";
    }
}