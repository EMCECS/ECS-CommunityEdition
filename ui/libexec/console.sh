#!/usr/bin/env bash

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

### TTY Detection

export IS_TTY=false
export IS_PIPE=false
export IS_REDIRECTION=false

if [[ -t 1 ]]; then
    export IS_TTY=true
fi

if [[ -p /dev/stdout ]]; then
    export IS_PIPE=true
fi

if [[ ! -t 1 && ! -p /dev/stdout ]]; then
    export IS_REDIRECTION=true
fi

### Logging and console output helpers

quiet_flag=false
verbose_flag=false

# Generic output logger that can take input on stdin or as arguments
# and write them to a file. Useful for things like command 2>&1 | log
# If log_file isn't set, it dumps to devnull
log_file="/dev/null"
log() {
    if [ -z "$*" ]; then
        while read -r line; do
            printf "%s\n" "${line}" >> "${log_file}"
            if $verbose_flag; then
                print "${line}"
            fi
        done
    else
        printf "%s\n" "${*}" >> "${log_file}"
        if $verbose_flag; then
            print "${line}"
        fi
    fi
}

qlog() {
    if [ -z "$*" ]; then
        while read -r line; do
            printf "%s\n" "${line}" >> "${log_file}"
        done
    else
        printf "%s\n" "${*}" >> "${log_file}"
    fi
}

print() {
    $need_nl && pw && need_nl=false
    printf "> %s\n" "${*}"
}

# Print if not quiet mode
o() {
    if ! $quiet_flag; then
        print "${*}"
    fi
    log "> [$0] ${*}"
}

# Print always
q() {
    print "${*}"
    log "> [$0] ${*}"
}

# Print only in verbose mode
v() {
    if $verbose_flag; then
        print "${*}"
    fi
    log "> [$0] ${*}"
}

# generic warning formatter
warn() {
    q "WARNING: ${*}"
}

# generic error formatter
error() {
    q "ERROR: ${*}"
}

# generic error formatter with exit 1
die() {
    error "${*}"
    # o "If you believe you have received this in error, please open an issue on github."
    exit 1
}

ask() {
    q "${*}"
    read -p " <y/N> " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# Progress bar inspired by Teddy Skarin's public domain bash ProgressBar
# https://github.com/fearside/ProgressBar/
total=$(grep '^p .*$' $0 | wc -l)
current=0
need_nl=false
bar=''
p() {
    msg="${*}"
    current="$((++current))"
    progress=$(( ( current * 100 / total * 100 ) / 100 ))
    done=$(( ( progress * 2 ) / 10 ))
    left=$(( 20 - done ))
    done=$(printf "%${done}s")
    left=$(printf "%${left}s")
    done="${done// /#}"
    left="${left// /-}"
    pcnt=$(printf "${progress}%%")
    pw
    bar="> ${pcnt} [${done}${left}] ${msg}"
    echo -en "\r${bar}"
    need_nl=true
}
pw() {
    printf "\r %${#bar}s\r"
}

wait_bar() {
    local _timeout="${1}"
    shift
    local _timeout_time="$(( $(epoch_now) + _timeout ))"
    echo -en "> ${*} "
    while [[ "$(epoch_now)" < "${_timeout_time}" ]]; do
        echo -n '.'
        sleep 1s
    done
    echo ''
}
