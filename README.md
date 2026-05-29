# PQC Web VM Lab

VM-based laboratory for measuring the operational impact of hybrid post-quantum TLS on a web infrastructure.

The lab compares a classical HTTPS service with a hybrid post-quantum TLS service and observes both through an ELK-based monitoring stack.

## Objectives

The project evaluates the feasibility of migrating web communications toward post-quantum cryptography by measuring:

- TLS handshake latency
- total request time
- service availability and HTTP success rate
- CPU and memory usage on the web servers
- logs and metrics collected through Elasticsearch and Kibana

The main comparison is between:

- a classical HTTPS Nginx web server
- an OQS-enabled hybrid TLS web server

## Architecture

| VM | IP address | Role |
|---|---:|---|
| `elk` | `192.168.56.10` | Elasticsearch + Kibana |
| `baseline` | `192.168.56.20` | Classical HTTPS Nginx server |
| `hybrid` | `192.168.56.30` | OQS/hybrid TLS Nginx server |
| `client` | `192.168.56.40` | Load generator and test runner |

Traffic flow:

```text
client VM ── HTTPS ──> baseline VM ── Filebeat/Metricbeat ──> elk VM
client VM ── hybrid TLS ──> hybrid VM ── Filebeat/Metricbeat ──> elk VM
```

The `client` VM generates the test traffic and writes CSV result files. The `baseline` and `hybrid` VMs expose web services and collect system/resource metrics. The `elk` VM stores and visualizes logs and metrics.

## Components

| Component | Purpose |
|---|---|
| Vagrant | Creates the virtual machines |
| Ansible | Installs and configures all services |
| Nginx | Classical HTTPS web server |
| OpenQuantumSafe Nginx | Hybrid post-quantum TLS web server |
| openquantumsafe/curl | Client used to force hybrid TLS groups |
| Elasticsearch | Stores logs and metrics |
| Kibana | Visualizes metrics, logs, and dashboards |
| Filebeat | Sends logs to Elasticsearch |
| Metricbeat | Sends CPU, memory, load, and system metrics |

## Requirements

On Fedora:

```bash
sudo dnf install -y vagrant VirtualBox ansible make unzip
```

VirtualBox kernel modules must be correctly installed and loaded.

Check VirtualBox status with:

```bash
VBoxManage --version
```

## Project setup

Start the VMs:

```bash
make up
```

Provision the infrastructure:

```bash
make provision
```

Verify the deployment:

```bash
make verify
```

Open Kibana:

```text
http://192.168.56.10:5601
```

## Experiment commands

Run the classical baseline test:

```bash
make baseline
```

Run the hybrid post-quantum TLS test:

```bash
make hybrid
```

Run both tests at the same time:

```bash
make both
```

Generate a summary of the CSV results:

```bash
make summarize
```

Destroy the lab:

```bash
make destroy
```

## Custom test duration

The test runner accepts four parameters:

```text
run-experiment.sh <baseline|hybrid> <duration_seconds> <concurrency> <interval_seconds>
```

Example: run a 15-minute baseline test with 5 parallel requests and 1-second intervals:

```bash
vagrant ssh client -c 'sudo /opt/pqc-lab/run-experiment.sh baseline 900 5 1'
```

Example: run a 15-minute hybrid test with the same profile:

```bash
vagrant ssh client -c 'sudo /opt/pqc-lab/run-experiment.sh hybrid 900 5 1'
```

Recommended initial test:

```bash
make baseline DURATION=60 CONCURRENCY=5 INTERVAL=1
make hybrid DURATION=60 CONCURRENCY=5 INTERVAL=1
make summarize
```

For stronger final measurements:

```bash
make clean-results
make baseline DURATION=43200 CONCURRENCY=5 INTERVAL=5
make hybrid DURATION=43200 CONCURRENCY=5 INTERVAL=5
make summarize
```

## Result files

Test results are saved in:

```text
./results/
```

The request timing CSV files contain:

```csv
timestamp,http_code,time_total,time_connect,time_appconnect,time_starttransfer,size_download
```

Important columns:

| Column | Meaning |
|---|---|
| `http_code` | HTTP response code |
| `time_connect` | TCP connection time |
| `time_appconnect` | TLS handshake time |
| `time_starttransfer` | Time until first byte |
| `time_total` | Total request duration |
| `size_download` | Response size in bytes |

Resource CSV files contain:

```csv
timestamp,cpu_percent,mem_used_mb,mem_total_mb,mem_percent,load_1m
```

Important columns:

| Column | Meaning |
|---|---|
| `cpu_percent` | CPU usage measured from `/proc/stat` |
| `mem_used_mb` | Used memory in MB |
| `mem_total_mb` | Total memory in MB |
| `mem_percent` | Memory usage percentage |
| `load_1m` | One-minute load average |

Typical generated files:

```text
baseline-YYYYMMDD-HHMMSS.csv
baseline-YYYYMMDD-HHMMSS.meta
baseline-resources-YYYYMMDD-HHMMSS.csv
hybrid-YYYYMMDD-HHMMSS.csv
hybrid-YYYYMMDD-HHMMSS.meta
hybrid-resources-YYYYMMDD-HHMMSS.csv
summary.csv
```

## Summary output

The summary script reads all request and resource CSV files and creates:

```text
results/summary.csv
```

The summary includes:

- request count
- success rate
- average TLS handshake time
- median TLS handshake time
- 95th percentile TLS handshake time
- average total request time
- 95th percentile total request time
- average CPU usage
- median CPU usage
- average memory usage
- average load

Use this file for tables in the report.

## TLS comparison logic

The baseline server uses classical HTTPS.

The hybrid server uses an OQS-enabled Nginx endpoint. The client forces the hybrid group during tests, for example:

```text
X25519MLKEM768
```

The verification command prints the negotiated TLS line when available. A successful hybrid verification should show a TLS 1.3 connection with a hybrid group such as:

```text
TLSv1.3 / TLS_AES_256_GCM_SHA384 / X25519MLKEM768
```

The main performance metric for TLS negotiation is:

```text
time_appconnect
```

This value measures the TLS handshake duration from the client side.

## Kibana usage

Kibana is available at:

```text
http://192.168.56.10:5601
```

Recommended filters for logs:

```text
server.mode : "baseline"
```

```text
server.mode : "hybrid"
```

Recommended filters for host metrics:

```text
host.name : "baseline"
```

```text
host.name : "hybrid"
```

Recommended dashboard panels:

| Panel | Data source | Filter |
|---|---|---|
| Baseline CPU | Metricbeat | `host.name : "baseline"` |
| Hybrid CPU | Metricbeat | `host.name : "hybrid"` |
| Baseline memory | Metricbeat | `host.name : "baseline"` |
| Hybrid memory | Metricbeat | `host.name : "hybrid"` |
| Baseline log volume | Filebeat | `server.mode : "baseline"` |
| Hybrid log volume | Filebeat | `server.mode : "hybrid"` |
| Baseline errors | Filebeat | `server.mode : "baseline" and message : "*error*"` |
| Hybrid errors | Filebeat | `server.mode : "hybrid" and message : "*error*"` |

## Dashboard import

Place exported Kibana dashboards in:

```text
kibana/exports/
```

The files must use the `.ndjson` extension.

Import dashboards manually with:

```bash
make import-dashboards
```

Dashboard import also runs during ELK provisioning if NDJSON files are present.

## Recommended benchmark workflow

For final results, use isolated tests first:

```bash
make baseline DURATION=900 CONCURRENCY=5 INTERVAL=1
make hybrid DURATION=900 CONCURRENCY=5 INTERVAL=1
make summarize
```

Use simultaneous tests only as an additional demo scenario:

```bash
make both DURATION=900 CONCURRENCY=5 INTERVAL=1
make summarize
```

Isolated tests are better for the report because the classical and hybrid services do not compete for host resources at the same time.

## Interpretation guide

The results should be interpreted as an operational comparison between classical HTTPS and hybrid post-quantum TLS.

A typical conclusion should discuss:

- whether both services returned successful HTTP responses
- how much `time_appconnect` increased in hybrid mode
- whether `time_total` increased proportionally
- whether CPU or memory increased on the hybrid VM
- whether the hybrid service remained stable under load

The project does not only measure cryptographic primitives in isolation. It evaluates the impact of hybrid post-quantum TLS inside a monitored web infrastructure.

## Useful commands

Check VM status:

```bash
vagrant status
```

SSH into the ELK VM:

```bash
vagrant ssh elk
```

SSH into the baseline server:

```bash
vagrant ssh baseline
```

SSH into the hybrid server:

```bash
vagrant ssh hybrid
```

SSH into the client VM:

```bash
vagrant ssh client
```

Check Elasticsearch:

```bash
curl http://192.168.56.10:9200
```

Check Kibana status:

```bash
curl http://192.168.56.10:5601/api/status
```

Check baseline HTTPS:

```bash
curl -k https://192.168.56.20
```

Check hybrid TLS from the client VM:

```bash
vagrant ssh client -c 'docker run --rm openquantumsafe/curl curl -vk https://192.168.56.30:4433 --curves X25519MLKEM768'
```

## Troubleshooting

### Elasticsearch does not start

Check the service logs:

```bash
vagrant ssh elk -c 'sudo journalctl -xeu elasticsearch.service --no-pager | tail -120'
```

Check the Elasticsearch log file:

```bash
vagrant ssh elk -c 'sudo tail -200 /var/log/elasticsearch/pqc-web-lab.log'
```

### Kibana is not ready

Check the API status:

```bash
curl http://192.168.56.10:5601/api/status
```

Check Kibana logs:

```bash
vagrant ssh elk -c 'sudo journalctl -xeu kibana.service --no-pager | tail -120'
```

### No CSV files appear in `results/`

Check the shared folder from the client VM:

```bash
vagrant ssh client -c 'ls -lah /vagrant/results'
```

Run a short test:

```bash
make baseline DURATION=60 CONCURRENCY=2 INTERVAL=1
```

### Hybrid verification fails

Check that the OQS container is running on the hybrid VM:

```bash
vagrant ssh hybrid -c 'sudo docker ps'
```

Check its logs:

```bash
vagrant ssh hybrid -c 'sudo docker logs oqs-nginx --tail 50'
```

## Cleanup

Stop all VMs:

```bash
vagrant halt
```

Destroy all VMs:

```bash
make destroy
```
