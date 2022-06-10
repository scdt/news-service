#!/usr/bin/env python3

import sys
import os
import inspect
from enum import Enum
import random
from fakesession import FakeSession
import json
import string
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonresponse import JsonResp
from PIL import Image, ImageDraw, ImageFont
from exif import Image as ExifImg
from ecdsa import SigningKey

""" <config> """
# SERVICE INFO
PORT = 8080

advisory_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFkdmlzb3J5IiwicmVhbG5hbWUiOiJhZHZpc29yeSIsImlkIjoxfQ.9g5FzrbUaewzDmOtBKJkDVwyE9jemUucjjHLUJ4iITg"
advisory_pk = SigningKey.from_string(b'\xb5\x1bp\x02i4\xcaz\xa7e\x10\xcd\x9c1x\x8c<\x88\x89v\xeb\xeb\xce\x8c')
# DEBUG -- logs to stderr, TRACE -- verbose log
DEBUG = os.getenv("DEBUG", True)
""" </config> """

TITLES = open(os.path.join(os.path.abspath(
    os.path.dirname(__file__)), "titles.txt")).read().split('\n')
FISHTEXT = open(os.path.join(os.path.abspath(
    os.path.dirname(__file__)), "fishtext.txt")).read().split('\n')
IMAGES = [os.path.join(os.path.abspath(os.path.dirname(
    __file__)), f"images/img_{i}.jpg") for i in range(1, 10)]
FONT = os.path.join(os.path.abspath(os.path.dirname(__file__)), "Roboto.ttf")

JSONResp = JsonResp()


def info():
    print('vulns: 1:1', flush=True, end="")
    exit(101)


def _register(s, username, realname, password):
    data = json.dumps({
        "username": username,
        "realname": realname,
        "password": password
    })

    try:
        r = s.post("/api/users", data=data)
    except Exception as e:
        die(ExitStatus.DOWN, f"Failed to register in service: {e}")

    if r.status_code != 200:
        die(ExitStatus.MUMBLE,
            f"Unexpected /api/users code: {r.status_code}")

    try:
        token = r.json()["access_token"]
    except Exception as e:
        die(ExitStatus.MUMBLE,
            f"Failed to get token after register in service: {e}")

    return token


def _login(s, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = s.get("/api/users/me", headers=headers)
    except Exception as e:
        die(ExitStatus.DOWN, f"Failed to register in service: {e}")

    if r.status_code != 200:
        die(ExitStatus.MUMBLE, f"Unexpected /auth/login code {r.status_code}")

    try:
        validate(instance=r.json(), schema=JSONResp.login)
    except Exception as e:
        die(ExitStatus.MUMBLE, f"Incorrect response format:\n{e}")

    return r.json()


def check(host: str):
    s = FakeSession(host, PORT)
    username = rand_string()
    password = rand_string()
    realname = rand_string()
    token = _register(s, username, realname, password)
    user = _login(s, token)

    s.headers = {"Authorization": f"Bearer {token}"}

    _log("Check posts")
    post_id = _check_posts(s)

    _log("Check images")
    _check_images(s, username)

    _log("Check reports")
    _check_reports(s, post_id)

    die(ExitStatus.OK, "Check ALL OK")


def put(host: str, flag_id: str, flag: str, vuln: str):
    _log("Putting flag")

    s = FakeSession(host, PORT)
    username = rand_string()
    password = rand_string()
    realname = rand_string()

    if vuln == "1":
        token = _register(s, username, realname, password)
        _login(s, token)
        s.headers = {"Authorization": f"Bearer {token}"}

        title = random.choice(TITLES)
        c = random.choice(FISHTEXT)
        r = _create_post(s, title, c, False)
        post_id = r["id"]
        title = random.choice(TITLES)
        r = _create_post(s, title, flag, True)
        private_post_id = r["id"]
        print(f"{token}@@{post_id}@@{private_post_id}", file=sys.stdout, flush=True)

    elif vuln == "2":
        img = random.choice(IMAGES)
        text = random.choice(TITLES)
        token = _register(s, username, flag, password)
        _login(s, token)

        s.headers = {"Authorization": f"Bearer {token}"}
        name = _create_image(img, text)
        _upload_image(s, name)

        print(token, file=sys.stdout, flush=True)

    die(ExitStatus.OK, "put end")


def get(host: str, flag_id: str, flag: str, vuln: str):
    _log("Getting flag")

    s = FakeSession(host, PORT)

    if vuln == "1":
        data = flag_id.split("@@")
        token = data[0]
        post_id = data[1]
        private_post_id = data[2]

        s.headers = {"Authorization": f"Bearer {token}"}
        _log("Check flag in private post")
        post = _get_post(s, private_post_id)
        if flag not in post:
            die(ExitStatus.CORRUPT, f"Can't find a flag in {post}")

        _log("Check flag in private post by advisory")
        s.headers = {"Authorization": f"Bearer {advisory_token}"}
        report = _report_post(s, post_id)
        signature = advisory_pk.sign(str.encode(report["username"])).hex()
        posts = _get_user_posts(s, report["id"], report["username"], signature)
        if flag not in posts:
            die(ExitStatus.CORRUPT, f"Can't find a flag in {posts}")

    elif vuln == "2":
        _log("Check flag in /api/users/me")
        me = _login(s, flag_id)

        if flag not in me["realname"]:
            die(ExitStatus.CORRUPT, f"Can't find a flag in {me}")


def _check_posts(s):
    title = random.choice(TITLES)
    c = random.choice(FISHTEXT)

    title_priv = random.choice(TITLES)
    c_priv = random.choice(FISHTEXT)

    _log(f"Create public post")
    r = _create_post(s, title, c)
    id_pub = r["id"]

    _log(f"Create private post")
    r = _create_post(s, title_priv, c_priv, True)
    id_priv = r["id"]

    _log(f"Check posts")
    if (c not in _get_post(s, id_pub)) or (c_priv not in _get_post(s, id_priv)):
        die(ExitStatus.MUMBLE, "failed to check posts")

    if c not in _get_posts(s):
        die(ExitStatus.MUMBLE, "failed to check public post")

    return id_pub


def _check_images(s, username):
    img = random.choice(IMAGES)
    text = random.choice(TITLES)

    name = _create_image(img, text)

    _log(f"Check image upload")
    url = _upload_image(s, name)

    _log(f"Check public link")
    if url not in _get_images(s):
        die(ExitStatus.MUMBLE, "failed to check image in public")

    _log(f"Check download image")
    _check_download(s, url, username)

    return True


def _check_reports(s, post_id):
    s.headers = {"Authorization": f"Bearer {advisory_token}"}
    _log("Check report post")
    _report_post(s, post_id)
    _log("Check get reports")
    reports = _get_reports(s)
    _log("Check get user's posts")
    try:
        for report in reports:
            validate(instance=report, schema=JSONResp.report)
            signature = advisory_pk.sign(str.encode(report['username'])).hex()
            _get_user_posts(s, report["id"], report["username"], signature)
    except ValidationError:
        die(ExitStatus.MUMBLE, "Failed to check reports: Incorrect report format")
    except Exception as e:
        die(ExitStatus.MUMBLE, f"Failed to report post: {e}")
    return True


def _create_image(img, text):
    image = Image.open(img)
    draw = ImageDraw.Draw(image)
    font_size = 5

    img_fraction = 0.5

    font = ImageFont.truetype(FONT, font_size, encoding='UTF-8')

    while font.getsize(text)[0] < img_fraction * image.size[0]:
        font_size += 1
        font = ImageFont.truetype(FONT, font_size)

    font_size = round((font_size - 1) * 1.8)
    font = ImageFont.truetype(FONT, font_size, encoding='UTF-8')
    w, h = font.getsize(text)

    draw.rectangle((0, 0, w, h), fill="black")
    draw.text((0, 0), text, font=font, color="pink")

    name = f'{rand_string()}.jpg'
    image.save(name)

    return name


def _check_download(s, url, username):
    r = s.get(f"{url}", allow_redirects=True)

    if r.status_code != 200:
        die(ExitStatus.MUMBLE,
            f"Unexpected /{url} status code: {r.status_code}")

    name = f"{rand_string()}.jpg"
    open(name, 'wb').write(r.content)

    with open(name, 'rb') as image_file:
        img = ExifImg(image_file)
        u_name = img.copyright
    os.remove(name)

    _log(f"Check username in an image")
    if u_name != username:
        die(ExitStatus.MUMBLE, f"no username found in an image")


def _upload_image(s, name):
    file = {
        'file': (name, open(name, "rb"), 'image/jpeg')
    }
    r = s.post('/api/images/', files=file)
    os.remove(name)

    if r.status_code != 200:
        die(ExitStatus.MUMBLE,
            f"Unexpected /api/images/ status code: {r.status_code}")

    return r.json()["url"]


def _get_posts(s):
    try:
        r = s.get(f"/api/posts/")
    except Exception as e:
        die(ExitStatus.DOWN, f"Failed to get post: {e}")

    if r.status_code != 200:
        die(ExitStatus.MUMBLE,
            f"Unexpected /api/posts/ status code: {r.status_code}")

    return r.text


def _get_images(s):
    try:
        r = s.get(f"/api/images/")
    except Exception as e:
        die(ExitStatus.DOWN, f"Failed to get post: {e}")

    if r.status_code != 200:
        die(ExitStatus.MUMBLE,
            f"Unexpected /api/posts/ status code: {r.status_code}")

    return r.text


def _get_post(s, post_id):

    try:
        r = s.get(f"/api/posts/{post_id}")
    except Exception as e:
        die(ExitStatus.DOWN, f"Failed to get post: {e}")
    if r.status_code != 200:
        die(ExitStatus.MUMBLE,
            f"Unexpected /api/posts/{post_id} status code: {r.status_code}")
    try:
        validate(instance=r.json(), schema=JSONResp.post)
    except Exception as e:
        die(ExitStatus.MUMBLE, f"Incorrect response format:\n{e}")
    return r.text


def _get_user_posts(s, report_id, username, signature):
    adv_msg = json.dumps({
        "report_id": report_id,
        "username": username,
        "signature": signature
    })
    try:
        r = s.post("/api/posts/adv", data=adv_msg)
    except Exception as e:
        die(ExitStatus.DOWN, f"Failed to get user's posts: {e}")

    if r.status_code != 200:
        die(ExitStatus.MUMBLE, f"Unexpected /api/posts/adv create {r.status_code}")

    return r.text


def _get_reports(s):
    try:
        r = s.get(f"/api/reports")
    except Exception as e:
        die(ExitStatus.DOWN, f"Failed to get reports: {e}")
    if r.status_code != 200:
        die(ExitStatus.MUMBLE,
            f"Unexpected /api/reports status code: {r.status_code}")
    try:
        reports = json.loads(r.text)
    except Exception as e:
        die(ExitStatus.MUMBLE, f"Incorrect response format:\n{e}")
    return reports


def _create_post(s, title, content, private=False):
    post = json.dumps({
        "title": title,
        "content": content,
        "private": private
    })

    try:
        r = s.post("/api/posts", data=post)
    except Exception as e:
        die(ExitStatus.DOWN, f"Failed create post: {e}")

    if r.status_code != 200:
        die(ExitStatus.MUMBLE, f"Unexpected /api/posts create {r.status_code}")

    try:
        validate(instance=r.json(), schema=JSONResp.create_post)
    except Exception as e:
        die(ExitStatus.MUMBLE, f"Incorrect response format:\n{e}")

    return r.json()


def _report_post(s, post_id):
    try:
        r = s.get(f"/api/posts/{post_id}/report")
        if r.status_code != 200:
            die(ExitStatus.MUMBLE, f"Unexpected /api/posts/{post_id}/report status code: {r.status_code}")
        report = json.loads(r.text)
        validate(instance=report, schema=JSONResp.report)
        return report
    except ValidationError as e:
        die(ExitStatus.MUMBLE, f"Incorrect report format: {e}")
    except Exception as e:
        die(ExitStatus.MUMBLE, f"Failed to report post: {e}")


class ExitStatus(Enum):
    OK = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104
    CHECKER_ERROR = 110


def _log(obj):
    if DEBUG and obj:
        caller = inspect.stack()[1].function
        print(f"[{caller}] {obj}", file=sys.stderr, flush=True)
    return obj


def die(code: ExitStatus, msg: str):
    if msg:
        print(msg, file=sys.stderr)
    exit(code.value)


def rand_string(len=12):
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(len))


def _main():
    try:
        cmd = sys.argv[1]
        if cmd == "info":
            info()
        elif cmd == "check":
            host = sys.argv[2]
            check(host)
        elif cmd == "put":
            host = sys.argv[2]
            fid, flag, vuln = sys.argv[3], sys.argv[4], sys.argv[5]
            put(host, fid, flag, vuln)
        elif cmd == "get":
            host = sys.argv[2]
            fid, flag, vuln = sys.argv[3], sys.argv[4], sys.argv[5]
            get(host, fid, flag, vuln)
        else:
            raise IndexError
    except Exception as e:
        die(
            ExitStatus.CHECKER_ERROR,
            f"Usage: {sys.argv[0]} check|put|get IP FLAGID FLAG VULN \n Exception:{e}",
        )


if __name__ == "__main__":
    _main()
