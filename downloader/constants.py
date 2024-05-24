from dataclasses import dataclass


@dataclass
class Constants:
    PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
    YT_DLP_FILENAME_TEMPLATE = "%(extractor)s/%(title).150B [%(id)s].%(ext)s"

    def yt_dlp_video_cmd(self, url: str) -> list[str]:
        return [
            "yt-dlp",
            "-f",
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format",
            "mp4",
            "-o",
            f"/storage/{self.YT_DLP_FILENAME_TEMPLATE}",
            "--concurrent-fragments",
            "4",
            url,
        ]

    def yt_dlp_audio_cmd(self, url: str) -> list[str]:
        return [
            "yt-dlp",
            "--extract-audio",
            "--audio-format",
            "mp3",
            "-o",
            f"/storage/audio/{self.YT_DLP_FILENAME_TEMPLATE}",
            url,
        ]


constants = Constants()
