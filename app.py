import requests
from flask import Flask, request, make_response
from config import url

app = Flask(__name__)

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
        fields = attachment.get('fields', [])

        html += '<font color="' + color + '">' if color else ''

        if title and title_link:
            plain += title + ' ' + title_link + '\n'
            html += '<b><a href="' + title_link + '">' + title + '</a></b><br/>\n'

        if text:
            plain += text + '\n'
            html += text + '<br/>\n'

        for field in fields:
            title = str(field.get('title', ''))
            value = str(field.get('value', ''))
            if title and value:
                plain += title + ': ' + value + '\n'
                html += '<b>' + title + '</b>: ' + value + '<br/>\n'

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

    return {"ok":True}

@app.route("/webhook/grafana/<hook>", methods=['POST', 'PUT'])
def grafana(hook):
    plain = ''
    html = ''
    incoming = request.json
    print('Got incoming /grafana hook: ' + str(incoming))

    title = str(incoming.get('title', ''))
    rule_url = str(incoming.get('ruleUrl', ''))
    rule_name = str(incoming.get('ruleName', ''))
    message = str(incoming.get('message', ''))
    state = str(incoming.get('state', ''))
    eval_matches = incoming.get('evalMatches', [])

    if title and rule_url and rule_name:
        plain += title + ' ' + rule_url + ': ' + rule_name + ' (' + state + ')\n'
        html += '<b><a href="' + rule_url + '">' + title + '</a></b>: ' + rule_name + ' (' + state + ')<br/>\n'

    if message:
        plain += message + '\n'
        html += message + '<br/>\n'

    for eval_match in eval_matches:
        metric = str(eval_match.get('metric', ''))
        value = str(eval_match.get('value', ''))
        if metric and value:
            plain += metric + ': ' + value + '\n'
            html += '<b>' + metric + '</b>: ' + value + '<br/>\n'

    if plain and html:
        json = {'text':plain,'html':html}
        print('Sending hookshot: ' + str(json))
        r = requests.post(url + hook, json=json)
    else:
        print('Invalid format, sending incoming as str.')
        r = requests.post(url + hook, json={'text':'Invalid format: ' + str(incoming)})

    return {"ok":True}

if __name__ == "__main__":
    app.run(port=9080, debug=True)
