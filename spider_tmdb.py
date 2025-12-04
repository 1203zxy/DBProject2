import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import csv

api_key = "314f9a1b19d1036a6fd958c9635bec01"
base_url = "https://api.themoviedb.org/3"


def create_session():
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session


session = create_session()


def get_movies_by_year(year, max_movies=1000):
    movies = []
    page = 1
    total_fetched = 0
    while total_fetched < max_movies:
        params = {
            "api_key": api_key,
            "primary_release_year": year,
            "sort_by": "popularity.desc",
            "page": page
        }
        try:
            resp = session.get(f"{base_url}/discover/movie", params=params)
            resp.raise_for_status()
            data = resp.json()
            movies.extend(data['results'])
            total_fetched += len(data['results'])
            if page >= data['total_pages'] or total_fetched >= max_movies:
                break
            page += 1
            time.sleep(0.3)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {year}, page {page}: {e}")
            break
    return movies[:max_movies]


def get_movie_details(movie_id):
    params = {"api_key": api_key}
    try:
        resp = session.get(f"{base_url}/movie/{movie_id}", params=params)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie details for ID {movie_id}: {e}")
        return None


def get_movie_credits(movie_id):
    params = {"api_key": api_key}
    try:
        resp = session.get(f"{base_url}/movie/{movie_id}/credits", params=params)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching credits for ID {movie_id}: {e}")
        return None


def get_person_details(person_id):
    params = {"api_key": api_key}
    try:
        resp = session.get(f"{base_url}/person/{person_id}", params=params)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching person details for ID {person_id}: {e}")
        return None


gender_map = {0: 'Unknown', 1: 'Female', 2: 'Male', 3: 'Non-binary'}

all_data = []
for year in range(2018, 2026):
    print(f"Fetching movies for {year}...")
    movies = get_movies_by_year(year)
    for movie in movies:
        movie_id = movie['id']
        details = get_movie_details(movie_id)
        if not details:
            continue
        credits = get_movie_credits(movie_id)
        if not credits:
            continue

        movie_name = details.get('title', '')
        release_year = year
        duration = details.get('runtime', '')
        countries = details.get('production_countries', [])
        country = countries[0]['name'] if countries else ''

        directors = [c for c in credits.get('crew', []) if c['job'] == 'Director']
        director_info = {'gender': '', 'lastname': '', 'firstname': '', 'birthyear': '', 'deathyear': ''}
        if directors:
            director = directors[0]
            director_details = get_person_details(director['id'])
            if director_details:
                director_name = director_details.get('name', '')
                name_parts = director_name.split(' ')
                director_info['firstname'] = name_parts[0]
                director_info['lastname'] = ' '.join(name_parts[1:])
                director_info['gender'] = gender_map.get(director_details.get('gender', 0), 'Unknown')
                director_info['birthyear'] = director_details.get('birthday', '')
                director_info['deathyear'] = director_details.get('deathday', '')

        cast = credits.get('cast', [])
        actor_info = []
        for i in range(min(3, len(cast))):
            actor = cast[i]
            actor_details = get_person_details(actor['id'])
            actor_data = {'firstname': '', 'lastname': '', 'gender': '', 'birthyear': '', 'deathyear': ''}
            if actor_details:
                actor_name = actor_details.get('name', '')
                name_parts = actor_name.split(' ')
                actor_data['firstname'] = name_parts[0]
                actor_data['lastname'] = ' '.join(name_parts[1:])
                actor_data['gender'] = gender_map.get(actor_details.get('gender', 0), 'Unknown')
                actor_data['birthyear'] = actor_details.get('birthday', '')
                actor_data['deathyear'] = actor_details.get('deathday', '')
            actor_info.append(actor_data)

        while len(actor_info) < 3:
            actor_info.append({'firstname': '', 'lastname': '', 'gender': '', 'birthyear': '', 'deathyear': ''})

        all_data.append([
            movie_name, country, release_year, duration,
            director_info['gender'], director_info['lastname'], director_info['firstname'],
            director_info['birthyear'], director_info['deathyear'],
            actor_info[0]['firstname'], actor_info[0]['lastname'], actor_info[0]['gender'],
            actor_info[0]['birthyear'], actor_info[0]['deathyear'],
            actor_info[1]['firstname'] if len(actor_info) > 1 else '',
            actor_info[1]['lastname'] if len(actor_info) > 1 else '',
            actor_info[1]['gender'] if len(actor_info) > 1 else '',
            actor_info[1]['birthyear'] if len(actor_info) > 1 else '',
            actor_info[1]['deathyear'] if len(actor_info) > 1 else '',
            actor_info[2]['firstname'] if len(actor_info) > 2 else '',
            actor_info[2]['lastname'] if len(actor_info) > 2 else '',
            actor_info[2]['gender'] if len(actor_info) > 2 else '',
            actor_info[2]['birthyear'] if len(actor_info) > 2 else '',
            actor_info[2]['deathyear'] if len(actor_info) > 2 else ''
        ])
        time.sleep(0.3)

csv_file = 'csv/movies_2018_2025.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'movie_name', 'country', 'release_year', 'duration',
        'director_gender', 'director_lastname', 'director_firstname', 'director_birthyear', 'director_deathyear',
        'actor1_firstname', 'actor1_lastname', 'actor1_gender', 'actor1_birthyear', 'actor1_deathyear',
        'actor2_firstname', 'actor2_lastname', 'actor2_gender', 'actor2_birthyear', 'actor2_deathyear',
        'actor3_firstname', 'actor3_lastname', 'actor3_gender', 'actor3_birthyear', 'actor3_deathyear'
    ])
    writer.writerows(all_data)

print(f"Total movies: {len(all_data)}")
