### 功能介绍

筛选出优质的Cloudflare IP（目前在暂不开源，以接口方式提供15分钟更新一次），并使用域名服务商提供的API解析到不同线路以达到网站加速的效果（目前只完成DNSPod，后续如果有需求将会加入其他运营商的）。

### 适用人群

1.小站长，网站经常被打或网站放置在国外需要稳定且速度相对快的CDN

2.科学上网加速，拯救移动线路（未测试）

### 使用方法

>  必要条件: 
>
> ★ Cloudflare自选IP并已接入到DNSPod，不知道怎么自选IP可以查看这个[教程](https://hostmonit.com/manually-select-ip/)
>
> ★ Python3、pip环境
>

1.安装urllib3

```python
pip install urllib3
```

2.登录[腾讯云后台](https://console.cloud.tencent.com/cam/capi),获取 SecretId、SecretKey

3.将脚本下载到本地修改cf2dns.py中的SecretId、SecretKey

4.修改脚本中域名配置信息，可配置多个域名和多个子域名

5.从[商店](https://shop.hostmonit.com)购买KEY，当然也可以用脚本中自带的，区别是脚本中自带的KEY是历史优选的Cloudflare IP（也可以从这个[网站](https://stock.hostmonit.com/CloudFlareYes)查到IP的信息），而购买的KEY是15分钟内获取到的最新的Cloudflare IP。

6.运行程序，如果能够正常运行可以选择cron定时执行（建议15分钟执行一次）

```python
python cf2dns.py
```

### 免责声明

> 1.网络环境错综复杂，适合我的不一定适合你，所以尽量先尝试免费的KEY或者购买试用版的KEY
>
> 2.有什么问题和建议请提issue或者Email我，不接受谩骂、扯皮、吐槽
>
> 3.为什么收费？ 这个标价我也根本不指望赚钱，甚至不够我国内一台VDS的钱。
>
> ★ 如果当前DNSPod有移动、联通、电信线路的解析将会覆盖掉

