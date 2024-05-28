url = "https://hookshot.mbot.ethz.ch/webhook/"
flask_params = {"template_folder": "template"}
hookshot_params = {"version": "v2", "msgtype": "m.notice"}


reserved_label_keys = ["grafana_folder", "alertname"]
special_annotation_keys = ["description", "summary"]

reserved_labels = {k: "" for k in reserved_label_keys}
special_annotations = {k: "" for k in special_annotation_keys}

incoming_default = {
    "receiver": "",
    "status": "",
    "orgId": 0,
    "alerts": [],
    "groupLabels": {},
    "commonLabels": {},
    "commonAnnotatons": {},
    "externalUrl": "",
    "version": "",
    "groupKey": "",
    "commonStartsAtParsed": "",  # computed
}

alert_default = {
    "status": "",
    "labels": {},
    "annotations": {},
    "startsAt": "",
    "endsAt": "",
    "values": {},
    "generatorURL": "",
    "fingerprint": "",
    "silenceURL": "",
    "imageURL": "",
    "uniqueLabels": "",  # computed
    "uniqueAnnotations": "",  # computed
    "startsAtParsed": "",  # computed
    "endsAtParsed": "",  # computed
}

msg_templates = ("default", "oneliner", "detailed", "detailed_table")
msg_template_default = "default"
