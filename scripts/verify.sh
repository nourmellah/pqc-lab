#!/usr/bin/env bash
set -euo pipefail

echo "[+] Running verification from client VM"
vagrant ssh client -c 'sudo /opt/pqc-lab/verify-project.sh'
