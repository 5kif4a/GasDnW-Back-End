import base64
import enum
import io
import json
from datetime import datetime
from types import GeneratorType

import pdfkit
import plotly.graph_objects as go
from flask import render_template, make_response
from plotly import io


# from api.models import db, Case


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
    response = make_response(pdf)
    response.headers['Content-Type'] = "application/pdf"
    response.headers['Content-Disposition'] = "attachment"

    return response
