#!/bin/bash

NAME="$(basename $0)"
PID_FILE="/var/run/$NAME.pid"
LOG_stdout="/var/log/$NAME/$NAME.log"
LOG_stderr="/var/log/$NAME/$NAME.err"

CMD="/usr/local/bin/goreplay"
CMD_ARGS=""

RED='\033[0;31m'
GREEN='\033[0;32m'
NO_COLOR='\033[0m'

echo_ok() {
  echo -e " \t\t\t[ ${GREEN}OK${NO_COLOR} ]"
}

echo_failed() {
  msg=" \t\t\t[ ${RED}FAILED${NO_COLOR} ]"
  if [ -z "$1" ] ; then
    echo -e $msg
  else
    echo -e "$msg [ $1 ]"
  fi
}

echo_running() {
  echo -e " \t\t\t[ ${GREEN}RUNNING${NO_COLOR} ] [ $1 ]"
}

echo_stopped() {
  echo -e " \t\t\t[ ${RED}STOPPED${NO_COLOR} ]"
}

get_pid() {
    cat "$PID_FILE"
}

is_running() {
    [ -f "$PID_FILE" ] && ps `get_pid` > /dev/null 2>&1
}

clean() {
  if [ -f "$PID_FILE" ] ; then
      rm "$PID_FILE"
  fi
}

starting() {
  ARGS="$@"
  nohup $CMD $ARGS >> $LOG_stdout 2>> $LOG_stderr &
  echo $! > "$PID_FILE"
  for i in {1..10}
  do
      if is_running ; then
          break
      fi
      sleep 1
  done
  return 0
}

start() {
  echo -n "Starting $NAME"
  if is_running ; then
    echo_failed "Already started"
    return 1
  else
    starting $CMD_ARGS

    if ! is_running ; then
        echo_failed "Unable to start, see $LOG_stdout and $LOG_stderr"
        clean
        return 1
    fi
  fi
  echo_ok
  return 0
}

stopping() {
  kill `get_pid`
  for i in {1..10}
  do
      if ! is_running ; then
          break
      fi
      sleep 1
  done
  return 0
}

stop() {
  echo -n "Stopping $NAME"
  if ! is_running ; then
    echo_failed "NOT running"
    return 1
  else
    stopping

    if is_running ; then
      echo_failed "May still be shutting down or shutdown may have failed"
      return 1
    fi

    clean
  fi
  echo_ok
  return 0
}

restart() {
  stop
  if [ $? -eq 0 ] ; then
    start
  fi
  return $?
}

status() {
  echo -n "Status of $NAME"
  if ! is_running ; then
    echo_stopped
    return 1
  fi
  echo_running "PID: `get_pid`"
  return 0
}

refresh-config() {
  return 0
}

case "$1" in
    start)
        $1
        ;;
    stop)
        $1
        ;;
    restart)
        $1
        ;;
    status)
        $1
        ;;
    *)
    echo $"Usage: $0 {start|stop|restart|status}"
    exit 2
esac
exit $?
