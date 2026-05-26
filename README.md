**PQC Web VM Lab**  
VM-based lab for measuring the operational impact of post-quantum/hybrid TLS on a web infrastructure.  
The lab compares:  
- **Baseline web server**: normal Nginx HTTPS  
- **Hybrid web server**: OQS-enabled Nginx endpoint using hybrid TLS from the OpenQuantumSafe demo image  
- **ELK observability**: Elasticsearch + Kibana  
- **Beats telemetry**: Filebeat + Metricbeat on the monitored VMs  
- **Client/load generator**: traffic scripts that collect CSV measurements such as time_appconnect and time_total  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCkJfE1pYGfHAiAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrse4dwF6o2O55YAAAAASUVORK5CYII=)  
**Architecture**  
| | | |  
|-|-|-|  
| **VM** | **IP** | **Role** |   
| elk | 192.168.56.10 | Elasticsearch + Kibana |   
| baseline | 192.168.56.20 | Classical HTTPS Nginx |   
| hybrid | 192.168.56.30 | OQS/hybrid TLS Nginx service |   
| client | 192.168.56.40 | Test runner + OQS curl client |   
   
Traffic flow:  
client VM ── HTTPS ──> baseline VM ── Filebeat/Metricbeat ──> elk VM  
 client VM ── hybrid TLS ──> hybrid VM ── Filebeat/Metricbeat ──> elk VM  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AUBBAsUfyNTCi9VwgEA3sWGAjJK2CbjNzVGcAAPzFtapV7V9PAAB47X4AEW4ELQDBN+AAAAAASUVORK5CYII=)  
**Requirements on the host**  
On Fedora:  
sudo dnf install -y vagrant VirtualBox ansible make unzip  
   
You also need the VirtualBox kernel modules working.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSNhRAF6EPYDLhGADSywEZJWQZeZ2aszAAD+4l6rrTq+ngAA8Nr1AIWsBDYDm5cLAAAAAElFTkSuQmCC)  
**Quick start**  
unzip pqc-web-vm-ansible-lab.zip  
 cd pqc-web-vm-ansible-lab  
 make up  
 make provision  
 make verify  
   
Open Kibana:  
http://192.168.56.10:5601  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSdYxZ4/mJjEsxE8W8GbCFuCLTOzVXsAAPzFuVZ3dXw9AQDgtesBxPEF3bv7x0IAAAAASUVORK5CYII=)  
**Run experiments**  
Baseline only:  
make baseline  
   
Hybrid only:  
make hybrid  
   
Both at the same time:  
make both  
   
Summarize CSV results:  
make summarize  
   
Copy results from the client VM to the host:  
make pull-results  
   
Results are copied to:  
./results/  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4NIGRTPXNaQBrWMGbCFuCLTOzV2cAAPzFvVZbdXw9AQDgtesBhZQEOYZGgUEAAAAASUVORK5CYII=)  
**Custom test duration/concurrency**  
From the host:  
vagrant ssh client -c 'sudo /opt/pqc-lab/run-experiment.sh baseline 3600 5 1'  
 vagrant ssh client -c 'sudo /opt/pqc-lab/run-experiment.sh hybrid 3600 5 1'  
   
Arguments:  
run-experiment.sh <baseline|hybrid> <duration_seconds> <concurrency> <pause_seconds>  
   
Example:  
sudo /opt/pqc-lab/run-experiment.sh hybrid 300 5 1  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCkLfE07YGfHAiAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrse4eQF6VhvmPsAAAAASUVORK5CYII=)  
**Important Kibana fields**  
Filebeat events include these fields:  
server.mode: baseline  
 server.mode: hybrid  
 service.name: baseline-nginx  
 service.name: hybrid-oqs-nginx  
   
Recommended Kibana filters:  
Baseline logs:  
server.mode : "baseline"  
   
Hybrid logs:  
server.mode : "hybrid"  
   
Metricbeat host metrics can be separated by:  
host.name : "baseline"  
 host.name : "hybrid"  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4NIGhrOTvaQBrWMGbCFuCLTOzV2cAAPzFvVZbdXw9AQDgtesBhYQEO+64Y8AAAAAASUVORK5CYII=)  
**Dashboard import**  
Place exported Kibana .ndjson files here:  
kibana/exports/  
   
Then run:  
make import-dashboards  
   
During provisioning, the ELK role also attempts to import any NDJSON dashboards found in kibana/exports/.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OMQ2AABAAsSPBCj5fFgpQwYwEZiywEZJWQZeZ2ao9AAD+4lyruzq+ngAA8Nr1AMTRBeEgNK9YAAAAAElFTkSuQmCC)  
**Why this design**  
The project description asks for a web-infrastructure experiment, not only a crypto microbenchmark:  
- simulate secured web traffic  
- compare classical TLS and hybrid PQC TLS  
- measure handshake latency  
- observe CPU/memory/logs in real time with ELK  
Therefore, the main experiment is based on real HTTP/TLS endpoints instead of only timing cryptographic algorithms in isolation.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAM0lEQVR4nO3OMQ0AIAwAwdIgBKl1gjacsGCAiZDcTT9+q6oRETMAAPjF6ify6QYAADdyA9Y0AypN+bdfAAAAAElFTkSuQmCC)  
**Notes about the hybrid server**  
For reliability, the hybrid VM runs the official OpenQuantumSafe Nginx demo image inside a dedicated VM.  
This keeps the **infrastructure VM-based** while avoiding a long and fragile source build of OpenSSL + OQS Provider + Nginx during every demo setup.  
The client VM uses openquantumsafe/curl to force a hybrid group such as:  
X25519MLKEM768  
   
The verification script prints the negotiated TLS line when available.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4NIGJjPWxpgGsYQVvImwJtszMXp0BAPAX91pt1fH1BACA164HhZwEOFrXVOsAAAAASUVORK5CYII=)  
**Destroy lab**  
make destroy  
   
