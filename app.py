import os
import json
import time

from datetime import datetime
from flask import (
        Flask,
        request,
        Response,
        render_template,
        render_template_string,
        )

import player

player.register("cruel")
player.register("astral")
player.register("violao")
player.register("jogador")
player.register("teclado")
player.register("mestre")

app = Flask(__name__)

GAME_MASTER = "iamthecreatorofthisworld"

ATTRIBUTES_POINTS = 5
ATTRIBUTES = ([
    "Força",
    "Reflexos",
    "Precição",
    "Presença",
    "Agilidade",
    "Inteligência",
    "Furtividade"
    ])

KNOWLEDGES_POINTS = 5
KNOWLEDGES = ([
    "Medicina",
    "Tecnologia",
    "Balística",
    "Combate",
    "Investigação",
    "Furto",
    "Línguas"
    ])

REG_ERR_NONE    = 0
REG_ERR_NAME    = 1
REG_ERR_SEX     = 2
REG_ERR_BIRTH   = 3
REG_ERR_VISUAL  = 4
REG_ERR_HISTORY = 5
REG_ERR_POINTS  = 6

REGISTRATION_ERRORS = ([
    "Registrado",
    "Caixa nome invalida",
    "Caixa sexo invalida",
    "Caixa nascimento invalida",
    "Caixa descrição visual invalida",
    "Caixa história invalida",
    "Abuso de pontos"
    ])

documents_dir = "documents/"
documents = os.listdir(documents_dir)
doc_index = 0

# __ply__ = ([
#     "astral",
#     "violao",
#     "jogador",
#     "teclado",
#     "cruel"
#     ])

# class Player:
#     VALUES = ["key", "name", "birth", "visual", "sex", "job", "history", "attributes", "knowledges"]
# 
#     def __init__(self, **kwargs):
#         values = {v: True for v in Player.VALUES}
# 
#         for k, v in kwargs.items():
#             if k in values:
#                 setattr(self, k, v)
#                 del values[k]
# 
#         setattr(self, "attributes", []); del values["attributes"]
#         setattr(self, "knowledges", []); del values["knowledges"]
# 
#         for attr in ATTRIBUTES:
#             if attr not in kwargs:
#                 raise Exception(f"Missing attribute: {attr}")
# 
#             self.attributes.append((attr, int(kwargs[attr])))
# 
#         for know in KNOWLEDGES:
#             if know not in kwargs:
#                 raise Exception(f"Missing knowledge: {know}")
# 
#             self.knowledges.append((know, int(kwargs[attr])))
# 
#         if len(values) > 0:
#             raise Exception(f"Invalid dictionary for player: missing {list(values.keys())}")
# 
#     def to_json(self):
#         return self.__dict__

# def ply_available(key):
#     return key in __ply__
# 
# def ply_registered(key):
#     return os.path.exists(f"players/{key}.html")
# 
# def ply_status(key):
#     if not ply_available(key):
#         return "invalid"
#     return "done" if ply_registered(key) else "todo"
# 
# def ply_register(player):
#     player_d = player.to_json()
# 
#     content = readfile("templates/player-info.html")
#     content = render_template_string(content, **player_d)
# 
#     with open(f"players/{player_d['key']}.html", "w+") as f:
#         f.write(content)
#     
#     return 0
# 
# def ply_can_register(key):
#     return (ply_exists(key) and ply_status(key) == "todo")

__uid__ = 0

def generate_uid():
    global __uid__
    __uid__ += 1
    return "c" + str(__uid__)

__msg__ = []

def add_message(msg, user):
    global __msg__
    msg_time = datetime.now().strftime("%H:%M:%S")
    __msg__.append([msg, msg_time, user])

def pop_message():
    global __msg__
    if len(__msg__) > 0:
        return __msg__.pop()
    return ["", "", ""]

def build_component_params():
    params = request.form if request.method == "POST" else {}
    return { "uid": generate_uid(), **params }

def readfile(filepath):
    content = ""
    with open(filepath, "r") as file:
        content = file.read()
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
                                         full_path=path + "/" + file,
                                         **params)

    return output, 200

@app.route("/document")
def __document__():
    global doc_index
    doc_index = 0

    doc_fname = documents[doc_index]
    doc_content = readfile(documents_dir + doc_fname)

    doc_content += f'<div id="doc-name" hx-swap-oob="true">{doc_fname}</div>'
    return doc_content

@app.route("/document/previous")
def __document_previous__():
    global doc_index
    doc_index -= 1

    if doc_index < 0:
        doc_index = len(documents) - 1

    doc_fname = documents[doc_index]
    doc_content = readfile(documents_dir + doc_fname)

    doc_content += f'<div id="doc-name" hx-swap-oob="true">{doc_fname}</div>'
    return doc_content

@app.route("/document/next")
def __document_name__():
    global doc_index
    doc_index += 1

    if doc_index >= len(documents):
        doc_index = 0

    doc_fname = documents[doc_index]
    doc_content = readfile(documents_dir + doc_fname)

    doc_content += f'<div id="doc-name" hx-swap-oob="true">{doc_fname}</div>'
    return doc_content

@app.route("/messages/<user>", methods=["GET", "POST"])
def __messages__(user):

    add_message("Hey!", "M")

    if user == GAME_MASTER and request.method == "GET":
        content = ""
        while True:
            msg, msg_time, user = pop_message()
            if msg == "":
                break
            msg = f"<p>[{msg_time}][{user}]: {msg}</p>"
            content += msg
        return content, 200
    elif request.method == "POST":
        message = request.form["message"]
        add_message("<p>" + message + "</p>")
        return "", 200
    return "", 400

@app.route("/player-info/<name>")
def __player_info__(name):
    player_info = players.get(name)
    if player_info == None:
        return "", 400

    return render_template("player-info.html", name=name, **player_info)

@app.route("/players")
def __player__():
    s = ""
    for name, player in players.items():
        s += f'<div class="char-entry" hx-get="/player-info/{name}" hx-trigger="click" hx-swap="none">{name}</div>'
    return Response(s)

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
    key = request.form.get("key", "[unknown]")
    app.logger.info("player register: attempt: %s", key)

    attrs = [(k, int(v)) for k, v in request.form.items() if k in ATTRIBUTES]
    if sum(map(lambda x: x[1], attrs)) > ATTRIBUTES_POINTS:
        return REGISTRATION_ERRORS[REG_ERR_POINTS], 400

    knows = [(k, int(v)) for k, v in request.form.items() if k in KNOWLEDGES]
    if sum(map(lambda x: x[1], knows)) > KNOWLEDGES_POINTS:
        return REGISTRATION_ERRORS[REG_ERR_POINTS], 400

    try:
        player.edit(**request.form)
    except player.ClientError as e:
        return str(e), 200
    except player.ServerError as e:
        app.logger.error(str(e))
        return "Erro desconhecido", 200

    return "Salvo", 200

@app.post("/validate")
def __validate__():
    id_ = request.form["id"]

    if id_ == GAME_MASTER:
        return render_template("master.html")

    try:
        p = player.get(id_)
        return render_template(
                "player-register.html", **p,
                knowledges_points_n=player.KNOWLEDGES_POINTS,
                attributes_points_n=player.ATTRIBUTES_POINTS)
    except player.ClientError as e:
        return str(e), 200, {"HX-Retarget": "#error"}
    except player.ServerError as e:
        app.logger.error(e)
        return "Erro desconhecido", 200, {"HX-Retarget": "#error"}
