import json
from os import path
import shelve
from datetime import datetime


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


def get_appointment_data(chat_id):
    with shelve.open(path.dirname(__file__) + '/../users_appointment') as db:
        return db.get(str(chat_id))


def delete_appointment(chat_id):
    with shelve.open(path.dirname(__file__) + '/../users_appointment') as db:
        del db[str(chat_id)]


def appointment_made(chat_id):
    with shelve.open(path.dirname(__file__) + '/../users_appointment') as db:
        if chat_id in db:
            return True
        else:
            return None


# проверяем, есть ли доступное время в клинике
def check_availability(clinic):
    clinics = get_clinics()
    dates = [i for i in clinics[clinic]['dates_available']]
    times = [clinics[clinic]['dates_available'][date] for date in dates]
    res = [len(i) != 0 for i in times]
    return any(res)


def visitors_list(fname, lname, id):
    with open(path.dirname(__file__) + '/../visitors_list.txt', 'a') as file:
        file.write(f'{datetime.now()} - {fname} {lname} - {id}\n')


# Удаляем все прошедшие даты
def delete_expired_dates():
    clinics = get_clinics()
    for clinic in clinics:
        for date in clinics[clinic]['dates_available']:
            if datetime.strptime(date, '%d/%m/%Y').date() < datetime.now().date():
                delete_date(clinic, date)

if __name__ == '__main__':
    delete_appointment(1157354030)
