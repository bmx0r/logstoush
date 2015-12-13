$config_hashES = {
  'ES_USER' => 'elasticsearch',
  'ES_GROUP' => 'elasticsearch',
}

class { 'elasticsearch':
  package_url => 'https://download.elasticsearch.org/elasticsearch/release/org/elasticsearch/distribution/rpm/elasticsearch/2.1.0/elasticsearch-2.1.0.rpm',
  java_install => true,
  init_defaults => $config_hashES,
}

elasticsearch::instance { 'es-01': 
  datadir => '/app/data/elasticsearch-data',
  config => { 'node.name' => $::hostname,
              'cluster.name' => 'ELK-cluster',
              'index.number_of_replicas' => '0',
            }
}




$config_hash = {
  'LS_USER' => 'logstash',
  'LS_GROUP' => 'logstash',
}
class { 'logstash':
  package_url => 'https://download.elastic.co/logstash/logstash/packages/centos/logstash-2.1.0-1.noarch.rpm',
  java_install => true,
  init_defaults => $config_hash,
}
  logstash::configfile { 'input_syslog':
   content => '
input {
       syslog {
              type => "syslog"
              port => "5544"
              }
      }
',
      order   => 10,
       }
