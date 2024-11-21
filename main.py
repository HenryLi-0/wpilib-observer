import time, requests

'''settings'''

# Observing
TARGET_REPO = "wpilibsuite/allwpilib"
OBSERVE_PR = 2*60
OBSERVE_ISSUE = 2*60
OBSERVE_RELEASE = 60*60
WEBHOOK = ""
WEBHOOK_PFP = "https://cdn.discordapp.com/attachments/1308965461550960761/1308985150989664316/observer_-_wpilib.png"
PING = "<@&797923529655189515>"

# Raspberry Pi
RPI = False
RPI_LED_PATH = "/sys/class/leds/ACT/"

# Verify
print("")
print(f"Checking Times:")
print(f"  Checking for new PRs every {round(OBSERVE_PR*100)/100} seconds")
print(f"  Checking for new Issues every {round(OBSERVE_ISSUE*100)/100} seconds")
print(f"  Checking for new Releases every {round(OBSERVE_RELEASE*100)/100} seconds")
print(f"Raspberry Pi: {RPI}")
input("Press [Enter] to Start!")

'''init'''
print("  Starting...")
def fancyformat(seconds):
    seconds = round(seconds)
    s = seconds % 60
    seconds = (seconds - s)/60
    m = seconds % 60
    seconds = (seconds - m)/60
    h = seconds % 24
    seconds = (seconds - h)/24
    d = seconds % 365
    seconds = (seconds - d)/365
    y = seconds
    print("Uptime: {:01}:{:02}:{:02}:{:02}:{:02}".format(round(y),round(d),round(h),round(m),round(s)))

def msg(message):
    data = {"content":(str(message)),"username":"WPILIB Observer","avatar_url":WEBHOOK_PFP}
    response = requests.post(WEBHOOK,json=data)
    return response
def getPRs():      return requests.get(f"https://api.github.com/repos/{TARGET_REPO}/pulls"   ).json()
def getIssues():   return requests.get(f"https://api.github.com/repos/{TARGET_REPO}/issues"  ).json()
def getReleases(): return requests.get(f"https://api.github.com/repos/{TARGET_REPO}/releases").json()

class Storage:
    def __init__(self, data):
        self.last = []
        for entry in data: self.last.append([entry["title"], entry["html_url"], entry["number"], entry["user"]["login"], entry["user"]["avatar_url"], entry["created_at"]])
    def compare(self, newdata):
        temp = []
        for entry in newdata: temp.append([entry["title"], entry["html_url"], entry["number"], entry["user"]["login"], entry["user"]["avatar_url"], entry["created_at"]])
        new = []
        for item in temp:
            if not(item in self.last): new.append(item)
        self.last = temp
        return new
        

print("  Fetching data...")
lastPRs = Storage(getPRs())
lastIssues = Storage(getIssues())
lastReleases = getReleases()

'''loop'''
print("  Loop starting...")
if RPI:
    with open(RPI_LED_PATH + "brightness", "w") as f: f.write("0")

initTime = time.time()
lastUpdate = time.time()
updates = 0
messageQueue = []
while True:
    if time.time() - lastUpdate >= 1:
        lastUpdate = time.time()
        if updates % OBSERVE_PR == 0:
            '''PULL REQUESTS'''
            new = lastPRs.compare()
            for event in new:
                messageQueue.append({
                    "content": "",
                    "username": "WPILIB Observer",
                    "avatar_url": "https://cdn.discordapp.com/attachments/1308965461550960761/1308985150989664316/observer_-_wpilib.png",
                    "embeds": [
                        {
                            "author": {
                                "name": "",
                                "icon_url": "https://cdn.discordapp.com/attachments/1308965461550960761/1308985150989664316/observer_-_wpilib.png" 
                            },
                            "title": f"New Pull Request",
                            "url": "https://discord.com/developers/docs/resources/webhook#webhook-resource",
                            "description": "[New Release!](https://discord.com/developers/docs/resources/webhook#webhook-resource)",
                            "color": 0x26E23B,
                            "footer": {
                                "text": f"Uptime: {fancyformat(lastUpdate-initTime)}"
                            }
                        }
                    ]
                })
        
        if updates % OBSERVE_ISSUE == 0:
            '''ISSUES'''
            pass

        if updates % OBSERVE_RELEASE == 0:
            '''RELEASES'''

            # TO-DO
            messageQueue.append({
                "content": "",
                "username": "WPILIB Observer",
                "avatar_url": "https://cdn.discordapp.com/attachments/1308965461550960761/1308985150989664316/observer_-_wpilib.png",
                "embeds": [
                    {
                        "author": {
                            "name": "",
                            "icon_url": "https://cdn.discordapp.com/attachments/1308965461550960761/1308985150989664316/observer_-_wpilib.png" 
                        },
                        "title": f"WAKE UP! NEW RELEASE! {PING}",
                        "url": "https://discord.com/developers/docs/resources/webhook#webhook-resource",
                        "description": "[New Release!](https://discord.com/developers/docs/resources/webhook#webhook-resource)",
                        "color": 0xffaa00,
                        "footer": {
                            "text": f"Uptime: {fancyformat(lastUpdate-initTime)}"
                        }
                    }
                ]
            })


        updates += 1
    
    if len(messageQueue) > 0:
        for data in messageQueue:
            response = requests.post(WEBHOOK,json=data)
            print(f"[{round(time.time()*100)/100}] - Update {updates} : Response {response.status_code}")
            with open(RPI_LED_PATH + "brightness", "w") as f:
                f.write("1")
                time.sleep(0.1)
                f.write("0")



# with open(RPI_LED_PATH + "brightness", "w") as f:
#     f.write("0")
# time.sleep(0.05)
# with open(RPI_LED_PATH + "brightness", "w") as f:
#     f.write("1")
# time.sleep(0.05)





