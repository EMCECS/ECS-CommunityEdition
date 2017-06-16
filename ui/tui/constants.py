# coding=utf-8

# Copyright (c) 2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

"""
A bunch of defaults and constants
"""

src_root = '/usr/local/src'
log_root = '/var/log'
host_root = '/opt/emc/ecs-install'
container_root = '/opt'
cache_root = '/var/cache/emc/ecs-install'
ssh_root = '{0}/ssh'.format(container_root)
ssl_root = '{0}/ssl'.format(container_root)
ansible_src_root = '{0}/ansible'.format(src_root)
ansible_log = '{0}/ecs-install.ansible.log'.format(log_root)
ui_src_root = '{0}/ui'.format(src_root)
ui_log = '{0}/ecs-install.ui.log'.format(log_root)
ui_etc = '{0}/etc'.format(ui_src_root)
ui_tui = '{0}/tui'.format(ui_src_root)
ansible_conf = '/etc/ansible'
ansible_root = "{0}/ansible".format(ui_src_root)
ansible_setup_templates = "{0}/templates".format(ansible_root)
ansible_setup_caches = "{0}/roles/installer_build_cache/vars".format(ansible_root)
ansible_group_vars = "{0}/group_vars".format(ansible_root)
ansible_vars = "{0}/vars".format(ansible_root)
ansible_facts = "{0}/facts".format(cache_root)
API_PROTOCOL = 'https'
API_PORT = '4443'
API_TIMEOUT = 60
API_RETRIES = 10
DIAGNOSTIC_PROTOCOL = 'http'
DIAGNOSTIC_PORT = '9101'
DIAGNOSTIC_TIMEOUT = API_TIMEOUT
DIAGNOSTIC_RETRIES = API_RETRIES
license_text = '''INCREMENT ViPR_Block EMCLM 2.0 permanent uncounted \
        VENDOR_STRING=CAPACITY=1024;CAPACITY_UNIT=TB;SWID=PXTYD1DZK59Y4C;PLC=VIPR; \
        HOSTID=ANY dist_info="ACTIVATED TO 49ers Inn" ISSUER=EMC \
        ISSUED=10-Jan-2014 NOTICE="ACTIVATED TO License Site Number: \
        PTA06JUN20131086059" SN=2162734 SIGN="003D CF8A 7CED 90ED 318E \
        47C9 001A F400 3A5D EEE7 81F0 704C CBDA 2F32 0745"
INCREMENT ViPR_HDFS EMCLM 2.0 permanent uncounted \
        VENDOR_STRING=SWID=PXTYD1DZK59Y4C;PLC=VIPR; HOSTID=ANY \
        dist_info="ACTIVATED TO 49ers Inn" ISSUER=EMC \
        ISSUED=10-Jan-2014 NOTICE="ACTIVATED TO License Site Number: \
        PTA06JUN20131086059" SN=2162734 SIGN="0073 059F D54D 7CC9 4ADA \
        0B13 6160 9100 688E 8167 37DA E911 28F2 CC96 798A"
INCREMENT ViPR_Object EMCLM 2.0 permanent uncounted \
        VENDOR_STRING=SWID=PXTYD1DZK59Y4C;PLC=VIPR; HOSTID=ANY \
        dist_info="ACTIVATED TO 49ers Inn" ISSUER=EMC \
        ISSUED=10-Jan-2014 NOTICE="ACTIVATED TO License Site Number: \
        PTA06JUN20131086059" SN=2162734 SIGN="000E BA65 2065 4DBD 8888 \
        CAEB 94EE F800 BAF0 FF51 A3F0 1E81 E731 4ECB FACC"
INCREMENT ViPR_Commodity EMCLM 2.0 permanent uncounted \
        VENDOR_STRING=SWID=PXTYD1DZK59Y4C;PLC=VIPR; HOSTID=ANY \
        dist_info="ACTIVATED TO 49ers Inn" ISSUER=EMC \
        ISSUED=10-Jan-2014 NOTICE="ACTIVATED TO License Site Number: \
        PTA06JUN20131086059" SN=2162734 SIGN="00A9 CFC9 7B10 0296 CF74 \
        3E4C 1AE7 2000 83E8 E135 63D4 7F79 0DC0 07B9 7969"
INCREMENT ViPR_CAS EMCLM 2.0 permanent uncounted \
        VENDOR_STRING=SWID=PXTYD1DZK59Y4C;PLC=VIPR; HOSTID=ANY \
        dist_info="ACTIVATED TO 49ers Inn" ISSUER=EMC \
        ISSUED=10-Jan-2014 NOTICE="ACTIVATED TO License Site Number: \
        PTA06JUN20131086059" SN=2162734 SIGN="009E 6082 66B8 3D16 69AC \
        9C84 8FDD DB00 C762 3EBB 52FC 04C8 72A2 A5A9 4CC8"
INCREMENT ViPR_ECS EMCLM 2.0 permanent uncounted \
        VENDOR_STRING=SWID=PXTYD1DZK59Y4C;PLC=VIPR; HOSTID=ANY \
        dist_info="ACTIVATED TO 49ers Inn" ISSUER=EMC \
        ISSUED=10-Jan-2014 NOTICE="ACTIVATED TO License Site Number: \
        PTA06JUN20131086059" SN=2162734 SIGN="0083 9DFC 8366 AA13 F5BB \
        6F30 B824 5F00 B261 A65B 6911 1334 0BCF 92CA 35D0"
INCREMENT ViPR_Unstructured EMCLM 2.0 permanent uncounted \
        VENDOR_STRING=CAPACITY=1024;CAPACITY_UNIT=TB;SWID=PXTYD1DZK59Y4C;PLC=VIPR; \
        HOSTID=ANY dist_info="ACTIVATED TO 49ers Inn" ISSUER=EMC \
        ISSUED=10-Jan-2014 NOTICE="ACTIVATED TO License Site Number: \
        PTA06JUN20131086059" SN=2162734 SIGN="00CF 2080 FDCA D7E1 CA22 \
        5DE7 DA9A 0000 1938 D26C 4AB5 76CB AA43 2662 0FCD"
INCREMENT ViPR_Controller EMCLM 2.0 permanent uncounted \
        VENDOR_STRING=CAPACITY=1024;CAPACITY_UNIT=TB;SWID=PXTYD1DZK59Y4C;PLC=VIPR; \
        HOSTID=ANY dist_info="ACTIVATED TO 49ers Inn" ISSUER=EMC \
        ISSUED=10-Jan-2014 NOTICE="ACTIVATED TO License Site Number: \
        PTA06JUN20131086059" SN=2162734 SIGN="00EC 6B99 FB75 280D B932 \
        75DD 21D1 EC00 5634 5848 462F 7ACD 0032 5081 2923"
'''
