#!/usr/bin/env python

import os
import shutil
import plistlib
from typing import List
from urllib.parse import urlparse, unquote


LIB_PATH = os.environ.get('ITUNES_LIB_PATH')

if not LIB_PATH:
    LIB_PATH = os.path.expanduser("~/Music/iTunes/iTunes Library.xml")

SYNC_FOLDER = os.environ.get('SYNC_FOLDER')


class Playlist:
    def __init__(self, playlist_name=None):
        self.name = playlist_name
        self.tracks = []
        self.is_folder = False
        self.playlist_persistent_id = None
        self.parent_persistent_id = None


class Song:
    name = None
    track_id = None
    artist = None
    album = None
    size = None
    total_time = None
    location = None
    location_escaped = None
    length = None

    def to_dict(self):
        return {key: value for (key, value) in self.__dict__.items()}


class Library:
    ignore_playlist = [
        "Library", "Music", "Movies", "TV Shows", "Purchased", "iTunes DJ", "Podcasts"
    ]

    def __init__(self, itunes_xml):
        self.il = plistlib.readPlist(itunes_xml)  # Much better support of xml special characters
        self.songs = {}
        self.get_songs()

    def get_songs(self):
        for trackid, attributes in self.il['Tracks'].items():
            s = Song()
            s.name = attributes.get('Name')

            s.track_id = int(attributes.get('Track ID')) if attributes.get('Track ID') else None
            s.artist = attributes.get('Artist')
            s.album = attributes.get('Album')
            s.size = int(attributes.get('Size')) if attributes.get('Size') else None
            s.total_time = attributes.get('Total Time')

            if attributes.get('Location'):
                s.location_escaped = attributes.get('Location')
                s.location = s.location_escaped
                s.location = unquote(urlparse(attributes.get('Location')).path[1:])

            s.length = int(attributes.get('Total Time')) if attributes.get('Total Time') else None

            self.songs[int(trackid)] = s

    def get_playlist_names(self, ignore_list=None) -> List[str]:
        if not ignore_list:
            ignore_list = self.ignore_playlist

        playlists = []
        for playlist in self.il['Playlists']:
            if playlist['Name'] not in ignore_list:
                playlists.append(playlist['Name'])
        return playlists

    def get_playlist(self, playlist_name):
        for playlist in self.il['Playlists']:
            if playlist['Name'] == playlist_name:
                # id 	playlist_id 	track_num 	url 	title 	album 	artist 	length 	uniqueid
                p = Playlist(playlist_name)
                p.is_folder = True if 'Folder' in playlist and playlist['Folder'] else False
                if 'Playlist Persistent ID' in playlist:
                    p.playlist_persistent_id = playlist['Playlist Persistent ID']
                if 'Parent Persistent ID' in playlist:
                    p.parent_persistent_id = playlist['Parent Persistent ID']

                track_number = 1
                # Make sure playlist was not empty
                if 'Playlist Items' in playlist:
                    for track in playlist['Playlist Items']:
                        t_id = int(track['Track ID'])
                        t = self.songs[t_id]
                        t.playlist_order = track_number
                        track_number += 1
                        p.tracks.append(t)
                return p


def replace_dots(origin_path: str):
    # replace path /Leningrad/CH.P.X./CH.P.X..mp3
    # to /Leningrad/CHPX/CHPX.mp3
    path, ext = origin_path.rsplit('.', maxsplit=1)
    return f"{path.replace('.', '')}.{ext}"


def copy_playlist(folder: str, tracks: List[Song], pl_name: str):
    tracks_for_playlist: List[str] = []

    for i, t in enumerate(tracks, start=1):
        print(f"{i} Copying {t.artist} - {t.name}")
        abs_location = f"/{t.location}"  # /Users/{user}/Music/iTunes/iTunes Media/Music/Kaleo/A_B/05 Hot Blood.mp3
        rel_location = abs_location.split('iTunes Media/Music')[1]  # /Kaleo/A_B/05 Hot Blood.mp3
        tracks_for_playlist.append(replace_dots(f".{rel_location}"))
        target_path = replace_dots(f"{folder}{rel_location}")
        if os.path.exists(target_path):
            continue
        target_dir = target_path.rsplit('/', maxsplit=1)[0]
        os.makedirs(target_dir, exist_ok=True)
        shutil.copyfile(abs_location, target_path)

    with open(f"{folder}/{pl_name}.m3u8", 'w') as f:
        print(f"Writing playlist {pl_name}")
        f.writelines(f"{line}\n" for line in tracks_for_playlist)


def main():
    print("Library path:")
    lib_path = input(f"({LIB_PATH})  ")
    if not lib_path:
        lib_path = LIB_PATH
    lib = Library(lib_path)

    print("Copy files to: ")
    sync_folder = input(f"({SYNC_FOLDER})  ")
    if not sync_folder:
        sync_folder = SYNC_FOLDER

    pls = lib.get_playlist_names()
    for i, pl in enumerate(pls):
        print(f"{i}) {pl}")

    print("=" * 15)
    pl_numbers = input("Which playlist to copy? Use comma separated values\n")
    for pl_number in pl_numbers.split(','):
        pl_number = int(pl_number)
        tracks = lib.get_playlist(pls[pl_number]).tracks

        copy_playlist(sync_folder, tracks, pls[pl_number])


if __name__ == '__main__':
    main()
