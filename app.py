import requests
from flask import Flask, make_response, render_template, request

from config import (
    flask_params,
    hookshot_params,
    msg_template_default,
    msg_templates,
    url,
)
from sanitize import grafana_sanitize_incoming

app = Flask(__name__, **flask_params)
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True


@app.route("/webhook/slack/<hook>", methods=["POST"])
def slack(hook):
    plain = ""
    html = ""
    incoming = request.json
    print("Got incoming /slack hook: " + str(incoming))

    attachments = incoming.get("attachments", [])
    username = str(incoming.get("username", ""))

    for attachment in attachments:
        color = str(attachment.get("color", "")).lower()
        title = str(attachment.get("title", ""))
        title_link = str(attachment.get("title_link", ""))
        text = str(attachment.get("text", ""))
        footer = str(attachment.get("footer", ""))
        fields = attachment.get("fields", [])

        html += '<font color="' + color + '">' if color else ""

        if title and title_link:
            plain += title + " " + title_link + "\n"
            html += '<b><a href="' + title_link + '">' + title + "</a></b><br/>\n"
        elif title:
            plain += title + "\n"
            html += "<b>" + title + "</b><br/>\n"

        if text:
            plain += text + "\n"
            html += text + "<br/>\n"

        for field in fields:
            title = str(field.get("title", ""))
            value = str(field.get("value", ""))
            if title and value:
                plain += title + ": " + value + "\n"
                html += "<b>" + title + "</b>: " + value + "<br/>\n"

        if footer:
            plain += footer + "\n"
            html += footer + "<br/>\n"

        html += "</font>" if color else ""

    if plain and html:
        if username:
            json = {"text": plain, "html": html, "username": username}
        else:
            json = {"text": plain, "html": html}
        print("Sending hookshot: " + str(json))
        r = requests.post(url + hook, json=json)
    else:
        print("Invalid format, sending unmodified.")
        r = requests.post(url + hook, json=incoming)

    response = make_response("ok", 200)
    response.mimetype = "text/plain"
    return response


@app.route("/webhook/grafana/<hook>", methods=["POST", "PUT"])
def grafana(hook):
    args = request.args
    
    template_type = args.get("template", msg_template_default)
    if template_type not in msg_templates:
        template_type = msg_template_default

    version = args.get("version", "v2")  # unused at the moment

    incoming = request.json
    print("Got incoming /grafana hook: " + str(incoming))

    sanitized = grafana_sanitize_incoming(incoming)

    plain = render_template(f"{template_type}.txt.jinja", **sanitized)
    html = render_template(f"{template_type}.html.jinja", **sanitized)

    json = {"text": plain, "html": html, **hookshot_params}
    print("Sending hookshot: " + str(json))
    r = requests.post(url + hook, json=json)

    return {"ok": True}
