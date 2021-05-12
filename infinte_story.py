import errors
import requests
import json

class Client:
    def __init__(self):
        # TODO no idea where this comes from looks like uuid4?
        self.deviceID = "2bf72c0b-8c73-415d-b417-f90859a3f176"
        return

    def NewStory(self, playerClass, name):
        r = requests.post(
            "https://api.infinitestory.app/start_story",
            data = json.dumps({"playerClass": playerClass, "name": name, "deviceId": self.deviceID}),
            headers = {"content-type": "application/json"})

        jsonResponse = r.json()
        if "uid" not in jsonResponse:
            print(r.content)
            return None, None, errors.ErrorAPI

        return jsonResponse["uid"], jsonResponse["storyBits"][1]["payload"], None

    def do(self, uid, action, action_type):
        r = requests.post(
            "https://api.infinitestory.app/act",
            data = json.dumps({"uid": uid, "type": "ACT_DO", "payload": action}),
            headers = {"content-type": "application/json", "authorization": self.deviceID})
        jsonResponse = r.json()
        if "newStoryBits" not in jsonResponse:
            print(r.content)
            return None, errors.ErrorAPI

        return jsonResponse["newStoryBits"][1]["payload"], None

    def Act(self, uid, action):
        return self.do(uid, action, "ACT_DO")

    def Say(self, uid, action):
        return self.do(uid, action, "ACT_SAY")

