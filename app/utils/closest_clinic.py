import asyncio
import aiohttp
from app.utils.db import get_clinics


async def locator(session, user_location, clinic):
    url = f'https://graphhopper.com/api/1/route?point={user_location}&point={clinic}' \
          f'&vehicle=car&locale=de&calc_points=false&key=cce8f5c4-5743-4402-bb09-07408bec0d55'
    async with session.get(url) as response:
        res = await response.json()
        return round(res['paths'][0]['time'] / 60000)


async def closest_clinic(user_location, clinics):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for clinic in clinics:
            clinic_location = ','.join(list(map(str, clinics[clinic]["location"])))
            resp = locator(session, user_location, clinic_location)
            tasks.append(resp)
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        router = dict(zip(clinics.keys(), responses))
        time = min(*router.values())
        clos_clinic = [key for key, value in router.items() if value == time]
        return clos_clinic[0], time


if __name__ == '__main__':
    print(asyncio.run(closest_clinic('23.11454590665909,113.31684676463547', get_clinics())))
