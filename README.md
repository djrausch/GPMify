# GPMify
A Python script for converting Google Play Music Playlists to Spotify
## Setup
There are some require paramerters you must configure inside of config.py. An example config is provided at config.py.example
### Google Credentials
Enter you gmail and password in your config.py file.
### Spotify App Credentials
You will need Spotify App Credentials. You can get those at [My Applications](https://developer.spotify.com/my-applications/#!/applications)

You can provide anything for the callback url. This will simply be used to get the token. If you can't think of a callback url, feel free to use https://djrausch.github.io/GPMify/

## Usage
Once you have setup your config.py, simply run from your terminal.
> python3 gpmify.py

## Libraries
This script is made possible with the following libraries
* [Spotipy](https://github.com/plamere/spotipy)
* [gmusicapi](https://github.com/simon-weber/gmusicapi)