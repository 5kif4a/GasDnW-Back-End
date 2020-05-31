import json
import re

from flask import request, Response
from flask_restful import Resource

from api.config import CLIENT_APP_BASE_URL
from api.cv import gen_video
from api.models import db, Device, MQ2Data, DHTData, Case, Log, Report, Subscriber, Notification, Camera
from api.utils import check_gas_level, LevelType, get_report_context, \
    pdf_response, send_mail_with_attachment, notify_about_warning, get_chunk
from .flask_app import api


# Views


class MQ2API(Resource):
    def get(self):
        """
        Получить последнюю запись в таблице
        :return: Tuple(JSON Object, HTTP Status Code)
        """
        try:
            if db.session.query(MQ2Data.id).count() > 0:
                obj = MQ2Data.query.order_by(-MQ2Data.id).first()
                return obj.as_dict(), 200

            return "No content", 204
        except Exception as e:
            print(e)
            return "Internal Server Error", 500

    def post(self):
        """
        Принять данные с датчика, проверить на уровень опасности, сгенерировать случай/событие
        :return: Tuple(JSON Object, HTTP Status Code)
        """
        try:
            sensor_data = request.get_json()
            lpg_value = sensor_data.get('LPG')
            co_value = sensor_data.get('CO')
            smoke_value = sensor_data.get('Smoke')
            device_id = sensor_data.get('device_id')

            # последние данные с датчиков
            last_mq2data = MQ2Data.query.order_by(MQ2Data.date_time.desc()).first()
            last_dhtdata = DHTData.query.order_by(DHTData.date_time.desc()).first()

            device = Device.query.get(device_id)

            # проверяем на уровень опасности
            level = check_gas_level(lpg_value, co_value, smoke_value)

            if level != 0:
                mq2data = MQ2Data(lpg=lpg_value, co=co_value, smoke=smoke_value, device_id=device_id)
                db.session.add(mq2data)
                db.session.commit()

                # разница во времени между последней и текущей зафиксированной инф-и о детекции газа
                time_diff = mq2data.date_time - last_mq2data.date_time
                note = f"Warning! Gas detected! " \
                       f"Location: {device.location}. " \
                       f"Gas concentration - LPG: {lpg_value} ppm - CO: {co_value} ppm - Smoke: {smoke_value} ppm."

                # если разница больше чем 30
                if time_diff.seconds > 30:
                    # создаем новый случай
                    case = Case()
                    case.note = note
                    case.level = LevelType(level)
                    case.dht_data.append(last_dhtdata)
                    case.mq2_data.append(mq2data)

                    db.session.flush()
                    case_id = case.id
                    notification = Notification(content=note, case_id=case_id)
                    db.session.add_all([case, notification])

                    # делаем рассылку уведомлений
                    message = json.dumps({
                        "type": "case",
                        "link": f"{CLIENT_APP_BASE_URL}/logs/cases/{case_id}",
                        "message": note
                    })

                    notify_about_warning(message)
                else:
                    # в противном случае связываем информацию с датчиков в последний случай
                    last_case = Case.query.order_by(Case.date_time.desc()).first()
                    last_case.dht_data.append(last_dhtdata)
                    last_case.mq2_data.append(mq2data)
                db.session.commit()

            return 200
        except Exception as e:
            print(e)
            return "Internal Server Error", 500


class DHTAPI(Resource):
    def get(self):
        """
        Получить последнюю запись в таблице
        :return: Tuple(JSON Object, HTTP Status Code)
        """
        try:
            if db.session.query(DHTData.id).count():
                obj = DHTData.query.order_by(-DHTData.id).first()
                return obj.as_dict(), 200

            return "No content", 204
        except Exception as e:
            print(e)
            return "Internal Server Error", 500

    def post(self):
        """
        Принять данные с датчика и добавить запись в таблицу
        :return: Tuple(JSON Object, HTTP Status Code)
        """
        try:
            sensor_data = request.get_json()
            temp = sensor_data.get('Temperature')
            hudimity = sensor_data.get('Hudimity')
            device_id = sensor_data.get('device_id')

            dhtdata = DHTData(temp=temp, hudimity=hudimity, device_id=device_id)
            db.session.add(dhtdata)
            db.session.commit()

            return 200
        except Exception as e:
            print(e)
            return "Internal Server Error", 500


class MQ2ListAPI(Resource):
    def get(self):
        try:
            q = MQ2Data.query.all()
            if len(q) > 0:
                resp = [row.as_dict() for row in q]
                return resp, 200
            else:
                return [], 204

        except Exception as e:
            print(e)
            return "Internal Server Error", 500


class DHTListAPI(Resource):
    def get(self):
        try:
            q = DHTData.query.all()
            if len(q) > 0:
                resp = [row.as_dict() for row in q]
                return resp, 200
            else:
                return [], 204

        except Exception as e:
            print(e)
            return "Internal Server Error", 500


class CaseAPI(Resource):
    def get(self, case_id):
        try:
            case = Case.query.get(case_id)
            mq2_data_list = [el.as_dict() for el in case.mq2_data]
            dht_data_list = [el.as_dict() for el in case.dht_data]

            res = {
                'case': case.as_dict(),
                'mq2_data_list': mq2_data_list,
                'dht_data_list': dht_data_list
            }

            return res, 200
        except Exception as e:
            print(e)
            return "Internal Server Error", 500


class LogAPI(Resource):
    def get(self, log_id):
        try:
            log = Log.query.get(log_id)
            camera = Camera.query.get(log.camera_id)
            location = camera.location

            log_dict = log.as_dict()
            log_dict['location'] = location
            res = {
                "log": log_dict
            }

            return res, 200
        except Exception as e:
            print(e)
            return "Internal Server Error", 500


class CreateLogAPI(Resource):
    def post(self):
        try:
            data = request.get_json()
            recognized_objects = data.get("recognized_objects")
            camera_id = data.get("camera_id")
            video_filename = data.get("filename")
            log = Log()
            log.camera_id = camera_id
            log.recognized_objects = recognized_objects
            log.video_filename = video_filename

            db.session.add(log)
            db.session.flush()
            log_id = log.id

            notification = Notification(content=recognized_objects, log_id=log_id)
            db.session.add(notification)

            message = json.dumps({
                "type": "camera_log",
                "link": f"{CLIENT_APP_BASE_URL}/logs/camera_logs/{log_id}",
                "message": recognized_objects
            })

            notify_about_warning(message)
            db.session.commit()

        except Exception as e:
            print(e)
            return "Internal Server Error", 500


class CaseListAPI(Resource):
    def get(self):
        try:
            q = Case.query.order_by(Case.date_time.desc()).all()
            if len(q) > 0:
                resp = [row.as_dict() for row in q]
                return resp, 200
            else:
                return [], 204
        except Exception as e:
            print(e)
            return "Internal Server Error", 500


class LogListAPI(Resource):
    def get(self):
        try:
            q = Log.query.order_by(Log.date_time.desc()).all()
            if len(q) > 0:
                resp = []
                for log in q:
                    obj = log.as_dict()
                    obj['location'] = log.camera.location
                    resp.append(obj)
                return resp, 200
            else:
                return [], 204
        except Exception as e:
            print(e)
            return "Internal Server Error", 500


class ReportListAPI(Resource):
    def get(self):
        try:
            reports = Report.query.order_by(Report.created_at.desc()).all()
            resp = []
            for report in reports:
                obj = report.as_dict()

                if report.case is not None:
                    case = report.case
                    obj['case_datetime'] = case.date_time
                    obj['case_level'] = case.level
                    obj['device_location'] = case.mq2_data[0].device.location
                if report.log is not None:
                    log = report.log
                    obj['log_datetime'] = log.date_time
                    obj['camera_location'] = log.camera.location

                resp.append(obj)
            return resp, 200
        except Exception as e:
            print(e)
            return "Internal Server Error", 500


class ReportAPI(Resource):
    def get(self, report_id):
        try:
            report = Report.query.get(report_id)
            resp = {
                "created_at": report.created_at,
                "content": report.content
            }

            if report.case is not None:
                case = report.case
                resp['case_datetime'] = case.date_time
                resp['case_level'] = case.level
                resp['case_note'] = case.note
                resp['device_location'] = case.mq2_data[0].device.location
                resp['mq2_data_list'] = [el.as_dict() for el in case.mq2_data]
                resp['dht_data_list'] = [el.as_dict() for el in case.dht_data]
            if report.log is not None:
                log = report.log
                resp['log_datetime'] = log.date_time
                resp['log_recognized_objects'] = log.recognized_objects
                resp['camera_location'] = log.camera.location
                resp['camera_id'] = log.camera.id
                resp['video_filename'] = log.video_filename

            return resp, 200

        except Exception as e:
            print(e)
            return "Internal Server Error", 500

    def delete(self, report_id):
        try:
            report = Report.query.get(report_id)
            db.session.delete(report)
            db.session.commit()
            return "OK", 200
        except Exception as e:
            print(e)
            return "Internal server error", 500


class CreateReportAPI(Resource):
    def post(self):
        try:
            request_data = request.get_json()
            content = request_data.get('content')
            case_id = request_data.get('case_id', None)
            log_id = request_data.get('log_id', None)

            report = Report(content=content, case_id=case_id, log_id=log_id)
            db.session.add(report)
            db.session.commit()

            return "Report created", 200
        except Exception as e:
            print(e)
            return "Internal Server Error", 500


class GenerateReportAPI(Resource):
    def get(self, report_id):
        context = get_report_context(report_id)
        return pdf_response("report.html", context=context)


class SubscriptionAPI(Resource):
    """
        POST creates a subscription
        GET returns vapid public key which clients uses to send around push notification
    """

    def get(self):
        from .config import VAPID_PUBLIC_KEY
        return Response(response=json.dumps({"public_key": VAPID_PUBLIC_KEY}),
                        content_type="application/json")

    def post(self):
        subscription_token = request.get_json("subscription_token")
        endpoint = subscription_token.get('endpoint')
        expiration_time = subscription_token.get('expirationTime')
        p256dh = subscription_token.get('keys').get('p256dh')
        auth = subscription_token.get('keys').get('auth')

        exists = db.session.query(Subscriber.id).filter_by(p256dh=p256dh).scalar() is not None

        if not exists:
            subscriber = Subscriber(endpoint=endpoint,
                                    expiration_time=expiration_time,
                                    p256dh=p256dh,
                                    auth=auth)
            db.session.add(subscriber)
            db.session.commit()
            return "Subscribed", 201
        return "OK", 200


class NotificationAPI(Resource):
    def post(self):
        try:
            notify_about_warning("test push")
            return "OK", 200
        except Exception as e:
            print(e)
            return "Internal server error", 500


class CameraAPI(Resource):
    def get(self):
        try:
            return Response(gen_video(),
                            mimetype="multipart/x-mixed-replace; boundary=frame")
        except Exception as e:
            print(e)
            return "Internal server error", 500


class VideoAPI(Resource):
    def get(self, filename):
        range_header = request.headers.get('Range', None)
        byte1, byte2 = 0, None
        if range_header:
            match = re.search(r'(\d+)-(\d*)', range_header)
            groups = match.groups()

            if groups[0]:
                byte1 = int(groups[0])
            if groups[1]:
                byte2 = int(groups[1])

        chunk, start, length, file_size = get_chunk(filename, byte1, byte2)
        resp = Response(chunk, 206, mimetype='video/mp4',
                        content_type='video/mp4', direct_passthrough=True)
        resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
        return resp


class MailAPI(Resource):
    def post(self):
        try:
            request_data = request.get_json()
            report_id = request_data.get('report_id')
            recipient_mail = request_data.get('recipient_mail')

            send_mail_with_attachment(report_id, recipient_mail)
            return "Mail sent", 200
        except Exception as e:
            print(e)
            return "Internal Server Error", 500


# Routes

# Routes for sensors
api.add_resource(MQ2API, '/mq2')
api.add_resource(DHTAPI, '/dht')

api.add_resource(MQ2ListAPI, '/mq2list')
api.add_resource(DHTListAPI, '/dhtlist')

api.add_resource(CaseAPI, '/cases/<int:case_id>')
api.add_resource(LogAPI, '/logs/<int:log_id>')
api.add_resource(CreateLogAPI, '/logs')

api.add_resource(CaseListAPI, '/cases')
api.add_resource(LogListAPI, '/logs')

api.add_resource(ReportAPI, '/reports/<int:report_id>')
api.add_resource(CreateReportAPI, '/reports')
api.add_resource(ReportListAPI, '/reports')
api.add_resource(GenerateReportAPI, '/report/generate/<int:report_id>')

api.add_resource(CameraAPI, '/camera')
api.add_resource(VideoAPI, '/video/<string:filename>')
api.add_resource(MailAPI, '/mail')

api.add_resource(SubscriptionAPI, '/subscription')
api.add_resource(NotificationAPI, '/notification')
