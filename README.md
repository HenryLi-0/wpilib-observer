# wpilib-observer

![](</wpilib observer 128x128.png>)

(the name and picture is a reference to a late 2000s/early 2010s sci-fi tv show)


### Goal

The Observer was created to send a message on Discord whenever a new PR or Release is created for a specific repository, using the GitHub API and Discord Webhooks! (since, as far as i researched, its not possible to setup webhooks directly for repositories you dont have administrative permissions in?) Currently still looking for any bugs or weird behaviors...


### Setup

Here's steps I used for a `Raspberry Pi Zero 2W` (realistically, this should be able to run on anything with python and an unblocked internet access, and optimally stay online)

1. `scp` the file from the computer to the raspberry pi (use the actual file location on the raspberry pi for the other steps)
2. `ssh` into the rasbperry pi with Windows Powershell
3. `nano main.py` and modify settings if needed (`TARGET_REPO`, `WEBHOOK` and `RPI`)
4. `sudo nohup python main.py &` to start running the script in the background
5. should run continuously until something breaks (check observer-logs to see dates and times and stuff)
   - use `ps aux | grep python` to check if its running
   - use `sudo kill [PID]` to kill the process (PID is in the number in the second column)


### Useful Github API Links and Docs

- https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-pull-requests
- https://api.github.com/repos/wpilibsuite/allwpilib/issues
- https://api.github.com/repos/wpilibsuite/allwpilib/pulls