import os
import sys
import math
import json
import time
import logging
import logging.handlers

from datetime import datetime
from flask import (
        Flask,
        request,
        Response,
        render_template,
        render_template_string,
        )

sys.path.append("./modules")

import player

from explorer import *
from html_builder import *

app = Flask(__name__)

""" #LOGGING """

SERVER_LOG_LEVEL   = 60
SERVER_ERROR_LEVEL = 70

MAX_LOG_FILE_SIZE  = 1024*5

handler_file_log = logging.handlers.RotatingFileHandler("server.log", maxBytes=MAX_LOG_FILE_SIZE)
handler_file_log.setLevel(SERVER_LOG_LEVEL)
handler_file_log.setFormatter(logging.Formatter("[%(asctime)s] %(module)s: %(message)s", "%d/%m/%Y %H:%M:%S"))

app.logger.addHandler(handler_file_log)

def log(msg, *args, **kwargs):
    return app.logger.log(SERVER_LOG_LEVEL, msg, *args, **kwargs)

def log_error(msg, *args, **kwargs):
    return app.logger.log(SERVER_ERROR_LEVEL, "ERROR: " + msg, *args, **kwargs)

""" #PLAYERS """

GAME_MASTER = "iamthecreatorofthisworld"

PLAYERS = ([
    "cruel",
    "astral",
    "violao",
    "jogador",
    "teclado",
    "mestre",
    "naval"
    ])

for name in PLAYERS:
    player.register(name)

""" #GAME-CONSTANTS """

REGISTRATION_ERRORS = ([
    "Registrado",
    "Caixa nome invalida",
    "Caixa sexo invalida",
    "Caixa nascimento invalida",
    "Caixa descrição visual invalida",
    "Caixa história invalida",
    "Abuso de pontos"
    ])

__uid__ = 0

def generate_uid():
    global __uid__
    __uid__ += 1
    return "c" + str(__uid__)

def build_component_params():
    params = request.form if request.method == "POST" else {}
    return { "uid": generate_uid(), **params }

def readfile(filepath):
    content = ""
    with open(filepath, "r") as file:
        content = file.read()
    return content

def readfile_utf8(filepath):
    content = ""
    with open(filepath, "rb") as file:
        content = file.read().decode("utf-8")
    return content

def serve_file(filepath, modifier=None, modifier_params={}):
    content = ""
    mimetype = "text/plain"

    with open(filepath, "rb") as file:
        content = file.read().decode("utf-8")

    if modifier and callable(modifier):
        # TODO: having `**` is making it specific.
        content = modifier(content, **modifier_params)

    if filepath.endswith(".css"):
        mimetype = "text/css"
    elif filepath.endswith(".html"):
        mimetype = "text/html"
    elif filepath.endswith(".js"):
        mimetype = "application/javascript"
    elif filepath.endswith(".mp3"):
        mimetype = "audio/mpeg"

    if content == "":
        content = "<p>404 ERROR</p>"

    return Response(content, mimetype=mimetype)

@app.route("/")
def __index__():
    return render_template("index.html")

@app.route("/dashboard")
def __dashboard__():
    return render_template("dashboard.html")

@app.route("/component/<name>", methods=["GET", "POST"])
def __component__(name):
    params = build_component_params()
    return serve_file(f"components/{name}.html", render_template_string, params)

@app.route("/component/list/<name>", methods=["POST"])
def __component_list__(name):
    component = readfile(f"components/{name}.html")
    if component == "":
        return "", 400

    path = request.form["path"]
    if not os.path.isdir(path):
        return "", 400

    output = ""

    for file in os.listdir(path):
        params = build_component_params()
        file_name = ".".join(file.split(".")[:-1])

        output += render_template_string(component,
                                         file_name=file_name,
                                         file_name_with_ext=file,
                                         full_path=path + "/" + file,
                                         **params)

    return output, 200

@app.route("/player/menu", methods=["POST"])
def __player_menu__():
    sheet = player.get(request.form["key"])
    return render_template("player-menu.html", **sheet)

@app.route("/live/<name>")
def __live__(name):
    sheet = player.get(name)

    pv = sheet["live"]["pv"]
    pe = sheet["live"]["pe"]

    pv = ((min(math.floor(pv/10), 1) * -1 + 1) * "0") + str(pv)
    pe = ((min(math.floor(pe/10), 1) * -1 + 1) * "0") + str(pe)

    return render_template_string("""
    <span><div class="icon">{% include "pv.svg" %}</div>{{pv}}</span>
    <span><div class="icon">{% include "pe.svg" %}</div>{{pe}}</span>
    """, pv=pv, pe=pe), 200

@app.route("/live/add", methods=["POST"])
def __live_add__():
    key = request.form["key"]
    value = int(request.form["value"])
    attribute = request.form["attribute"]

    player.add_to_live_attribute(key, attribute, value)
    return "", 200

@app.route("/sheet/<name>")
def __sheet__(name):
    sheet = player.get(name)
    if sheet == None:
        return "", 400
    return render_template("sheet.html", **sheet)

@app.route("/attrs/<name>")
def __attrs__(name):
    sheet = player.get(name)
    if sheet == None:
        return "", 400
    return render_template("attrs.html", **sheet)

@app.route("/inventory/<name>")
def __inventory__(name):
    sheet = player.get(name)
    return render_template("inventory.html", **sheet)

@app.route("/inventory/set/<name>", methods=["POST"])
def __inventory_set__(name):
    slot = int(request.form.get("slot", ""))
    item = str(request.form.get("item", ""))
    player.set_inventory_slot(name, slot, item)
    return "", 200

@app.route("/players/list")
def __player__():
    s = ""
    for name in PLAYERS:
        s += f"""
        <div>
          <span
            hx-get="/sheet/{name}"
            hx-swap="innerHTML"
            hx-target="#char-docv">{name}</span>
          <span> :: </span>
          <span
            hx-get="/attrs/{name}"
            hx-swap="innerHTML"
            hx-target="#char-docv">atributos</span>
          <br>
          (<form hx-post="/live/add" hx-swap="none">
            <input type="hidden" name="key" value="{name}"/>
            <input type="hidden" name="attribute" value="pv"/>
            <input type="hidden" name="value" value="+1"/>
            <input type="submit" value="+1pv">
          </form>
          <span> | </span>
          <form hx-post="/live/add" hx-swap="none">
            <input type="hidden" name="key" value="{name}"/>
            <input type="hidden" name="attribute" value="pv"/>
            <input type="hidden" name="value" value="-1"/>
            <input type="submit" value="-1pv">
          </form>)
          <br>
          (<form hx-post="/live/add" hx-swap="none">
            <input type="hidden" name="key" value="{name}"/>
            <input type="hidden" name="attribute" value="pe"/>
            <input type="hidden" name="value" value="+1"/>
            <input type="submit" value="+1pe">
          </form>
          <span> | </span>
          <form hx-post="/live/add" hx-swap="none">
            <input type="hidden" name="key" value="{name}"/>
            <input type="hidden" name="attribute" value="pe"/>
            <input type="hidden" name="value" value="-1"/>
            <input type="submit" value="-1pe">
          </form>)
        </div>
        """
    return s, 200

@app.route("/player/<player_id>")
def __player_page__(player_id):
    return serve_file("pages/player.html")

@app.route("/player-list")
def __player_list__():
    html = ""

    for filepath in os.listdir("documents/players"):
        name, ext = filepath.split(".")
        html += "<div "
        html += f'hx-get="/player-doc/{name}"'
        html += 'hx-target=".char-info"'
        html += ">"
        html += f"{name}"
        html += "</div>\n"
    return html

@app.route("/player-register", methods=["POST"])
def __player_register__():
    key = request.form.get("key", "")

    try:
        edit = player.edit(key, is_form=True)
        edit(request.form)
    except player.ClientError as e:
        return str(e), 200
    except player.ServerError as e:
        log_error(str(e))
        return "Erro desconhecido", 200

    log(f"{key} updated informations")

    return "Salvo", 200

def document_entry(file, full_path):
    e = Element("a")
    e.inner(file)
    e.set("href", "#")
    e.set("style", "display: block")
    e.set("hx-get", "/explorer/documents/" + file)
    e.set("hx-target", "#document-viewer")
    return e

@app.route("/explorer/documents/<name>", methods=["GET"])
def __explorer_documents_get__(name):
    explorer_ = Explorer("./documents")
    found, full_path = explorer_.find(name)

    if not found:
        return "", 400

    html_string = readfile_utf8(full_path)
    return html_string, 200

@app.route("/explorer/documents", methods=["GET"])
def __explorer_douments__():
    explorer_ = Explorer("./documents")
    content = explorer_.fmap(document_entry)
    return content, 200

@app.route("/src/<file_name>", methods=["GET"])
def __explorer_audios__(file_name):
    explorer_ = Explorer("./static/audios")

    found, full_path = explorer_.find(file_name)
    if not found:
        return "", 400

    source = Element("source")
    source.set("src", full_path)
    source.set("type", "audio/mpeg")

    return str(source), 200

@app.post("/validate")
def __validate__():
    id_ = request.form["id"]

    if id_ == GAME_MASTER:
        return render_template("master.html")
    try:
        page = ""

        if id_.endswith("!"):
            id_ = id_[:-1]
            page = "player.html"
        else:
            page = "player-register.html"

        sheet = player.get(id_)

        log(f"'{page}' accessed by {id_}")

        return render_template(
                page, **sheet,
                knowledges_points_n=player.KNOWLEDGES_POINTS,
                attributes_points_n=player.ATTRIBUTES_POINTS)
    except player.ClientError as e:
        return str(e), 200, {"HX-Retarget": "#error"}
    except player.ServerError as e:
        log_error(str(e))
        return "Erro desconhecido", 200, {"HX-Retarget": "#error"}

@app.route("/timer", methods=["GET"])
def __timer__():
    return render_template("timer.html")
