import re
import random
import datetime
import time
import hashlib
import base64
from bs4 import BeautifulSoup
import requests
import threading
from ..models import FunPic


class Tools:
    '''解析哈希过后的img url'''
    @staticmethod
    def parse(img_hash, constant):
        q = 4
        constant = Tools.parse_md5(constant)
        o = Tools.parse_md5(constant[0:16])
        l = img_hash[0:q]
        c = o + Tools.parse_md5(o + l)
        img_hash = img_hash[q:]
        k = Tools.decode_base64(img_hash)
        h = list(range(256))
        b = list(range(256))

        for g in range(0, 256):
            b[g] = ord(c[g % len(c)])

        f = 0
        for g in range(0, 256):
            f = (f + h[g] + b[g]) % 256
            tmp = h[g]
            h[g] = h[f]
            h[f] = tmp

        result = ""
        p = 0
        f = 0
        for g in range(0, len(k)):
            p = (p + 1) % 256
            f = (f + h[p]) % 256
            tmp = h[p]
            h[p] = h[f]
            h[f] = tmp
            result += chr(k[g] ^ (h[(h[p] + h[f]) % 256]))
        result = result[26:]
        return result

    '''提供parse()函数需要的md5()'''
    @staticmethod
    def parse_md5(src):
        m = hashlib.md5()
        m.update(src.encode("utf8"))
        return m.hexdigest()

    '''提供parse()所需要的decode_base64()'''
    @staticmethod
    def decode_base64(data):
        missing_padding = 4 - len(data) % 4
        if missing_padding:
            data += '=' * missing_padding
        return base64.b64decode(data)

#
# class Infos:
#     # global infos
#     HEADERS = {
#         'Accept-Language': 'zh-CN,zh;q=0.9',
#         'Cookie': 'nsfw-click-load=off; bad-click-load=on; gif-click-load=on',  # 关闭NSFW
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
#         AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.99 Safari/537.36'
#     }
#
#     JS_FILE = None


class Spider:

    def __init__(self, url='http://jandan.net/ooxx', page_num=3, mode='rank'):
        self.Headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': 'nsfw-click-load=off; bad-click-load=on; gif-click-load=on',  # 关闭NSFW
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.99 Safari/537.36'
        }
        self.Js_file = None
        self.url = url
        self.page_num = page_num
        self.mode = mode
        self._constant = ''
        self.soup_list = []
        self.links = []
        self.index_list = []
        random.seed(datetime.datetime.now())  # 设置随机数种子
        self.init_soup_list()
        self.init_constant()

    def init_soup_list(self):
        '''返回包含page_num个beautifsoup对象的列表 page_num是返回的页面数目
        已验证可爬取无聊图http://jandan.net/pic 和 妹子图 http://jandan.net/ooxx'''
        for i in range(self.page_num):
            # time.sleep(1)
            print('Url:', self.url)
            html = requests.get(self.url, headers=self.Headers).text
            soup = BeautifulSoup(html, 'lxml')
            self.soup_list.append(soup)
            self.url = 'http:' + \
                       soup.select('.previous-comment-page')[0]['href']  # 得到下一页的url

    def init_constant(self):
        # js中加密函数的常量参数是在某段时间内是固定的 所以可以只在构造函数钟获取一次
        if self.Js_file is None:  # js文件只获取一次 多次会跳转页面
            j = self.soup_list[0].find('script', {'src': re.compile(
                r'\/\/cdn.jandan.net\/static\/min.*?\.js')})
            js_file_url = "http://" + j['src'][2:]
            print('js_file_url=' + js_file_url)
            self.Js_file = requests.get(js_file_url, headers=self.Headers).text
        cons = re.search(
            r'var\sc=.\w+\(e,\"(\w+)\"\)', self.Js_file)  # 得到原js函数中的一个用于解析的字符串实参
        self._constant = cons.group(1)

    def link_antihash(self):
        for soup in self.soup_list:
            for item in soup.select('.img-hash'):
                self.links.append(item.text)  # 得到所有哈希过后的图片地址

    def get_rank_index(self):
        '''筛选图片 得到评价相对好的图片 参数为beautifulsoup对象'''
        votes_list = soup.find('ol', {'class': 'commentlist'}).find_all(
            'div', {'class': 'jandan-vote'})
        like_socres = []  # 每张图片的oo数
        unlike_socres = []  # 每张图片的xx数
        # index_list = []  # 高质量图片的下标
        for vote in votes_list:
            like = vote.find(
                'span', {'class': 'tucao-like-container'}).find('span').string
            like_socres.append(int(like))
            unlike = vote.find(
                'span', {'class': 'tucao-unlike-container'}).find('span').string
            unlike_socres.append(int(unlike))
        for index in map(like_socres.index, like_socres):
            # 选取oo大于xx三倍 且 xx小于25的图片
            if (like_socres[index] > unlike_socres[index] * 3) and (unlike_socres[index] < 25):
                self.index_list.append(index)

    def get_random_index(self, pic_num, pic_num_max):
        '''在一定index范围内获得随机的下标 或 选取全部下标 参数为得到的图片数与页面最大图片数'''
        # index_list = []
        if pic_num < pic_num_max * 0.75:  # 防止传入参数超过边界 选取数接近总数时随机效率会很低 故取0.75*max
            for i in range(pic_num):
                index = int(random.random() * pic_num_max)
                while index in self.index_list:  # 随机选取的图片已存在时 再次选取
                    index = int(random.random() * pic_num_max)
                self.index_list.append(index)
        else:  # 参数越界后选取全部图片
            for i in range(pic_num_max):
                self.index_list.append(i)


class Downloader:

    def __init__(self, spider, max_threads=10):
        self.url_list = spider.pages
        self.thread_lock = threading.BoundedSemaphore(value=max_threads)  # 设置最大线程数
        self.Headers = spider.Headers


    def download_pic(self, file_name, url):
        print('Pic: ', file_name)
        with open('pics/' + file_name, 'wb') as pic:
            pic.write(requests.get(url, headers=self.Headers).content)
        self.thread_lock.release()  # 释放线程锁


class LinkSaver:
    Pic = FunPic()


# def spider(soup, pic_num=3, Mode='random'):
#     '''处理解析后的地址 选择图片 保存图片
#     参数为beautifulsoup对象 每页爬取图片数pic_num 选取图片的方式Mode有'Random'与'HighQuality'两种方式'''
#     result = get_constant_and_hash(soup)
#     constant = result[0]  # 用于parse()的常量字符串
#     hash_list = result[1]  # 哈希过后的图片地址list
#     index_list = []  # 需要保存的图片在hash_list中的下标
#
#     if Mode is 'random':  # 根据参数选择图片下载模式
#         index_list = get_random_index(pic_num, len(hash_list))
#     elif Mode is 'rank':
#         index_list = get_rank_index(soup)
#     else:
#         return None
#
#     for index in index_list:
#         img_hash = hash_list[index]
#         url = 'http:' + Tools.parse(img_hash, constant)
#         replace = re.match(r'(.*\.sinaimg\.cn\/)(\w+)(\/.+\.gif)', url)
#         if replace:
#             url = replace.group(1) + 'large' + replace.group(3)  # 获得原图url
#         ext_match = re.match(r'.*(\.\w+)', url)
#         extension_name = ext_match.group(1)  # 获得图片扩展名
#         md5 = hashlib.md5()
#         md5.update(url.encode("utf8"))  # 用md5后的图片url作为文件名
#         file_name = md5.hexdigest() + extension_name
#         Infos.HEADERS['host'] = 'wx3.sinaimg.cn'  # 此处利用了HEADERS 但会使其不能再用于获取html
#         thread_lock.acquire()  # 获得线程锁
#         thread = threading.Thread(target=download_pic, args=(file_name, url))
#         thread.start()  # 线程开始


# def main():
#     '''main'''
#     soup_list = get_soup_list(page_num=2)  # 妹子图
#     # soup_list = get_soup_list('http://jandan.net/pic', 5)  # 无聊图
#     for soup in soup_list:
#         time.sleep(2)
#         spider(soup, pic_num=100, Mode='Random')
