import asyncio
from asyncio import run
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

# async def insert_database(list):
#     objects = []
#     async with Session() as session:
#         session.add_all()

async def main():
    await init_orm()
    http_session = aiohttp.ClientSession()
    MAX_WORKERS = 10
    for persons_chunk in chunked(range(1, 1001), MAX_WORKERS):
        corolist = [get_persons(http_session, person_id) for person_id in persons_chunk]
        results = await asyncio.gather(*corolist)
        for person in results:
            person['films'] = await get_arr_links(http_session=http_session, film_links=person['films'], type='title')
            person['homeworld'] = await get_homeworld(http_session=http_session, link=person['homeworld'])
            person['vehicles'] = await get_arr_links(http_session=http_session, film_links=person['vehicles'], type='name')
            person['starships'] = await get_arr_links(http_session=http_session, film_links=person['starships'], type='name')
            person.pop(['created', 'edited', 'url'])
            print(person)

    await http_session.close()
asyncio.run(main())