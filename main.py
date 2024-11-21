import time, requests

'''settings'''

# Observing
TARGET_REPO = "wpilibsuite/allwpilib"
OBSERVE_EVERY = 3
OBSERVE_PR = 1
OBSERVE_ISSUE = 1
OBSERVE_RELEASE = 60
WEBHOOK = ""
WEBHOOK_PFP = "https://cdn.discordapp.com/attachments/1308965461550960761/1308985150989664316/observer_-_wpilib.png"

# Raspberry Pi
RPI = False
RPI_LED_PATH = "/sys/class/leds/ACT/"

# Verify
print("")
print(f"Checking {round(1/OBSERVE_EVERY*60*100)/100} times per minute (every {round(OBSERVE_EVERY*100)/100} seconds)")
print(f"  Checking for new PRs every {round(OBSERVE_PR*OBSERVE_EVERY*100)/100} seconds")
print(f"  Checking for new Issues every {round(OBSERVE_ISSUE*OBSERVE_EVERY*100)/100} seconds")
print(f"  Checking for new Releases every {round(OBSERVE_RELEASE*OBSERVE_EVERY*100)/100} seconds")
print(f"Raspberry Pi: {RPI}")
input("Press [Enter] to Start!")

'''init'''
print("  Starting...")
def msg(message):
    data = {"content":(str(message)),"username":"WPILIB Observer","avatar_url":WEBHOOK_PFP}
    response = requests.post(WEBHOOK,json=data)
    return response
def getPRs():      return requests.get(f"https://api.github.com/repos/{TARGET_REPO}/pulls"   ).json()
def getIssues():   return requests.get(f"https://api.github.com/repos/{TARGET_REPO}/issues"  ).json()
def getReleases(): return requests.get(f"https://api.github.com/repos/{TARGET_REPO}/releases").json()
def getCommits():  return requests.get(f"https://api.github.com/repos/{TARGET_REPO}/commits" ).json()

lastPRs = getPRs()
lastIssues = getIssues()
lastReleases = getReleases()
lastCommits = getCommits()



'''loop'''
print("  Loop starting...")
if RPI:
    with open(RPI_LED_PATH + "brightness", "w") as f: f.write("0")

lastUpdate = time.time()
while True:

    




# with open(RPI_LED_PATH + "brightness", "w") as f:
#     f.write("0")
# time.sleep(0.05)
# with open(RPI_LED_PATH + "brightness", "w") as f:
#     f.write("1")
# time.sleep(0.05)





