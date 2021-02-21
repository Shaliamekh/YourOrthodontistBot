import json
from os import path


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


if __name__ == '__main__':
    print(add_datetime('ДЕНТиК (ул. Тургенева, 23)', '05/08/2018', '10.50'))
