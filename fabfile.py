from fabric.api import *
from fabric.contrib.files import *
from fabtools.vagrant import vagrant
from fabtools import require
from fabtools import service
import fabtools
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

@task
def install_es_package(with_repo=True, with_java=True):
    if with_repo:
        sudo('rpm --import https://packages.elastic.co/GPG-KEY-elasticsearch')
        upl = put(local_path='ES/repofile/elasticsearch.repo',remote_path='/etc/yum.repos.d/',use_sudo=True)
        if upl.failed:
            print "Upload failed"
            exit(1)
    require.rpm.package('elasticsearch')
    require.rpm.package(java_pkg)

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

@task
def config_ls_instance(name,typels):
    """To config es instance : 
       - Deploy an init script
       - Deploy a sysconfig file
       - Deploy rules (the logstash conf file)
    """
    create_ls_instance(name)
    pushconfig_ls(name,typels)
    if not fabtools.service.is_running("logstash-%s" % name):
        fabtools.service.start("logstash-%s" % name)
    else:
        fabtools.service.restart("logstash-%s" % name)

def pushconfig_ls(name,typels):
    """
       TODO
       typels will define default input/output/filter you can create your own in the template dir
    """
    context = {
                'name' : name,
                'typels' : typels,
              }
    upload_template("LS/templates/%(typels)s-input.tpl" % context,"/etc/logstash-%(name)s/conf.d/10-input.conf" % context, context, use_sudo=True, mode='0644' )
    upload_template("LS/templates/%(typels)s-filter.tpl" % context,"/etc/logstash-%(name)s/conf.d/20-filter.conf" % context, context, use_sudo=True, mode='0644' )
    upload_template("LS/templates/%(typels)s-output.tpl" % context,"/etc/logstash-%(name)s/conf.d/30-output.conf" % context, context, use_sudo=True, mode='0644' )
    sudo('rm -f /etc/logstash-%(name)s/conf.d/*.bak' % context)


def create_ls_instance(name,user="logstash"):
    #TODO add variable in context/template
    context = { 'name' : name,
              }
    upload_template("LS/templates/logstash-init.tpl","/etc/init.d/logstash-%(name)s" % context, context, use_sudo=True, mode='0755' )
    upload_template("LS/templates/logstash-sysconfig.tpl","/etc/sysconfig/logstash-%(name)s" % context, context, use_sudo=True)
    #create /etc/logstash-indexer/conf.d
    require.directory('/etc/logstash-%(name)s/conf.d/' % context, owner=user, use_sudo=True)
    require.directory('/etc/logstash-%(name)s/pattern.d/' % context, owner=user, use_sudo=True)
    sudo("chkconfig --add logstash-%(name)s" % context)
    sudo("chkconfig logstash-%(name)s on" % context)

