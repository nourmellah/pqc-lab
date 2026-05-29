# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.box_check_update = false

  config.vm.synced_folder ".", "/vagrant", disabled: false

  machines = {
    "elk" =>      { ip: "192.168.56.10", memory: 4096, cpus: 2 },
    "baseline" => { ip: "192.168.56.20", memory: 2048, cpus: 2 },
    "hybrid" =>   { ip: "192.168.56.30", memory: 2048, cpus: 2 },
    "client" =>   { ip: "192.168.56.40", memory: 1024, cpus: 1 }
  }

  machines.each do |name, opts|
    config.vm.define name do |node|
      node.vm.hostname = name
      node.vm.network "private_network", ip: opts[:ip]

      node.vm.provider "virtualbox" do |vb|
        vb.name = "pqc-#{name}"
        vb.memory = opts[:memory]
        vb.cpus = opts[:cpus]
      end
    end
  end
end
