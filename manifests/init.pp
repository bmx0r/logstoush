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
        require  => Package['git'],
    }
    class { 'apache':
        default_vhost        => false,
    }
    apache::vhost { 'kibana.example.com':
        port          => '80',
        docroot       => '/opt/kibana',
        docroot_owner => 'apache',
        docroot_group => 'apache',
    }
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
            'name' => $::hostname
           },
           'index' => {
                       'number_of_replicas' => '0',
                       'number_of_shards'   => '5'
                      },
           'cluster' => {
                         'name' => 'ESClusterName',
                         },
          },
  status => 'enabled',
}

}
