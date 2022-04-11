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

    if 'attachments' in incoming:
        for attachment in incoming['attachments']:
            color = ''
            if 'color' in attachment:
                color = str(attachment['color']).lower()
            html += '<font color="' + color + '">' if color else ''
            if 'title' in attachment:
                title = str(attachment['title'])
                if 'title_link' in attachment:
                    title_link = str(attachment['title_link'])
                    plain += title + ' ' + title_link + '\n'
                    html += '<b><a href="' + title_link + '">' + title + '</a></b><br/>\n'
                else:
                    plain += title + '\n'
                    html += '<b>' + title + '</b>\n'
            if 'text' in attachment:
                text = str(attachment['text'])
                plain += text + '\n'
                html += text + '<br/>\n'
            if 'fields' in attachment:
                for field in attachment['fields']:
                    if 'title' in field and 'value' in field:
                        title = str(field['title'])
                        value = str(field['value'])
                        plain += title + ': ' + value + '\n'
                        html += '<b>' + title + '</b>: ' + value + '<br/>\n'
            html += '</font>' if color else ''

    if plain and html:
        json = {'text':plain,'html':html}
        print('Sending hookshot: ' + str(json))
        r = requests.post(url + hook, json=json)
    else:
        print('Invalid format, sending unmodified.')
        r = requests.post(url + hook, json=incoming)

    return {"ok":True}

@app.route("/webhook/grafana/<hook>", methods=['POST'])
def grafana(hook):
    plain = ''
    html = ''
    incoming = dict(request.json)
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
