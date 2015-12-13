###############################
# Default settings for logstash
###############################

# Override Java location
#JAVACMD=/usr/bin/java

# Set a home directory
#LS_HOME=/var/lib/logstash

# Arguments to pass to logstash agent
#LS_OPTS=""

# Arguments to pass to java
#LS_HEAP_SIZE="500m"
#LS_JAVA_OPTS="-Djava.io.tmpdir=$HOME"

# pidfiles aren't used for upstart; this is for sysv users.
#LS_PIDFILE=/var/run/logstash.pid

# user id to be invoked as; for upstart: edit /etc/init/logstash.conf
#LS_USER=logstash

# logstash logging
#LS_LOG_FILE=/var/log/logstash/logstash.log
#LS_USE_GC_LOGGING="true"

# logstash configuration directory
#LS_CONF_DIR=/etc/logstash/conf.d

# Open file limit; cannot be overridden in upstart
#LS_OPEN_FILES=16384

# Nice level
#LS_NICE=19

# If this is set to 1, then when `stop` is called, if the process has
# not exited within a reasonable time, SIGKILL will be sent next.
# The default behavior is to simply log a message "program stop failed; still running"
KILL_ON_STOP_TIMEOUT=0
