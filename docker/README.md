### 增加dddb/cf2dns docker镜像  --update 2024.6.4

> 使用方法

1. 拉取cf2dns docker镜像 `docker pull dddb/cf2dns`

2. 新建cf2dns_docker工作路径 `cd ~ && mkdir -p cf2dns_docker/logs && cd cf2dns_docker`

3. 下载所需配置文件 `wget --no-check-certificate -qO ./config.ini https://raw.githubusercontent.com/ddgth/cf2dns/master/docker/src/config.ini`

4. 根据注释修改`config.ini`配置文件

5. 运行docker镜像 `docker run -d -v ~/cf2dns_docker/config.ini:/cf2dns/src/config.ini -v ~/cf2dns_docker/logs:/cf2dns/logs dddb/cf2dns`

6. 查看运行日志 `tail -100f ~/cf2dns_docker/logs/cf2dns.log`