#@IgnoreInspection BashAddShebang

quotize() {
    local yarr=(${*})
    local size=$(( ${#yarr[@]} - 1 ))
    for ((i=0; i < size; i++)); do
        echo -n "\"${yarr[i]}\", "
    done
    echo -n "\"${yarr[size]}\""
}

render_build_entrypoint() {
    if ! [ -z "${build_entrypoint}" ]; then
        echo -n "ENTRYPOINT [ "
        quotize $build_entrypoint
        echo " ]"
    fi
}

render_build_cmd() {
    if ! [ -z "${build_cmd}" ]; then
        echo -n "CMD [ "
        quotize $build_cmd
        echo " ]"
    fi
}

#####
# The wonderful YAY Yamlesque parser for bash by John Lane
# @LICENSE: MIT refer-to https://github.com/johnlane/random-toolbox
# This copy has been refactored to flatten namespaces for easier use in shipit.
# @ORIGIN: https://github.com/johnlane/random-toolbox
####

#
# YAY - a bash Yamlesque parser
#
# YAML is a data configuration format consisting of hierarchial "collections"
# of named data items. Yay is a parser that understands a subset of YAML, or
# Yamlesque, that is indended as a way to provide basic configuration or other
# data to bash shell scripts.
#
# Yamlesque has a structured syntax that is a small subset of YAML. Valid
# Yamlesque is also valid YAML but the reverse isn't necessarily true due to
# Yamlesque only supporting a basic subset of the YAML syntax. The name *Yay*
# is a reminder that _**Yaml ain't Yamlesque!**_
#
# Valid Yamlesque will pass a YAML validity check: http://www.yamllint.com. The
# full YAML specification is at http://yaml.org. Yamlesque meets the following
# format specification:
#
#     <indent><key>:[<value>]
#
# Yay is inspired by http://stackoverflow.com/a/21189044
#                and https://gist.github.com/pkuczynski/8665367
#
#
# MIT License. See https://github.com/johnlane/random-toolbox
#
########################################################### JL 20150720i #####
#
# Yamlesque is written in a plain text file and such files contain one or more
# input lines that consist of identifiers that are separated by whitespace:
#
# *  an indent
# *  a key
# *  a colon (:)
# *  a value
#
# Lines beginning with the octothorpe character (`#` aka `hash`, `sharp` or
# `pound`) are ignored, as is any trailing part of a line beginning with it.

# In general, whitespace is ignored except when it is leading whitespace, in
# which case it is considered to be an indent. An indent is zero or more pairs
# of space characters (`TAB` isn't valid YAML), each representing one level of
# indentation.
#
# Note that, unlike YAML, two spaces must be used for each level of indentation.
#
# If a line does not have a value then it defines a new collection of key/value
# pairs which follow in subsequent lines and have one more level of indent.
#
# If a value is given then the key defines a setting in the collection. If the
# value is wrapped in quotation marks then these are removed, otherwise the
# value is used as-is including whitespace.
#
# Yay provides a bash function that reads an appropriately formatted data file
# and produces associative array definitions containing the data read from the
# file.
#
# This `yay_parse` function reads a Yay file and returns `bash` commands that
# can be executed to define *associative* arrays containing the data defined
# in the file. It takes one or two arguments:
#
#    yay_parse <filename> [<dataset>]
#
# Where `<filename>` is the name of the file. If the given name doesn't exist
# then further searches are performed with the suffixes `.yay` and `.yml`
# appended . The first matching file is used.
#
# The `<dataset>` is a label that is used to prefix the arrays that get
# created to reduce the risk of collisions. If omitted then the filename,
# less its suffix, is used.
#
# There are various ways to apply Yay definitions to the current shell environment:
#
# * `eval $(yay_parse demo)`
# * `source <(yay_parse demo)`
# * `yay_parse demo | source /dev/stdin`
#
# However, the easiest approach is to use the `yay` helper which loads data
# from the given file and creates arrays in the current environment.
#
# $ yay demo
#
# Yay uses associative arrays which are a feature of Bash version 4. It will
# not work with other bash versions.
#
# Usage
#
# First, include the Yay source in a script and then load a file
#
#    #!/bin/bash
#    . /path/to/yay
#    yay demo
#
# This leaves at least one array that is named after the data set. It will
# have entries per top-level key/value pair. It will also have a special
# entry called `keys` that contains a space-delimited string of the names of
# all such keys. Another special entry called `children` lists the names of
# further arrays defining other data sets within it. Such arrays follow the
# same structure.
#
# Here is a recursive example that displays a data set:
#
#    # helper to get array value at key
#    value() { eval echo \${$1[$2]}; }
#
#    # print a data set
#    print_dataset() {
#      for k in $(value $1 keys)
#      do
#        echo "$2$k = $(value $1 $k)"
#      done
#
#      for c in $(value $1 children)
#      do
#        echo -e "$2$c\n$2{"
#        print_dataset $c "  $2"
#        echo "$2}"
#      done
#    }
#
#    yay demo
#    print_dataset demo
#

yay_parse() {

   # find input file
   for f in "$1" "$1.yay" "$1.yml"
   do
     [[ -f "$f" ]] && input="$f" && break
   done
   [[ -z "$input" ]] && exit 1

   # use given dataset prefix or imply from file name
   [[ -n "$2" ]] && local prefix="$2" || {
     local prefix=$(basename "$input"); prefix=${prefix%.*}
   }

   echo "declare -g -A $prefix;"

   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -n -e "s|^\($s\)\($w\)$s:$s\"\(.*\)\"$s\$|\1$fs\2$fs\3|p" \
          -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p" "$input" |
   awk -F$fs '{
      indent       = length($1)/2;
      key          = $2;
      value        = $3;

      # No prefix or parent for the top level (indent zero)
      root_prefix  = "'$prefix'_";
      if (indent ==0 ) {
        prefix = "";          parent_key = "'$prefix'";
      } else {
        prefix = "";          parent_key = keys[indent-1];
      }

      keys[indent] = key;

      # remove keys left behind if prior row was indented more than this row
      for (i in keys) {if (i > indent) {delete keys[i]}}

      if (length(value) > 0) {
         # value
         printf("%s[%s]=\"%s\";\n", parent_key , key, value);
         printf("%s[keys]+=\" %s\";\n", parent_key , key);
      } else {
         # collection
         printf("%s[children]+=\" %s\";\n", parent_key , key);
         printf("declare -g -A %s;\n", key);
         printf("%s[parent]=\"%s%s\";\n", key, prefix, parent_key);
      }
   }'
}

# helper to load yay data file
yay() { eval $(yay_parse "$@"); }

# helper to get array value at key
value() { eval echo \${$1[$2]}; }

# print a data collection

# print a data collection
print_collection() {
  for k in $(value $1 keys)
  do
    echo "$2$k = $(value $1 $k)"
  done

  for c in $(value $1 children)
  do
    echo -e "$2c:$c\n$2{"
    print_collection $c "  $2"
    echo "$2}"
  done
}

print_flat() {
  for k in $(value $1 keys)
  do
    echo "$1_$k=$(value $1 $k)"
  done

  for c in $(value $1 children)
  do
    print_flat $c "$2"
  done
}

import_vars() {
  for k in $(value $1 keys)
  do
    eval $1_$k='$(value $1 $k)'
  done

  for c in $(value $1 children)
  do
    import_vars $c "$2"
  done
}


###### The handy dandy bash templater
# Johan Haleby's fork, but crammed into a bash function and given some magical powers.
# @LICENSE: Unknown/Unstated refer-to https://github.com/johanhaleby/bash-templater
# Replaces all {{VAR}} by the $VAR value in a template file and outputs it
# and any {{VAR}} with "render" in its name will call a function to get its value.
# @ORIGIN: https://github.com/johanhaleby/bash-templater
# @UPSTREAM: https://github.com/lavoiesl/bash-templater

var_value() {
    eval echo \$$1
}

templater() {
    #readonly PROGNAME=$(basename $0)

    config_file="<none>"
    print_only="false"
    silent="false"

    usage="Template error."

    if [ $# -eq 0 ]; then
      echo "$usage"
      exit 1
    fi

    if [[ ! -f "${1}" ]]; then
        echo "You need to specify a template file" >&2
        echo "$usage"
        exit 1
    fi

    template="${1}"

    if [ "$#" -ne 0 ]; then
        while [ "$#" -gt 0 ]
        do
            case "$1" in
            -h|--help)
                echo "$usage"
                exit 0
                ;;
            -p|--print)
                print_only="true"
                ;;
            -f|--file)
                config_file="$2"
                ;;
            -s|--silent)
                silent="true"
                ;;
            --)
                break
                ;;
            -*)
                echo "Invalid option '$1'. Use --help to see the valid options" >&2
                exit 1
                ;;
            # an option argument, continue
            *)  ;;
            esac
            shift
        done
    fi

    vars=$(grep -oE '\{\{[A-Za-z0-9_]+\}\}' "${template}" | sort | uniq | sed -e 's/^{{//' -e 's/}}$//')

    if [[ -z "$vars" ]]; then
        if [ "$silent" == "false" ]; then
            echo "Warning: No variable was found in ${template}, syntax is {{VAR}}" >&2
        fi
    fi

    # Load variables from file if needed
    if [ "${config_file}" != "<none>" ]; then
        if [[ ! -f "${config_file}" ]]; then
          echo "The file ${config_file} does not exists" >&2
          echo "$usage"
          exit 1
        fi

        # Create temp file where & and "space" is escaped
        tmpfile=`mktemp`
        sed -e "s;\&;\\\&;g" -e "s;\ ;\\\ ;g" "${config_file}" > $tmpfile
        source $tmpfile
    fi

    replaces=""

    # Reads default values defined as {{VAR=value}} and delete those lines
    # There are evaluated, so you can do {{PATH=$HOME}} or {{PATH=`pwd`}}
    # You can even reference variables defined in the template before
    defaults=$(grep -oE '^\{\{[A-Za-z0-9_]+=.+\}\}' "${template}" | sed -e 's/^{{//' -e 's/}}$//')

    for default in $defaults; do
        var=$(echo "$default" | grep -oE "^[A-Za-z0-9_]+")
        current=`var_value $var`

        # Replace only if var is not set
        if [[ -z "$current" ]]; then
            eval $default
        fi

        # remove define line
        replaces="-e '/^{{$var=/d' $replaces"
        vars="$vars
    $current"
    done

    vars=$(echo $vars | sort | uniq)

    if [[ "$print_only" == "true" ]]; then
        for var in $vars; do
            value=`var_value $var`
            echo "$var = $value"
        done
        exit 0
    fi

    # Replace all {{VAR}} by $VAR value
    for var in $vars; do
        # magic to run a command to get a value
        if [ "${var#*render}" != "${var}" ]; then
            value="$(${var})"
        else
            value=`var_value $var`
            if [[ -z "$value" ]]; then
                if [ $silent == "false" ]; then
                    echo "Warning: $var is not defined and no default is set, replacing by empty" >&2
                fi
            fi
        fi
        # Escape slashes
        value=$(echo "$value" | sed 's/\//\\\//g');
        replaces="-e 's/{{$var}}/${value}/g' $replaces"
    done

    escaped_template_path=$(echo $template | sed 's/ /\\ /g')
    eval sed $replaces "$escaped_template_path"
}
