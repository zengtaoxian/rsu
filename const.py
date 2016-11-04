#!/usr/bin/env python
# -*- coding: UTF-8 -*-

CONF_FILE = 'conf.json'

LOG_DIR = 'log'
LOG_FILE_NAME = 'rsu.log'
LOG_FILE_BACKUP_COUNT = 5
LOG_FILE_MAX_SIZE = 1024 * 1024 * 10


DL_BUFFER_SIZE = 1024 * 1024 * 10

BASE_DIR_KEY = 'base_dir'
LOG_LEVEL_KEY = 'log_level'
SCAN_TIME_KEY = 'scan_time'
FILE_DIR_KEY = 'file_dir'
DLFAIL_DIR_KEY = 'dlfail_dir'
ULFAIL_DIR_KEY = 'ulfail_dir'
DONE_DIR_KEY = 'done_dir'
FTP_IP_KEY = 'ftp_ip'
FTP_PORT_KEY = 'ftp_port'
FTP_USERNAME_KEY = 'ftp_username'
FTP_PASSWORD_KEY = 'ftp_password'
FTP_DLT_NUM_KEY = 'ftp_dlt_num'
OSS_ULT_NUM_KEY = 'oss_ult_num'
PROC_POOL_NUM_KEY = 'pool_num'
OSS_ENDPOINT_KEY = 'endpoint'
OSS_KEY_ID_KEY = 'key_id'
OSS_KEY_SECRET_KEY = 'key_secret'
OSS_BUCKET_KEY = 'bucket'
OSS_BRAND_MAP_KEY = 'brand_map'

FTP_SUFFIX = '.ftp'
DLING_SUFFIX = '.dling'
DLFAIL_SUFFIX = '.dlfail'
WAV_SUFFIX = '.wav'
ULING_SUFFIX = '.uling'
ULFAIL_SUFFIX = '.ulfail'
