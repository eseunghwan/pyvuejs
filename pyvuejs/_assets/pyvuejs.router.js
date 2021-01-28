
class RouterLink extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        this.addEventListener("click", this.$on_click, true);
    }

    $on_click(ev) {
        var view = document.getElementsByTagName("router-view")[0].firstChild;
        var endpoint = ev.target.getAttribute("to");
        view.data = "/routes" + endpoint;
    }
}

class RouterView extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        this.innerHTML = "";
        this.appendChild(document.createElement("object"));
    }
}


customElements.define("router-link", RouterLink);
customElements.define("router-view", RouterView);
