import typing as T
from dataclasses import dataclass


@dataclass
class Constants:
    PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
    YT_DLP_FILENAME_TEMPLATE = "%(extractor)s/%(title).150B [%(id)s].%(ext)s"

    def yt_dlp_video_cmd(self, url: str, path: T.Optional[str] = None) -> list[str]:
        if not path:
            path = f"/storage/{self.YT_DLP_FILENAME_TEMPLATE}"
        else:
            path = f"{path}/%(title).150B [%(id)s].%(ext)s"

        return [
            "yt-dlp",
            "-f",
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format",
            "mp4",
            "-o",
            path,
            "--concurrent-fragments",
            "4",
            url,
        ]

    def yt_dlp_audio_cmd(self, url: str, path: T.Optional[str] = None) -> list[str]:
        if not path:
            path = f"/storage/audio/{self.YT_DLP_FILENAME_TEMPLATE}"
        else:
            path = f"{path}/%(title).150B [%(id)s].%(ext)s"

        return [
            "yt-dlp",
            "--extract-audio",
            "--audio-format",
            "mp3",
            "-o",
            path,
            url,
        ]


constants = Constants()
