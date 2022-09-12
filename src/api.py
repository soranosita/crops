import time
import json

import requests

from errors import AuthenticationError


class GazelleAPI:
    def __init__(self, site_url, tracker_url, auth_header, rate_limit):
        self._s = requests.session()
        self._s.headers.update(auth_header)
        self._rate_limit = rate_limit
        self._last_used = 0

        self.sitename = self.__class__.__name__
        self.site_url = site_url
        self.tracker_url = tracker_url
        self._api_url = f"{self.site_url}/ajax.php"
        self.announce_url = self._get_announce_url(tracker_url)

    def _get(self, action, params, raw=False):
        while True:
            now = time.time()
            if (now - self._last_used) > self._rate_limit:
                self._last_used = now
                params["action"] = action
                r = self._s.get(self._api_url, params=params)
                if raw:
                    return r
                return r.text
            else:
                time.sleep(0.2)

    def _get_announce_url(self, tracker_url):
        account_info = self.get_account_info()
        if account_info["status"] != "success":
            raise AuthenticationError(f"Invalid API key for {self.sitename}.")
        passkey = account_info["response"]["passkey"]
        return f"{tracker_url}/{passkey}/announce"

    def get_account_info(self):
        t = self._get("index", {})
        return json.loads(t)

    def find_torrent(self, hash_):
        t = self._get("torrent", {"hash": hash_})
        return json.loads(t)

    def download_torrent(self, torrent_id):
        t = self._get("download", {"id": torrent_id}, raw=True)
        return t


class OPS(GazelleAPI):
    def __init__(self, api_key, delay_in_seconds=2):
        super().__init__(
            site_url="https://orpheus.network",
            tracker_url="https://home.opsfet.ch",
            auth_header={"Authorization": f"token {api_key}"},
            rate_limit=delay_in_seconds
        )


class RED(GazelleAPI):
    def __init__(self, api_key, delay_in_seconds=1):
        super().__init__(
            site_url="https://redacted.ch",
            tracker_url="https://flacsfor.me",
            auth_header={"Authorization": api_key},
            rate_limit=delay_in_seconds
        )
