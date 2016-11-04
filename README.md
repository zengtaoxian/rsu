##rsu是什么?
录音同步组件

##rsu有哪些功能？

* 从ftp服务器上下载录音文件
* 将录音文件上传到阿里云

##安装和更新
1. mv rsu-xx.tar.gz path
2. cd path
3. tar -xf rsu-xx.tar.gz
4. cd rsu-xx
5. python setup.py install

##卸载
* pip uninstall rsu

##配置项
* base_dir:文件夹基准路径
* file_dir:文件文件夹
* dlfail_dir:下载失败文件夹
* ulfail_dir:上传失败文件夹
* done_dir:成功文件夹
* log_level:打印级别
* scan_time:文件扫描时间(扫描间隔时间)
* ftp_ip:ftp服务器ip
* ftp_port:ftp端口
* ftp_username:ftp用户名
* ftp_password:ftp密码
* pool_num:进程池数量(下载和上传的总和)
* endpoint:阿里云上传的endpoint
* key_id:阿里云上传的key_id
* key_secret:阿里云上传的key_secret
* bucket:阿里云上传的bucket
* brand_map:品牌路径映射(可配置多条, 未配置的默认使用品牌作为路径)

##执行
* 运行:python rsu.py start
* 停止:python rsu.py stop
* 重启:python rsu.py restart

##有问题反馈
在使用中有任何问题，欢迎反馈给我，可以用以下联系方式跟我交流

* 邮件: zengtaoxian@163.com
* QQ: 1192420585
