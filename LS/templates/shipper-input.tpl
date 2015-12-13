input {
  file {
    path => "/var/log/messages"
    type => "syslog-local"
  }

  syslog {
    type => "syslog"
    port => "1514"
  }
}
