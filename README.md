如果你使用的华为云 那么请移步 https://github.com/Arronlong/py_scripts/tree/master/scripts/cf2dns
感谢小伙伴的辛勤付出 搞定了华为云这个世纪难题

### 功能介绍

筛选出优质的Cloudflare IP（目前在暂不开源，以接口方式提供15分钟更新一次），并使用域名服务商提供的API解析到不同线路以达到网站加速的效果（目前只完成DNSPod和阿里云DNS，后续如果有需求将会加入其他运营商的）。

**详细的使用场景请移步我的[小站](https://hostmonit.com/cloudflare-select-ip-plus/)**


### 适用人群

1. 小站长，网站经常被打或网站放置在国外需要稳定且速度相对快的CDN
2. 服务器在国外但是想建站的小伙伴
3. 科学上网加速，拯救移动线路（未测试）

### 使用方法

>  必要条件: 
>
> ★ Cloudflare自选IP并已接入到DNSPod或阿里云DNS，不知道怎么自选IP可以查看这个[教程](https://hostmonit.com/manually-select-ip/)
>
> ★ Python3、pip环境

#### 方法一：GitHub Actions 运行（推荐）

1. 登录[腾讯云后台](https://console.cloud.tencent.com/cam/capi)或者[阿里云后台](https://help.aliyun.com/document_detail/53045.html?spm=a2c4g.11186623.2.11.2c6a2fbdh13O53),获取 SecretId、SecretKey，如果使用阿里云DNS，注意需要添加DNS控制权限**AliyunDNSFullAccess**

2. Fork本项目到自己的仓库![fork.png](https://img.hostmonit.com/images/2020/11/05/fork.png)

3. 进入第二步中Fork的项目，点击Settings->Secrets-New secret，分别是DOMAINS，KEY，SECRETID，SECRETKEY。

   > - DOMAINS  需改域名信息，填写时注意不要有换行  例如：`{"hostmonit.com": {"@": ["CM","CU","CT"], "shop": ["CM", "CU", "CT"], "stock": ["CM","CU","CT"]},"4096.me": {"@": ["CM","CU","CT"], "vv":["CM","CU","CT"]}}`
   > - KEY      API密钥，从[商店](https://shop.hostmonit.com)购买KEY，也可以使用这个KEY `o1zrmHAF` ，区别是 `o1zrmHAF` 是历史优选的Cloudflare IP(也可以从这个[网站](https://stock.hostmonit.com/CloudFlareYes)查到IP的信息)，而购买的KEY是15分钟内获取到的对各运营商速度最优的的Cloudflare IP
   > - SECRETID  第一部中从[腾讯云后台](https://console.cloud.tencent.com/cam/capi)或者[阿里云后台](https://help.aliyun.com/document_detail/53045.html?spm=a2c4g.11186623.2.11.2c6a2fbdh13O53),获取到的 `SECRETID  `
   > - SECRETKEY  第一部中从[腾讯云后台](https://console.cloud.tencent.com/cam/capi)或者[阿里云后台](https://help.aliyun.com/document_detail/53045.html?spm=a2c4g.11186623.2.11.2c6a2fbdh13O53),获取到的 `SECRETKEY`

   ![secret.png](https://img.hostmonit.com/images/2020/11/05/secret.png)

4. 修改您项目中的 `cf2dns_actions.py`文件中的`AFFECT_NUM`和`DNS_SERVER`参数，继续修改`.github/workflows/run.yml` 文件，定时执行的时长(建议15分钟执行一次)，最后点击 `start commit` 提交即可在Actions中的build查看到执行情况，如果看到 `cf2dns` 执行日志中有 `CHANGE DNS SUCCESS` 详情输出，即表示运行成功。**需要注意观察下次定时是否能正确运行，有时候GitHub Actions 挺抽风的**

   ![modify.png](https://img.hostmonit.com/images/2020/11/05/modify.png)

   

   ![commit.png](https://img.hostmonit.com/images/2020/11/05/commit.png)

   

   ![build.png](https://img.hostmonit.com/images/2020/11/05/build.png)

#### 方法二：在自己的VPS或电脑中运行

1. 安装运行脚本所需依赖

```python
pip install -r requirements.txt
```

2. 登录[腾讯云后台](https://console.cloud.tencent.com/cam/capi)或者[阿里云后台](https://help.aliyun.com/document_detail/53045.html?spm=a2c4g.11186623.2.11.2c6a2fbdh13O53),获取 SecretId、SecretKey，如果使用阿里云DNS，注意需要添加DNS控制权限**AliyunDNSFullAccess**

3. 将脚本下载到本地修改cf2dns.py中的SecretId、SecretKey

4. 修改脚本中域名配置信息，可配置多个域名和多个子域名，注意选择DNS服务商

5. (可选)从[商店](https://shop.hostmonit.com)购买KEY，当然也可以用脚本中自带的，区别是脚本中自带的KEY是历史优选的Cloudflare IP(也可以从这个[网站](https://stock.hostmonit.com/CloudFlareYes)查到IP的信息)，而购买的KEY是15分钟内获取到的最新的Cloudflare IP。

6. 运行程序，如果能够正常运行可以选择cron定时执行(建议15分钟执行一次)

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

