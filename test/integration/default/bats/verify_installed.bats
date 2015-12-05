
@test 'ES is installed' {
  rpm -qa |grep elasticsearch
}

@test 'ES is Running' {
  ps -ef |grep java |grep elastic
}

@test 'ES status is green' {
  curl -XGET 'http://localhost:9200/_cluster/health?pretty=true'|grep green
}

@test 'logstash is installed' {
  rpm -qa |grep logstash
}
