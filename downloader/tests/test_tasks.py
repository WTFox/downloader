from downloader.constants import constants as c

TEST_URL = "https://www.youtube.com/watch?v=123"


def test__yt_dlp_video_cmd():
    assert c.yt_dlp_video_cmd(TEST_URL) == [
        "yt-dlp",
        "--trim-filenames",
        "120",
        "-f",
        "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format",
        "mp4",
        "-o",
        f"/storage/{c.YT_DLP_FILENAME_TEMPLATE}",
        TEST_URL,
    ]


def test__yt_dlp_audio_cmd():
    assert c.yt_dlp_audio_cmd(TEST_URL) == [
        "yt-dlp",
        "--trim-filenames",
        "120",
        "--extract-audio",
        "--audio-format",
        "mp3",
        "-o",
        f"/storage/{c.YT_DLP_FILENAME_TEMPLATE}/audio",
        TEST_URL,
    ]
