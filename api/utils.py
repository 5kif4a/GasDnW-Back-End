import base64
import enum
import io
import json
from datetime import datetime
from types import GeneratorType

import pdfkit
import plotly.graph_objects as go
from flask import render_template, make_response
from flask_mail import Message
from plotly import io
from pywebpush import webpush, WebPushException


def know_level(value, low, moderate, danger, emergency):
    if value in range(low, moderate):
        return 1
    elif value in range(moderate + 1, danger):
        return 2
    elif value in range(danger + 1, emergency):
        return 3
    elif value > emergency:
        return 4
    else:
        return 0


def check_gas_level(lpg_value, co_value, smoke_value):
    lpg_level = know_level(value=lpg_value, low=5500, moderate=6900, danger=10000, emergency=18000)
    co_level = know_level(value=co_value, low=10, moderate=24, danger=50, emergency=400)
    smoke_level = know_level(value=smoke_value, low=10, moderate=24, danger=50, emergency=400)
    general_level = max(lpg_level, co_level, smoke_level)
    return general_level


class LevelType(enum.Enum):
    low = 1
    moderate = 2
    dangerous = 3
    emergency = 4

    def __str__(self):
        return self.name


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.__str__()
        if isinstance(obj, LevelType):
            return obj.__str__()
        if isinstance(obj, GeneratorType):
            return str(obj.__next__())
        return json.JSONEncoder.default(self, obj)


def create_plot(**data):
    fig = go.Figure()

    for i in range(len(data['y'])):
        fig.add_trace(
            go.Scatter(
                x=data['x'],
                y=data['y'][i],
                name=data['legends'][i])
        )

    fig.update_layout(autosize=False,
                      height=300,
                      margin=dict(
                          l=30,
                          r=0,
                          b=0,
                          t=0
                      ),
                      legend_orientation="h",
                      legend=dict(x=0, y=-.2))
    return fig


def convert_to_base64(fig):
    svg = io.to_image(fig, format='svg')
    svg_base64 = base64.b64encode(svg).decode('ascii')
    return svg_base64


def generate_pdf(template, context):
    html = render_template(template, context=context)
    import api.config as config
    cfg = pdfkit.configuration(wkhtmltopdf=bytes(config.PATH_TO_WKHTMLTOPDF, 'utf8'))
    pdf = pdfkit.from_string(html, False, configuration=cfg)
    return pdf


def pdf_response(template, context):
    pdf = generate_pdf(template, context)
    response = make_response(pdf)
    response.headers['Content-Type'] = "application/pdf"
    response.headers['Content-Disposition'] = "attachment"
    return response


def get_report_context(report_id):
    from api.models import Report

    report = Report.query.get(report_id)
    context = {
        "created_at": report.created_at,
        "content": report.content
    }
    if report.case is not None:
        case = report.case
        context['case_datetime'] = case.date_time
        context['case_level'] = case.level
        context['case_note'] = case.note
        context['device_location'] = case.mq2_data[0].device.location
        mq2_data_list = [el.as_dict() for el in case.mq2_data]
        dht_data_list = [el.as_dict() for el in case.dht_data]

        gas_dates = [el['date_time'] for el in mq2_data_list]
        lpg = [el['lpg'] for el in mq2_data_list]
        co = [el['co'] for el in mq2_data_list]
        smoke = [el['smoke'] for el in mq2_data_list]

        temphud_dates = [el['date_time'] for el in dht_data_list]
        temp = [el['temp'] for el in dht_data_list]
        hud = [el['hudimity'] for el in dht_data_list]

        gas_data = {
            "x": gas_dates,
            "y": [lpg, co, smoke],
            "legends": ["LPG, ppm", "CO, ppm", "Smoke, ppm"]
        }

        temphud_data = {
            "x": temphud_dates,
            "y": [temp, hud],
            "legends": ["Temperature, C", "Hudimity, %"]
        }

        gas_plot = create_plot(**gas_data)
        temphud_plot = create_plot(**temphud_data)
        context['gas_base64'] = convert_to_base64(gas_plot)
        context['temphud_base64'] = convert_to_base64(temphud_plot)

    if report.log is not None:
        log = report.log
        context['log_datetime'] = log.date_time
        context['log_recognized_objects'] = log.recognized_objects
        context['camera_location'] = log.camera.location

    return context


def send_mail_with_attachment(report_id, recipient_mail):
    from api.flask_app import mail
    subject = "GasDnW"
    body = "Gas Detection & Warning - Gas Leak Moritoring system automatically generated report"

    msg = Message(subject=subject, body=body, recipients=[recipient_mail])

    context = get_report_context(report_id)
    pdf = generate_pdf("report.html", context)

    msg.attach(filename="gasdnw report.pdf", content_type="application/pdf", data=pdf)

    mail.send(msg)


def send_web_push(subscription_information, message_body):
    from api.config import VAPID_PRIVATE_KEY, VAPID_CLAIMS
    return webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims=VAPID_CLAIMS
    )


def notify_about_warning(message):
    from api.models import Subscriber
    subscribers = Subscriber.query.all()

    for subscriber in subscribers:
        try:
            token = {
                'endpoint': subscriber.endpoint,
                'expirationTime': subscriber.expiration_time,
                'keys': {
                    'p256dh': subscriber.p256dh,
                    'auth': subscriber.auth
                }
            }
            send_web_push(token, message)
        except WebPushException as e:
            print(e)
            continue

