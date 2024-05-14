import requests
from flask import Flask, request, make_response, render_template

from config import url, hookshot_params, flask_params, msg_templates, msg_template_default
from validate import grafana_validate_incoming


app = Flask(__name__, **flask_params)


@app.route("/webhook/slack/<hook>", methods=['POST'])
def slack(hook):
    plain = ''
    html = ''
    incoming = request.json
    print('Got incoming /slack hook: ' + str(incoming))

    attachments = incoming.get('attachments', [])
    username = str(incoming.get('username', ''))

    for attachment in attachments:
        color = str(attachment.get('color', '')).lower()
        title = str(attachment.get('title', ''))
        title_link = str(attachment.get('title_link', ''))
        text = str(attachment.get('text', ''))
        footer = str(attachment.get('footer', ''))
        fields = attachment.get('fields', [])

        html += '<font color="' + color + '">' if color else ''

        if title and title_link:
            plain += title + ' ' + title_link + '\n'
            html += '<b><a href="' + title_link + '">' + title + '</a></b><br/>\n'
        elif title:
            plain += title + '\n'
            html += '<b>' + title + '</b><br/>\n'

        if text:
            plain += text + '\n'
            html += text + '<br/>\n'

        for field in fields:
            title = str(field.get('title', ''))
            value = str(field.get('value', ''))
            if title and value:
                plain += title + ': ' + value + '\n'
                html += '<b>' + title + '</b>: ' + value + '<br/>\n'

        if footer:
            plain += footer + '\n'
            html += footer + '<br/>\n'

        html += '</font>' if color else ''

    if plain and html:
        if username:
            json = {'text':plain,'html':html,'username':username}
        else:
            json = {'text':plain,'html':html}
        print('Sending hookshot: ' + str(json))
        r = requests.post(url + hook, json=json)
    else:
        print('Invalid format, sending unmodified.')
        r = requests.post(url + hook, json=incoming)

    response = make_response('ok', 200)
    response.mimetype = "text/plain"
    return response

@app.route("/webhook/grafana/<hook>", methods=['POST', 'PUT'])
def grafana(hook):
    """
    see https://grafana.com/docs/grafana/latest/alerting/alerting-rules/manage-contact-points/integrations/webhook-notifier/
    todo:
    - handle query params to select different templates
    - handle empty -> default
    """

    args = request.args
    if "template" in args.keys():
        template_type = args.get("template")
        if template_type not in msg_templates:
            template_type = msg_template_default
    else:
        template_type = msg_template_default

    if "version" in args.keys():
        version = args.get("version")
    else:
        version = "v2"

    print(args)
    print(f"template: {template_type}, version: {version}")

    incoming = request.json
    print('Got incoming /grafana hook: ' + str(incoming))

    if not isinstance(incoming, dict):
        incoming = dict()

    grafana_validate_incoming(incoming)

    t = lambda fmt: f"{template_type}.{fmt}.jinja"
    plain = render_template(t("txt"), **incoming)
    html = render_template(t("html"), **incoming)

    if plain and html:
        json = {'text':plain,'html':html, **hookshot_params}
        print('Sending hookshot: ' + str(json))
        r = requests.post(url + hook, json=json)
    else:
        print('Invalid format, sending incoming as str.')
        r = requests.post(url + hook, json={'text':'Invalid format: ' + str(incoming)})

    return {"ok":True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9080, debug=True)
