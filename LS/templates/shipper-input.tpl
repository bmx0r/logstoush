input {
  file {
    path => "/var/log/messages"
    type => "syslog-local"
  }

  tcp {
    port => 1514
    type => syslog
  }
  udp {
    port => 1514
    type => syslog
  }
}
