#@IgnoreInspection BashAddShebang

# DEPRECATED: shell-style environment flags are deprecated and will be replaced
# DEPRECATED: by new context system, but some scripts may still depend on these.
DRONE=${DRONE:-false}
BUILD=${BUILD:-false}
MONITOR=${DRONE:-false}

etc="${root}/ui/etc"
export etc
source "${etc}/release.conf"

if [ -f "${root}/release.conf" ]; then
    source "${root}/release.conf"
fi

if [ -f "${root}/bootstrap.conf" ]; then
    source "${root}/bootstrap.conf"
fi

source "${lib}/console.sh"
log_file="${root}/install.log"

source "${lib}/osutils.sh"
source "${lib}/dockerutils.sh"
source "${lib}/shipit.lib.sh"

yay "${etc}/config.yml"
import_vars config
