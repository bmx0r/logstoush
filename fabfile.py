from fabric.api import *
from fabtools.vagrant import vagrant
from fabtools import require

env.roledefs.update({
    'kibana_node': ['www1', 'www2'],
    'elasticsearch_nodes': ['default'],
    'logstash_shipper_node': ['lgss'],
    'logstash_indexer_node': ['lgsi'],
    'redis_node': ['redis1'],
})



env.GIT_REPO_URL="git://github.com/bmx0r/vimconfig.git"
java_pkg="java-1.8.0-openjdk"

@task
def uname():
    run('uname -a')


def _is_pkg_installed(pkg_name):
    with settings(warn_only=True):
        rc = sudo('rpm -qa | grep %s' % pkg_name)
    if rc.failed:
        return False
    else:
        print "pkg %s already installed" % pkg_name
        return True

@task
def install_es_package(with_repo=True, with_java=True):
    if not _is_pkg_installed('elasticsearch'):
        if with_repo:
            sudo('rpm --import https://packages.elastic.co/GPG-KEY-elasticsearch')
            upl = put(local_path='ES/repofile/elasticsearch.repo',remote_path='/etc/yum.repos.d/',use_sudo=True)
            if upl.failed:
                exit(1)
            sudo('yum repolist')
        sudo('yum install elasticsearch -y')
    if not _is_pkg_installed(java_pkg):
        sudo('yum install -y %s' % java_pkg)

@task
def config_es():
    """Not implemented we start with default"""

@task
def enable_es():
    sudo('chkconfig --add elasticsearch')
    sudo('chkconfig elasticsearch on')
    sudo('service elasticsearch start')



@roles('elasticsearch_nodes')
@task
def setup_ES():
    install_es_package()
    config_es()
    enable_es()


########################################
#LOGSTASH

@task
def install_logstash_pkg(with_repo=True, with_java=True):
    if with_repo:
        sudo('rpm --import https://packages.elastic.co/GPG-KEY-elasticsearch')
        upl = put(local_path='LS/repofile/logstash.repo',remote_path='/etc/yum.repos.d/',use_sudo=True)
        if upl.failed:
                exit(1)
    require.rpm.package('logstash')
    require.rpm.package(java_pkg)

