#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import multiprocessing
import datetime
import time
import os
import sys
import json
import oss2
import ftplib
import logging
import logging.handlers
from const import *
from cloghandler import ConcurrentRotatingFileHandler as FileHandler
import signal
from daemon import Daemon

user_cfg = None


def load_cfg():
    """
    加载配置
    """

    _levelNames = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARN': logging.WARNING,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET,
    }

    with open(CONF_FILE) as f:
        global user_cfg
        user_cfg = json.load(f)

    log_dir = os.path.join(user_cfg[BASE_DIR_KEY], LOG_DIR)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, LOG_FILE_NAME)
    log = logging.getLogger()
    log_file = os.path.abspath(log_path)
    log_handler = FileHandler(filename=log_file,
                              maxBytes=LOG_FILE_MAX_SIZE,
                              backupCount=LOG_FILE_BACKUP_COUNT)

    fmt = "[%(asctime)s] %(process)d %(levelname)s %(lineno)d %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt)
    log_handler.setFormatter(formatter)

    log.addHandler(log_handler)
    log.setLevel(_levelNames.get(user_cfg[LOG_LEVEL_KEY], logging.INFO))


def get_file_path(dir_date, file_name, suffix):
    """
    获取文件路径
    :param dir_date: 文件夹日期
    :param file_name: 文件名
    :param suffix: 后缀
    """
    return '{0}{1}/{2}/{3}{4}'.format(user_cfg[BASE_DIR_KEY],
                                      user_cfg[FILE_DIR_KEY],
                                      dir_date, file_name, suffix)


def get_upload_path(file_name, suffix):
    """
    获取上传路径
    :param file_name: 文件名
    :param suffix: 后缀
    """
    _, brand, _, file_date = file_name.rsplit('_')
    app_dir = user_cfg[OSS_BRAND_MAP_KEY].get(brand, brand)
    return '{0}/{1}/{2}{3}'.format(app_dir, file_date, file_name, suffix)


def init_pool():
    """
    初始化进程池, 忽略SIGINT信号, 防止CTRL+C退出时打印出错
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class ScanLocalFileWork:
    def __init__(self):
        self.proc_pool = multiprocessing.Pool(
            processes=user_cfg[PROC_POOL_NUM_KEY], initializer=init_pool)
        self.suffix_handle = {
            FTP_SUFFIX: self.notify_download,
            DLING_SUFFIX: self.downloading,
            DLFAIL_SUFFIX: self.download_fail,
            WAV_SUFFIX: self.notify_upload,
            ULING_SUFFIX: self.uploading,
            ULFAIL_SUFFIX: self.upload_fail
        }

    @staticmethod
    def get_yesterday_dir():
        """
        获取昨天文件夹
        """
        yesterday = datetime.date.today() + datetime.timedelta(days=-1)
        yesterday_date = yesterday.strftime('%Y%m%d')
        yesterday_dir = '{0}{1}/{2}'.format(user_cfg[BASE_DIR_KEY],
                                            user_cfg[FILE_DIR_KEY],
                                            yesterday_date)
        logging.debug("yesterday_dir:{0}".format(yesterday_dir))
        return yesterday_date, yesterday_dir

    @staticmethod
    def get_today_dir():
        """
        获取今天文件夹
        """
        today = datetime.date.today()
        today_date = today.strftime('%Y%m%d')
        today_dir = '{0}{1}/{2}'.format(user_cfg[BASE_DIR_KEY],
                                        user_cfg[FILE_DIR_KEY],
                                        today_date)
        logging.debug("today_dir:{0}".format(today_dir))
        return today_date, today_dir

    def notify_download(self, dir_date, file_name, suffix):
        """
        通知下载
        :param dir_date: 文件夹日期
        :param file_name: 文件名
        :param suffix: 后缀
        """
        old_path = get_file_path(dir_date, file_name, suffix)
        new_path = old_path.replace(suffix, DLING_SUFFIX)
        logging.debug("notify_download, old_path:{0}, new_path:{1}".format(
            old_path, new_path))
        try:
            os.rename(old_path, new_path)
        except Exception, e:
            logging.error("e:{0}, old_path:{1}, new_path:{2}".format(
                e, old_path, new_path))
        self.proc_pool.apply_async(download_task,
                                   args=(dir_date, file_name, suffix))

    @staticmethod
    def downloading(dir_date, file_name, suffix):
        """
        下载中
        :param dir_date: 文件夹日期
        :param file_name: 文件名
        :param suffix: 后缀
        """
        pass

    @staticmethod
    def download_fail(dir_date, file_name, suffix):
        """
        下载失败
        :param dir_date: 文件夹日期
        :param file_name: 文件名
        :param suffix: 后缀
        """
        old_path = get_file_path(dir_date, file_name, suffix)
        new_path = old_path.replace(user_cfg[FILE_DIR_KEY],
                                    user_cfg[DLFAIL_DIR_KEY]).replace(
            suffix, FTP_SUFFIX)
        new_dir = os.path.dirname(new_path)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        logging.warn("download_fail, old_path:{0}, new_path:{1}".format(
            old_path, new_path))
        try:
            os.rename(old_path, new_path)
        except Exception, e:
            logging.error("e:{0}, old_path:{1}, new_path:{2}".format(
                e, old_path, new_path))

    def notify_upload(self, dir_date, file_name, suffix):
        """
        通知上传
        :param dir_date: 文件夹日期
        :param file_name: 文件名
        :param suffix: 后缀
        """
        old_path = get_file_path(dir_date, file_name, suffix)
        new_path = old_path.replace(suffix, ULING_SUFFIX)
        logging.debug("notify_upload, old_path:{0}, new_path:{1}".format(
            old_path, new_path))
        try:
            os.rename(old_path, new_path)
        except Exception, e:
            logging.error("e:{0}, old_path:{1}, new_path:{2}".format(
                e, old_path, new_path))
        self.proc_pool.apply_async(upload_task, (dir_date, file_name, suffix))

    @staticmethod
    def uploading(dir_date, file_name, suffix):
        """
        上传中
        :param dir_date: 文件夹日期
        :param file_name: 文件名
        :param suffix: 后缀
        """
        pass

    @staticmethod
    def upload_fail(dir_date, file_name, suffix):
        """
        上传失败
        :param dir_date: 文件夹日期
        :param file_name: 文件名
        :param suffix: 后缀
        """
        old_path = get_file_path(dir_date, file_name, suffix)
        new_path = old_path.replace(user_cfg[FILE_DIR_KEY],
                                    user_cfg[ULFAIL_DIR_KEY]).replace(
            suffix, WAV_SUFFIX)
        new_dir = os.path.dirname(new_path)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        logging.warn("upload_fail, old_path:{0}, new_path:{1}".format(old_path,
                                                                      new_path))

        try:
            os.rename(old_path, new_path)
        except Exception, e:
            logging.error("e:%{0}, old_path:{1}, new_path:{2}".format(
                e, old_path, new_path))

    def scan_dir(self, dir_date, dir_path):
        """
        扫描文件夹
        :param dir_date: 文件夹日期
        :param dir_path: 文件夹路径
        """
        for file_name in os.listdir(dir_path):
            try:
                file_name, suffix = file_name.rsplit('.', 1)
                suffix = '.' + suffix
                logging.debug(
                    "scan_dir, dir_date:{0}, file_name:{1}, suffix:{2}".format(
                        dir_date, file_name, suffix))
                self.suffix_handle[suffix](dir_date, file_name, suffix)
            except Exception, e:
                logging.error("e:{0}, file_name:{1}".format(e, file_name))

    def run(self):
        """
        执行
        """
        while True:
            yesterday_date, yesterday_dir = self.get_yesterday_dir()
            if os.path.exists(yesterday_dir):
                self.scan_dir(yesterday_date, yesterday_dir)

            today_date, today_dir = self.get_today_dir()
            if os.path.exists(today_dir):
                self.scan_dir(today_date, today_dir)

            time.sleep(user_cfg[SCAN_TIME_KEY])

    def exit(self):
        self.proc_pool.close()
        self.proc_pool.join()


def scan_work():
    """
    扫描工作进程
    """
    logging.warn("scan_proc, pid:{0}".format(os.getpid()))

    scan = ScanLocalFileWork()
    scan.run()


def download_task(dir_date, file_name, suffix):
    """
    下载任务
    :param dir_date: 文件夹日期
    :param file_name: 文件名
    :param suffix: 后缀
    """
    old_path = get_file_path(dir_date, file_name, DLING_SUFFIX)
    new_path = old_path.replace(DLING_SUFFIX, DLFAIL_SUFFIX)
    try:
        with open(old_path, 'wb') as f:
            ftp = ftplib.FTP()
            try:
                ftp.set_pasv(True)
                ftp.connect(user_cfg[FTP_IP_KEY], user_cfg[FTP_PORT_KEY])
                ftp.login(user_cfg[FTP_USERNAME_KEY],
                          user_cfg[FTP_PASSWORD_KEY])
                ftp.retrbinary('RETR ' + file_name + WAV_SUFFIX, f.write,
                               DL_BUFFER_SIZE)
                ftp.close()
                new_path = old_path.replace(DLING_SUFFIX, WAV_SUFFIX)
            except Exception, e:
                ftp.close()
                logging.error("e:{0}, file_name:{1}".format(e, file_name))
    except Exception, e:
        logging.error("e:{0}, old_path:{1}".format(e, old_path))

    logging.debug(
        "download_task, suffix:{0}, old_path:{1}, new_path:{2}".format(
            suffix, old_path, new_path))

    try:
        os.rename(old_path, new_path)
    except Exception, e:
        logging.error("e:{0}, old_path:{1}, new_path:{2}".format(
            e, old_path, new_path))


def upload_task(dir_date, file_name, suffix):
    """
    上传任务
    :param dir_date: 文件夹日期
    :param file_name: 文件名
    :param suffix: 后缀
    """
    auth = oss2.Auth(user_cfg[OSS_KEY_ID_KEY],
                     user_cfg[OSS_KEY_SECRET_KEY])
    bucket = oss2.Bucket(auth, user_cfg[OSS_ENDPOINT_KEY],
                         user_cfg[OSS_BUCKET_KEY])

    old_path = get_file_path(dir_date, file_name, ULING_SUFFIX)
    new_path = old_path.replace(ULING_SUFFIX, ULFAIL_SUFFIX)
    upload_path = get_upload_path(file_name, suffix)
    try:
        result = bucket.put_object_from_file(upload_path, old_path)
        if result.status == 200:
            new_path = old_path.replace(user_cfg[FILE_DIR_KEY],
                                        user_cfg[DONE_DIR_KEY]).replace(
                ULING_SUFFIX, suffix)
            url = 'http://{0}.{1}/{2}'.format(user_cfg[OSS_BUCKET_KEY],
                                              user_cfg[OSS_ENDPOINT_KEY],
                                              upload_path)
            logging.info("url:{0}".format(url))
        else:
            logging.warn("upload_task, status:{0}, upload_path:{1}".format(
                result.status, upload_path))
    except Exception, e:
        logging.error("e:{0}, upload_path:{1}, old_path:{2}".format(
            e, upload_path, old_path))
    new_dir = os.path.dirname(new_path)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    logging.debug(
        "upload_task, suffix:{0}, old_path:{1}, new_path:{2}".format(
            suffix, old_path, new_path))

    try:
        os.rename(old_path, new_path)
    except Exception, e:
        logging.error(
            "e:{0}, old_path:{1}, new_path:{2}".format(e, old_path, new_path))


class Rsu(Daemon):
    """录音同步组件"""

    def __init__(self, proc_name):
        Daemon.__init__(self, proc_name)
        self.proc_list = []

        multiprocessing.freeze_support()

        base_dir = user_cfg[BASE_DIR_KEY]
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        dir_list = [user_cfg[FILE_DIR_KEY], user_cfg[DLFAIL_DIR_KEY],
                    user_cfg[ULFAIL_DIR_KEY], user_cfg[DONE_DIR_KEY]]
        for file_dir in dir_list:
            full_dir = os.path.join(base_dir, file_dir)
            if not os.path.exists(full_dir):
                os.makedirs(full_dir)

    def run(self):
        """
        运行
        """
        logging.warn("main_run, pid:{0}".format(os.getpid()))
        self.proc_list.append(multiprocessing.Process(target=scan_work,
                                                      name="scan"))
        for proc in self.proc_list:
            proc.start()

        logging.debug(self.proc_list)
        logging.warn(user_cfg)

        for proc in self.proc_list:
            proc.join()


def main():
    try:
        load_cfg()
        main_pid = os.getpid()

        if len(sys.argv) == 2:
            rsu = Rsu(sys.argv[0])
            if 'start' == sys.argv[1]:
                logging.warn("main_proc, pid:{0}, start".format(main_pid))
                rsu.start()
            elif 'stop' == sys.argv[1]:
                logging.warn("main_proc, pid:{0}, stop".format(main_pid))
                rsu.stop()
            elif 'restart' == sys.argv[1]:
                logging.warn("main_proc, pid:{0}, restart".format(main_pid))
                rsu.restart(main_pid)
            else:
                print 'Unknown command {0}'.format(sys.argv[1])
                sys.exit(2)
            sys.exit(0)
        else:
            print 'Usage: {0} start|stop|restart'.format(sys.argv[0])
            sys.exit(2)
    except Exception, e:
        logging.error("e:{0}".format(e))


if __name__ == '__main__':
    main()
