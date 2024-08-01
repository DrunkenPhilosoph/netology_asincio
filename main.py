import asyncio
import aiohttp
from more_itertools import chunked
from models import init_orm, StarWarsPerson, Session


async def get_persons(http_session ,person_id):
    response = await http_session.get(f'https://swapi.dev/api/people/{person_id}/')
    json = await response.json()
    return json

async def get_homeworld(http_session, link):
    response = await http_session.get(link)
    json = await response.json()
    return json['name']

async def get_arr_links(http_session, film_links, type):
    tasks = [
        (await http_session.get(link)).json()
        for link in film_links
    ]
    responses = await asyncio.gather(*tasks)
    name = [response[type] for response in responses]
    return name

async def insert_database(persons):
    async with Session() as session:
        async with session.begin():
            for person_data in persons:
                films_str = ', '.join(person_data.get('films', []))
                species_str = ', '.join(person_data.get('species', []))
                vehicles_str = ', '.join(person_data.get('vehicles', []))
                starships_str = ', '.join(person_data.get('starships', []))

                person = StarWarsPerson(
                    birth_year=person_data['birth_year'],
                    eye_color=person_data['eye_color'],
                    films=films_str,
                    gender=person_data['gender'],
                    hair_color=person_data['hair_color'],
                    height=person_data['height'],
                    homeworld=person_data['homeworld'],
                    mass=person_data['mass'],
                    name=person_data['name'],
                    skin_color=person_data['skin_color'],
                    species=species_str,
                    starships=starships_str,
                    vehicles=vehicles_str,
                )
                session.add(person)
        await session.commit()


async def main():
    await init_orm()
    http_session = aiohttp.ClientSession()
    MAX_WORKERS = 5

    for persons_chunk in chunked(range(1, 100), MAX_WORKERS):
        corolist = [get_persons(http_session, person_id) for person_id in persons_chunk]
        results = await asyncio.gather(*corolist)
        persons_to_insert = []
        for person in results:
            print(person)
            if 'detail' not in person:
                print(1)
                person['films'] = await get_arr_links(http_session=http_session, film_links=person['films'], type='title')
                person['species'] = await get_arr_links(http_session=http_session, film_links=person['species'], type='name')
                person['homeworld'] = await get_homeworld(http_session=http_session, link=person['homeworld'])
                person['vehicles'] = await get_arr_links(http_session=http_session, film_links=person['vehicles'],
                                                     type='name')
                person['starships'] = await get_arr_links(http_session=http_session, film_links=person['starships'],
                                                          type='name')
                persons_to_insert.append(person)
            else:
                continue

        await insert_database(persons_to_insert)

    await http_session.close()
asyncio.run(main())