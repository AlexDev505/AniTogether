class Overlay {
    constructor(el) {
        this.el = el
        this.align = el.dataset.align
        this.content = el.querySelector(".overlay-content")
        this.bg = document.createElement("div")
        this.bg.classList.add("overlay-bg")
        this.onopen = null
        el.insertBefore(this.bg, this.content)

        if (!el.dataset.unclosable)
            this.bg.onclick = () => {this.hide()}
        if (el.dataset.easyclose)
            this.el.onclick = () => (this.hide())
    }
    show() {
        if (this.align == "right" || this.align == "left") {
            this.el.style = "transition: transform 0s; transform: translateX(0%);"
            this.content.style = "transition: transform 0.3s; transform: translateX(0%);"
        }
        else if (this.align == "center") {
            this.el.style = "transition: transform 0s; transform: scale(1);"
            this.content.style = "transition: transform 0.3s; transform: scale(1);"
        }
        this.bg.style.display = "flex"
        if (this.onopen)
            this.onopen()
    }
    hide() {
        if (this.align == "right") {
            this.el.style = "transition: transform 0.3s; transform: translateX(100%);"
            this.content.style = "transition: transform 1s; transform: translateX(100%);"
        }
        else if (this.align == "left") {
            this.el.style = "transition: transform 0.3s; transform: translateX(-100%);"
            this.content.style = "transition: transform 1s; transform: translateX(-100%);"
        }
        else if (this.align == "center") {
            this.el.style = "transition: transform 0.3s; transform: scale(0);"
            this.content.style = "transition: transform 1s; transform: scale(0);"
        }
        this.bg.style.display = "none"
    }
}

var overlays = {}
for (overlay_el of document.getElementsByClassName("overlay")) {
    overlays[overlay_el.id] = new Overlay(overlay_el)
}

function overlay(el_id) {
    return overlays[el_id]
}
