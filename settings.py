OBSERVE_EVERY = 3
OBSERVE_PR = 1
OBSERVE_ISSUE = 1
OBSERVE_RELEASE = 60



print("")
print(f"Checking {round(1/OBSERVE_EVERY*60*100)/100} times per minute (every {round(OBSERVE_EVERY*100)/100} seconds)")
print(f"  Checking for new PRs every {round(OBSERVE_PR*OBSERVE_EVERY*100)/100} seconds")
print(f"  Checking for new Issues every {round(OBSERVE_ISSUE*OBSERVE_EVERY*100)/100} seconds")
print(f"  Checking for new Releases every {round(OBSERVE_RELEASE*OBSERVE_EVERY*100)/100} seconds")