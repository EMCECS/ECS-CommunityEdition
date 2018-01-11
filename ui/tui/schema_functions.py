# -*- coding: utf-8 -*-
import socket
import re

Ipv4AddressRegex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
Ipv4CidrRegex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$"
HostnameRegex = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
UnixPathRegex = "^(\/[^\/ ]*)+\/?$"
AlphanumericRegex = "^[a-zA-Z0-9]+([_-]?[a-zA-Z0-9])*$"
DockerImageRegex = "^(?:(?=[^:\/]{1,253})(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(?:\.(?!-)[a-zA-Z0-9-]{1,63}(?<!-))*(?::[0-9]{1,5})?\/)?((?![._-])(?:[a-z0-9._-]*)(?<![._-])(?:\/(?![._-])[a-z0-9._-]*(?<![._-]))*)(?::(?![.-])[a-zA-Z0-9_.-]{1,128})?$"
S3SecretKeyRegex = "(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"
ValidCryptoMethodRegex = "^(rsa|ed25519)$"
def __validate_regex(regex, value, error_message="Validation failed"):
    pattern = re.compile(regex)
    m = pattern.match(value)
    if not m:
        raise Exception(error_message)

def ipv4_address(value, rule_obj, path):
    __validate_regex(Ipv4AddressRegex, value, "Not a valid IPv4 address: '%s' (%s)" % (value, path))
    return True

def ipv4_cidr(value, rule_obj, path):
    __validate_regex(Ipv4CidrRegex, value, "Not a valid IPv4 CIDR: '%s' (%s)" % (value, path))
    return True

def unix_path(value, rule_obj, path):
    __validate_regex(UnixPathRegex, value, "Not a valid unix path: '%s' (%s)" % (value, path))
    return True

def alphanumeric(value, rule_obj, path):
    """
    - start and end with an alphanumeric character
    - accept underscore and hyphen, but followed by an alphanumeric character
    """
    __validate_regex(AlphanumericRegex, value, "Not a valid name: '%s' (%s)" % (value, path))
    return True

def docker_image(value, rule_obj, path):
    __validate_regex(DockerImageRegex, value, "Not a valid Docker image: '%s' (%s)" % (value, path))
    return True

def s3_secret_key(value, rule_obj, path):
    __validate_regex(S3SecretKeyRegex, value, "Not a valid S3 Secret Key: '%s' (%s)" % (value, path))
    return True

def valid_crypto_method(value, rule_obj, path):
    __validate_regex(ValidCryptoMethodRegex, value, "Not a supported crypto method: '%s' (%s)" % (value, path))
    return True

def valid_hostname(value, rule_obj, path):
    __validate_regex(HostnameRegex, value, "Not a valid hostname: '%s' (%s)" % (value, path))
    return True
