from fabric.api import *
from fabtools.vagrant import vagrant

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



@task
def deploy_vimconfig (force=False):
    """
    git clone bmx0r/vimconfig from repo in github to $HOME/.vim.
    """
    if force :
        print "Forced Mode ON : get rid of old .vim directory"
        run('rm -rf $HOME/.vim')
        run('rm $HOME/.vimrc')
    print('=== CLONE FROM GITHUB ===')
    run("git clone %s %s" % (env.GIT_REPO_URL, ".vim"))
    run("ln -s $HOME/.vim/.vimrc $HOME/.vimrc")
    with cd('$HOME/.vim'):
        run('git submodule init')
        run('git submodule update')
        run('git submodule foreach git submodule init')
        run('git submodule foreach git submodule update')
    sudo('pip install pyflakes pep8 flake8 mccabe')


