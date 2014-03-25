import os

hosts = ["10.78.56.11",
    "10.78.56.8",
    "10.78.56.6",
    "10.78.56.12",
    "10.78.56.10",
    "10.78.56.7",
    "10.78.56.13"]

for host in hosts:
  os.system("scp zinc.deb decatech@{0}:~/".format(host))
  os.system("ssh decatech@{0} 'sudo dpkg -r zinc; sudo dpkg -i zinc.deb'".format(host))
