import json

import requests
import time


class GazelleAPI:
    def __init__(self, api_url, auth_header, rate_limit):
        self._s = requests.session()

        self._api_url = api_url
        self._s.headers.update(auth_header)

        self.sitename = self.__class__.__name__
        self._rate_limit = rate_limit
        self._last_used = 0

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

    def find_torrent(self, hash):
        t = self._get("torrent", {"hash": hash})
        return json.loads(t)

    def download_torrent(self, torrent_id):
        t = self._get("download", {"id": torrent_id}, raw=True)
        return t


class OPS(GazelleAPI):
    def __init__(self, api_key, delay_in_seconds=2):
        super().__init__(
            api_url="https://orpheus.network/ajax.php",
            auth_header={"Authorization": f"token {api_key}"},
            rate_limit=delay_in_seconds
        )


class RED(GazelleAPI):
    def __init__(self, api_key, delay_in_seconds=1):
        super().__init__(
            api_url="https://redacted.ch/ajax.php",
            auth_header={"Authorization": api_key},
            rate_limit=delay_in_seconds
        )
