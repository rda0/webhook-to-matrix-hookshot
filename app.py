import requests
from flask import Flask, request, make_response

url = 'https://hookshot.mbot.ethz.ch/webhook/'

app = Flask(__name__)

@app.route("/webhook/slack/<hook>", methods=['POST'])
def slack(hook):
    plain = ''
    html = ''
    markdown = ''
    incoming = request.json

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

    if text and html:
        r = requests.post(url + hook, json={'text':plain,'html':html})
    else:
        print('Invalid format: ' + incoming)
        r = requests.post(url + hook, json=incoming)

    return {"ok":True}

@app.route("/webhook/grafana/<hook>", methods=['POST'])
def grafana(hook):
    incoming = request.json
    r = requests.post(url + hook, json=incoming)
    return incoming

if __name__ == "__main__":
    app.run(port=9080, debug=True)
