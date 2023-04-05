import apiKey
import requests
import time

# Configurable constants
RADARR_URL = "http://RADARR_URL:RADARR_PORT/api/v3/movie"
AITHER_URL = "https://aither.cc"
NOT_FOUND_FILE = "not_found.txt"
SLEEP_TIME = 0.5

# LOGIC CONSTANT - DO NOT TWEAK !!!
RESOLUTION_MAP = {
    "4320": 1,
    "2160": 2,
    "1080": 3,
    "1080p": 4,
    "720": 5,
    "576": 6,
    "576p": 7,
    "480": 8,
    "480p": 9,
}

# Function to get all movies from Radarr
def get_all_movies():
    response = requests.get(RADARR_URL, headers={"X-Api-Key": apiKey.radarr_key})
    movies = response.json()
    return movies


# Function to search for a movie in Aither using its TMDB ID + resolution if found
def search_movie(tmdb_id, resolution=None):
    if resolution is not None:
        url = f"{AITHER_URL}/api/torrents/filter?tmdbId={tmdb_id}&resolutions[0]={resolution}&api_token={apiKey.aither_key}"
    else:
        url = f"{AITHER_URL}/api/torrents/filter?tmdbId={tmdb_id}&api_token={apiKey.aither_key}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception if the request failed
    torrents = response.json()["data"]
    return torrents


# Main function to loop through movies and search for them in Aither
def main():
    # Get all movies from Radarr
    movies = get_all_movies()

    # Open a file for writing "Not found" messages
    not_found_file = open(NOT_FOUND_FILE, "w")

    # Loop through each movie and search for it in Aither using its TMDB ID
    for movie in movies:
        title = movie["title"]
        tmdb_id = movie["tmdbId"]
        movie_resolution = movie["movieFile"]["quality"]["quality"]["resolution"]
        aither_resolution = RESOLUTION_MAP.get(str(movie_resolution))
        print(f"Checking {title}... ", end="")
        try:
            torrents = search_movie(tmdb_id, aither_resolution)
        except Exception as e:
            print(f"Error: {str(e)}")
            not_found_file.write(f"{title} - Error: {str(e)}\n")
        else:
            if len(torrents) == 0:
                print(
                    f"Not found in local copy resolution of {movie_resolution} on AITHER"
                )
                # Write the "Not found" message to the file
                not_found_file.write(
                    f"Not found in local copy resolution of {movie_resolution} on AITHER\n"
                )
            else:
                print(f"Found in local copy resolution of {movie_resolution} on AITHER")
                time.sleep(SLEEP_TIME)

    # Close the file
    not_found_file.close()


if __name__ == "__main__":
    main()
