var player = videojs('my-video')
const websocket = new WebSocket(host);

window.onkeydown = function(e){
    if (e.code == "Space")
        player.controlBar.playToggle.handleClick_()
    else if (e.code == "ArrowRight")
        player.currentTime(player.currentTime() + 10)
    else if (e.code == "ArrowLeft")
        player.currentTime(player.currentTime() - 10)
}

player.boundHandleTechDoubleClick_ = function(_){}
player.handleTechDoubleClick_ = function(_){}
player.controlBar.fullscreenToggle.handleClick = function(){
    if (!document.fullscreenElement)
        document.getElementById("central-frame").requestFullscreen()
    else
        document.exitFullscreen()
}
document.onfullscreenchange = (event) => {
    pywebview.api.toggle_player_full_screen_app(!!document.fullscreenElement)
};
player.on('loadedmetadata', function(){
    player.poster(null)
});

var homeButton = player.controlBar.addChild('button', {}, 0)
var homeButtonDom = homeButton.el()
homeButton.addClass("custom-button vjs-home-btn")
homeButtonDom.innerHTML = '<span></span>'
homeButton.controlText("Главное меню")
homeButtonDom.onclick = function () {window.open('/','_self')}

var pauseRequestButton   = player.controlBar.addChild('button', {}, 0)
var pauseRequestButtonDom = pauseRequestButton.el()
pauseRequestButton.addClass("custom-button vjs-pause-request-btn")
pauseRequestButtonDom.innerHTML = '<span></span>'
pauseRequestButton.controlText("Попросить поставить на паузу")
pauseRequestButtonDom.onclick = sendPauseRequest

var rewindRequestButton   = player.controlBar.addChild('button', {}, 0)
var rewindRequestButtonDom = rewindRequestButton.el()
rewindRequestButton.addClass("custom-button vjs-rewind-request-btn")
rewindRequestButtonDom.innerHTML = '<span></span>'
rewindRequestButton.controlText("Попросить отмотать назад")
rewindRequestButtonDom.onclick = sendRewindRequest

var synchronizeButton   = player.controlBar.addChild('button', {}, 0)
var synchronizeButtonDom = synchronizeButton.el()
synchronizeButton.addClass("custom-button vjs-synchronize-btn")
synchronizeButtonDom.innerHTML = '<span></span>'
synchronizeButton.controlText("Синхронизироваться с хостом")
synchronizeButtonDom.onclick = synchronize

var playlistButton = player.controlBar.addChild('button', {}, 0)
var playlistButtonDom = playlistButton.el()
playlistButton.addClass("custom-button vjs-playlist-btn")
playlistButtonDom.innerHTML = '<span></span>'
playlistButton.controlText("Список эпизодов")
playlistButtonDom.onclick = showEpisodesOverlay

function showEpisodesOverlay() {
    document.getElementById("episodes-overlay").style = "transition: transform 0s; transform: translateX(0%);"
    document.getElementById("episodes-overlay-content").style = "transition: transform 0.3s; transform: translateX(0%);"
    document.getElementById("episodes-overlay-bg").style.display = "flex"
}
function hideEpisodesOverlay() {
    document.getElementById("episodes-overlay").style = "transition: transform 0.3s; transform: translateX(-100%);"
    document.getElementById("episodes-overlay-content").style = "transition: transform 1s; transform: translateX(-100%);"
    document.getElementById("episodes-overlay-bg").style.display = "none"
}
document.getElementById("episodes-overlay-bg").onclick = hideEpisodesOverlay
hideEpisodesOverlay()

var roomButton = player.controlBar.addChild('button', {}, 0)
var roomButtonDom = roomButton.el()
roomButton.addClass("custom-button vjs-room-btn")
roomButtonDom.innerHTML = '<span></span>'
roomButton.controlText("Меню комнаты")
roomButtonDom.onclick = showRoomOverlay

function showRoomOverlay() {
    document.getElementById("room-overlay").style = "transition: transform 0s; transform: translateX(0%);"
    document.getElementById("room-overlay-content").style = "transition: transform 0.3s; transform: translateX(0%);"
    document.getElementById("room-overlay-bg").style.display = "flex"
}
function hideRoomOverlay() {
    document.getElementById("room-overlay").style = "transition: transform 0.3s; transform: translateX(-100%);"
    document.getElementById("room-overlay-content").style = "transition: transform 1s; transform: translateX(-100%);"
    document.getElementById("room-overlay-bg").style.display = "none"
}
document.getElementById("room-overlay-bg").onclick = hideRoomOverlay
hideRoomOverlay()

var resolutionButton = player.controlBar.addChild('button', {}, 0)
var resolutionButtonDom = resolutionButton.el()
resolutionButton.addClass("custom-button vjs-resolution-btn")
resolutionButtonDom.innerHTML = '<span></span>'
resolutionButton.controlText("Качество видео")
resolutionButtonDom.onclick = toggleResolutionContainer

var resolutionsContainer = document.createElement("div")
resolutionsContainer.id = "resolutions-container"
resolutionButtonDom.appendChild(resolutionsContainer)
toggleResolutionContainer()

function toggleResolutionContainer() {
    resolutionsContainer.hidden = !resolutionsContainer.hidden
}
function createResolutionButtons() {
    resolutionsContainer.innerHTML = ''
    for (let i = 0; i < resolutions.length; i++) {
        var resolution_item = document.createElement("div")
        resolution_item.classList.add(`resolution-${resolutions[i]}`)
        if (resolution == resolutions[i])
            resolution_item.classList.add('active')
        resolutionsContainer.appendChild(resolution_item)
        resolution_item.onclick = function () {changeResolution(resolutions[i])}
    }
}
function changeResolution(new_resolution) {
    document.getElementsByClassName(`resolution-${resolution}`)[0].classList.remove('active')
    document.getElementsByClassName(`resolution-${new_resolution}`)[0].classList.add('active')
    resolutionButtonDom.firstElementChild.style.content = `url(static/images/resolution_${new_resolution}.svg)`
    resolution = new_resolution
    current_time = player.currentTime()
    paused = player.paused()
    player.src({
        type: 'application/x-mpegURL',
        src: 'https://' + title.player.host + title.player.list[episode].hls[resolution]
    });
    player.currentTime(current_time)
    if (!paused)
        player.play()
}


var _episodes = -1
function initTitle() {
    _episodes = title.type.episodes
    if (_episodes == null)
        _episodes = Object.keys(title.player.list).length

    html = ""
    for (let i = 0; i < Object.keys(title.player.list).length; i++) {
        html = html + `<div class="episodes-list-item" onclick="setEpisode('${i+1}')">
          <span>Серия ${i + 1}</span>
        </div>`
    }
    document.getElementById('episodes-list').innerHTML = html
}

function setEpisode(episode_number) {
    history.pushState({}, null, `/watch?title_id=9419&episode=${episode_number}&room_id=${room_id}`);
    websocket.send(JSON.stringify({"command": "set_episode", "episode": episode_number}))
    initEpisode(episode_number)
}
function initEpisode(episode_number) {
    document.getElementById('episodes-list').childNodes[episode - 1].classList.remove('active')
    document.getElementById('episodes-list').childNodes[episode_number - 1].classList.add('active')
    episode = episode_number

    if (title.player.list[episode].preview)
        player.poster(anilibria_storage_url + title.player.list[episode].preview)

    resolutions = []
    if (title.player.list[episode].hls['fhd'])
        resolutions.push('fhd')
    if (title.player.list[episode].hls['hd'])
        resolutions.push('hd')
    if (title.player.list[episode].hls['sd'])
        resolutions.push('sd')

    if (!resolutions.includes(resolution))
        resolution = resolutions[0]

    player.src({
        type: 'application/x-mpegURL',
        src: 'https://' + title.player.host + title.player.list[episode].hls[resolution]
    });

    createResolutionButtons()

    doAjax(
        "/api/update_history",
        "POST",
        function(){},
        {
            "title_id": title.id,
            "last_watched_episode": episode,
            "episodes_count": _episodes
        }
    )
}


var members = {}
var me = -1
var mute_new_members = false
lastRequest = 0

function showMessage(message) {
  window.setTimeout(() => window.alert(message), 50);
}
function setMuteNewMembers(value) {
    mute_new_members = value
}
function toggleMuteMember(member_id) {
    members[member_id] = !members[member_id]
    setMuteButtonIcon(member_id)
}
function setMuteButtonIcon(member_id) {
    elem = document.querySelector(`.room-member[data-user-id='${member_id}'] .mute-btn`)
    if (!elem) return
    if (members[member_id])
        elem.style = "background: url(/static/images/muted.svg)"
    else
        elem.style = "background: url(/static/images/no_muted.svg)"
}
function addMemberElement(member_id) {
    html = `<div class="room-member" data-user-id="${member_id}">
      <span>Гость ${member_id}</span>
      <button class="mute-btn" onclick="toggleMuteMember(${member_id})"></button>
    </div>
    `
    container = document.getElementById("members-list")
    container.innerHTML = container.innerHTML + html
    setMuteButtonIcon(member_id)
}
function addRequestCard(user_id, text) {
    html = `<div class="request-card">
      <span>${text}</span>
      <button class="mute-btn" onclick="toggleMuteMember(${user_id});this.parentElement.remove()"></button>
    </div>`
    container = document.getElementById("requests-overlay")
    container.innerHTML = container.innerHTML + html
    setTimeout(function(){container.lastChild.style = "transform: scale(1);"},100);
    setTimeout(function(){if (container.children[0]) container.children[0].style = "transform: scale(0);"},2000);
    setTimeout(function(){if (container.children[0]) container.children[0].remove()},2200);
}
function addPauseRequestCard(user_id) {
    addRequestCard(user_id, `Гость ${user_id} просит поставить на паузу`)
}
function addRewindRequestCard(user_id) {
    addRequestCard(user_id, `Гость ${user_id} просит отмотать назад`)
}
function sendRequest(data) {
    if (Date.now() - lastRequest < 2000) return
    lastRequest = Date.now()
    websocket.send(JSON.stringify(data))
}
function sendPauseRequest() {
    sendRequest({"command": "pause_request"})
}
function sendRewindRequest() {
    sendRequest({"command": "rewind_back_request"})
}
function synchronize() {
    websocket.send(JSON.stringify({"command": "playback_time_request"}))
}

var _seeking = false
var _seeking_start = 0
player.on("pause", function () {
    console.log("paused")
    if (hoster)
      websocket.send(JSON.stringify({"command": "pause"}))
})
player.on("playing", function(value) {
    _seeking = false
    if (hoster) {
        websocket.send(JSON.stringify({
            "command": "play", "time": Date.now() / 1000, "playback_time": player.currentTime()
        }))
    } else {
        if (_seeking_start != 0) {
            cur_time = Date.now()
            if (cur_time - _seeking_start > 1000)
                player.currentTime(player.currentTime() + (cur_time - _seeking_start) / 1000 + 1)
        }
        _seeking_start = 0
    }

    console.log("playing " + player.currentTime())
})
player.on("seeking", function () {
    _seeking = true
    console.log("seeking")
    if (hoster) {
        websocket.send(JSON.stringify({
            "command": "seek", "time": Date.now() / 1000, "playback_time": player.currentTime()
        }))
    } else {
        _seeking_start = Date.now()
    }
})
player.on("waiting", function(value) {
    if (_seeking) return
    console.log("waiting")
    if (hoster) {
        websocket.send(JSON.stringify({"command": "pause"}))
    } else {
        _seeking_start = Date.now()
    }
})

websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data)
    console.log(event)
    switch (event.type) {
        case "init":
          onInit(event)
          break
        case "join":
          onJoin(event)
          break
        case "pause":
          onPause()
          break
        case "play":
          onPlay(event)
          break
        case "seek":
          onSeek(event)
          break
        case "set_episode":
          onSetEpisode(event)
          break
        case "playback_time_request":
          onPlaybackTimeRequest(event)
          break
        case "playback_time_request_answer":
          onPlaybackTimeRequestAnswer(event)
          break
        case "leave_room":
          onLeaveRoom(event)
          break
        case "hoster_promotion":
          onHosterPromotion()
          break
        case "pause_request":
          onPauseRequest(event)
          break
        case "rewind_back_request":
          onRewindRequest(event)
          break
        case "error":
          onError(event)
          break
        default:
          throw new Error(`Unsupported event type: ${event.type}.`)
    }
})
function onInit(data) {
    room_id = data.room_id
    for (member of data.members) {
        members[member] = mute_new_members
    }
    me = data.me
    document.getElementById("room-id").innerHTML = room_id
    for (member of Object.keys(members)) {
        if (member != me)
            addMemberElement(member)
    }

    if (hoster) {
        history.pushState({}, null, "/watch?title_id=9419&episode=0&room_id="+room_id);
        return
    }
    title_id = data.title_id
    episode = data.episode
    doAjax("/api/get_title", "POST", onTitleLoaded, {"title_id": title_id})
}
function onJoin(data) {
    members[data.user_id] = mute_new_members
    addMemberElement(data.user_id)
}
function onPause() {
    player.pause()
}
function onPlay(data) {
    cur_time = Date.now() / 1000
    send_time = data.time
    playback_time = data.playback_time + (cur_time - send_time)
    player.currentTime(playback_time)
    player.play()
}
function onSeek(data) {
    cur_time = Date.now() / 1000
    send_time = data.time
    playback_time = data.playback_time + (cur_time - send_time)
    player.pause()
    player.currentTime(playback_time)
}
function onSetEpisode(data) {
    episode = data.episode
    initEpisode(episode)
}
function onPlaybackTimeRequest(data) {
    user_id = data.user_id
    websocket.send(JSON.stringify({
        "command": "playback_time_request_answer",
        "time": Date.now() / 1000,
        "playback_time": player.currentTime(),
        "user_id": user_id
    }))
}
function onPlaybackTimeRequestAnswer(data) {
    cur_time = Date.now() / 1000
    send_time = data.time
    playback_time = data.playback_time + (cur_time - send_time)
    player.currentTime(playback_time)
    if (data.playing)
        player.play()
    else
        player.pause()
}
function onLeaveRoom(data) {
    user_id = data.user_id
    elem = document.querySelector(`.room-member[data-user-id='${user_id}']`)
    if (elem)
        elem.remove()
}
function onHosterPromotion() {
    playlistButton.show()
    roomButton.show()
    synchronizeButton.hide()
    pauseRequestButton.hide()
    rewindRequestButton.hide()
    hoster = true
    history.pushState({}, null, `/watch?title_id=9419&episode=${episode}&room_id=${room_id}`);
}
function onPauseRequest(data) {
    if (!members[data.sender])
        addPauseRequestCard(data.sender)
}
function onRewindRequest(data) {
    if (!members[data.sender])
        addRewindRequestCard(data.sender)
}
function onError(data) {
    if (data.code == 1)  // Room does not exist
        if (title_id) {
            window.open(`/watch?title_id=${title_id}&episode=${episode}`,'_self')
        } else {
            window.open('/','_self')
        }
}

function hosterInit() {
    initTitle()
    initEpisode(episode)
    websocket.addEventListener("open", () => {
        websocket.send(JSON.stringify({"command": "create", "title_id": title.id, "episode": episode}))
    });
    pauseRequestButton.hide()
    rewindRequestButton.hide()
    synchronizeButton.hide()
}

function guestInit() {
    history.pushState({}, null, "/watch?room_id="+room_id);
    websocket.addEventListener("open", () => {
        websocket.send(JSON.stringify({"command": "join", "room_id": room_id}))
    });
    playlistButton.hide()
    roomButton.hide()
}
function onTitleLoaded(response) {
    if (this.responseText) {
        response = JSON.parse(this.responseText)
        if (response.status != "ok") {
            console.log(`Title "${response.title_id}" not found. ${response.msg}`)
            return
        }
        title = response.title
        initTitle()
        initEpisode(episode)
        websocket.send(JSON.stringify({"command": "playback_time_request"}))
    }
}

if (hoster)
    hosterInit()
else
    guestInit()
