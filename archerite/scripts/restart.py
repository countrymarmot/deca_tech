import os

hosts = ["10.78.56.11",
    "10.78.56.8",
    "10.78.56.6",
    "10.78.56.12",
    "10.78.56.10",
    "10.78.56.7",
    "10.78.56.13"]

controller = "10.78.56.9"
os.system("ssh decatech@{0} 'redis-cli flushall'".format(controller))
os.system("ssh decatech@{0} \"killall celeryd; killall tmux; tmux new-session -d 'cd ~/archerite; celeryd --app=celeryapp -Q controller'; tmux new-window -d 'cd ~/archerite; python onyxcontroller.py'\"".format(controller))

for host in hosts:
  os.system("ssh decatech@{0} \"killall zinc; killall tmux; tmux new-session -d 'cd ~/archerite; celeryd -c 1 --app=celeryapp'\"".format(host))
