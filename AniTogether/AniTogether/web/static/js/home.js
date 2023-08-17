var title_ids = []

function onLoadPosterForHistoryItem() {
    if (!this.responseText) {return}
    response = JSON.parse(this.responseText)
    if (response.status != "ok") {
        console.log(`Loading poster for title ${response.title_id} failed. ${response.message}`)
        return
    }
    style = "background-image: url(" + response.poster_url + ")"
    document.getElementById("poster-" + response.title_id).style = style
}

function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
}

lastSearch = 0
async function searchTitles() {
    var query = String(document.getElementById("search-release").value)
    if (query.length == 0)
        hideSearchResults()
        hideSearchAnimation()
    if (query.length < 3)
        return

    showSearchAnimation()
    if (Date.now() - lastSearch < 1000) {
        await delay(1000);
    }
    if (document.getElementById("search-release").value != query)
        return

    lastSearch = Date.now()

    doAjax("/api/search_titles", "POST", onSearchTitles, {"query": query});
}

function hideSearchResults() {
    document.getElementById("search-result-container").style = "display: none"
}
function showSearchResults() {
    document.getElementById("search-result-container").style = "display: block"
}
function hideSearchAnimation() {
    document.getElementById("search-animation").style = "transform: scale(0)"
}
function showSearchAnimation() {
    document.getElementById("search-animation").style = "transform: scale(1)"
}

function onSearchTitles(resp) {
    if (!this.responseText) return
    try {
        response = JSON.parse(this.responseText)
    } catch (err) {return}
    if (response.status != "ok") {
        console.log(`Searching "${response.query}" failed. ${response.msg}`)
        return
    }
    if (response.query != document.getElementById("search-release").value)
        return
    html = ""
    for (title of response.titles) {
        html = html + `\n<div class="search-result-item" onmousedown="createRoom(${title.id})">
          <div class="search-result-item-poster" style="background-image: url(${title.poster})"></div>
          <div class="search-result-item-title">
            <div class="search-result-item-title-ru">${title.name_ru}</div>
            <div class="search-result-item-title-alt">${title.name_alt}</div>
          </div>
        </div>`
    }
    document.getElementById("search-result-container").innerHTML = html
    showSearchResults()
    hideSearchAnimation()
}

function createRoom(title_id, episode="0") {
    document.getElementById("loading-text").innerHTML = "создание комнаты"
    overlay("loading-overlay").show()
    doAjax(
        `${getHttpHost(host)}/create_room?title_id=${title_id}&episode=${episode}`,
        "GET", onRoomReady, {}
    )
}
function joinRoom() {
    room_id = document.getElementById("room-id-input").value
    if (!room_id)
        return

    document.getElementById("loading-text").innerHTML = "поиск комнаты"
    overlay("loading-overlay").show()
    doAjax(`${getHttpHost(host)}/get_room?room_id=${room_id}`, "GET", onRoomReady, {})
}
function onRoomReady() {
    overlay("loading-overlay").hide()
    if (!this.responseText) {return}
    response = JSON.parse(this.responseText)
    if (response.status != "ok") {
        console.log(`Creating room failed: [${response.code}] ${response.message}`)
        if (response.code == 1)
            document.getElementById("info-text").innerHTML = "такой комнаты не существует"
            overlay("info-overlay").show()
        return
    }
    window.open(
        `/watch?title_id=${response.title_id}&episode=${response.episode}&room_id=${response.room_id}`,
        '_self'
    )
}

function checkUpdate(bg=false) {
    doAjax(
        "https://api.github.com/repos/AlexDev505/AniTogether/releases", "GET",
        onGetReleases(bg), {}
    )
}
function onGetReleases(bg) {
    return function() {
        if (!this.responseText) {return}
        response = JSON.parse(this.responseText)
        last_release = response[0]
        last_version = last_release.tag_name
        if (last_version == version && !bg) {
            document.getElementById("info-text").textContent = "У вас установлена новейшая версия"
            overlay("info-overlay").show()
        }
        else if (last_version != version) {
            document.getElementById("last-version").textContent = last_version
            overlay("versions-overlay").show()
        }
    }
}
function update_app() {
    overlay("versions-overlay").hide()
    pywebview.api.update_app().then((response) => {
        overlay("loading-overlay").hide()
        if (response.message) {
            document.getElementById("info-text").innerHTML = (
                response.message +
                `\nвы можете <a href="https://github.com/AlexDev505/AniTogether/releases/latest" target="_blank">скачать обновление используя свой браузер</a>`
            )
            overlay("info-overlay").show()
        }
    })
    document.getElementById("loading-text").textContent = "загрузка обновления"
    overlay("loading-overlay").show()
}

window.addEventListener("DOMContentLoaded", (event) => {
    for (title_id of title_ids) {
        doAjax("/api/get_title_poster_url", "POST", onLoadPosterForHistoryItem, {"title_id": title_id});
    }
    document.getElementById("about-btn").onclick = () => {overlay("about-overlay").toggle()}
    if (start_info)
        overlay("info-overlay").show()
    if (check_version)
        checkUpdate(true)
})
