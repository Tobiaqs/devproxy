# Add this script to root's crontab as such:
# * * * * * python3 /home/me/devproxy/cron/update_wg_ip_addresses.py
# 
# The location of proxy_https_safelist_wg.conf will be automatically found based
# on the path of this script.
# This script has to be on root's crontab, as it needs to read the WireGuard configuration.


from pathlib import Path
import subprocess

devproxy_root = Path(__file__).parent.parent

proxy_https_safelist_wg = devproxy_root / "proxy_https_safelist_wg.conf"

p = subprocess.run(["wg"], capture_output=True)
lines = p.stdout.decode("utf-8").split("\n")

ips = set()

for line in lines:
  if line.startswith("  endpoint: "):
    ips.add(line[12:].split(":")[0])

current_config = open(proxy_https_safelist_wg, "r").read()

output = """# The contents of this file are automatically generated by update_wg_ip_addresses.py
# Do not edit this file manually, your changes will be overwritten
"""

for ip in sorted(ips):
  output += f"allow {ip};\n"

if output != current_config:
  open(proxy_https_safelist_wg, "w").write(output)
  subprocess.run(["docker", "compose", "exec", "nginx", "nginx", "-s", "reload"], cwd=devproxy_root)
