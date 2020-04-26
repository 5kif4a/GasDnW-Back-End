from flask_admin.contrib.sqla import ModelView

from api.app import admin
from api.config import DEBUG
from api.models import *

only_read_models = [MQ2Data, DHTData]
models = [Device, Case, Log, Report, Notification]

if DEBUG:
    models.append(Camera)
else:
    only_read_models.append(Camera)


class OnlyReadModelView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False


def generate_model_views_list(models, model_view):
    return [model_view(model, db.session) for model in models]


modelviews = generate_model_views_list(models, ModelView) + \
             generate_model_views_list(only_read_models, OnlyReadModelView)
admin.add_views(*modelviews)
