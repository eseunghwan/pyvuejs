
customElements.define(
    "pvue-component",
    class extends HTMLElement {
        constructor() {
            super();
        }
    
        connectedCallback() {
            var viewer = document.createElement("object");
            viewer.setAttribute("type", "text/html");
            viewer.setAttribute("data", `/components/${this.getAttribute("endpoint")}`);
            
            this.appendChild(viewer);
        }
    }
);
