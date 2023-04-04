import apiKey
import requests
import time

sonarr_url = "http://SONARR_URL:SONARR_PORT/api/series"
headers = {"X-Api-Key": apiKey.sonarr_key}

aither_url = "https://aither.cc"

# Function to get all movies from Radarr
def get_all_shows():
    response = requests.get(f"{sonarr_url}", headers=headers)
    movies = response.json()
    return movies


# Function to search for a movie in UNIT3D using its TMDB ID
def search_show(tvdb_id):
    response = requests.get(
        f"{aither_url}/api/torrents/filter?tvdbId={tvdb_id}&api_token={apiKey.aither_key}"
    )
    torrents = response.json()["data"]
    return torrents


# Get all movies from Radarr
shows = get_all_shows()

# Open a file for writing "Not found" messages
not_found_file = open("not_found_sonarr.txt", "w")

# Loop through each movie and search for it in UNIT3D using its TMDB ID
for show in shows:
    title = show["title"]
    tvdb_id = show["tvdbId"]
    print(f"Checking {title}... ", end="")
    torrents = search_show(tvdb_id=tvdb_id)
    if len(torrents) == 0:
        print("Not found in Aither")
        # Write the "Not found" message to the file
        not_found_file.write(f"{title} not found in AITHER\n")
        time.sleep(0.5)
    else:
        print("Found in AITHER")
        time.sleep(0.5)

# Close the file
not_found_file.close()
