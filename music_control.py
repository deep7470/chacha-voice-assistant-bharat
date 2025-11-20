import os
import time
import random
from pathlib import Path
from threading import Thread
import pygame
# ----------------------------------------------------------
# 🖥️ System Volume Control (Windows)
# ----------------------------------------------------------

# 🎵 Configuration
MUSIC_DIR = r"C:\Users\hp\Music"
playlist = []
current_track_index = -1
is_paused = False
is_stopped = False
music_initialized = False
volume_level = 0.7  # default 70%


# ----------------------------------------------------------
# 🎚️ Mixer Initialization
# ----------------------------------------------------------
def init_mixer():
    """Initialize pygame mixer once."""
    global music_initialized
    if not music_initialized:
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(volume_level)
            music_initialized = True
            print("✅ Music mixer initialized.")
        except Exception as e:
            print("❌ Mixer init error:", e)


# ----------------------------------------------------------
# 🎵 Build Playlist
# ----------------------------------------------------------
def build_playlist():
    """Scan folder and build a shuffled playlist."""
    global playlist
    playlist.clear()
    music_path = Path(MUSIC_DIR)

    if not music_path.exists():
        print(f"⚠️ Music folder not found: {MUSIC_DIR}")
        return

    for ext in ('*.mp3', '*.wav', '*.ogg', '*.m4a', '*.wma'):
        playlist.extend(sorted(str(x) for x in music_path.glob(ext)))

    if not playlist:
        print("⚠️ No songs found in music folder.")
        return

    random.shuffle(playlist)
    print(f"🎵 Playlist ready: {len(playlist)} songs found.")


# ----------------------------------------------------------
# ▶️ Play Track
# ----------------------------------------------------------
def play_track(index=None):
    """Play a song by index or continue from the current one."""
    global current_track_index, is_paused, is_stopped

    init_mixer()

    if not playlist:
        build_playlist()
    if not playlist:
        return

    # Continue from current if nothing else provided
    if index is None:
        index = 0 if current_track_index == -1 else current_track_index

    index = max(0, min(index, len(playlist) - 1))
    track = playlist[index]

    try:
        is_stopped = False
        pygame.mixer.music.load(track)
        pygame.mixer.music.play()
        current_track_index = index
        is_paused = False
        print(f"▶️ Now playing: {os.path.basename(track)}")
        Thread(target=_auto_next, daemon=True).start()
    except Exception as e:
        print("❌ Music play error:", e)


# ----------------------------------------------------------
# ⏭️ Auto-Next Track
# ----------------------------------------------------------
def _auto_next():
    """Automatically play next song after the current one finishes."""
    global current_track_index, is_stopped
    while True:
        try:
            if not pygame.mixer.get_init():
                return
            if not pygame.mixer.music.get_busy():
                if not is_paused:  # only go next if song really finished
                    break
                else:
                    time.sleep(1)
                    continue

            time.sleep(1)
        except pygame.error:
            return

    if not is_stopped and playlist:
        next_index = (current_track_index + 1) % len(playlist)
        play_track(next_index)


# ----------------------------------------------------------
# ⏭️ Manual Next
# ----------------------------------------------------------
def play_next():
    """Play the next track manually."""
    global current_track_index
    if not playlist:
        build_playlist()
    if not playlist:
        return
    next_index = (current_track_index + 1) % len(playlist)
    play_track(next_index)


# ----------------------------------------------------------
# ⏯️ Pause Music
# ----------------------------------------------------------
def pause_music():
    """Pause the currently playing music safely."""
    global is_paused
    try:
        if not pygame.mixer.get_init():
            init_mixer()
        # Try to pause regardless of get_busy() hiccups
        if not is_paused:
            pygame.mixer.music.pause()
            is_paused = True
            print("⏸️ Music paused.")
        else:
            print("⚠️ Music already paused.")
    except Exception as e:
        print("❌ Pause error:", e)



# ----------------------------------------------------------
# ▶️ Resume / Unpause
# ----------------------------------------------------------
def resume_music():
    """Resume paused music."""
    global is_paused
    try:
        if not pygame.mixer.get_init():
            init_mixer()
        if is_paused:
            pygame.mixer.music.unpause()
            is_paused = False
            print("▶️ Music resumed.")
        else:
            if not pygame.mixer.music.get_busy():
                play_track(current_track_index)
            else:
                print("⚠️ No paused song to resume.")
    except Exception as e:
        print("❌ Resume error:", e)


# ----------------------------------------------------------
# ⏹️ Stop
# ----------------------------------------------------------
def stop_music():
    """Stop music playback (without auto-next)."""
    global is_stopped
    if not pygame.mixer.get_init():
        return
    if pygame.mixer.music.get_busy():
        is_stopped = True
        pygame.mixer.music.stop()
        print("⏹️ Music stopped.")
    else:
        print("⚠️ No music is currently playing.")


# ----------------------------------------------------------
# 🔊 Volume Control
# ----------------------------------------------------------
def set_volume(level: float):
    """
    Set volume level (0.0 to 1.0).
    Example: set_volume(0.5) → 50% volume
    """
    if not pygame.mixer.get_init():
        init_mixer()
    try:
        level = max(0.0, min(level, 1.0))
        pygame.mixer.music.set_volume(level)
        print(f"🔊 Volume set to {int(level * 100)}%.")
    except Exception as e:
        print("❌ Volume set error:", e)



def volume_up(step=0.1):
    """Increase volume gradually."""
    global volume_level
    set_volume(volume_level + step)


def volume_down(step=0.1):
    """Decrease volume gradually."""
    global volume_level
    set_volume(volume_level - step)


def mute():
    """Mute the volume."""
    set_volume(0.0)


def max_volume():
    """Set maximum volume."""
    set_volume(1.0)


# ----------------------------------------------------------
# 🎶 Get Info
# ----------------------------------------------------------
def get_current_track():
    """Return current track name or None."""
    if current_track_index == -1 or not playlist:
        return None
    return os.path.basename(playlist[current_track_index])






def set_system_volume(level_percent: int):
    """Set system master volume using nircmd (0–100%)."""
    try:
        level_percent = max(0, min(level_percent, 100))
        # 65535 is the max volume value for nircmd
        volume_value = int(65535 * (level_percent / 100))
        os.system(f"C:\\Users\\hp\\nircmd.exe setsysvolume {volume_value}")
        print(f"🔊 System volume set to {level_percent}%.")
    except Exception as e:
        print("❌ System volume control error:", e)
