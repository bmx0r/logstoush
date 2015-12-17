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
    'kibana_node': ['www1', 'www2'],
    'elasticsearch_nodes': ['default'],
    'logstash_shipper_node': ['lgss'],
    'logstash_indexer_node': ['lgsi'],
    'redis_node': ['redis1'],
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
@task
def deploy_redis(version="3.0.5"):
    require_user('redis', home='/var/lib/redis', system=True)
    require_directory('/var/lib/redis', owner='redis', use_sudo=True)
    dest_dir = '/opt/redis-%(version)s' % locals()
    require_directory(dest_dir, use_sudo=True, owner='redis')
    if not is_file('%(dest_dir)s/redis-server' % locals()):
        tarball = 'redis-%(version)s.tar.gz' % locals()
        require_file(tarball, url="http://download.redis.io/releases/%s"% tarball)
        run('tar xzf %(tarball)s' % locals())
        with cd('redis-%(version)s' % locals()):
                run('make')
                sudo('make install PREFIX=%s' % dest_dir)
                sudo('chown redis: %(dest_dir)s/*' % locals())
        sudo('rm -rf redis-%(version)s %(tarball)s' % locals())

@task
def deploy_redis_instance(port=6379):
    upload_template("REDIS/%(port)s.conf" % locals(),"/etc/redis/%(port)s.conf" % locals(), locals() ,use_sudo=True,mode='644')
    upload_template("REDIS/redis_%(port)s" % locals(),"/etc/init.d/redis_%(port)s" % locals(), locals(),use_sudo=True,mode='755')
    sudo('chkconfig --add redis_%(port)s' % locals())
    sudo('chkconfig redis_%(port)s on' % locals())
    sudo('service redis_%(port)s start' % locals())


