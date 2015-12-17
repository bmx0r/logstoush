output {
  stdout { codec => rubydebug }
  redis {
    data_type => list
    key => "logstash"
  }
}
