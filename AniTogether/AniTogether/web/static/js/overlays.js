class Overlay {
    constructor(el) {
        this.el = el
        this.align = el.dataset.align
        this.content = el.querySelector(".overlay-content")

        if (!this.align.includes("top")) {
            this.bg = document.createElement("div")
            this.bg.classList.add("overlay-bg")
            el.insertBefore(this.bg, this.content)
            if (!el.dataset.unclosable)
                this.bg.onclick = () => {this.hide()}
        }

        if (el.dataset.closeText) {
            this.close_text = document.createElement("div")
            this.close_text.classList.add("overlay-close-text")
            this.close_text.innerHTML = "нажмите чтобы закрыть"
            this.close_text.onclick = () => (this.hide())
            this.content.appendChild(this.close_text)
        }
        if (el.dataset.closeBtn) {
            this.close_btn = document.createElement("div")
            this.close_btn.classList.add("overlay-close-btn")
            this.close_btn.onclick = () => (this.hide())
            this.content.appendChild(this.close_btn)
        }
        if (el.dataset.easyClose) {
            this.content.onclick = () => (this.hide())
        }
    }
    show() {
        if (this.align == "right" || this.align == "left") {
            this.el.style = "transition: transform 0s; transform: translateX(0%);"
            this.content.style = "transition: transform 0.3s; transform: translateX(0%);"
            this.bg.style.display = "flex"
        }
        else if (this.align == "center") {
            this.el.style = "transition: transform 0s; transform: scale(1);"
            this.content.style = "transition: transform 0.3s; transform: scale(1);"
            this.bg.style.display = "flex"
        }
        else if (this.align == "top-left") {
            this.el.style = "transform: scale(1);"
        }
    }
    hide() {
        if (this.align == "right") {
            this.el.style = "transition: transform 0.3s; transform: translateX(100%);"
            this.content.style = "transition: transform 1s; transform: translateX(100%);"
            this.bg.style.display = "none"
        }
        else if (this.align == "left") {
            this.el.style = "transition: transform 0.3s; transform: translateX(-100%);"
            this.content.style = "transition: transform 1s; transform: translateX(-100%);"
            this.bg.style.display = "none"
        }
        else if (this.align == "center") {
            this.el.style = "transition: transform 0.3s; transform: scale(0);"
            this.content.style = "transition: transform 1s; transform: scale(0);"
            this.bg.style.display = "none"
        }
        else if (this.align == "top-left") {
            this.el.style = "transform: scale(0);"
        }
    }
}

var overlays = {}
for (overlay_el of document.getElementsByClassName("overlay")) {
    overlays[overlay_el.id] = new Overlay(overlay_el)
}

function overlay(el_id) {
    return overlays[el_id]
}
