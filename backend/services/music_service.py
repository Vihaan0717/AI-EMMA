import os
import vlc
import yt_dlp
import threading
import time
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("MusicService")

class MusicService:
    """
    Orpheus Music Engine.
    Handles searching, streaming, and controlling music via VLC and yt-dlp.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MusicService, cls).__new__(cls)
            cls._instance._init_player()
        return cls._instance

    def _init_player(self):
        # Configure VLC instance
        # On Windows, we might need to specify the path if it's not detected
        self.vlc_instance = vlc.Instance('--no-video --quiet')
        self.player = self.vlc_instance.media_player_new()
        
        self.queue: List[Dict] = []
        self.current_index = -1
        self.is_playing = False
        
        # yt-dlp options for audio-only extraction
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

    def search_and_add(self, query: str) -> str:
        """Searches for a song and adds it to the queue."""
        logger.info(f"Searching for: {query}")
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)
                if not info or 'entries' not in info or not info['entries']:
                    return "No results found."
                
                video = info['entries'][0]
                song_data = {
                    'id': video['id'],
                    'title': video['title'],
                    'url': video['url'],
                    'duration': video.get('duration', 0),
                    'uploader': video.get('uploader', 'Unknown')
                }
                
                self.queue.append(song_data)
                logger.info(f"Added to queue: {song_data['title']}")
                
                # Auto-play if nothing is playing
                if not self.is_playing and self.current_index == -1:
                    self.play_next()
                    
                return f"Added to queue: {song_data['title']}"
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Error: {e}"

    def play_next(self):
        """Plays the next song in the queue."""
        if self.current_index + 1 < len(self.queue):
            self.current_index += 1
            song = self.queue[self.current_index]
            self._start_stream(song['url'])
            return f"Playing: {song['title']}"
        else:
            self.is_playing = False
            return "End of queue."

    def _start_stream(self, stream_url: str):
        """Internal: Sets the media and starts playback."""
        media = self.vlc_instance.media_new(stream_url)
        self.player.set_media(media)
        self.player.play()
        self.is_playing = True
        
        # Start a thread to monitor end of track
        threading.Thread(target=self._monitor_end, daemon=True).start()

    def _monitor_end(self):
        """Polls VLC for the end of the track to trigger next song."""
        while self.is_playing:
            state = self.player.get_state()
            if state == vlc.State.Ended:
                logger.info("Song ended. Playing next...")
                self.play_next()
                break
            time.sleep(1)

    def pause(self) -> str:
        if self.player.is_playing():
            self.player.pause()
            return "Music paused."
        return "Nothing is playing."

    def resume(self) -> str:
        if not self.player.is_playing() and self.current_index != -1:
            self.player.play()
            return "Music resumed."
        return "Nothing to resume."

    def stop(self) -> str:
        self.player.stop()
        self.is_playing = False
        return "Music stopped."

    def skip(self) -> str:
        return self.play_next()

    def seek(self, seconds: int) -> str:
        """Seeks forward or backward in seconds."""
        current_time = self.player.get_time() # in ms
        new_time = current_time + (seconds * 1000)
        self.player.set_time(max(0, new_time))
        return f"Seeked {'forward' if seconds > 0 else 'backward'} {abs(seconds)}s."

    def get_status(self) -> Dict:
        """Returns the current playback status."""
        song = self.queue[self.current_index] if self.current_index != -1 else None
        return {
            "is_playing": self.player.is_playing(),
            "current_song": song['title'] if song else "None",
            "queue_length": len(self.queue),
            "position": self.player.get_position(), # 0.0 to 1.0
            "volume": self.player.audio_get_volume()
        }

    def duck(self, level: int = 15):
        """Reduces volume to 'level' for barge-in."""
        logger.info(f"Ducking music volume to {level}%")
        self.player.audio_set_volume(level)

    def unduck(self, level: int = 100):
        """Restores volume to 'level'."""
        self.player.audio_set_volume(level)

    def interrupt(self):
        """Fully pauses music during user speech."""
        if self.is_playing:
            logger.info("Interrupting music for user speech...")
            self.pause()

# Global Instance
music_service = MusicService()
