var title_ids = []

function onLoadPosterForHistoryItem(response) {
    if (this.responseText) {
        response = JSON.parse(this.responseText)
        if (response["status"] != "ok") {
            console.log(`Loading poster for title ${response['title_id']} failed. ${response['msg']}`)
            return
        }
        style = "background-image: url(" + response["poster_url"] + ")"
        document.getElementById("poster-" + response["title_id"]).style = style
    }
}

window.addEventListener("DOMContentLoaded", (event) => {
    for (title_id of title_ids) {
        doAjax("/api/get_title_poster_url", "POST", onLoadPosterForHistoryItem, {"title_id": title_id});
    }
})

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

function onSearchTitles(response) {
    if (this.responseText) {
        response = JSON.parse(this.responseText)
        if (response["status"] != "ok") {
            console.log(`Searching "${response['query']}" failed. ${response['msg']}`)
            return
        }
        if (response["query"] != document.getElementById("search-release").value)
            return
        html = ""
        for (title of response["titles"]) {
            html = html + `\n<div class="search-result-item" onmousedown="window.open('/watch?title_id=${title['id']}','_self')">
              <div class="search-result-item-poster" style="background-image: url(${title['poster']})"></div>
              <div class="search-result-item-title">
                <div class="search-result-item-title-ru">${title['name_ru']}</div>
                <div class="search-result-item-title-alt">${title['name_alt']}</div>
              </div>
            </div>`
        }
        document.getElementById("search-result-container").innerHTML = html
        showSearchResults()
        hideSearchAnimation()
    }
}

function joinRoom() {
    room_id = document.getElementById("room-id-input").value
    if (!room_id)
        return
    window.open(`/watch?room_id=${room_id}`,'_self')
}