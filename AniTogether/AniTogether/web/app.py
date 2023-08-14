import json
import os
import sys
from functools import wraps

from flask import Flask, render_template, request, jsonify
from loguru import logger

from .services import history, anilibria, tools


if getattr(sys, "frozen", False):
    ROOT_DIR = getattr(sys, "_MEIPASS")
else:
    ROOT_DIR = os.path.dirname(__file__)

app = Flask(
    __name__,
    template_folder=os.path.join(ROOT_DIR, "templates"),
    static_folder=os.path.join(ROOT_DIR, "static"),
)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1  # disable caching
app.config["TOKEN"] = ""


def verify_token(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        data = json.loads(request.data)
        token = data.get("token")
        if token == app.config["TOKEN"]:
            return function(*args, **kwargs)
        else:
            raise Exception("Authentication error")

    return wrapper


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/")
def index():
    return render_template(
        "home.html",
        token=app.config["TOKEN"],
        history=history.load(),
        version=os.environ["VERSION"],
    )


@app.route("/watch")
def watch():
    data = request.args.to_dict()
    room_id = data.get("room_id")
    title_id = data.get("title_id")
    episode = data.get("episode")
    if episode in {None, "0"}:
        episode = "1"

    if room_id:
        return join_to_room(room_id, title_id, episode)
    return create_room(title_id, episode)


def create_room(title_id, episode):
    try:
        title = anilibria.get_title(title_id)
    except anilibria.AnilibriaError as err:
        logger.error(f"{type(err).__name__}: {str(err)}")
        return jsonify(dict(status="error", msg=str(err), title_id=title_id))

    return render_template(
        "player.html",
        token=app.config["TOKEN"],
        title=title,
        title_id=title_id,
        episode=episode,
        resolution="hd",
        host=os.environ["HOST"],
        hoster=True,
        room_id="",
        anilibria_storage_url=anilibria.STORAGE_URL,
    )


def join_to_room(room_id, title_id: int | None, episode: str | None):
    return render_template(
        "player.html",
        token=app.config["TOKEN"],
        title={},
        title_id=title_id,
        episode=episode or "",
        resolution="hd",
        host=os.environ["HOST"],
        hoster=False,
        room_id=room_id,
        anilibria_storage_url=anilibria.STORAGE_URL,
    )


@app.route("/api/get_title_poster_url", methods=["POST"])
@verify_token
def get_title_poster_url():
    data = json.loads(request.data)
    title_id = data["title_id"]

    try:
        title = anilibria.get_title(title_id)
    except anilibria.AnilibriaError as err:
        logger.error(f"{type(err).__name__}: {str(err)}")
        return jsonify(dict(status="error", msg=str(err), title_id=title_id))

    poster_url = anilibria.STORAGE_URL + title["posters"]["original"]["url"]

    return jsonify(dict(status="ok", title_id=title_id, poster_url=poster_url))


@app.route("/api/get_title", methods=["POST"])
@verify_token
def get_title():
    data = json.loads(request.data)
    title_id = data["title_id"]

    try:
        title = anilibria.get_title(title_id)
    except anilibria.AnilibriaError as err:
        logger.error(f"{type(err).__name__}: {str(err)}")
        return jsonify(dict(status="error", msg=str(err), title_id=title_id))

    return jsonify(dict(status="ok", title=title))


@app.route("/api/search_titles", methods=["POST"])
@verify_token
def search_titles():
    data = json.loads(request.data)
    query = data["query"]

    try:
        titles = anilibria.search_titles(query)
    except anilibria.AnilibriaError as err:
        logger.error(f"{type(err).__name__}: {str(err)}")
        return jsonify(dict(status="error", msg=str(err), query=query))

    titles = [
        dict(
            id=title["id"],
            name_ru=title["names"]["ru"],
            name_alt=title["names"]["en"] or title["names"]["alternative"],
            poster=(
                anilibria.STORAGE_URL
                + (title["posters"]["small"] or title["posters"]["original"])["url"]
            ),
        )
        for title in titles
    ]

    return jsonify(dict(status="ok", titles=titles, query=query))


@app.route("/api/update_history", methods=["POST"])
@verify_token
def update_history():
    data = json.loads(request.data)
    title_id = data["title_id"]
    last_watched_episode = int(data["last_watched_episode"])
    episodes_count = data.get("episodes_count") or 0
    logger.opt(colors=True).debug(
        f"Updating history: title_id: "
        f"<y>{title_id}</y> - <y>{last_watched_episode}</y>/<y>{episodes_count}</y>"
    )
    history.update(
        title_id,
        episodes_count=episodes_count,
        last_watched_episode=last_watched_episode,
    )
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(debug=True)
