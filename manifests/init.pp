stage { pre: before => Stage[main] }

node my-apache{
    package {'git':
        ensure => present;
    }

    vcsrepo { '/opt/kibana':
        ensure   => present,
        provider => git,
        source   => 'https://github.com/elasticsearch/kibana.git',
        owner    => 'apache',
        group    =>  'apache',
        require  => [Package['git'],Class['apache']],
    }
    class { 'apache':
        default_vhost        => false,
    }
    apache::vhost { 'kibana.example.com':
        port          => '80',
        docroot       => '/opt/kibana',
        docroot_owner => 'apache',
        docroot_group => 'apache',
        proxy_pass => [
                        { 'path' => '/es', 'url' => "balancer://es00/" },
                      ],
    }
    apache::balancer { 'es00': 
        collect_exported  => 'False',
        proxy_set         => {'stickysession' => 'JSESSIONID'},
    }
    apache::balancermember { "${::fqdn}-es01":
        balancer_cluster => 'es00',
        url              => "http://192.168.3.100:9200",
        options          => ['ping=5', 'disablereuse=on', 'retry=5', 'ttl=120'],
      }

    Package['git'] -> Class['apache'] 
}
node my-es{
    file{'espackage':
      path    => '/tmp/elasticsearch-1.3.1.noarch.rpm',
      source  => '/etc/puppet/files/elasticsearch-1.3.1.noarch.rpm',
      ensure  => 'present',
    }
    file{'logstashpackage':
      path    => '/tmp/logstash-1.4.2-1_2c0f5a1.noarch.rpm',
      source  => '/etc/puppet/files/logstash-1.4.2-1_2c0f5a1.noarch.rpm',
      ensure  => 'present',
    }
    file{'logstashcontribpackage':
      path    => '/tmp/logstash-contrib-1.4.2-1_efd53ef.noarch.rpm',
      source  => '/etc/puppet/files/logstash-contrib-1.4.2-1_efd53ef.noarch.rpm',
      ensure  => 'present',
    }
# elasticSearch
class { 'elasticsearch':
  java_install  => true,
  manage_repo   => false,
  package_url => 'file:/tmp/elasticsearch-1.3.1.noarch.rpm',
  #repo_version  => '1.1',
  datadir       => '/var/lib/elasticsearch-data'
}
elasticsearch::instance { 'my-es-01':
  config => {
          'node' => {
            'name' => 'es1'
           },
           'index' => {
                       'number_of_replicas' => '2',
                       'number_of_shards'   => '5'
                      },
           'cluster' => {
                         'name' => 'ESClusterName',
                         },
          },
  status => 'enabled',
}
elasticsearch::instance { 'my-es-02':
  config => {
          'node' => {
            'name' => 'es2'
           },
           'index' => {
                       'number_of_replicas' => '2',
                       'number_of_shards'   => '5'
                      },
           'cluster' => {
                         'name' => 'ESClusterName',
                         },
          },
  status => 'enabled',
}
# install logstash
$config_hash = {
        'LS_USER' => 'logstash',
        'LS_GROUP' => 'logstash',
        'START' => 'true',
       }
        
class { 'logstash':
  init_defaults => $config_hash,
  package_url         => 'file:/tmp/logstash-1.4.2-1_2c0f5a1.noarch.rpm',
  manage_repo  => false,
  status => 'disabled',
  #  install_contrib     => true,
  #contrib_package_url => 'file:/tmp/logstash-contrib-1.4.2-1_efd53ef.noarch.rpm'
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
    
}
