#!/usr/bin/env bash

# Borrowed regex from
# http://stackoverflow.com/questions/942824/how-to-investigate-ports-opened-by-a-certain-process-in-linux

# prints all open ports from /proc/net/*
#

# reoder bytes, byte4 is byte1 byte2 is byte3 ...
reorder_byte(){
    if [ ${#1} -ne 8 ]; then
        echo "missuse of function reorderByte"
        exit
    fi

    local byte1="${1%??????}"
    local byte2="${1%????}"
    byte2="${byte2#??}"
    local byte3="${1%??}"
    byte3="${byte3#????}"
    local byte4="${1#??????}"
    echo "$byte4$byte3:$byte2$byte1"
}

# on normal intel platform the byte order of the ipv6 address in /proc/net/*6 has to be reordered.
ip6hex2dec(){
    local ip_str="${1%%:*}"
    local ip6_port="0x${1##*:}"
    local ipv6="$(reorder_byte ${ip_str%????????????????????????})"
    local shiftmask="${ip_str%????????????????}"
    ipv6="$ipv6:$(reorder_byte ${shiftmask#????????})"
    shiftmask="${ip_str%????????}"
    ipv6="$ipv6:$(reorder_byte ${shiftmask#????????????????})"
    ipv6="$ipv6:$(reorder_byte ${ip_str#????????????????????????})"
    ipv6=$(echo $ipv6 | awk '{ gsub(/(:0{1,3}|^0{1,3})/, ":"); sub(/(:0)+:/, "::");print}')
    printf "%s,%d" "$ipv6" "$ip6_port"
}

ip4hex2dec () {
    local ip4_1octet="0x${1%???????????}"
    local ip4_2octet="${1%?????????}"
    ip4_2octet="0x${ip4_2octet#??}"
    local ip4_3octet="${1%???????}"
    ip4_3octet="0x${ip4_3octet#????}"
    local ip4_4octet="${1%?????}"
    ip4_4octet="0x${ip4_4octet#??????}"
    local ip4_port="0x${1##*:}"

    # if not used inverse
    #printf "%d.%d.%d.%d:%d" "$ip4_1octet" "$ip4_2octet" "$ip4_3octet" "$ip4_4octet" "$ip4_port"
    printf "%d.%d.%d.%d,%d" "$ip4_4octet" "$ip4_3octet" "$ip4_2octet" "$ip4_1octet" "$ip4_port"
}

get_listening_sockets() {
    awk '
        /.*:.*:.*/ {

            split(FILENAME"/"$2"/"$4, portparts, "/")

            if ( ( portparts[4] == "tcp" && portparts[6] == "0A" )  ||
                 ( portparts[4] == "tcp6" && portparts[6] == "0A" ) ||
                 ( portparts[4] == "udp" && portparts[6] == "07" )  ||
                 ( portparts[4] == "udp6" && portparts[6] == "07" ) ) {

                print portparts[4]","portparts[5]

            }

        }
        ' /proc/net/{udp,tcp,udp6,tcp6,raw,raw6}
}

for listener in $(get_listening_sockets); do

        proto="${listener%%,*}"
        hex_address="${listener##*,}"

        if [ "#${proto#???}" = "#6" ]; then
            addr_port="$(ip6hex2dec ${hex_address})"
        else
            addr_port="$(ip4hex2dec ${hex_address})"
        fi

        addr="${addr_port%%,*}"
        port="${addr_port##*,}"

        echo "port $port/$proto is listening on $addr"

done
