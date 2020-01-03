import os
import sys

from ..helpers import fzf
from .. import spotify


def home_screen(config):
    choices = {
        'Search Library': 'search',
        'Current Playback [!]': 'current_playback',
        'Devices': 'list_devices',
        'Play/Pause': 'resume',
        'Update Cache': 'update_cache',
    }
    chosen = fzf.run_fzf(list(choices.keys()), prompt='[Home] > ')[0]
    if chosen == '':
        return None,
    return choices[chosen],


def list_devices(config):
    sp = spotify.get_spotify_client(config)
    choices = {d['name']: d['id'] for d in sp.devices()['devices']}
    chosen = fzf.run_fzf(list(choices.keys()), prompt='[Devices] > ')[0]
    if chosen == '':
        return 'home_screen',
    with open(os.path.join(config['cache_path'], 'device'), 'w') as ofi:
        ofi.write(choices[chosen])
    return 'device_actions',


def device_actions(config):
    with open(os.path.join(config['cache_path'], 'device'), 'r') as ifi:
        device_id = ifi.read()
    sp = spotify.get_spotify_client(config)
    sp.transfer_playback(device_id)
    return 'home_screen',


def resume(config):
    sp = spotify.get_spotify_client(config)
    pb = sp.current_playback()
    if pb['is_playing']:
        sp.pause_playback()
    else:
        sp.start_playback()
    return 'home_screen',


def update_cache(config):
    spotify.update_cache(config)
    return 'home_screen',


def search(config):
    chosen = fzf.run_piped_fzf(spotify.sink_all_tracks, config,
                               prompt='[Search] > ')[0]
    result = list(map(str.strip, chosen.split('::')))
    if len(result) > 1:
        return song_actions(result, config)
    else:
        return 'home_screen',


def song_actions(result, config):
    choices = {
        'Play Song in Playlist': 'play_song_in_playlist',
        'Play Album in Playlist': 'play_album_in_playlist',
        'Play Album': 'play_album',
    }
    # TODO: add prompt
    chosen = fzf.run_fzf(list(choices.keys()))[0]
    if chosen == '':
        return 'search',
    return choices[chosen], [result[-1], config]
    # return getattr(sys.modules[__name__], choices[chosen])(result[-1], config)


def play_song_in_playlist(song_id, config):
    return 'home_screen',
