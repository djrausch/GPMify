import json

from gmusicapi import Mobileclient
import urllib.request
import urllib.parse
import os
import spotipy
import spotipy.util as util

from config import config


class GPMify:

    def __init__(self):
        self.api = Mobileclient()
        self.playlist_songs = []
        self.playlists = []
        self.library = []
        self.uris = []
        self.chunks = []
        self.username = ""
        self.token = ""

        self.human_readable_google_playlists = []
        self.selected_google_playlist_id = ""

        self.spotify_playlist_id = ""

    def google_login(self):
        self.api.login(config["google"]["email"], config["google"]["password"], Mobileclient.FROM_MAC_ADDRESS)

    def get_google_library(self):
        self.library = self.api.get_all_songs()

    def get_spotify_uri_for_songs_in_playlist(self):
        not_found = 0
        for playlist_song in self.playlist_songs:
            # print(playlist_song)
            artist = urllib.parse.quote_plus(playlist_song['artist'].replace(':', ' '))
            album = urllib.parse.quote_plus(
                playlist_song['album'].replace(':', ' ').replace('-', '').replace('Single', ''))
            title = urllib.parse.quote_plus(playlist_song['title'].replace(':', ' ').replace('feat.', ''))

            url = "https://api.spotify.com/v1/search?type=track&q={}%20{}".format(album, title)
            print(url)
            f = urllib.request.urlopen(url)
            content = f.read().decode(f.headers.get_content_charset())

            try:
                uri = (json.loads(content)['tracks']['items'][0]['uri'])
                self.uris.append(uri)
                self.chunks = [self.uris[x:x + 100] for x in range(0, len(self.uris), 100)]
            except IndexError:
                not_found += 1
        print("{} songs not found on Spotify".format(not_found))

    def add_track(self, track):
        self.playlist_songs.append(track)

    def get_google_playlists(self):
        self.playlists = self.api.get_all_playlists()

    def show_google_playlists(self):
        for playlist in self.playlists:
            playlist_to_add = {
                "id": playlist['id'],
                "name": playlist['name']
            }
            self.human_readable_google_playlists.append(playlist_to_add)
        for i, human_playlist in enumerate(self.human_readable_google_playlists):
            print("{}) {}".format(i, human_playlist['name']))

    def set_google_playlist_selection(self, selection_index):
        self.selected_google_playlist_id = self.human_readable_google_playlists[selection_index]['id']

    def set_spotify_playlist_id(self, playlist_id):
        self.spotify_playlist_id = playlist_id

    def get_google_playlist_songs(self):
        self.playlist_songs = []
        self.playlists = self.api.get_all_user_playlist_contents()
        for playlist in self.playlists:
            if playlist['id'] == self.selected_google_playlist_id:
                for track in playlist['tracks']:
                    try:
                        track_to_add = {
                            "title": track['track']['title'],
                            "artist": track['track']['artist'],
                            "album": track['track']['album']
                        }
                        self.add_track(track_to_add)
                    except KeyError:
                        for atrack in self.library:
                            if atrack['id'] == track['trackId']:
                                track_to_add = {
                                    "title": atrack['title'],
                                    "artist": atrack['artist'],
                                    "album": atrack['album']
                                }
                                self.add_track(track_to_add)
                                # print(playlist['tracks'])
                                # a2c45b14-fc8b-3950-8ac3-b2a81892fdd8

        print("{} songs in playlist".format(len(self.playlist_songs)))

    def setup_spotify_api(self):
        os.environ["SPOTIPY_CLIENT_ID"] = config["spotify"]["client_id"]
        os.environ["SPOTIPY_CLIENT_SECRET"] = config["spotify"]["client_secret"]
        os.environ["SPOTIPY_REDIRECT_URI"] = config["spotify"]["redirect_uri"]

        self.username = config["spotify"]["username"]

        scope = 'playlist-read-private playlist-modify-private playlist-modify-public'
        self.token = util.prompt_for_user_token(self.username, scope)

    def add_songs_to_spotify_playlist(self):
        if self.token:
            sp = spotipy.Spotify(auth=self.token)
            for chunk in self.chunks:
                sp.user_playlist_add_tracks(self.username, self.spotify_playlist_id, chunk)
        else:
            print("BAD TOKEN")


if __name__ == '__main__':
    gpmify = GPMify()
    print("GPMify - Move Google Music Playlists to Spotify")
    print("In order to use this client, you need to enter required credentials in config.py. For help visit...")
    print("Attempting to login to Google")
    gpmify.google_login()
    print("Getting you Google Music Playlists....")
    gpmify.get_google_playlists()
    gpmify.show_google_playlists()
    google_playlist_selection = int(input("Playlist number: "))
    gpmify.set_google_playlist_selection(google_playlist_selection)
    print("Getting the Google Playlist...")
    gpmify.get_google_playlist_songs()
    print("Ok time to setup your Spotfiy Account. If you haven't used this client before, a popup from spotify will"
          " come up asking you to authorize the application")
    gpmify.setup_spotify_api()
    spotify_playlist_id = input("Spotify Playlist ID to copy to: ")
    gpmify.set_spotify_playlist_id(spotify_playlist_id)
    gpmify.get_spotify_uri_for_songs_in_playlist()
    gpmify.add_songs_to_spotify_playlist()
    print("Complete!")
