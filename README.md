# aither-exists-check
Lightweight script that checks your Radarr+sonarr media libraries against Aither's uploaded movie torrents

## Setup / Run
1. Firstly, install Python if not already on your system (in cmd, `python -V`). Version shouldn't strictly matter, unless it is way back at version 2.x.x (latest is 3.11)
2. If necessary, `pip install requests`
3. Fill in your API keys for Aither, Radarr & Sonarr in a file named `apiKey.py` (copy `apiKeySample.py` for reference)
4. Run with `python main.py` for Radarr or `python mainsonarr.py` for Sonarr.

**Notice: running on Linux may need you to use `python3` rather than just `python`**
