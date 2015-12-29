from fabric.api import *
from fabric.contrib.files import *
from fabtools.vagrant import vagrant
from fabtools import require
from fabtools import service
import fabtools

from fabtools.files import is_file
from fabtools.require import directory as require_directory
from fabtools.require import file as require_file
from fabtools.require import user as require_user
from fabtools.require.rpm import packages as require_rpm_packages
from fabtools.system import distrib_family
from fabtools.utils import run_as_root


env.roledefs.update({
    'kibana_nodes': ['www1', 'www2'],
    'elasticsearch_nodes': ['default'],
    'logstash_shipper_nodes': ['lgss'],
    'logstash_indexer_nodes': ['lgsi'],
    'redis_nodes': ['redis1'],
})
env.roledefs.update({
    'kibana_nodes': ['vagrant'],
    'elasticsearch_nodes': ['vagrant'],
    'logstash_shipper_nodes': ['vagrant'],
    'logstash_indexer_nodes': ['vagrant'],
    'redis_nodes': ['vagrant'],
})



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
    """This task install/config/enable ES on all nodes define in role elasticsearch_nodes"""
    install_es_package()
    config_es()
    enable_es()


########################################
#LOGSTASH

@task
def setup_all_LS_instance():
    """Deploy 2 instance of LS on each host with role logstash_shipper_node& logstash_indexer_node(shipper + indexer)"""
    setup_LS_shipper()
    setup_LS_indexer()

@roles('logstash_shipper_nodes')
@task
def setup_LS_shipper():
    """This task deploy a logstash_shipper instance on role logstash_shipper_node"""
    install_logstash_pkg()
    config_ls_instance("shipper","shipper")

@roles('logstash_indexer_nodes')
@task
def setup_LS_indexer():
    """This task deploy a logstash_indexer instance on role logstash_indexer_node"""
    install_logstash_pkg()
    config_ls_instance("indexer","indexer")

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
       - Restart service if needed
    """
    create_ls_instance(name)
    pushconfig_ls(name,typels)
    sudo("/etc/init.d/logstash-%s configtest" % name)
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
    upload_template("LS/templates/%(typels)s-input.tpl" % context,"/etc/logstash-%(name)s/conf.d/10-input.conf" % context, context, use_sudo=True, mode='0644', use_jinja=True )
    upload_template("LS/templates/%(typels)s-filter.tpl" % context,"/etc/logstash-%(name)s/conf.d/20-filter.conf" % context, context, use_sudo=True, mode='0644',use_jinja=True )
    upload_template("LS/templates/%(typels)s-output.tpl" % context,"/etc/logstash-%(name)s/conf.d/30-output.conf" % context, context, use_sudo=True, mode='0644', use_jinja=True )
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

################################
# REDIS
@roles("redis_nodes")
@task
def setup_redis():
    """Install + setup startup of one redis instance"""
    install_redis()
    deploy_redis_instance()

@task
def install_redis(version="3.0.5",url="http://download.redis.io/releases/"):
    """Downloads source + build + install Redis 3.0.5"""
    require_user('redis', home='/var/lib/redis', system=True)
    require.rpm.package('gcc')
    require.rpm.package('make')
    require_directory('/var/lib/redis', owner='redis', use_sudo=True)
    dest_dir = '/opt/redis-%(version)s' % locals()
    data_dir = '/data/redis/'
    conf_dir = '/etc/redis/'
    require_directory(dest_dir, use_sudo=True, owner='redis')
    require_directory(data_dir, use_sudo=True, owner='redis')
    require_directory(conf_dir, use_sudo=True, owner='redis')
    if not is_file('%(dest_dir)s/redis-server' % locals()):
        tarball = 'redis-%(version)s.tar.gz' % locals()
        require_file(tarball, url=url+tarball)
        run('tar xzf %(tarball)s' % locals())
        with cd('redis-%(version)s' % locals()):
                run('make')
                sudo('make install PREFIX=%(dest_dir)s' % locals())
                sudo('chown redis: %(dest_dir)s/*' % locals())
        sudo('rm -rf redis-%(version)s %(tarball)s' % locals())

@task
def deploy_redis_instance(port=6379):
    """create a startupscript and a config + start or restart of the instance"""
    upload_template("REDIS/%(port)s.conf" % locals(),"/etc/redis/%(port)s.conf" % locals(), locals() ,use_sudo=True,mode='644')
    upload_template("REDIS/redis_%(port)s" % locals(),"/etc/init.d/redis_%(port)s" % locals(), locals(),use_sudo=True,mode='755')
    require_directory('/data/redis/%(port)s' % locals(), use_sudo=True, owner='redis')
    sudo('chkconfig --add redis_%(port)s' % locals())
    sudo('chkconfig redis_%(port)s on' % locals())
    if not fabtools.service.is_running("redis_%(port)s" % locals()):
        fabtools.service.start("redis_%(port)s" % locals())
    else:
        fabtools.service.restart("redis_%(port)s" % locals())



#######################################
# Kibana
@roles('kibana_nodes')
@task
def deploy_kibana(version="4.3.1", dest_dir="/opt",url="https://download.elastic.co/kibana/kibana/"):
    """
       - Download if neccessary
       - untar in /opt
       - config to use ES
       - create start/stop
    
    """
    if not is_file('%(dest_dir)s/kibana-server' % locals()):
        tarball = 'kibana-%(version)s-linux-x64.tar.gz' % locals()
        require_file(tarball, url=url+tarball)
        sudo('tar xzf %(tarball)s' % locals())
        sudo('mv kibana-%(version)s-linux-x64 %(dest_dir)s/' % locals())
        append('%(dest_dir)s/kibana-%(version)s-linux-x64/config/kibana.yml' % locals(), 'elasticsearch.url: "http://localhost:9200"', use_sudo=True)
        sudo('rm -rf kibana-%(version)s-linux-x64.tar.gz' % locals())
        sudo('%(dest_dir)s/kibana-%(version)s-linux-x64/bin/kibana &' % locals())


#########################################
#Full ELK stack
@task
def setup_full_ELK():
    """
    Setup a full elk stack according to theroles define at the top
    Be carreful to adapt the template if running on multiple host (ie logstash input for indexer & output for shipper)
    must point to the redis instance 
    """
    setup_redis()
    setup_ES()
    setup_all_LS_instance()
    deploy_kibana()

