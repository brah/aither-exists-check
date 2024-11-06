import apiKey
import requests
import time
import argparse
from guessit import guessit
import logging

# Just to sameline the logs while logging to file also
class NoNewlineStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            if record.levelno == logging.INFO and msg.endswith("... "):
                stream.write(msg)
            else:
                stream.write(msg + "\n")
            self.flush()
        except Exception:
            self.handleError(record)


# Configurable constants
AITHER_URL = "https://aither.cc"
RADARR_API_SUFFIX = "/api/v3/movie"
SONARR_API_SUFFIX = "/api/v3/series"
NOT_FOUND_FILE_RADARR = "not_found_radarr.txt"
NOT_FOUND_FILE_SONARR = "not_found_sonarr.txt"
INITIAL_SLEEP_TIME = 10
MAX_SLEEP_TIME = 60

# LOGIC CONSTANT - DO NOT TWEAK !!!
# changing this may break resolution mapping for dvd in search_movie
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

CATEGORY_MAP = {
    "movie": 1,
    "tv": 2
}

TYPE_MAP = {
    "FULL DISC": 1,
    "REMUX": 2,
    "ENCODE": 3,
    "WEB-DL": 4,
    "WEBRIP": 5,
    "HDTV": 6,
    "OTHER": 7,
    "MOVIE PACK": 10,
}

BANNED_GROUPS = ['4K4U', 'AROMA', 'd3g', 'edge2020', 'EMBER', 'EVO', 'FGT', 'FreetheFish', 'Hi10', 'HiQVE', 'ION10', 'iVy', 'Judas', 'LAMA', 'MeGusta', 'nikt0', 'OEPlus', 'OFT', 'OsC', 'PYC',
                              'QxR', 'Ralphy', 'RARBG', 'RetroPeeps', 'SAMPA', 'Sicario', 'Silence', 'SkipTT', 'SPDVD', 'STUTTERSHIT', 'SWTYBLZ', 'TAoE', 'TGx', 'Tigole', 'TSP', 'TSPxL', 'VXT', 'Weasley[HONE]',
                              'Will1869', 'x0r', 'YIFY']

# Setup logging
logger = logging.getLogger("customLogger")
logger.setLevel(logging.INFO)

# Console handler with a simpler format
console_handler = NoNewlineStreamHandler()
console_formatter = logging.Formatter("%(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File handler with detailed format
file_handler = logging.FileHandler("script.log")
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


# Setup function to prompt user for missing API keys and URLs if critical for the selected mode(s)
def setup(radarr_needed, sonarr_needed):
    missing = []

    if not apiKey.aither_key:
        missing.append("Aither API key")
        apiKey.aither_key = input("Enter your Aither API key: ")

    if radarr_needed:
        if not apiKey.radarr_key:
            missing.append("Radarr API key")
            apiKey.radarr_key = input("Enter your Radarr API key: ")
        if not apiKey.radarr_url:
            missing.append("Radarr URL")
            apiKey.radarr_url = input(
                "Enter your Radarr URL (e.g., http://RADARR_URL:RADARR_PORT): "
            )

    if sonarr_needed:
        if not apiKey.sonarr_key:
            missing.append("Sonarr API key")
            apiKey.sonarr_key = input("Enter your Sonarr API key: ")
        if not apiKey.sonarr_url:
            missing.append("Sonarr URL")
            apiKey.sonarr_url = input(
                "Enter your Sonarr URL (e.g., http://SONARR_URL:SONARR_PORT): "
            )

    if missing:
        with open("apiKey.py", "w") as f:
            f.write(f'aither_key = "{apiKey.aither_key}"\n')
            f.write(f'radarr_key = "{apiKey.radarr_key}"\n')
            f.write(f'sonarr_key = "{apiKey.sonarr_key}"\n')
            f.write(f'radarr_url = "{apiKey.radarr_url}"\n')
            f.write(f'sonarr_url = "{apiKey.sonarr_url}"\n')

    # Alert the user about missing non-critical variables
    if not radarr_needed and (not apiKey.radarr_key or not apiKey.radarr_url):
        logger.warning(
            "Radarr API key or URL is missing. Radarr functionality will be limited."
        )
    if not sonarr_needed and (not apiKey.sonarr_key or not apiKey.sonarr_url):
        logger.warning(
            "Sonarr API key or URL is missing. Sonarr functionality will be limited."
        )


# Function to get all movies from Radarr
def get_all_movies(session):
    radarr_url = apiKey.radarr_url + RADARR_API_SUFFIX
    response = session.get(radarr_url, headers={"X-Api-Key": apiKey.radarr_key})
    response.raise_for_status()  # Ensure we handle request errors properly
    movies = response.json()
    return movies


# Function to get all shows from Sonarr
def get_all_shows(session):
    sonarr_url = apiKey.sonarr_url + SONARR_API_SUFFIX
    response = session.get(sonarr_url, headers={"X-Api-Key": apiKey.sonarr_key})
    response.raise_for_status()  # Ensure we handle request errors properly
    shows = response.json()
    return shows


# Function to search for a movie in Aither using its TMDB ID + resolution if found
def search_movie(session, movie, movie_resolution, movie_type):
    tmdb_id = movie["tmdbId"]

    # build the search url
    if movie_resolution is not None:
        url = f"{AITHER_URL}/api/torrents/filter?categories[0]={CATEGORY_MAP['movie']}&tmdbId={tmdb_id}&resolutions[0]={movie_resolution}&api_token={apiKey.aither_key}"
    else:
        url = f"{AITHER_URL}/api/torrents/filter?categories[0]={CATEGORY_MAP['movie']}&tmdbId={tmdb_id}&api_token={apiKey.aither_key}"

    if movie_type:
        url += f"&types[0]={movie_type}"
    
    while True:
        response = session.get(url)
        if response.status_code == 429:
            logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)
            sleep_time = min(sleep_time * 2, MAX_SLEEP_TIME)
        else:
            response.raise_for_status()  # Raise an exception if the request failed
            torrents = response.json()["data"]
            time.sleep(INITIAL_SLEEP_TIME)  # Respectful delay
            return torrents


# Function to search for a show in Aither using its TVDB ID
def search_show(session, tvdb_id, sleep_time=INITIAL_SLEEP_TIME):
    url = f"{AITHER_URL}/api/torrents/filter?tvdbId={tvdb_id}&api_token={apiKey.aither_key}"
    
    while True:
        response = session.get(url)
        if response.status_code == 429:
            logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)
            sleep_time = min(sleep_time * 2, MAX_SLEEP_TIME)
        else:
            response.raise_for_status()  # Raise an exception if the request failed
            torrents = response.json()["data"]
            time.sleep(INITIAL_SLEEP_TIME)  # Respectful delay
            return torrents

def get_movie_resolution(movie):
    # get resolution from radarr if missing try pull from media info
    try:
        movie_resolution = movie.get("movieFile").get("quality").get("quality").get("resolution")
        # if no resolution like with dvd quality. try parse from mediainfo instead
        if not movie_resolution:
            mediainfo_resolution = movie.get("movieFile").get("mediaInfo").get("resolution")
            width, height = mediainfo_resolution.split("x")
            movie_resolution = height
    except KeyError:
        movie_resolution = None
    return movie_resolution

def get_video_type(source, modifier):
    source = (source or '').lower()
    modifier = (modifier or '').lower()

    if source == 'bluray':
        if modifier == 'remux':
            return 'REMUX'
        elif modifier == 'full':
            return 'FULL DISC'
        else:
            return 'ENCODE'
    elif source in ['webdl', 'web-dl']:
        return 'WEB-DL'
    elif source in ['webrip', 'web-rip']:
        return 'WEBRIP'
    elif source == 'hdtv':
        return 'HDTV'
    else:
        return 'OTHER'


# Function to process each movie
def process_movie(session, movie, not_found_file):
    title = movie["title"]
    logger.info(f"Checking {title}... ")

    # verify radarr actually has a file entry if not skip check and save api call
    if not "movieFile" in movie:
        logger.info(
            f"[Skipped: local]. No file found in radarr for {title}"
        )
        return

    # skip check if group is banned.
    if "releaseGroup" in movie["movieFile"] and \
            movie["movieFile"]["releaseGroup"].casefold() in map(str.casefold, BANNED_GROUPS):
        logger.info(
            f"[Banned: local] group ({movie['movieFile']['releaseGroup']}) for {title}"
        )
        return

    try:
        quality_info = movie.get("movieFile").get("quality").get("quality")
        source = quality_info.get("source")
        modifier = quality_info.get("modifier")
        video_type = get_video_type(source, modifier)
        aither_type = TYPE_MAP.get(video_type.upper())
        movie_resolution = get_movie_resolution(movie)
        aither_resolution = RESOLUTION_MAP.get(str(movie_resolution))
        torrents = search_movie(session, movie, aither_resolution, aither_type)
    except Exception as e:
        if "429" in str(e):
            logger.warning(f"Rate limit exceeded while checking {title}. Will retry.")
        else:
            logger.error(f"Error: {str(e)}")
            not_found_file.write(f"{title} - Error: {str(e)}\n")
    else:
        if len(torrents) == 0:
            try:
                movie_file = movie["movieFile"]["path"]
                if movie_file:
                    logger.info(
                        f"[{movie_resolution} {video_type}] not found on AITHER"
                    )
                    not_found_file.write(f"{movie_file}\n")
                else:
                    logger.info(
                        f"[{movie_resolution} {video_type}] not found on AITHER (No media file)"
                    )
            except KeyError:
                logger.info(
                    f"[{movie_resolution} {video_type}] not found on AITHER (No media file)"
                )
        else:
            release_info = guessit(torrents[0].get("attributes").get("name"))
            if "release_group" in release_info \
                    and release_info["release_group"].casefold() in map(str.casefold, BANNED_GROUPS):
                logger.info(
                    f"[Trumpable: Banned] group for {title} [{movie_resolution} {video_type}] on AITHER"
                )
            else :
                logger.info(
                     f"[{movie_resolution} {video_type}] already exists on AITHER"
                )


# Function to process each show
def process_show(session, show, not_found_file):
    title = show["title"]
    tvdb_id = show["tvdbId"]
    logger.info(f"Checking {title}... ")
    try:
        torrents = search_show(session, tvdb_id)
    except Exception as e:
        if "429" in str(e):
            logger.warning(f"Rate limit exceeded while checking {title}. Will retry.")
        else:
            logger.error(f"Error: {str(e)}")
            not_found_file.write(f"{title} - Error: {str(e)}\n")
    else:
        if len(torrents) == 0:
            logger.info("Not found in Aither")
            not_found_file.write(f"{title} not found in AITHER\n")
        else:
            logger.info("Found in AITHER")


# Main function to handle both Radarr and Sonarr
def main():
    parser = argparse.ArgumentParser(
        description="Check Radarr or Sonarr library against Aither"
    )
    parser.add_argument("--radarr", action="store_true", help="Check Radarr library")
    parser.add_argument("--sonarr", action="store_true", help="Check Sonarr library")

    args = parser.parse_args()

    radarr_needed = args.radarr or (not args.sonarr and not args.radarr)
    sonarr_needed = args.sonarr or (not args.sonarr and not args.radarr)
    setup(
        radarr_needed=radarr_needed, sonarr_needed=sonarr_needed
    )  # Ensure API keys and URLs are set

    if not args.radarr and not args.sonarr:
        logger.info("No arguments specified. Running both Radarr and Sonarr checks.\n")

    try:
        with requests.Session() as session:
            if args.radarr or (not args.sonarr and not args.radarr):
                if apiKey.radarr_key and apiKey.radarr_url:
                    movies = get_all_movies(session)
                    with open(
                        NOT_FOUND_FILE_RADARR, "w", encoding="utf-8", buffering=1
                    ) as not_found_file:
                        for movie in movies:
                            process_movie(session, movie, not_found_file)
                else:
                    logger.warning(
                        "Skipping Radarr check: Radarr API key or URL is missing.\n"
                    )

            if args.sonarr or (not args.sonarr and not args.radarr):
                if apiKey.sonarr_key and apiKey.sonarr_url:
                    shows = get_all_shows(session)
                    with open(
                        NOT_FOUND_FILE_SONARR, "w", encoding="utf-8", buffering=1
                    ) as not_found_file:
                        for show in shows:
                            process_show(session, show, not_found_file)
                else:
                    logger.warning(
                        "Skipping Sonarr check: Sonarr API key or URL is missing.\n"
                    )
    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user. Exiting.\n")


if __name__ == "__main__":
    main()
