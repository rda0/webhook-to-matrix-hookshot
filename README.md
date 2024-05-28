# Webhook to Matrix Hookshot

This API translates incoming webhooks into generic webhooks (hookshot).

1. Receive Grafana webhook alert
2. Prepare alert data (error handling, add additional values)
3. Apply data to selected template (html, text)
4. Send out notification to hookshot

## Configuration

`https://webhooks.mbot.ethz.ch/webhook/grafana/<hook>?template=<template>&version=<version>`

| Param      | Description                     | Optional |
| ---------- | ------------------------------- | -------- |
| `hook`     | Hookshot ID of your webhook     |          |
| `template` | Template name (see table below) | Yes      |
| `version`  | API version (currently ignored) | Yes      |

This is the URL needed by Grafana. Create a new contact point and paste it.

## How to run

`flask --app app --debug run`

Set hostname and port with `-h` and `-p` respectively.

## Templates

| Name             | Description                 |
| ---------------- | --------------------------- |
| `default`        | shows important values      |
| `oneliner`       | `default` but more concise  |
| `detailed`       | `default` but better        |
| `detailed_table` | `detailed` with html tables |

For mor details see [templates](/templates.md).

## Jinja Templates

| `<template_name>` |                                                           |
| ----------------- | --------------------------------------------------------- |
| Path HTML         | `template/<template_name>.html.jinja`                     |
| Path Text         | `template/<template_name>.txt.jinja`                      |
| Registration      | Append `<template_name>` to `msg_templates` `(config.py)` |

- Info
  - Template rendering context (variables available in the template):
    - Incoming grafana alert data
    - Additional values (see below)
  - Error handling: missing/invalid data is interpreted as empty/zero
- Keep in mind
  - Use `alert['values']` (and not `alert.values`) to keep Jinja happy
  - Only use html tags allowed by the matrix spec
  - Remove unnecessary whitespace

### Rendering Context

You can use every value provided by Grafana. For a complete list see [Grafana Docs](https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/webhook-notifier/).

#### Reserved / Special Values

These values come directly from Grafana but have a special meaning or are used to
compute additional values and are thus explained here.

|                     | Value                              | Description |
| ------------------- | ---------------------------------- | ----------- |
| Reserved Labels     | `alert.labels['alertname']`        |             |
|                     | `alert.labels['grafana_folder']`   |             |
| Special Annotations | `alert.annotations['description']` |             |
|                     | `alert.annotations['summary]`      |             |
| Timestamps          | `alert['startsAt']`                |             |
|                     | `alert['endsAt']`                  |             |

**Note:** Reserved labels / special annotations also apply to `commonLabels`, `commonAnnotations`

#### Additional Values

These values are added to the incoming Grafana alert which is then applied to the Jinja template

```jsonc
{
  "normalLabels": {},
  "normalAnnotations": {},
  "alerts": [
    {
      "uniqueLabels": {},
      "uniqueAnnotations": {},
      "valuesForJinja": {},
      "startsAtParsed": "",
      "endsAtParsed": "",
    },
    (...)
  ],
  "commonStartsAtParsed": "",
  "commonEndsAtParsed": "",
}
```

| Value                  | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `normalLabels`         | Labels that are not "reserved"                   |
| `normalAnnotations`    | Annotations that are not "special"               |
| `uniqueLabels`         | Labels not in `commonLabels`                     |
| `uniqueAnnotations`    | Annotations not in `commonAnnotations`           |
| `startsAtParsed`       | Formatted version of `startsAt`                  |
| `endsAtParsed`         | Formatted version of `endsAt`                    |
| `commonStartsAtParsed` | `startsAtParsed` if same on every alert instance |
| `commonEndsAtParsed`   | `endsAtParsed` if same on every alert instance   |

### Inherit Template

Inherit from another text template if you only want to change html

```jinja
{%- include "detailed.txt.jinja" -%}
```

## Links

- [Matrix message spec](https://spec.matrix.org/latest/client-server-api/#mroommessage-msgtypes)
- [Hookshot webhook handling](https://matrix-org.github.io/matrix-hookshot/latest/setup/webhooks.html#webhook-handling)
- Grafana
  - [Alerts webhook format](https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/webhook-notifier/)
  - [Labels and annotations](https://grafana.com/docs/grafana/next/alerting/fundamentals/alert-rules/annotation-label/)
