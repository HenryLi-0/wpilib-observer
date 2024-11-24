import time, requests, os, math

'''settings'''

# Observing
TARGET_REPO = "microsoft/vscode" #"wpilibsuite/allwpilib"
OBSERVE_PR = 2*60
OBSERVE_ISSUE = 2*60
OBSERVE_RELEASE = 60*60
WEBHOOK = ""
WEBHOOK_PFP = "https://cdn.discordapp.com/attachments/1308965461550960761/1308985150989664316/observer_-_wpilib.png"
RELEASE_PING = "<@&797923529655189515>"

ERROR_PING = "<@791376513316552744>"
MAX_ERRORS = 1

# Raspberry Pi
RPI = False
RPI_LED_PATH = "/sys/class/leds/ACT/"

if RPI:
    with open(RPI_LED_PATH + "brightness", "w") as f:
        f.write("1")

# Setup logs
LOG_PATH = os.path.join(f"observer-logs-{round(time.time())}.txt")
with open(LOG_PATH, "w") as f:
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
# log( "     | Press [Enter] to Start!")
# if not(input("")) == "":
#     log( "     |  | User Cancel!")
#     exit("Cancelled!") 

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
    return "{:01}:{:02}:{:02}:{:02}:{:02}".format(round(y),round(d),round(h),round(m),round(s))

def msg(message):
    data = {"content":(str(message)),"username":"WPILIB Observer","avatar_url":WEBHOOK_PFP}
    return requests.post(WEBHOOK,json=data)
def requestsGet(target):
    response = requests.head("https://api.github.com/rate_limit")
    if response.status_code == 200:
        limits = response.json()
        if limits['resources']['core']['remaining'] == 0:
            wait = math.floor(limits['resources']['core']['reset']) - math.floor(time.time()) + 5
            log("[!]  | Rate Limited! Sleeping for {} seconds...".format(wait))
            time.sleep(wait)
    return requests.get(target)
def getOpenPRs():
    log("     | Fetch Open PRs...")
    response = requestsGet(f"https://api.github.com/repos/{TARGET_REPO}/pulls?state=open")
    log("     |  | Response: {}".format(response.status_code))
    return response
def getClosedPRs():
    log("     | Fetch Closed PRs...")
    response = requestsGet(f"https://api.github.com/repos/{TARGET_REPO}/pulls?state=closed")
    log("     |  | Response: {}".format(response.status_code))
    return response
def getIssues():
    log("     | Fetch Issues...")
    response = requestsGet(f"https://api.github.com/repos/{TARGET_REPO}/issues"  )
    log("     |  | Response: {}".format(response.status_code))
    return response
def getReleases():
    log("     | Fetch Releases...")
    response = requestsGet(f"https://api.github.com/repos/{TARGET_REPO}/releases")
    log("     |  | Response: {}".format(response.status_code))
    return response

class Storage:
    def __init__(self, data, startFromInit = True):
        self.ids = []
        for entry in data: self.ids.append(entry["id"])
        if startFromInit:
            self.startFromInit = True
            self.starting = data[0]["number"]
    def compare(self, newdata):
        temp = []
        for entry in newdata: temp.append(entry["id"])
        new = []
        for item in temp:
            if not(item in self.ids): 
                if not(self.startFromInit) or (self.startFromInit and entry["number"] > self.starting):
                    new.append(entry)
        self.ids = temp
        return new
        

log("[!] FETCHING START DATA...")
lastOpenPRs = Storage(getOpenPRs().json())
lastClosedPRs = Storage(getClosedPRs().json(), False)
lastReleases = Storage(getReleases().json())

'''loop'''
log("[!] LOOP STARTING...")
if RPI:
    with open(RPI_LED_PATH + "brightness", "w") as f:
        f.write("0")

initTime = math.floor(time.time())
lastUpdate = math.floor(time.time())
updates = 0
messageQueue = []
errors = 0

requests.post(WEBHOOK,json={"content":"The WPILIB Observer is observing!","username":"WPILIB Observer","avatar_url":WEBHOOK_PFP})

while True:
    now = math.floor(time.time())
    if now - lastUpdate >= 1:
        lastUpdate = now
        if updates % OBSERVE_PR == 0:
            '''PULL REQUESTS'''
            '''OPEN PRS'''
            response = getOpenPRs()
            if str(response.status_code) != "200": errors += 1
            new = lastOpenPRs.compare(response.json())
            for entry in new:
                messageQueue.append({
                    "content": "<@791376513316552744>",
                    "username": "WPILIB Observer", "avatar_url": WEBHOOK_PFP,
                    "embeds": [{
                            "author": {"name": str(entry["user"]["login"]), "icon_url": str(entry["user"]["avatar_url"])},
                            "title": "New PR #{}: {}".format(entry["number"], entry["title"]),
                            "url": str(entry["html_url"]),
                            "description": "{}\n{}\n{}".format(entry["body"], "Created at " + entry["created_at"]),
                            "color": 0x26E23B, "footer": {"text": "Uptime: {}".format(fancyformat(lastUpdate-initTime))}
                        }]
                })

            '''CLOSED PRS'''
            response = getClosedPRs()
            if str(response.status_code) != "200": errors += 1
            new = lastOpenPRs.compare(response.json())
            for entry in new:
                if str(entry["merged_at"]) != "null": # Merged!                
                    messageQueue.append({
                        "content": "",
                        "username": "WPILIB Observer", "avatar_url": WEBHOOK_PFP,
                        "embeds": [{
                                "author": {"name": str(entry["user"]["login"]), "icon_url": str(entry["user"]["avatar_url"])},
                                "title": "Merged PR #{}: {}".format(entry["number"], entry["title"]),
                                "url": str(entry["html_url"]),
                                "description": "{}\n{}\n{}".format(entry["body"], "Created at " + entry["created_at"]),
                                "color": 0xD525E5, "footer": {"text": "Uptime: {}".format(fancyformat(lastUpdate-initTime))}
                            }]
                    })
                else: # Closed!
                    messageQueue.append({
                        "content": "",
                        "username": "WPILIB Observer", "avatar_url": WEBHOOK_PFP,
                        "embeds": [{
                                "author": {"name": str(entry["user"]["login"]), "icon_url": str(entry["user"]["avatar_url"])},
                                "title": "Closed PR #{}: {}".format(entry["number"], entry["title"]),
                                "url": str(entry["html_url"]),
                                "description": "{}\n{}".format("Created at " + entry["created_at"]),
                                "color": 0xE63226, "footer": {"text": "Uptime: {}".format(fancyformat(lastUpdate-initTime))}
                            }]
                    })
        if updates % OBSERVE_RELEASE == 0:
            '''RELEASES'''
            response = getReleases()
            if str(response.status_code) != "200": errors += 1
            new = lastReleases.compare(response.json())
            for entry in new:
                if str(entry["prerelease"]) == "false":
                    messageQueue.append({
                        "content": "",
                        "username": "WPILIB Observer", "avatar_url": WEBHOOK_PFP,
                        "embeds": [{
                                "author": {"name": str(entry["author"]["login"]), "icon_url": str(entry["author"]["avatar_url"])},
                                "title": "New Release: {}".format(entry["name"]),
                                "url": str(entry["html_url"]),
                                "description": "{}\n{}\n{}".format("Wake up" + RELEASE_PING + ", there's a new release!", entry["body"], "Created at " + entry["created_at"]),
                                "color": 0xffaa00, "footer": {"text": f"Uptime: {fancyformat(lastUpdate-initTime)}"}
                            }]
                    })
                else:
                    messageQueue.append({
                        "content": "",
                        "username": "WPILIB Observer", "avatar_url": WEBHOOK_PFP,
                        "embeds": [{
                                "author": {"name": str(entry["author"]["login"]), "icon_url": str(entry["author"]["avatar_url"])},
                                "title": "New Prerelease: {}".format(entry["name"]),
                                "url": str(entry["html_url"]),
                                "description": "{}\n{}".format(entry["body"], "Created at " + entry["created_at"]),
                                "color": 0x9F8859, "footer": {"text": f"Uptime: {fancyformat(lastUpdate-initTime)}"}
                            }]
                    })
        updates += 1

    if len(messageQueue) > 0:
        for data in messageQueue:
            response = requests.post(WEBHOOK,json=data)
            log(f"[!]  | Sent Discord Message : Update {updates} : Response {response.status_code}")
            if str(response.status_code)[0] != "2":
                errors += 1
        messageQueue = []

    if RPI:
        with open(RPI_LED_PATH + "brightness", "w") as f:
            f.write(str((time.time() % 2 > 1) + 0))

    if errors >= MAX_ERRORS:
        if RPI:
            with open(RPI_LED_PATH + "brightness", "w") as f:
                f.write("1")
        log("Allowed errors exceeded! Stopping program for safety! Final Uptime: {}".format(fancyformat(lastUpdate-initTime)))
        requests.post(WEBHOOK,json={"content":"{} The WPILIB Observer has stopped observing (check logs)!".format(ERROR_PING),"username":"WPILIB Observer","avatar_url":WEBHOOK_PFP})
        exit("Program stopped! Check logs!")