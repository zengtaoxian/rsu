录音同步组件

一、安装和更新
1.mv rsu-xx.tar.gz /root/ftp
2.cd /root/ftp
3.tar -xf rsu-xx.tar.gz
4.cd rsu-xx
5.python setup.py install

二、卸载
1.pip uninstall rsu

三、配置项
base_dir:文件夹基准路径
  例如:"/root/ftp/"
file_dir:文件文件夹
  例如:"file"
dlfail_dir:下载失败文件夹
  例如:"dlfail"
ulfail_dir:上传失败文件夹
  例如:"ulfail"
done_dir:成功文件夹
  例如:"done"
log_level:打印级别
  例如:"DEBUG", "INFO"
scan_time:文件扫描时间(扫描间隔时间)
ftp_ip:ftp服务器ip
ftp_port:ftp端口
ftp_username:ftp用户名
ftp_password:ftp密码
pool_num:进程池数量(下载和上传的总和)
  例如:6
endpoint:阿里云上传的endpoint
key_id:阿里云上传的key_id
key_secret:阿里云上传的key_secret
bucket:阿里云上传的bucket
brand_map:品牌路径映射(可配置多条, 未配置的默认使用品牌作为路径)

四、执行
(注意:程序为守护进程, 自带监控程序)
运行:python rsu.py start
停止:python rsu.py stop
重启:python rsu.py restart
