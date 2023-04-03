import apiKey
import requests
import time

radarr_url = "http://RADARR_URL:RADARR_PORT/api/v3/movie"
headers = {"X-Api-Key": apiKey.radarr_key}

response = requests.get(radarr_url, headers=headers)

aither_url = "https://aither.cc"

# Function to get all movies from Radarr
def get_all_movies():
    response = requests.get(f"{radarr_url}", headers=headers)
    movies = response.json()
    return movies


# Function to search for a movie in UNIT3D using its TMDB ID
def search_movie(tmdb_id):
    response = requests.get(
        f"{aither_url}/api/torrents/filter?tmdbId={tmdb_id}&api_token={apiKey.aither_key}"
    )
    torrents = response.json()["data"]
    return torrents


# Get all movies from Radarr
movies = get_all_movies()

# Open a file for writing "Not found" messages
not_found_file = open("not_found.txt", "w")

# Loop through each movie and search for it in UNIT3D using its TMDB ID
for movie in movies:
    title = movie["title"]
    tmdb_id = movie["tmdbId"]
    print(f"Checking {title}... ", end="")
    torrents = search_movie(tmdb_id)
    if len(torrents) == 0:
        print("Not found in UNIT3D")
        # Write the "Not found" message to the file
        not_found_file.write(f"{title} not found in AITHER\n")
        time.sleep(0.5)
    else:
        print("Found in AITHER")
        time.sleep(0.5)

# Close the file
not_found_file.close()
