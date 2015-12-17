output{
  if "_grokparsefailure" in [tags] {
      file { path => "/var/log/logstash/failed_syslog_events-%{+YYYY-MM-dd}" }
  }
  stdout { codec => rubydebug }
  elasticsearch {
    hosts => "127.0.0.1"
 }
}
