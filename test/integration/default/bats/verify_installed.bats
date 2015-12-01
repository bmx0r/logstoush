
@test 'ES is installed' {
  rpm -qa |grep elasticsearch
}

@test 'ES is Running' {
  ps -ef |grep java |grep elastic
}
@test 'logstash is installed' {
  rpm -qa |grep logstash
}
