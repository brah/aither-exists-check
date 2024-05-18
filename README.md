# Aither Exists Check

A lightweight script to check your Radarr and Sonarr media libraries against Aither's uploaded movie torrents.

## Setup / Run

### Prerequisites

- Python 3.x installed on your system.
- Radarr and (or) Sonarr installed and configured.

### Installation

1. Clone or download this repository.
2. Navigate to the project directory.
3. Install the required Python packages using `pip`:

   ```sh
   pip install requests
   ```

### Configuration

1. Create a file named `apiKey.py` in the project directory with the following contents - refer to apiKeySample.py:

   ```python
   aither_key = ""
   radarr_key = ""
   sonarr_key = ""
   radarr_url = ""
   sonarr_url = ""
   ```

2. The first time you run the script, you will be prompted to enter your API keys and URLs for Aither, Radarr, and Sonarr. The script will save these values to `apiKey.py` for future use.

### Usage

To run the script, use the following commands:

- To check the Radarr library:

  ```sh
  python main.py --radarr
  ```

- To check the Sonarr library:

  ```sh
  python main.py --sonarr
  ```

- To check both libraries (default if no arguments are provided):

  ```sh
  python main.py
  ```

### Notes

- Ensure the Radarr URL is the base URL (e.g., `http://media.server:7878`) and the script will append `/api/v3/movie`.
- Ensure the Sonarr URL is the base URL (e.g., `http://media.server:8989`) and the script will append `/api/v3/series`.
- The script respects Aither's rate limits with a delay of 2 seconds between requests.

## Output

The script generates two files to record movies and shows not found in Aither:

- `not_found_radarr.txt`: Records movies from Radarr not found in Aither.
- `not_found_sonarr.txt`: Records shows from Sonarr not found in Aither.

## Logging

The script logs detailed messages to `script.log` and provides concise output on the console.
