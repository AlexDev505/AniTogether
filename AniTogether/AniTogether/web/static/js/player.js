const player = videojs('my-video')
const websocket = new WebSocket(getWsHost(host));

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

var pauseRequestButton = player.controlBar.addChild('button', {}, 0)
var pauseRequestButtonDom = pauseRequestButton.el()
pauseRequestButton.addClass("custom-button vjs-pause-request-btn")
pauseRequestButtonDom.innerHTML = '<span></span>'
pauseRequestButton.controlText("Попросить поставить на паузу")
pauseRequestButtonDom.onclick = sendPauseRequest

var rewindRequestButton = player.controlBar.addChild('button', {}, 0)
var rewindRequestButtonDom = rewindRequestButton.el()
rewindRequestButton.addClass("custom-button vjs-rewind-request-btn")
rewindRequestButtonDom.innerHTML = '<span></span>'
rewindRequestButton.controlText("Попросить отмотать назад")
rewindRequestButtonDom.onclick = sendRewindRequest

var synchronizeButton = player.controlBar.addChild('button', {}, 0)
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
playlistButtonDom.onclick = () => {overlay("episodes-overlay").show()}

var roomButton = player.controlBar.addChild('button', {}, 0)
var roomButtonDom = roomButton.el()
roomButton.addClass("custom-button vjs-room-btn")
roomButtonDom.innerHTML = '<span></span>'
roomButton.controlText("Меню комнаты")
roomButtonDom.onclick = () => {overlay("room-overlay").show()}

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
    doAjax("/api/update_resolution", "POST", function(){}, {"resolution": resolution})
}

player.volume(volume)

function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
}

var _lastVolumeChange = 0
player.on("volumechange", async function() {
    if (volume == player.volume().toFixed(2))
        return
    var _volume = player.volume().toFixed(2)
    if (Date.now() - _lastVolumeChange < 1000)
        await delay(1000)
    if (player.volume().toFixed(2) != _volume)
        return
    _lastVolumeChange = Date.now()
    volume = _volume
    doAjax("/api/update_volume", "POST", function(){}, {"volume": volume})
})


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
    cur_episode_el = document.getElementById('episodes-list').childNodes[episode_number - 1]
    cur_episode_el.classList.add('active')
    document.getElementById("episodes-overlay-content").scrollTop = cur_episode_el.offsetTop
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
var hoster = false
var time_correction = 0
lastRequest = 0

function getTime() {
    return utcNow() - time_correction
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
            "command": "play", "time": getTime(), "playback_time": player.currentTime()
        }))
    } else {
        if (_seeking_start != 0) {
            cur_time = getTime()
            if (cur_time - _seeking_start > 1)
                player.currentTime(player.currentTime() + (cur_time - _seeking_start) + 1)
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
            "command": "seek", "time": getTime(), "playback_time": player.currentTime()
        }))
    } else {
        _seeking_start = getTime()
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
        case "server_time_request_answer":
          onServerTimeRequestAnswer(event)
          break
        case "error":
          onError(event)
          break
        default:
          throw new Error(`Unsupported event type: ${vent.type}.`)
    }
})
function onInit(data) {
    websocket.send(JSON.stringify({"command": "server_time_request", "time": utcNow()}))

    for (member of data.members) {
        members[member] = mute_new_members
    }
    me = data.me
    hoster = me == members[0]

    document.getElementById("room-id").innerHTML = room_id
    for (member of Object.keys(members)) {
        if (member != me)
            addMemberElement(member)
    }

    if (hoster) {
        history.pushState({}, null, "/watch?title_id=9419&episode=0&room_id="+room_id)
        playlistButton.show()
        roomButton.show()
    } else {
        websocket.send(JSON.stringify({"command": "playback_time_request"}))
        synchronizeButton.show()
        pauseRequestButton.show()
        rewindRequestButton.show()
    }

    document.getElementById("room-loading").remove()
}
function onJoin(data) {
    members[data.user_id] = mute_new_members
    addMemberElement(data.user_id)
}
function onPause() {
    player.pause()
}
function onPlay(data) {
    cur_time = getTime()
    send_time = data.time
    playback_time = data.playback_time + (cur_time - send_time)
    player.currentTime(playback_time)
    player.play()
}
function onSeek(data) {
    cur_time = getTime()
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
        "time": getTime(),
        "playback_time": player.currentTime(),
        "user_id": user_id
    }))
}
function onPlaybackTimeRequestAnswer(data) {
    cur_time = getTime()
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
function onServerTimeRequestAnswer(data) {
    client_time = data.client_time
    client_now = utcNow()
    requests_delay = (client_now - client_time) / 2
    server_time = data.server_time + requests_delay
    time_correction = (client_now - server_time).toFixed(2)
}
function onError(data) {
    if (data.code == 1)  // Room does not exist
        window.open('/','_self')
}

function init() {
    initTitle()
    initEpisode(episode)
    websocket.addEventListener("open", () => {
        websocket.send(JSON.stringify({"command": "join", "room_id": room_id}))
    });
    pauseRequestButton.hide()
    rewindRequestButton.hide()
    synchronizeButton.hide()
    playlistButton.hide()
    roomButton.hide()
}

init()
