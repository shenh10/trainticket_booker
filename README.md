火车票订票助手(python版)
--测试团队外协作
===================================
由于精力原因本工具不再继续维护。Bybass非常好的实现了本脚本的功能，且更稳定更强大，有需要的同学可移步[Bypass](http://www.12306bypass.com/)
### 更新
2018-01-11 splinter改为selenium, 修改座位种类，添加对选座的支持（默认连续坐席）
2015-12-17 修复配置文件空格问题
2015-12-17 修复几处bug

### 关于该小工具
该脚本适用于12306刷票，无图形界面，需要安装python。原理为利用chrome测试工具自动化模拟鼠标点击买票，略慢于基于HTTP Request爬虫模式，优点是对网站升级与框架改变较鲁邦，且免去刷票软件缴费排队的优先级困扰。适合Mac与Linux用户及对python有一定了解的用户(Windows下安装python也可)。脚本有一定安装需求，请先配置好环境再运行此脚本。本脚本无法绕过验证码输入，需要用户手动输入验证码。具体功能见下节

### 功能介绍
- 支持多车站(起始、到达) ，脚本将自动查询各个起始终点站的排列组合
- 多日期(可列举各个日期或日期范围，无上限)
- 支持席别选择、车次选择
- 支持学生票
- 支持铃声提醒
- 支持多个乘车人
- 支持失败次数超过阈值放弃该车次
- 刷票间隔约1s
- 支持自动提交

### 安装条件
- [Chrome浏览器](https://www.google.com/chrome/browser/desktop/index.html)
- [Chrome Driver](https://sites.google.com/a/chromium.org/chromedriver/) (Mac 用户可通过brew install chromedriver安装)
- [Chrome Driver](http://npm.taobao.org/mirrors/chromedriver) (阿里国内的)
- python 2.7
- selenium
- pygame
- configparser

### 安装方法
- 网上下载对应操作系统的Chrome浏览器并安装
- 安装Chrome Driver `解压到程序目录内，或者解压下来加入到 path 里`
- 安装python(Mac 与Linux一般已预装)
- 安装pip
- 安装依赖包
``` bash
pip install selenium pygame configparser
```

### 使用方法
打开terminal，切换到脚本所在目录
``` bash
cd {YOUR_PATH_TO_THE_SCRIPT}/conf
```
从模板拷贝一份设置文件
``` bash
cp conf.ini.template conf.ini
cd ../
```
在conf.ini中设置你的用户名密码，根据注释设定对应参数；此处最重要的是获取你的起始到达站的cookie值,并填在[STATIONCOOKIE]区域下，模板中有广州和北京为示例。获取方法：打开12306 票查询界面，输入你的起始终点站与日期，点击查询。
<br>
在Chrome中右键, 选择Inspect，Chrome将弹出开发者工具。
选择Resources > Cookies > www.12306.cn
对应'_jc_save_fromStation'和'_jc_save_toStation'的值就是你的起始/终点站的cookie值，将其以‘站名=cookie值’的形式填在[STATIONCOOKIE]区域。
<br>
安装好上述依赖之后，运行脚本
``` bash
python crawler.py [config_file_path]
```
浏览器将自动跳转到登陆界面（用户名密码已填好），此时脚本停在了调试暂停状态
``` bash
(pdb)
```
在Chrome中输入验证码点击登录, 脚本输入c
``` bash
(pdb)c
```
用户便可坐等脚本自动刷新了。若刷到了余票，浏览器自动跳转到提交界面，只需输入验证码点提交即可。
<br>
脚本界面此时会显示'是否抢票成功(Y/N)'，若用户此时已抢到票，输入Y，程序退出；否则输入N，浏览器自动返回查询界面继续刷票。

### 退出程序
按Ctrl-C 退出程序（浏览器窗口随之退出）

### To do
- 包装程序
- 用户界面
- 多平台可移植

### 联系我
若有仍和疑问、建议或批评，可以给[我](thushenhan@gmail.com)发信。
