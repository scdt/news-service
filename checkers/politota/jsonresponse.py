class JsonResp():

    def __init__(self):
        self.login = {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "realname": {"type": "string"},
                "id": {"type": "number"},
            },
            "required":["username","realname","id"]
        }
        self.create_post = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
                "id": {"type": "number"},
                "owner_username": {"type": "string"},
            },
            "required":["title","content","id","owner_username"]
        }

        self.post = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
                "id": {"type": "number"},
                "owner_username": {"type": "string"},
            },
            "required":["title","content","id","owner_username"]
        }