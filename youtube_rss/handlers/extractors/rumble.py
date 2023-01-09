# import itertools
import re

from yt_dlp.compat import compat_HTTPError
from yt_dlp.extractor.rumble import RumbleChannelIE, RumbleEmbedIE
from yt_dlp.utils import (
    ExtractorError,
    int_or_none,
    parse_duration,
    parse_iso8601,
    traverse_obj,
    unescapeHTML,
)


class CustomRumbleEmbedIE(RumbleEmbedIE):
    def _real_extract(self, url):
        video_id = self._match_id(url)
        video = self._download_json(
            "https://rumble.com/embedJS/u3/",
            video_id,
            query={"request": "video", "ver": 2, "v": video_id},
        )

        sys_msg = traverse_obj(video, ("sys", "msg"))
        if sys_msg:
            self.report_warning(sys_msg, video_id=video_id)

        if video.get("live") == 0:
            live_status = "not_live" if video.get("livestream_has_dvr") is None else "was_live"
        elif video.get("live") == 1:
            live_status = "is_upcoming" if video.get("livestream_has_dvr") else "was_live"
        elif video.get("live") == 2:
            live_status = "is_live"
        else:
            live_status = None

        formats = []
        for ext, ext_info in (video.get("ua") or {}).items():
            for height, video_info in (ext_info or {}).items():
                meta = video_info.get("meta") or {}
                if not video_info.get("url"):
                    continue
                if ext == "hls":
                    if meta.get("live") is True and video.get("live") == 1:
                        live_status = "post_live"
                    formats.extend(
                        self._extract_m3u8_formats(
                            video_info["url"],
                            video_id,
                            ext="mp4",
                            m3u8_id="hls",
                            fatal=False,
                            live=live_status == "is_live",
                        )
                    )
                    continue
                formats.append(
                    {
                        "ext": ext,
                        "url": video_info["url"],
                        "format_id": "%s-%sp" % (ext, height),
                        "height": int_or_none(height),
                        "fps": video.get("fps"),
                        **traverse_obj(
                            meta,
                            {
                                "tbr": "bitrate",
                                "filesize": "size",
                                "width": "w",
                                "height": "h",
                            },
                            default={},
                        ),
                    }
                )
        self._sort_formats(formats)

        subtitles = {
            lang: [
                {
                    "url": sub_info["path"],
                    "name": sub_info.get("language") or "",
                }
            ]
            for lang, sub_info in (video.get("cc") or {}).items()
            if sub_info.get("path")
        }

        author = video.get("author") or {}
        thumbnails = traverse_obj(video, ("t", ..., {"url": "i", "width": "w", "height": "h"}))
        if not thumbnails and video.get("i"):
            thumbnails = [{"url": video["i"]}]

        if live_status in {"is_live", "post_live"}:
            duration = None
        else:
            duration = int_or_none(video.get("duration"))

        # Custom Additions``
        # embed_page = self._download_webpage(url, video_id, note="Downloading embed page")
        # canonical_url = self._search_regex(
        #     r'<link\s+rel="canonical"\s*href="(.+?)"', embed_page, "canonical URL", default=url
        # )
        # webpage = self._download_webpage(canonical_url, video_id)
        # description = self._html_search_regex(
        #     r'media-description">([^<]+)<', webpage, "description", default=None, fatal=False
        # )
        # view_count = self._html_search_regex(
        #     r'media-heading-info">([0-9,]+) Views<',
        #     webpage,
        #     "view_count",
        #     default=None,
        #     fatal=False,
        # )
        # if view_count:
        #     view_count = int_or_none(view_count.replace(",", ""))

        return {
            "id": video_id,
            "title": unescapeHTML(video.get("title")),
            "formats": formats,
            "subtitles": subtitles,
            "thumbnails": thumbnails,
            "timestamp": parse_iso8601(video.get("pubDate")),
            "channel": author.get("name"),
            "channel_url": author.get("url"),
            "duration": duration,
            "uploader": author.get("name"),
            "live_status": live_status,
            # "description": description,
            # "view_count": view_count,
        }


class CustomRumbleChannelIE(RumbleChannelIE):
    def entries(self, url, playlist_id, webpage, **kwargs):
        try:
            webpage = self._download_webpage(
                f"{url}?page=1", playlist_id, note="Downloading page 1"
            )
        except ExtractorError as e:
            if isinstance(e.cause, compat_HTTPError) and e.cause.code == 404:
                return
            raise
        # for video_url in re.findall(r"class=video-item--a\s?href=([^>]+\.html)", webpage):
        #     yield self._build_entry(video_url)
        for container in re.findall(
            r'<li class="video-listing-entry">(.+?)</li>', webpage, flags=re.DOTALL
        ):
            yield self._build_entry(container=container, **kwargs)

    def _build_entry(self, container, **kwargs):
        video_id = re.search(r"\/(v[^-]*)-", container).group(1)
        video_url = re.search(r"class=video-item--a\s?href=([^>]+\.html)", container).group(1)

        # title = re.search(r'title="([^\"]+)"', container).group(1)
        title = re.search(r"class=video-item--title>([^\<]+)<\/h3>", container).group(1)
        # description = re.search(r'<p class="description"\s*>(.+?)</p>', container).group(1)
        timestamp = parse_iso8601(re.search(r'datetime=([^">]+)>', container).group(1))
        thumbnail = re.search(r"src=([^\s>]+)", container).group(1)
        duration = parse_duration(
            re.search(r"class=video-item--duration data-value=([^\">]+)>", container).group(1)
        )
        return {
            **kwargs,
            **self.url_result("https://rumble.com" + video_url),
            "id": video_id,
            "display_id": video_id,
            "title": title,
            "description": None,
            "timestamp": timestamp,
            "thumbnail": thumbnail,
            "duration": duration,
        }

    def _real_extract(self, url):
        url, playlist_id = self._match_valid_url(url).groups()
        webpage = self._download_webpage(
            f"{url}?page=1", note="Downloading webpage", video_id=playlist_id
        )
        thumbnail = re.search(r"class=listing-header--thumb src=([^\s>]+)", webpage).group(1)
        channel = re.search(r"class=ellipsis-1>([^\">]+)<", webpage).group(1)
        channel_id = re.search(r"href=\/c\/([^\">]+)", webpage).group(1)
        channel_url = "https://rumble.com/c/" + channel_id
        uploader = channel
        uploader_id = channel_id
        uploader_url = channel_url
        kwargs = {
            "url": url,
            "thumbnail": thumbnail,
            "description": None,
            "title": f"{channel}'s Rumble Channel",
            "channel": channel,
            "channel_id": channel_id,
            "channel_url": channel_url,
            "uploader": uploader,
            "uploader_id": uploader_id,
            "uploader_url": uploader_url,
        }
        return self.playlist_result(
            self.entries(url, playlist_id, webpage=webpage), playlist_id=playlist_id, **kwargs
        )
