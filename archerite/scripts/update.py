"""
Update the onyx deploy.

Currently only works for archerite v1.
"""
import os


hosts = ["10.78.56.4"]
for host in hosts:
  os.system("ssh decatech@{0} 'rm -rf archerite'".format(host))
  os.system("scp -r archerite decatech@{0}:~/".format(host))
  os.system("ssh decatech@{0} \"killall zinc; killall tmux; tmux new-session -d 'cd ~/archerite; celeryd -c 1 --app=celeryapp'\"".format(host))

controller = "10.78.56.3"
os.system("ssh decatech@{0} 'rm -rf archerite'".format(controller))
os.system("ssh decatech@{0} 'redis-cli flushall'".format(controller))
os.system("scp -r archerite decatech@{0}:~/".format(controller))
os.system("ssh decatech@{0} \"killall celeryd; killall tmux; tmux new-session -d 'cd ~/archerite; celeryd --app=celeryapp -Q controller'; tmux new-window -d 'cd ~/archerite; python onyxcontroller.py'\"".format(controller))
