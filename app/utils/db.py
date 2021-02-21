import json
from os import path
import shelve


def get_clinics():
    with open(path.dirname(__file__) + '/../clinics_db.json', 'r') as db:
        return json.load(db)


def add_clinic(name, longitude, latitude):
    clinics = get_clinics()
    clinics[name] = {
        'location': [longitude, latitude],
        'dates_available': {}
    }
    with open(path.dirname(__file__) + '/../clinics_db.json', 'w') as db:
        json.dump(clinics, db, ensure_ascii=False, indent=4)


def delete_clinic(name):
    clinics = get_clinics()
    del clinics[name]
    with open(path.dirname(__file__) + '/../clinics_db.json', 'w') as db:
        json.dump(clinics, db, ensure_ascii=False, indent=4)


def add_datetime(cliniс, date, time):
    clinics = get_clinics()
    if date not in clinics[cliniс]['dates_available']:
        clinics[cliniс]['dates_available'][date] = [time]
    elif time not in clinics[cliniс]['dates_available'][date]:
        clinics[cliniс]['dates_available'][date].append(time)
    else:
        return 'Такое время уже доступно в указанную дату'
    with open(path.dirname(__file__) + '/../clinics_db.json', 'w') as db:
        json.dump(clinics, db, ensure_ascii=False, indent=4)
        return 'Дата и время успешно добавлены'


# TODO: функции по удалению дат и времени


def set_appointment_data(chat_id, user_data):
    with shelve.open(path.dirname(__file__) + '/../users_appointment') as db:
        db[str(chat_id)] = user_data
        return


def get_appointment_data(chat_id):
    with shelve.open(path.dirname(__file__) + '/../users_appointment') as db:
        return db.get(str(chat_id))


def appointment_made(chat_id):
    with shelve.open(path.dirname(__file__) + '/../users_appointment') as db:
        if chat_id in db:
            return True
        else:
            return None


if __name__ == '__main__':
    print(get_appointment_data('2155455'))
