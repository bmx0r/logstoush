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
# elasticSearch
class { 'elasticsearch':
  java_install  => true,
  manage_repo   => true,
  repo_version  => '1.1',
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

}
