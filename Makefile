DURATION ?= 300
CONCURRENCY ?= 5
INTERVAL ?= 1

.PHONY: up provision verify baseline hybrid both summarize pull-results import-dashboards stop destroy status

up:
	vagrant up --no-provision

provision:
	ansible-playbook -i inventory.ini site.yml

verify:
	./scripts/verify.sh

baseline:
	mkdir -p results
	vagrant ssh baseline -c 'sudo /opt/pqc-lab/collect-resources.sh baseline $(DURATION) $(INTERVAL)' &
	vagrant ssh client -c 'sudo /opt/pqc-lab/run-experiment.sh baseline $(DURATION) $(CONCURRENCY) $(INTERVAL)'
	wait

hybrid:
	mkdir -p results
	vagrant ssh hybrid -c 'sudo /opt/pqc-lab/collect-resources.sh hybrid $(DURATION) $(INTERVAL)' &
	vagrant ssh client -c 'sudo /opt/pqc-lab/run-experiment.sh hybrid $(DURATION) $(CONCURRENCY) $(INTERVAL)'
	wait

both:
	mkdir -p results
	vagrant ssh baseline -c 'sudo /opt/pqc-lab/collect-resources.sh baseline $(DURATION) $(INTERVAL)' &
	vagrant ssh hybrid -c 'sudo /opt/pqc-lab/collect-resources.sh hybrid $(DURATION) $(INTERVAL)' &
	vagrant ssh client -c 'sudo /opt/pqc-lab/run-both.sh $(DURATION) $(CONCURRENCY) $(INTERVAL)'
	wait

summarize:
	vagrant ssh client -c 'sudo python3 /opt/pqc-lab/summarize-results.py /vagrant/results /vagrant/results/summary.csv'

pull-results:
	mkdir -p results
	vagrant ssh client -c 'sudo tar -C /opt/pqc-lab/results -czf /tmp/pqc-results.tgz .'
	vagrant ssh-config client > .client-ssh-config
	scp -F .client-ssh-config client:/tmp/pqc-results.tgz results/pqc-results.tgz
	tar -xzf results/pqc-results.tgz -C results
	@echo "[OK] Results copied to ./results"

import-dashboards:
	./scripts/import-dashboards.sh

status:
	vagrant status

stop:
	vagrant halt

destroy:
	vagrant destroy -f
