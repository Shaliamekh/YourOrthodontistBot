import asyncio
import asyncpg
from datetime import datetime
import config


class DBHelper:

    async def __aenter__(self):
        self.connection = await asyncpg.connect(host=config.pg_host, port=config.pg_port, user=config.pg_user,
                                                password=config.pg_password, database=config.pg_database)
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connection.close()


async def get_clinics_with_appointments_available():
    try:
        async with DBHelper() as conn:
            rows = await conn.fetch('''
                                    SELECT DISTINCT name FROM orthodontist.clinic c JOIN 
                                                     orthodontist.appointment a on c.id = a.clinic_id LEFT JOIN
                                                     orthodontist.appointment_made am on a.id = am.appointment_id
                                    WHERE date>now() AND user_id is Null
                                    ORDER BY name
                                    ''')
        clinics = []
        for row in rows:
            clinics.append(row['name'])
        return clinics
    except Exception:
        return None


async def get_all_clinics():
    try:
        async with DBHelper() as conn:
            rows = await conn.fetch('SELECT name FROM orthodontist.clinic ORDER BY name')
        clinics = []
        for row in rows:
            clinics.append(row['name'])
        return clinics
    except Exception:
        return None


async def get_location_by_clinic(clinic):
    try:
        async with DBHelper() as conn:
            row = await conn.fetchrow('SELECT latitude, longitude FROM orthodontist.clinic WHERE name=$1',
                                      clinic)
        return [str(row['latitude']), str(row['longitude'])]
    except Exception as e:
        return e

async def add_clinic(name, latitude, longitude):
    try:
        async with DBHelper() as conn:
            await conn.execute('''
                               INSERT INTO orthodontist.clinic (name, latitude, longitude) VALUES ($1, $2, $3)
                               ''', name, latitude, longitude)
            row = await conn.fetchrow('SELECT * FROM orthodontist.clinic WHERE name=$1', name)
        return [i for i in row.values()]
    except Exception:
        return None


async def delete_clinic(name):
    try:
        async with DBHelper() as conn:
            await conn.execute('DELETE FROM orthodontist.clinic WHERE name=$1', name)
        return name
    except Exception:
        return None


async def get_dates_available_by_clinic(clinic):
    try:
        async with DBHelper() as conn:
            rows = await conn.fetch('''
                                    SELECT DISTINCT date
                                    FROM orthodontist.clinic c JOIN 
                                         orthodontist.appointment a on c.id = a.clinic_id LEFT JOIN
                                         orthodontist.appointment_made am on a.id = am.appointment_id
                                    WHERE date>now() AND user_id is Null AND name = $1
                                    ORDER BY date
                                    ''', clinic)
        dates = []
        for row in rows:
            dates.append(row['date'].strftime('%d/%m/%Y'))
        return dates
    except Exception:
        return None


async def get_time_available_by_clinic_date(clinic, date):
    try:
        async with DBHelper() as conn:
            rows = await conn.fetch('''
                                    SELECT time 
                                    FROM orthodontist.clinic c JOIN 
                                         orthodontist.appointment a on c.id = a.clinic_id LEFT JOIN
                                         orthodontist.appointment_made am on a.id = am.appointment_id
                                    WHERE date>now() AND user_id is Null AND name = $1 AND date = $2
                                    ''', clinic, datetime.strptime(date, '%d/%m/%Y'))
        timetable = []
        for row in rows:
            timetable.append(row['time'].strftime('%H:%M'))
        return timetable
    except Exception:
        return None


async def add_appointment_available(clinic, date, time):
    try:
        async with DBHelper() as conn:
            await conn.execute('''
                               INSERT INTO orthodontist.appointment (clinic_id, date, time)
                               SELECT orthodontist.clinic.id, $2, $3 FROM orthodontist.clinic WHERE name=$1
                               ''', clinic, datetime.strptime(date, '%d/%m/%Y'), datetime.strptime(time, '%H:%M'))
            row = await conn.fetchrow('SELECT * FROM orthodontist.appointment WHERE date=$1 AND time=$2',
                                      datetime.strptime(date, '%d/%m/%Y'), datetime.strptime(time, '%H:%M'))
        return row
    except Exception:
        return None


async def delete_appointment_available(clinic, date, time):
    try:
        async with DBHelper() as conn:
            await conn.execute('DELETE FROM orthodontist.appointment WHERE date=$1 AND time=$2',
                               datetime.strptime(date, '%d/%m/%Y'), datetime.strptime(time, '%H:%M'))
        return clinic, date, time
    except Exception:
        return None


async def delete_appointments_available_by_date(clinic, date):
    try:
        async with DBHelper() as conn:
            await conn.execute('''
                               DELETE FROM orthodontist.appointment
                               WHERE clinic_id=(SELECT id FROM orthodontist.clinic WHERE name=$1) AND date=$2
                               ''', clinic, datetime.strptime(date, '%d/%m/%Y'))
        return clinic, date
    except Exception:
        return None


async def get_all_appointments_available():
    try:
        schedule = ''
        clinics = await get_all_clinics()
        async with DBHelper() as conn:
            for clinic in clinics:
                schedule += '<b>' + clinic + ':</b>\n'
                rows_date = await conn.fetch('''
                                        SELECT DISTINCT date
                                        FROM orthodontist.clinic c JOIN 
                                             orthodontist.appointment a on c.id = a.clinic_id LEFT JOIN
                                             orthodontist.appointment_made am on a.id = am.appointment_id
                                        WHERE date>now() AND user_id is Null AND name = $1
                                        ''', clinic)
                for date in rows_date:
                    schedule += '<i>' + date['date'].strftime('%d/%m/%Y') + '</i>: '
                    # print(type(date['date']))
                    rows_time = await conn.fetch('''
                                            SELECT time
                                            FROM orthodontist.clinic c JOIN
                                                 orthodontist.appointment a on c.id = a.clinic_id LEFT JOIN
                                                 orthodontist.appointment_made am on a.id = am.appointment_id
                                            WHERE date>now() AND user_id is Null AND name = $1 AND date = $2
                                            ''', clinic, date['date'])
                    for time in rows_time:
                        schedule += time['time'].strftime('%H:%M') + ', '
                    schedule += '\n'
        return schedule
    except Exception:
        return None


async def make_appointment(date, time, user_id, name, phone_number, problem_description):
    try:
        async with DBHelper() as conn:
            await conn.execute('''
                               INSERT INTO orthodontist.patient (user_id, name, phone_number)
                               VALUES ($1, $2, $3)
                               ON CONFLICT (user_id) DO UPDATE SET name = $2, phone_number = $3
                               ''', user_id, name, phone_number)
            await conn.execute('''
                               INSERT INTO orthodontist.appointment_made 
                               (appointment_id, user_id, problem_description)
                               SELECT id, $3, $4 FROM orthodontist.appointment WHERE date=$1 AND time=$2
                               ''', datetime.strptime(date, '%d/%m/%Y'), datetime.strptime(time, '%H:%M'),
                               user_id, problem_description)
            r = await conn.execute('SELECT * FROM orthodontist.appointment_made WHERE user_id=$1', user_id)
        return r
    except Exception:
        return None


async def get_appointment_data(user_id):
    try:
        async with DBHelper() as conn:
            row = await conn.fetchrow('''
                                SELECT c.name as clinic, date, time, p.name, phone_number, problem_description       
                                FROM orthodontist.clinic c JOIN
                                     orthodontist.appointment a ON c.id = a.clinic_id JOIN
                                     orthodontist.appointment_made am ON a.id = am.appointment_id JOIN 
                                     orthodontist.patient p ON am.user_id = p.user_id
                                WHERE date>now() AND am.user_id = $1
                                ''', user_id)
        return row
    except Exception:
        return None


async def delete_appointment(user_id):
    try:
        async with DBHelper() as conn:
            data = await get_appointment_data(user_id)
            await conn.execute('''
                               DELETE FROM orthodontist.appointment_made am
                                      USING orthodontist.appointment a
                               WHERE am.appointment_id = a.id and date>now() AND am.user_id=$1
                               ''', user_id)
        return data
    except Exception:
        return None


if __name__ == '__main__':
    pass

    # print(asyncio.run(get_clinics_with_appointments_available()))
    # print(asyncio.run(get_all_clinics()))
    # print(asyncio.run(add_clinic('У Ромы', 24.5645665, 54.656262)))
    # print(asyncio.run(delete_clinic('У Ромы')))
    # print(asyncio.run(add_appointment_available('Имплант (ул. 40 лет победы, 178/1)', '15/03/2021', '11:00')))
    print(asyncio.run(get_dates_available_by_clinic('Имплант (ул. 40 лет победы, 178/1)')))
    # print(asyncio.run(get_time_available_by_clinic_date('Имплант (ул. 40 лет победы, 178/1)', '16/03/2021')))
    # # print(asyncio.run(add_appointment_available('ДЕНТиК (ул. Тургенева, 23)', '27/01/2021', '11:30')))
    # # print(asyncio.run(delete_appointments_available_by_date('ДЕНТиК (ул. Тургенева, 23)', '27/01/2021')))
    # # print((asyncio.run(delete_appointment_available('ДЕНТиК (ул. Тургенева, 23)', '27/01/2021', '11:30'))))
    # print(asyncio.run(get_all_appointments_available()))
    # # print(asyncio.run(make_appointment('27/04/2021', '10:00', 123458, 'Ольга', '++75213648925', 'Болииит')))
    # print(asyncio.run(make_appointment('13/03/2021', '10:30', 12545862,
    #                                    'Пимен Панчанка', '+72596246', 'Болит зубик')))
    # print(asyncio.run(get_appointment_data(1157354030)))
    # print(asyncio.run(delete_appointment(123459)))
    # print(asyncio.run(get_location_by_clinic('ДЕНТиК (ул. Тургенева, 23)')))
