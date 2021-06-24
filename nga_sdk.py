import requests
import time
import os
import json
import re

import demjson

def clear_html_re(src_html):
    '''
    正则清除HTML标签
    :param src_html:原文本
    :return: 清除后的文本
    '''
    content = re.sub(r"</?(.+?)>", "", src_html) # 去除标签
    # content = re.sub(r"&nbsp;", "", content)
    dst_html = re.sub(r"\s+", "", content)  # 去除空白字符
    return dst_html

def logging(text):
    print(text)

# 使用cookies登录，从控制台-网络-当前网址-标头中找到字符串形式存储的cookies作为参数传入。
# * 在控制台使用document.cookie返回的cookie无法用于登录，切记
def set_cookies(cookie_str):
    cookies_1 = {}
    for line in cookie_str.split(';'):
        key, value = line.split('=', 1)
        cookies_1[key] = value
    return cookies_1

# 去除可能存在的的控制字符
def remove_control_chars(str_input):
    return str_input

# lite=js会返回js文件，它的主体是一个json，但包含一个变量名，这里是去除掉这个变量名
# 这里输入的参数应该是一个requests请求的返回对象，返回dict
def translate_js(jstext):
    return json.loads(remove_control_chars(jstext.text)[33:], strict=False)

class NGA(object):
    def __init__(self):
        self.url = "https://ngabbs.com"   # 设置泥潭的URL，默认为bbs.nga.cn * 总之记得加斜杠
        self.get_cookies()
        self.login()

    def get_cookies(self):
        # 在同一目录下存储一个名为cookies的文件储存字符串形式的cookies
        if "cookies" in os.listdir('.'):
            logging("检测到已经存在的cookies，尝试使用该cookies...")
            with open("cookies", "r") as f:
                self.cookies = set_cookies(f.read())
            return True
        else:
            logging("没有检测到cookies，请输入一个...")
            cookie_str = input()
            self.cookies = set_cookies(cookie_str)
            with open("cookies", "w") as f:
                f.write(cookie_str)
            return True


    def login(self):
        # 将cookies写入session
        self.session = requests.Session()
        self.session.cookies.update(self.cookies)
        r = self.session.get(url=self.url + "/thread.php?fid=-7&lite=js")   # 水区需要登录才能访问，用来做验证
        if "[查看所需的权限/条件]" not in r.text:
            logging("登录成功...")
            return True
        else:
            logging("登陆失败，打印返回值。你可能需要更新cookies...")
            logging(r.text)
            return False

    # 添加附件(在做了在做了)
    def upload_attachments(self):
        return "", ""

    # 添加附件（上传图片并返回引用链接）
    def upload_image(self, fid, tid, filenamelist):
        imageUrl = []
        imageTag = []
        attachments = []
        attachments_check = []
        pid = self.image_save_pid(tid)
        for f in filenamelist:
            loopCheck = 1
            while loopCheck == 1:
                try:
                    url=self.url+f"/post.php?lite=js"
                    post_data = {
                        "aciton":"modify",
                        "tid":tid,
                        "pid":pid,
                        "__inchst": "UTF8"
                    }
                    r = self.session.post(url=url, data=post_data, cookies=self.cookies)
                    result = translate_js(r)
                    auth = result['data']['auth']
                    attach_url = result['data']['attach_url']
                    files = {'attachment_file1': ('image.jpg', open(f, 'rb'))}
                    payload = {
                        'v2': 1,
                        'func': 'upload',
                        'auth': auth,
                        'lite': 'js',
                        'fid':'-7340336',
                        'attachment_file1_dscp': '',
                        'attachment_file1_url_utf8_name': 'image',
                        'attachment_file1': files,
                        'attachment_file1_watermark': ''
                    }
                    r = requests.post(attach_url, files=files, data = payload)
                    js_json = remove_control_chars(r.text)[33:]
                    data = demjson.decode(js_json)
                    
                    imageUrl.append('./' + data['data']['url'])
                    imageTag.append('[img]./' + data['data']['url'] + '[/img]')
                    attachments.append(data['data']['attachments'])
                    attachments_check.append(data['data']['attachments_check'])
                    loopCheck = 0
                except:
                    pass
        post_attachments = ''
        post_attachments_check = ''
        for a in attachments:
            post_attachments = post_attachments + '\t' + a
        for a_c in attachments_check:
            post_attachments_check = post_attachments_check + '\t' + a_c
        self.modify_reply(tid, pid, '', '存图.jpg.zip', post_attachments[1:], post_attachments_check[1:])
        return imageUrl,imageTag


    # 用于查询图楼最后一帖的位置（PID），并返回附件数量，用于计算是否需要创建新回复（用于存图）
    def image_save_pid(self, tid):
        url=self.url+f"/read.php?lite=js"
        post_data = {
            "tid":tid
        }
        r = self.session.post(url=url, data=post_data, cookies=self.cookies)
        js_json = remove_control_chars(r.text)[33:]
        data = demjson.decode(js_json)
        replies = data['data']['__T']['replies']
        page = ((replies + 1) // 20) + 1
        repo_max = replies % 20
        post_data = {
            "tid":tid,
            "page":page
            
        }
        r = self.session.post(url=url, data=post_data, cookies=self.cookies)
        js_json = remove_control_chars(r.text)[33:]
        data = demjson.decode(js_json)
        if 'attachs' in data['data']['__R'][str(repo_max)]:
            image_list = data['data']['__R'][str(repo_max)]['attachs']
            image_len = len(image_list)
        else:
            image_len = 0
        pid = data['data']['__R'][str(repo_max)]['pid']
       
        if image_len <= 25:
            return pid
        else:
            self.reply_post(tid, "", "这是正文.zsbd")
            #time.sleep(2)
            return pid            
            

    # 将标题设置为蓝色（需版务权限）
    def set_blue(self, tid):
        url=self.url+f"/nuke.php?lite=js"
        post_data = {
            "__lib":"topic_color",
            "__act":"set",
            "tid":tid,
            "font": ",blue",  # blue\red\green\orange\silver  # B 加粗\I 斜体\U 删除线，需要用逗号隔开，例如[,B,blue]
            "opt":"20", # 基础 48，-14 移出精华区，-15 加入精华区，-24 移除推荐值，-28 增加推荐值
            "raw":"3"
        }
        r = self.session.post(url=url, data=post_data, cookies=self.cookies)
        js_json = remove_control_chars(r.text)[33:]
        data = demjson.decode(js_json)
        logging("对tid:" + str(tid) + "操作的结果：" + data['data']['0'].encode('latin-1').decode('gbk'))
        
    # 将帖子设置为隐藏（需版务权限）
    def set_hide(self, tid):
        url=self.url+f"/nuke.php?lite=js"
        post_data = {
            "__lib":"topic_lock",
            "__act":"set",
            "ids":str(tid)+',0',
            "ton": "0",
            "toff":"0",
            "pon":"1026", #隐藏，1024是锁定，1026是锁隐（即1024+2）
            "poff":"0",#这个设置成2的话，则是解除隐藏，1024是解除锁定，1026是解除锁隐（即1024+2）
            "raw":"3"
        }
        r = self.session.post(url=url, data=post_data, cookies=self.cookies)
        js_json = remove_control_chars(r.text)[33:]
        data = demjson.decode(js_json)
        logging("对tid:" + str(tid) + "操作的结果：" + data['data']['0'].encode('latin-1').decode('gbk'))


    # 自动翻译检查
    def check_auto_translate(self):
        return 0
    
    # 获取主题列表
    # thread.php单独访问时显示论坛内的全部主题，添加限制条件可以用于筛选主题，例如此函数所做的那样
    # 而添加一个searchpost字段(默认会赋值1，实际上无需赋值)会显示论坛内的全部回复
    def get_posts(self, fid=0, page=1, recommend=0, order_by=0, nounion=0, authorid=0, searchpost=False):
        fid = f"&fid={fid}" if fid else ""
        page = f"&page={page}"
        recommend = "&recommend=1" if recommend else ""         # 是否搜寻精品贴
        order_by = f"&order_by={order_by}" if order_by else ""  # 排序依据，postdatedesc为按照发帖时间排序，lastpostdesc为按照回复时间排序(默认)
        authorid = f"&authorid={authorid}" if authorid else ""  # 搜索特定用户的发言
        nounion = f"&nounion={nounion}"                         # 是否搜寻子版面，0为搜寻1为不搜寻
        searchpost = "&searchpost=1" if searchpost else ""      # 见上方注释
        url = self.url + "/thread.php?lite=js" + fid + page + recommend + order_by + nounion + authorid + searchpost
        r = self.session.get(url)
        thread = translate_js(r)
        
        if 'error' in thread:
            # 如果检测到错误
            logging ("ERROR：" + thread['error']['0'])
            return False
        
        # 原数据是一个键为字符串编号的dict，这里直接转化为list输出更方便索引
        return [i for i in thread['data']['__T'].values()]

    # 获取特定主题的内容
    def get_single_post(self, tid, page=1, authorid=0):
        tid = f"&tid={tid}"                                     # 这里tid就是必选的了
        page = f"&page={page}"
        authorid = f"&authorid={authorid}" if authorid else ""  # 搜索特定用户的发言
        url = self.url + "/read.php?lite=js" + tid + page + authorid
        r = self.session.get(url)
        read = translate_js(r)

        if 'error' in read:
            # 如果检测到错误
            logging ("ERROR：" + read['error']['0'])
            return False

        # 这里需要输出主题信息、主题中的用户信息以及每层的内容，就不转化为list了(可能存在抽楼，楼层号不一定是连续的)，就改一下键名
        return {
            "forum": read['data']['__F'],
            "post": read['data']['__T'],
            "replys": read['data']['__R'],
            "users": read['data']['__U']
        }


    # 发表新主题，要求的是fid(版面号)
    def new_post(self, fid, post_subject, post_content):
        return self.posting(fid=fid, url=self.url + f"/post.php?lite=js", action='new', subject=post_subject, content=post_content)

    # 回复一个主题，要求的是tid(主题号)
    def reply_post(self, tid, reply_subject, reply_content):
        return self.posting(tid=tid, url=self.url + f"/post.php?lite=js", action='reply', subject=reply_subject, content=reply_content)

    # 编辑一个主题，要求的是tid
    def modify_post(self, tid, post_subject, post_content):
        return self.posting(tid=tid, url=self.url + f"/post.php?lite=js", action='modify', subject=post_subject, content=post_content)

    
    # 回复一个回复
    # 1. 对回复的操作除了pid(回复号)，fid和tid也都需要提供(为什么呀)
    # 2. 事实上回复一个回复是通过引用的形式完成的，即你点击回复按钮之后会在输入栏里默认加载类似于
    #    [b]Reply to [pid=450243169,15617411,1]Reply[/pid] Post by [uid=36270126]_江天万里霜_[/uid] (2020-09-05 01:01)[/b]
    #    的内容，但是使用API发表回复时你需得手动添加进去。
    # 3. 虽然但是，即使回复中没有引用的内容，只要是通过reply这一post请求发送的回复都会使被回复方收到消息。
    def reply_reply(self, tid, pid, reply_subject, reply_content):
        url=self.url+f"/read.php?lite=js"
        post_data = {
            "pid":pid
        }
        r = self.session.post(url=url, data=post_data, cookies=self.cookies)
        js_json = remove_control_chars(r.text)[33:]
        data = demjson.decode(js_json)
        
        uid = data['data']['__R']['0']['authorid']
        username = data['data']['__U'][str(uid)]['username']
        postdate = data['data']['__R']['0']['postdate']
        reply_text = '[b]Reply to [pid=' + str(pid) + ',' + str(tid) + ',1]Reply[/pid] Post by [uid=' + str(uid) + ']' + username + '[/uid] (' + postdate + ')[/b]\n'
        reply_content = reply_text + reply_content
        return self.posting(tid=tid, pid=pid, url=self.url + f"/post.php?lite=js", action='reply', subject=reply_subject, content=reply_content)

    
    # 编辑一个回复，同上
    def modify_reply(self, tid, pid, reply_subject, reply_content, reply_attachments="", reply_attachments_check=""):
        return self.posting(tid=tid, pid=pid, url=self.url + f"/post.php?lite=js", action='modify', subject=reply_subject, content=reply_content, attachments=reply_attachments, attachments_check=reply_attachments_check)





    # 处理发帖
    def posting(self, fid=0, tid=0, pid=0, url="", action="", subject="", content="内容过短或过长", attachments="", attachments_check=""):
        # 步骤1：在发帖/回复/引用/编辑页面加上lite=js参数和即可输出javscript格式的数据(我他妈也不知道这一步有什么用)
        # 那就不要了
        # 步骤2：添加附件
        #attachments, attachments_check = self.upload_attachments()  #原作者调用的上传附件命令，该命令无上传功能，仅返回空字符串
        #attachments, attachments_check = self.upload_image(tid, pid)        #我修改的上传附件命令，暂废弃
            
        
        # 步骤3：查询版面是否存在强制分类

        # 步骤4：获取版面翻译表
        has_auto_translate = self.check_auto_translate()

        # 步骤5：提交POST
        post_data = {
            "step": 2,
            "action": action,
            "post_subject": subject,
            "post_content": content,
            "attachments": attachments,
            "attachments_check": attachments_check,
            "has_auto_translate": has_auto_translate,
            "__inchst": "UTF8"
        }
        if fid:
            post_data['fid'] = fid
        if tid:
            post_data['tid'] = tid
        if pid:
            post_data['pid'] = pid            
        r = self.session.post(url=url, data=post_data, cookies=self.cookies)
        result = translate_js(r)
        print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
        err_ID = result['data']['__MESSAGE']['0']        
        if err_ID == "":
            # __MESSAGE字段的0是错误ID，不返回则说明发帖成功，打印提示信息文字(字段1和2)并返回True
            # 注意二哥给的数据接口文档里字段2是HTTP状态码，但是现在是3
            logging(result['data']['__MESSAGE']['1'])
            err_ID = '0'  #只是为了我后续处理方便，所以赋值0
            if re.search('\[AUTO\]', subject):
                tid = result['error']['2']#获取tid，用于设置标题颜色
                self.set_blue(tid)
            if re.search('\[图片转存\]', subject):
                tid = result['error']['2']#获取tid，用于设置帖子隐藏
                self.set_hide(tid)
            if action == 'new': #如果是发表新主题，则获取新主题的tid，并将其返回
                new_tid = result['data']['__MESSAGE']['5']
                logging('帖子ID(tid)为:' + str(new_tid))
                return err_ID, new_tid
            return err_ID
        else:
            # 若错误则返回错误的具体内容
            logging("ERROR " + result['error']['0'] + " " + result['error']['1'] + " " + result['error']['2'])
            err_message = result['data']['__MESSAGE']['1']
            if err_ID == 39 and action in ('new','reply','modify'):# 如果系统提示发帖过快（ID39），将自动等待系统提示的秒数后自动重发
                pattern = re.compile('(\d+)秒')
                wait_seconds = int((pattern.findall(err_message))[0])
                logging('系统提示发帖过快')
                for i in range(wait_seconds+1):
                    logging('程序将在' + str(wait_seconds + 1 - i) + '秒后重新发帖')
                    time.sleep(1)
                if action == 'new':
                    self.new_post(fid, subject, content)
                elif action == 'reply':
                    self.reply_post(tid, subject, content)
                elif action == 'modify':
                    # 不知道为什么编辑在触发发帖过快并根据系统提示等待指定秒数后，会出现"找不到帖子"的提示
                    # 一开始以为是少了什么参数，但多次测试发现只要再经过一定时间，就能重新编辑，这在网页版时是不会有这种情况的
                    # 所以最终的处理方案是再等待30秒（试过等待21秒依然有可能触发"找不到帖子"，懒得再试所以直接设置成30秒）
                    wait_seconds = 30
                    for i in range(wait_seconds):
                        logging('重新倒计时:' + str(wait_seconds - i) + '秒')
                        time.sleep(1)
                    if pid == 0:
                        self.modify_post(tid, subject, content)
                    else:
                        self.modify_reply(tid, pid, subject, content, attachments, attachments_check)

            return err_ID, err_message






        

