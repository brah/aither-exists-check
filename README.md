# Aither Exists Check

A lightweight Python script to check your Radarr and Sonarr media libraries against Aither's uploaded movie torrents.
As this script becomes more granular, and checking against Aither's resolutions, editions etc. it is more and more recommended you *double check* before proceeding to upload!

## Features

- Compare your Radarr and Sonarr libraries with Aither's torrent listings.
- Log missing movies and TV shows from your libraries, respecting banned groups, trumpables, etc.
- Respect Aither's API rate limits.

## Prerequisites

- Python 3.x installed on your system.
- Radarr and/or Sonarr configured and running.

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/brah/aither-exists-check.git
   ```

2. Navigate to the project directory:

   ```bash
   cd aither-exists-check
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

## Docker
1. Clone this repository:
   ```bash
   git clone https://github.com/brah/aither-exists-check.git
   ```
2. Navigate to the project directory:
   ```bash
   cd aither-exists-check
   ```
3. Build the docker image:
    ```bash
   docker build -t aither-exists-check:latest .
   ```
4. Run the docker image. Correct the paths below to map correct config file location and output directory.
```bash
docker run --user 1000:1000 --name aither-exists --rm -it \
-v ./config/apiKey.py:/aither-exists-check/apiKey.py \
-v ./output:/output/ \
aither-exists-check:latest --radarr
```

## Configuration

1. Create a file named `apiKey.py` in the project directory with the following contents - refer to apiKeySample.py:

   ```python
    aither_key = ""
    radarr_key = ""
    sonarr_key = ""
    radarr_url = ""
    sonarr_url = ""
   ```

2. The first time you run the script, you'll be prompted to input your API keys and URLs. The script saves these to `apiKey.py` for future use.

## Usage

To run the script, use one of the following commands:

- To check the Radarr library:

  ```bash
  python main.py --radarr
  ```

- To check the Sonarr library:

  ```bash
  python main.py --sonarr
  ```

- To check both libraries (default):

  ```bash
  python main.py
  ```

## Output

The script generates two output files:

- `not_found_radarr.txt`: Lists movies in Radarr not found in Aither.
- `not_found_sonarr.txt`: Lists shows in Sonarr not found in Aither.

## Logging

Detailed logs are stored in `script.log`, while concise output is displayed on the console.

## Contributors

Special thanks to those who have contributed:

- [@DefectiveDev](https://github.com/defectivedev)
