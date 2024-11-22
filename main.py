import time, requests, os

'''settings'''

# Observing
TARGET_REPO = "microsoft/vscode" #"wpilibsuite/allwpilib"
OBSERVE_PR = 2*60
OBSERVE_ISSUE = 2*60
OBSERVE_RELEASE = 60*60
WEBHOOK = ""
WEBHOOK_PFP = "https://cdn.discordapp.com/attachments/1308965461550960761/1308985150989664316/observer_-_wpilib.png"
PING = "<@&797923529655189515>"

# Raspberry Pi
RPI = False
RPI_LED_PATH = "/sys/class/leds/ACT/"

if RPI:
    with open(RPI_LED_PATH + "brightness", "w") as f:
        f.write("1")

# Setup logs
LOG_PATH = os.path.join(f"observer-logs-{round(time.time())}.txt")
with open(LOG_PATH, "x") as f:
    f.write(str(time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime())))
def log(message):
    msg = "{} - {}".format(str(time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime())), message)
    with open(LOG_PATH, "a") as f:
        f.write("\n" + msg)
        print(msg)

# Verify
log( "[!] PREPARE")
log(f"     | Checking Times:")
log(f"     |  | Checking for new PRs every {round(OBSERVE_PR*100)/100} seconds")
log(f"     |  | Checking for new Issues every {round(OBSERVE_ISSUE*100)/100} seconds")
log(f"     |  | Checking for new Releases every {round(OBSERVE_RELEASE*100)/100} seconds")
log(f"     | Raspberry Pi: {RPI}")
log( "     | Press [Enter] to Start!")
if not(input("")) == "":
    log( "     |  | User Cancel!")
    exit("Cancelled!") 

'''init'''
log("[!] STARTING")
log("     | Starting...")
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
def getPRs():
    log("     | Fetching PRs...")
    return requests.get(f"https://api.github.com/repos/{TARGET_REPO}/pulls"   )
def getIssues():
    log("     | Fetching Issues...")
    return requests.get(f"https://api.github.com/repos/{TARGET_REPO}/issues"  )
def getReleases():
    log("     | Fetching Releases...")
    return requests.get(f"https://api.github.com/repos/{TARGET_REPO}/releases")

class Storage:
    def __init__(self, data):
        self.ids = []
        for entry in data: self.ids.append(entry["number"])
    def compare(self, newdata):
        temp = []
        for entry in newdata: temp.append(entry["number"])
        new = []
        for item in temp:
            if not(item in self.ids): new.append(entry)
        self.ids = temp
        return new
        

log("[!] FETCHING START DATA...")
lastPRs = Storage(getPRs().json())
lastIssues = Storage(getIssues().json())
lastReleases = getReleases().json()

'''loop'''
log("[!] LOOP STARTING...")
if RPI:
    with open(RPI_LED_PATH + "brightness", "w") as f:
        f.write("0")

initTime = time.time()
lastUpdate = time.time()
updates = 0
messageQueue = []
endLoop = False

requests.post(WEBHOOK,json={"content":"The WPILIB Observer is observing!","username":"WPILIB Observer","avatar_url":WEBHOOK_PFP})

while True:
    if time.time() - lastUpdate >= 1:
        lastUpdate = time.time()
        if updates % OBSERVE_PR == 0:
            '''PULL REQUESTS'''
            # [entry["title"], entry["html_url"], entry["number"], entry["user"]["login"], entry["user"]["avatar_url"], entry["created_at"]]
            response = getPRs()
            if str(response.status_code)[0] == "4":
                endLoop = True
            new = lastPRs.compare(response.json())
            for entry in new:
                messageQueue.append({
                    "content": "<@791376513316552744>",
                    "username": "WPILIB Observer",
                    "avatar_url": WEBHOOK_PFP,
                    "embeds": [
                        {
                            "author": {
                                "name": str(entry["user"]["login"]),
                                "icon_url": str(entry["user"]["avatar_url"]) 
                            },
                            "title": "New PR #{}: {}".format(entry["number"], entry["title"]),
                            "url": str(entry["html_url"]),
                            "description": "{}\n{}\n{}".format(entry["body"], "TO-DO", entry["created_at"]),
                            "color": 0x26E23B,
                            "footer": {
                                "text": "Uptime: {}".format(fancyformat(lastUpdate-initTime))
                            }
                        }
                    ]
                })
        
        if updates % OBSERVE_ISSUE == 0 and False:
            '''ISSUES'''
            pass

        if updates % OBSERVE_RELEASE == 0 and False:
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
            log(f"[!]  | Sent Discord Message : Update {updates} : Response {response.status_code}")
            if str(response.status_code)[0] != "2":
                endLoop = True

    if RPI:
        with open(RPI_LED_PATH + "brightness", "w") as f:
            f.write(str((time.time() % 2 > 1) + 0))

    if endLoop:
        if RPI:
            with open(RPI_LED_PATH + "brightness", "w") as f:
                f.write("1")
        log("Issue occured, stopping program for safety! Final Uptime: {}".format(fancyformat(lastUpdate-initTime)))
        exit("Program stopped! Check logs!")


# with open(RPI_LED_PATH + "brightness", "w") as f:
#     f.write("0")
# time.sleep(0.05)
# with open(RPI_LED_PATH + "brightness", "w") as f:
#     f.write("1")
# time.sleep(0.05)





