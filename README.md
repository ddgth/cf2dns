### 修复腾讯云 DNS 无法调用 —— update 2023.1.3

   [API 2.0下线通知](https://cloud.tencent.com/document/product/1278/82311) By github@z0z0r4
   
### 新增支持 Actions 自选更新 v4 或 v6 —— update 2022.12.19

> 使用方法

   1. 修改 **`.github/workflows/run.yml`**

   2. 新增 secret **`DOMAINSV6`**

### 新增支持华为云 DNS —— update 2022.10.25

> 使用方法

   1. 安装依赖 **`pip install -r requirements.txt`**

   2. 修改配置文件 **`DNS_SERVER`** **`SECRETID`**  **`SECRETKEY`** **`REGION_HW`**

### 新增优选 IPv6 功能 —— update 2022.07.06

> 使用方法

​	更新代码，修改脚本中的 `TYPE` 参数即可

### 新增默认线路记录 —— update 2021.12.15

如果需要使用默认线路，请将默认线路的cname记录移除或改为其他线路

默认：DEF

境外：AB

### Faker GFW —— update 2021.08.08

最近有很多小伙伴正遭受假墙并伴随着被勒索的困扰，现在增加了预防假墙攻击的功能

> 实现方式

​	之前不管您使用免费的 key 还是付费的 key 所筛选出来的 Cloudflare IP 都是多人共享的，如果其中有人的网站刚好被假墙，而您自选出来的 IP 刚好和他的相同，那么您的网站也有被假墙的风险，当然我也使用了各种手动去解决这个方法，比如增加接口返回 IP 数、随机获取优选 IP 等，但最总还是不能完全杜绝这情况的发现，所以现增加了一个优选 IP 池，只需在您的 key 后面加上 **`fgfw`** ,您就会每次执行脚本都能获取到 **最新的独享优选 IP** ，由于这需要消耗更多的服务器硬件和带宽资源，那么每次调用获取最新的独享优选 IP 时，您只能获取到每个运营商的 **2 条** 优选记录，并且每次调用您将消耗更多的 key 调用次数，执行频率建议与您DNS服务商的最小 TTL 保持一直（记得把脚本中的 TTL 参数也修改了）。

> 使用方法：

1. 新用户：在您购买的 KEY 后面加上 **`fgfw`** ，并按照下面教程使用即可
2. 新用户：每个运营商的 **2 条** 优选记录，所以您需要删除目前已经存在的之前优选的 A 记录然后在您购买的 KEY 后面加上 **`fgfw`** 即可。

***

### 功能介绍

筛选出优质的 Cloudflare IP（目前在暂不开源，以接口方式提供 15 分钟更新一次），并使用域名服务商提供的 API 解析到不同线路以达到网站加速的效果（目前只完成 DNSPod 和阿里云 DNS，后续如果有需求将会加入其他运营商的）。

**详细的使用场景请移步我的 [小站](https://blog.hostmonit.com/cloudflare-select-ip-plus/)**


### 适用人群

1. 小站长，网站经常被打或网站放置在国外需要稳定且速度相对快的 CDN
2. 服务器在国外但是想建站的小伙伴
3. 科学上网加速，拯救移动线路（未测试）

### 使用方法

>  必要条件: 
>
>  ★ Cloudflare 自选 IP 并已接入到 DNSPod 或阿里云 DNS ，不知道怎么自选 IP 可以查看这个 [教程](https://blog.hostmonit.com/manually-select-ip/)
>
>  ★ Python3、pip 环境

#### 方法一：在自己的 VPS 或电脑中运行（推荐）

1. 安装运行脚本所需依赖；

```python
pip install -r requirements.txt
```

2. 登录 [腾讯云后台](https://console.cloud.tencent.com/cam/capi)或者[阿里云后台](https://help.aliyun.com/document_detail/53045.html?spm=a2c4g.11186623.2.11.2c6a2fbdh13O53) ,获取 SecretId 、 SecretKey ，如果使用阿里云 DNS ，注意需要添加 DNS 控制权限 **AliyunDNSFullAccess** ；

3. 将脚本下载到本地修改 cf2dns.py 中的 SecretId 、 SecretKey ；

4. 修改脚本中域名配置信息，可配置多个域名和多个子域名，注意选择 DNS 服务商；

5. (可选)从 [商店](https://shop.hostmonit.com) 购买 KEY ，当然也可以用脚本中自带的，区别是脚本中自带的 KEY 是历史优选的 Cloudflare IP (也可以从这个 [网站](https://stock.hostmonit.com/CloudFlareYes) 查到 IP 的信息)，而购买的 KEY 是 15 分钟内获取到的最新的 Cloudflare IP 。

6. 运行程序，如果能够正常运行可以选择 cron 定时执行(建议15分钟执行一次)

```python
python cf2dns.py
```

#### 方法二： GitHub Actions 运行

1. 登录 [腾讯云后台](https://console.cloud.tencent.com/cam/capi) 或者 [阿里云后台](https://help.aliyun.com/document_detail/53045.html?spm=a2c4g.11186623.2.11.2c6a2fbdh13O53) ，获取 SecretId 、 SecretKey ，如果使用阿里云 DNS ，注意需要添加 DNS 控制权限 **AliyunDNSFullAccess** ；

2. Fork 本项目到自己的仓库 ；

   ![fork.png](https://img.hostmonit.com/images/2020/11/05/fork.png)

3. 进入第二步中 Fork 的项目，点击 Settings -> Secrets and variables -> Actions -> New repository secret ，分别是 `DOMAINS` ， `KEY` ， `SECRETID` ， `SECRETKEY` 。

   > - `DOMAINS`  需改域名信息，填写时注意不要有换行  例如：

```
{"hostmonit.com": {"@": ["CM","CU","CT"], "shop": ["CM", "CU", "CT"], "stock": ["CM","CU","CT"]},"4096.me": {"@": ["CM","CU","CT"], "vv":["CM","CU","CT"]}}
```

   > - `DOMAINSV6` 如果需要更新 AAAA 解析请增加此 secrets ，格式同 `DOMAINS` 。
   > - `KEY`      API 密钥，从 [商店](https://shop.hostmonit.com) 购买 KEY ，也可以使用这个 KEY `o1zrmHAF` ，区别是 `o1zrmHAF` 是历史优选的 Cloudflare IP (也可以从这个 [网站](https://stock.hostmonit.com/CloudFlareYes) 查到 IP 的信息)，而购买的 KEY 是 15 分钟内获取到的对各运营商速度最优的的 Cloudflare IP
   > - `SECRETID`  第 1 步中从 [腾讯云后台](https://console.cloud.tencent.com/cam/capi) 或者 [阿里云后台](https://help.aliyun.com/document_detail/53045.html?spm=a2c4g.11186623.2.11.2c6a2fbdh13O53) ，获取到的 `SECRETID`
   > - `SECRETKEY`  第 1 步中从 [腾讯云后台](https://console.cloud.tencent.com/cam/capi) 或者 [阿里云后台](https://help.aliyun.com/document_detail/53045.html?spm=a2c4g.11186623.2.11.2c6a2fbdh13O53) ，获取到的 `SECRETKEY`

   ![secret.png](https://img.hostmonit.com/images/2023/03/04/actions.png)

4. 由于 GitHub 官方出于安全考虑，默认不允许 Fork 到的仓库使用 GitHub Actions ，为了下一步顺利进行，需要手动去 Actions 标签页开启；

<img width="1212" alt="image" src="https://github.com/Mrered/cf2dns/assets/34948506/fa3405be-c0f5-427c-83e0-fbf8a0f30511">

5. 修改您项目中的 `cf2dns_actions.py` 文件中的 `AFFECT_NUM` 和 `DNS_SERVER` 参数，继续修改 `.github/workflows/run.yml` 文件，定时执行的时长(建议 15 分钟执行一次)，最后点击 `start commit` 提交即可在 Actions 中的 build 查看到执行情况，如果看到 `cf2dns` 执行日志中有 `CHANGE DNS SUCCESS` 详情输出，即表示运行成功。**需要注意观察下次定时是否能正确运行，有时候 GitHub Actions 挺抽风的**。

   ![modify.png](https://img.hostmonit.com/images/2020/11/05/modify.png)

   ![commit.png](https://img.hostmonit.com/images/2020/11/05/commit.png)

   ![build.png](https://img.hostmonit.com/images/2020/11/05/build.png)

### 免责声明

> 1.网络环境错综复杂，适合我的不一定适合你，所以尽量先尝试免费的 KEY 或者购买试用版的 KEY
>
> 2.有什么问题和建议请提 issue 或者 Email 我，不接受谩骂、扯皮、吐槽
>
> 3.为什么收费？ 这个标价我也根本不指望赚钱，甚至不够我国内一台 VDS 的钱。
>
> ★ 如果当前 DNSPod 有移动、联通、电信线路的解析将会覆盖掉

