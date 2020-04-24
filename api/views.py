from flask import request, Response
from flask_restful import Resource

from api.cv import gen_video
from api.models import db, Device, MQ2Data, DHTData, Case, Log
from api.utils import check_gas_level, LevelType
from .app import api


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
                    db.session.add(case)
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
        case = Case.query.get(case_id)
        mq2_data_list = [el.as_dict() for el in case.mq2_data]
        dht_data_list = [el.as_dict() for el in case.dht_data]

        res = {
            'case': case.as_dict(),
            'mq2_data_list': mq2_data_list,
            'dht_data_list': dht_data_list
        }

        return res, 200


class LogAPI(Resource):
    def get(self, log_id):
        obj = Log.query.get(log_id)
        return obj.as_dict(), 200


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


class ReportView(Resource):
    def get(self):
        return

    def post(self):
        return


class NotificationView(Resource):
    def get(self):
        return

    def post(self):
        return


class CameraAPI(Resource):
    def get(self, camera_number):
        return Response(gen_video(camera_number),
                        mimetype="multipart/x-mixed-replace; boundary=frame")


# Routes

# Routes for sensors
api.add_resource(MQ2API, '/mq2')
api.add_resource(DHTAPI, '/dht')

api.add_resource(MQ2ListAPI, '/mq2list')
api.add_resource(DHTListAPI, '/dhtlist')

api.add_resource(CaseAPI, '/cases/<int:case_id>')
api.add_resource(LogAPI, '/logs/<int:log_id>')

api.add_resource(CaseListAPI, '/cases')
api.add_resource(LogListAPI, '/logs')

api.add_resource(CameraAPI, '/camera/<int:camera_number>')
