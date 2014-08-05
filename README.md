POC ES+Kibana+logstash
=======================

Quick setup of a dev env
tested on : 
- Vagrant version 1.2.2,1.6.3
- VirtualBox 4.2.12,4.3.14

git clone https://github.com/bmx0r/logstoush

update the vagrant file to use an IP that is not in conflict with your network
`cd logstoush`
`git submodule init`
`git submodule update`
`git submodule foreach git submodule init`
`git submodule foreach git submodule update`
`vagrant up`

use your favorite browse to check :

http://192.168.3.10/src/index.html#/dashboard/file/default.json
http://192.168.3.10:9200/_plugin/head/
http://192.168.3.10:9200/_plugin/paramedic/index.html

Enjoy...
