import json
from os import path
import shelve


# TODO: переделать все функции под try

def get_clinics():
    with open(path.dirname(__file__) + '/../clinics_db.json', 'r') as db:
        return json.load(db)


def add_clinic(name, latitude, longitude):
    clinics = get_clinics()
    clinics[name] = {
        'location': [latitude, longitude],
        'dates_available': {}
    }
    with open(path.dirname(__file__) + '/../clinics_db.json', 'w') as db:
        json.dump(clinics, db, ensure_ascii=False, indent=4)


def delete_clinic(name):
    clinics = get_clinics()
    del clinics[name]
    with open(path.dirname(__file__) + '/../clinics_db.json', 'w') as db:
        json.dump(clinics, db, ensure_ascii=False, indent=4)


def add_datetime(clinic, date, time):
    clinics = get_clinics()
    if date not in clinics[clinic]['dates_available']:
        clinics[clinic]['dates_available'][date] = [time]
    elif time not in clinics[clinic]['dates_available'][date]:
        clinics[clinic]['dates_available'][date].append(time)
    else:
        return 'Такое время уже доступно в указанную дату'
    with open(path.dirname(__file__) + '/../clinics_db.json', 'w') as db:
        json.dump(clinics, db, ensure_ascii=False, indent=4)
        return 'Дата и время успешно добавлены'


def delete_date(clinic, date):
    clinics = get_clinics()
    del clinics[clinic]['dates_available'][date]
    with open(path.dirname(__file__) + '/../clinics_db.json', 'w') as db:
        json.dump(clinics, db, ensure_ascii=False, indent=4)


def delete_time(clinic, date, time):
    clinics = get_clinics()
    index = clinics[clinic]['dates_available'][date].index(time)
    del clinics[clinic]['dates_available'][date][index]
    with open(path.dirname(__file__) + '/../clinics_db.json', 'w') as db:
        json.dump(clinics, db, ensure_ascii=False, indent=4)


def get_schedule():
    schedule = ''
    clinics = get_clinics()
    for clinic in clinics:
        schedule = schedule + '<b>' + clinic + '</b>' + ':\n'
        for date in clinics[clinic]['dates_available']:
            schedule = schedule + '<i>' + date + '</i>' + ': ' \
                       + ', '.join(clinics[clinic]['dates_available'][date]) + '\n'
    return schedule


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
    delete_time("ДЕНТиК (ул. Тургенева, 23)", "20/10/2021", "10.30")
