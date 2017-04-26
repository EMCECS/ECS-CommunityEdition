#!/bin/ash
##############################################################################
# APK Fastest Mirror 0.9.4 - A Pure BusyBox APK mirror selector for Alpine
# MIT License (See: https://github.com/padthaitofuhot/apkfastestmirror)
#
# Usage
# -h, --help        Show usage and exit
# -q, --quiet       Be quiet - only print results
#     --shut-up     Be more quiet - print nothing
# -v, --verbose     Be verbose - print progress (default)
#     --http-only   Only use HTTP checks to determine mirror performance
#     --icmp-only   Only use ICMP checks to determine mirror performance
# -s, --samples <n> Test performance n times before selecting mirror
#                       the default is two samples.
# -r, --replace     Replace /etc/apk/repositories with fastest mirror
# -u, --update      Update APK indexes (default, useful with --replace)
#     --genconf     Create /etc/apk/fastestmirror.conf if it does not
#                   already exist and exit
#     --install     Install as /usr/local/bin/apkfastestmirror and exit
#@############################################################################
#
# All variables that can be set in the script header can also be set in
# the config file: /etc/apk/apkfastestmirror.conf
#
# If the config file exists, its variables override the script.
# If arguments are given on the command line, they override the config file.
#
### Behavior Variables
#
# The contents of /etc/apk/repositories will be replaced whenever this script
# runs if replace_apk_repositories is 'true'.
replace_apk_repositories=true
#
# Run `apk update` if replace_apk_repositories=true or given the --replace
# argument at runtime.
update_indexes_after_replace=false
#
# Get a progress bar :)
verbose=true
#
# Show the results
show_results=false
#
### Mirror Variables
#
# Your local HTTP mirrors
mirrors_local=""
#
# Unlisted HTTP mirrors to query
mirrors_unlisted="
http://alpine.gliderlabs.com/alpine/
http://dl-cdn.alpinelinux.org/alpine/
"
#
# At least one published mirror that should generally be reachable
mirrors_published="
http://nl.alpinelinux.org/alpine/
"
#
### Measurement Variables
#
# Got firewall problems? Maybe these can help.
icmp_only=false
http_only=false
#
# Number of times to perform sampling before returning results
sampling_rounds=2
#
# Number of times to ICMP ping each mirror host
icmp_count=6
#
# Timeout in seconds when waiting for a mirror list (MIRRORS.txt) HTTP source
# to respond before ignoring it for the current run
http_timeout=1
#
# "on" or "off"; defaults to "on", but does nothing unless the $http_proxy
# environment variable is set
http_use_proxy=on
# When using proxies, you will want to set `sampling_rounds` to something > 1
# to prime the proxy's cache. If you do not, a suboptimal mirror may be
# selected if, for example, the proxy gets a cache hit on a slower mirror and
# a cache miss on the mirror apkfastestmirror would have otherwise selected.
#
#@@###########################################################################

set -o pipefail

if [ -f /etc/apk/apkfastestmirror.conf ]; then
    source /etc/apk/apkfastestmirror.conf
fi

usage() {
    sed '/^#@/{q}' $0 | egrep -v -E '#!|##|^$'
}

if ! O=$(
         getopt \
         -l verbose,genconf,install,replace,update,help,quiet,samples:,shut-up,http-only,icmp-only \
         -o vuhqrs: \
         -n "${0}" \
         -- ${@}
        ); then
    usage
    exit 1
fi

eval set -- "${O}"
while true; do
    case "$1" in
    -v|--verbose)
        verbose=true
        shift
        ;;
    -q|--quiet)
        verbose=false
        show_results=true
        shift
        ;;
       --shut-up)
        verbose=false
        show_results=false
        shift
        ;;
    --genconf)
        if [ -f "/etc/apk/apkfastestmirror.conf" ]; then
            echo "Config file /etc/apk/apkfastestmirror.conf already exists."
            echo "Remove it and rerun with --genconf to regenerate."
            exit 1
        else
            echo "Generating /etc/apk/apkfastestmirror.conf"
            sed '/^#@@/{q}' $0 | egrep -v -E '#!|##|^$' >/etc/apk/apkfastestmirror.conf
            exit $?
        fi
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    --install)
            echo "Installing to /usr/local/bin/apkfastestmirror"
            install -o root -g root -m 755 -cD -p "${0}" /usr/local/bin/apkfastestmirror || exit 1
            ash $0 --genconf
            exit $?
        ;;
    -r|--replace)
        replace_apk_repositories=true
        shift
        ;;
    -u|--update)
        update_indexes_after_replace=true
        shift
        ;;
    -s|--samples)
        sampling_rounds="${2}"
        shift 2
        ;;
    --icmp-only)
        icmp_only=true
        shift
        ;;
    --http-only)
        http_only=true
        shift
        ;;
    --)
        shift
        break
        ;;
    *)
        usage
        exit 1
        ;;
    esac
done

##############################################################################

# Assemble list of MIRRORS.txt HTTP sources
mirrorlist_sources="
$(
    for mirror in ${mirrors_local} ${mirrors_unlisted} ${mirrors_published}; do \
        echo ${mirror}/MIRRORS.txt; \
    done
 )
"

# Fetch mirrorlists from sources
$verbose && echo "Fetching mirror lists"
mirrorlist="
${mirrors_local}
${mirrors_unlisted}
$(
    for source in ${mirrorlist_sources}; do \
        wget -O- -q -Y ${http_use_proxy} -T ${http_timeout} ${source}; \
    done \
    | sort \
    | uniq \
    | sed '/^$/d'
 )
"

# Use time, $?, and wget -T to time http requests
# to mirrors and filter those that don't respond.
# Pipes into the icmp runner, providing the
# url, host, and time wget took to access the mirror
# in decimal seconds.
parallel_http_ping() {
    url=$1

    if $icmp_only || fetchtime="$(
                    time \
                    wget -O/dev/null -q \
                        -Y ${http_use_proxy} \
                        -T ${http_timeout} \
                        "${url}" \
                    2>&1 \
                  )";

    then
        $icmp_only && fetchtime=1
        echo -e "${url}\n${fetchtime}" | awk '
            /^http/ {
                split($1, urlparts, "/")
                print $1
                print urlparts[3]
            }
            /^real/ {
                fetchtime = $2 * 60 + $3
                print fetchtime
            }
        '
        $verbose && 1>&2 echo -n "#"
    else
        $verbose && 1>&2 echo -n "."
        return 1
    fi

}

# Pings the mirror a few times and calculates a weighted
# speed and reliability metric from http fetchtime, packet
# loss, and round-trip times.
#
# fetchtime = The time it took wget to contact a mirror,
#             request MIRRORS.txt, and receive it.
# rtval = Round-trip min, max, and avg are summed to
#         represent jitter and link congestion.
# plval = A dropped packet is weighted the same as the round-
#         trip sum, since that's roughly what would be lost
#         if TCP had to retransmit a packet
# idx = The sum of rtval and plval, multiplied by
#       the fetchtime. It can happen that a host may respond
#       slowly to ICMP or TCP setup, but ultimately yields
#       a fast transfer. Conversely, local mirror on an
#       old 10baseT switch might ping and TCP handshake
#       fast, but may be slower to transfer than a remote
#       mirror accessible via a 10G OC transit.
#       By weighing against fetchtime, these scenarios are
#       passably accounted for.
#
# Once metrics are calculated for all reachable mirrors,
# they are sorted by idx (lower is better) and the top
# of the list is returned as the winning mirror.
parallel_icmp_ping() {
    # since we're not using while-read, we should use
    # read -t here to avoid failure modes where we somehow
    # get called even though pipeline should have died.
    read -r -t 1 url
    read -r -t 1 host
    read -r -t 1 fetchtime

    if (
         ( $http_only \
           && echo -e "packet loss 0 0 0 0 0\nround-trip 0 0 0/0/1\n"
         ) \
         ||  ping -q -c "${icmp_count}" -W 1 -w "${icmp_count}" "${host}" 2>/dev/null \
       ) \
       | awk -v url="${url}" \
             -v host="${host}" \
             -v fetchtime="${fetchtime}" '
        /packet loss/ {
            loss = $7
        }
        /round-trip/ {
            split($4, s, "/")
            rtval = s[0] + s[1] + s[3]
            plval = loss * rtval
            idx = rtval + plval
            idx *= fetchtime
            print idx, host, url
        }
    ';
    then
        $verbose && 1>&2 echo -n "#"
    else
        $verbose && 1>&2 echo -n "."
    fi
}

# Look pretty
mirror_count="$(set -- $mirrorlist; echo $#)"
$verbose && echo "Determining fastest mirror"
_foot=']'
##
winners="$(mktemp)"
for round in $(seq 1 "${sampling_rounds}"); do

    $verbose && _head="$(printf 'Sampling (%s/%s) [' ${round} ${sampling_rounds})"
    $verbose && _pad="$(( ${#_head} + ${#_foot} ))"
    $verbose && printf "%$(( ( mirror_count * 2 ) + _pad - 1 ))s%s\r%s" ' ' "${_foot}" "${_head}"

    reachable="$(mktemp)"

    for mirror in ${mirrorlist}; do
        parallel_http_ping ${mirror} | parallel_icmp_ping 1>>${reachable} &
    done
    wait

    grep -v '^0  $' "${reachable}" | sort -n -t ' ' -k 1 | head -1 >>"${winners}"

    rm -f "${reachable}"

    $verbose && printf "\r%$(( ( mirror_count * 2 ) + _pad + 1 ))s\r"
done
##

set -- $(sort -n -t ' ' -k 1 "${winners}" | head -1)
rm -f "${winners}"

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    $verbose && echo "ERR: No hosts could be reached, not touching /etc/apk/repositories"
    exit 1
fi

# Spam to terminal and (if enabled) update the APK repo file
output_results() {
    $replace_apk_repositories && new_repositories="$(mktemp)"
    while read -r line; do
        $replace_apk_repositories && echo "${line}" >>"${new_repositories}"
        $show_results && echo "${line}"
    done
    $replace_apk_repositories && mv -f "${new_repositories}" /etc/apk/repositories
}

v="$(source /etc/os-release; echo ${PRETTY_NAME} | cut -d ' ' -f 3)"
echo "${3}" | awk -v v="${v}" '
    {
        print $1 v "/main"
        print $1 v "/community"
        print "@edge_main " $1 "edge" "/main"
        print "@edge_community " $1 "edge" "/community"
        print "@edge_testing " $1 "edge" "/testing"
    }
' | output_results

$verbose && echo "OK: ${2} (metric ${1})"

$replace_apk_repositories && $update_indexes_after_replace && $verbose && apk update
$replace_apk_repositories && $update_indexes_after_replace && ! $verbose && apk -q update

exit 0

# refs:
# http://wiki.alpinelinux.org/wiki/Awk
