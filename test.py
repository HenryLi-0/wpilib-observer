import requests

response = requests.get("https://api.github.com/repos/wpilibsuite/allwpilib/issues")
print(response.status_code)

info = response.json()

for pr in info:
    print(pr["title"], pr["url"])


class DiscordWebhook:
    def __init__(self,url,webhook="    "):
        self.url = url
        self.name = webhook
        self.avatar = ""
    def sendmessage(self,message):
        data = {"content":(str(message)),"username":self.name,"avatar_url":self.avatar}
        response = requests.post(self.url,json=data)
        print(self, response,response.status_code,response.request.body)
    def sendrawmessage(self,rawmessage):
        data = rawmessage
        response = requests.post(self.url,json=data)
        print(self, response,response.status_code,response.request.body)
    def rename(self,name):
        self.name = str(name)
    def reavatar(self,avatarlink):
        self.avatar = avatarlink

