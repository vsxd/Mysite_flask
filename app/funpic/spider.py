import re
import os
import random
import datetime
import time
import hashlib
import base64
from bs4 import BeautifulSoup
import requests
import threading
from ..models import FunPic
from .. import db


class Tools:

    @staticmethod
    def parse(img_hash, constant):
        # 反哈希 解析出图片地址
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


class Spider:

    def __init__(self, url='http://jandan.net/ooxx', page_num=3):
        self.Headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': 'nsfw-click-load=off; bad-click-load=on; gif-click-load=on',  # 关闭NSFW
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.99 Safari/537.36'
        }
        self.Js_file = None
        self.url = url
        self.page_num = page_num
        self._constant = ''
        self.soup_list = []
        self.links = []

        self.init_soup_list()
        self.init_constant()
        self.links_antihash()

    def init_soup_list(self):
        for i in range(self.page_num):
            time.sleep(0.5)
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
            # print('js_file_url=' + js_file_url)
            self.Js_file = requests.get(js_file_url, headers=self.Headers).text
        cons = re.search(
            r'var\sc=.\w+\(e,\"(\w+)\"\)', self.Js_file)  # 得到原js函数中的一个用于解析的字符串实参
        self._constant = cons.group(1)

    def links_antihash(self):
        for soup in self.soup_list:
            for item in soup.select('.img-hash'):
                url = 'http:' + Tools.parse(item.text, self._constant)  # 使用Tools类的解析方法反哈希
                replace = re.match(r'(.*\.sinaimg\.cn\/)(\w+)(\/.+\.gif)', url)
                if replace:
                    url = replace.group(1) + 'large' + replace.group(3)  # 获得原图url
                self.links.append(url)  # 添加图片地址


class Downloader:

    def __init__(self, spider=Spider(), max_threads=10, mode='rank'):
        self.index_list = []
        self.url_list = spider.links
        self._soup_list = spider.soup_list
        self._page_num = spider.page_num
        self.thread_lock = threading.BoundedSemaphore(value=max_threads)  # 设置最大线程数
        self.Headers = spider.Headers.update({'host': 'wx3.sinaimg.cn'})
        if mode is 'all':
            self.get_index_randomed(pic_num=len(self.url_list))
        elif mode is 'rank':
            self.get_index_ranked()
        else:
            random.seed(datetime.datetime.now())  # 设置随机数种子
            self.get_index_randomed()

    def download_pic(self):
        for index in self.index_list:
            self.thread_lock.acquire()  # 获得线程锁
            print(self.url_list[index])
            print(type(self.url_list[index]))
            thread = threading.Thread(target=self._download_thread,
                                      args=(self.url_list[index], ))
            # 此处有疑问，args=([实参])？ 而不是 args=(实参)？
            # 其实args=tuple，当只有一个实参时，需要args=(实参, )
            thread.start()  # 线程开始

    def _download_thread(self, url):
        # 下载线程
        file_name = os.path.basename(url)
        print('Pic: ', file_name)
        with open('pics/' + file_name, 'wb') as pic:
            pic.write(requests.get(url, headers=self.Headers).content)
        self.thread_lock.release()  # 释放线程锁

    '''获得随机的下标 或选取全部下标'''
    def get_index_randomed(self, pic_num=5):
        pic_num = pic_num * self._page_num
        pic_num_max = len(self.url_list)
        if pic_num < pic_num_max:
            index = [i for i in range(len(self.url_list))]
            for i in range(pic_num):
                ind = int(random.random() * len(index))
                self.index_list.append(index.pop(ind))
        else:  # 如果pic_nupdownum大于max则选择全部下标
            for i in range(pic_num_max):
                self.index_list.append(i)

    '''筛选图片 得到评价相对好的图片'''
    def get_index_ranked(self):
        for soup in self._soup_list:
            votes_list = soup.find('ol', {'class': 'commentlist'}).find_all(
                'div', {'class': 'jandan-vote'})
            like_scores = []  # 每张图片的oo数
            unlike_scores = []  # 每张图片的xx数
            for vote in votes_list:
                like = vote.find(
                    'span', {'class': 'tucao-like-container'}).find('span').string
                like_scores.append(int(like))
                unlike = vote.find(
                    'span', {'class': 'tucao-unlike-container'}).find('span').string
                unlike_scores.append(int(unlike))
            for index in map(like_scores.index, like_scores):
                # 选取oo大于xx三倍 且 xx小于25的图片
                if (like_scores[index] > unlike_scores[index] * 3) and (unlike_scores[index] < 25):
                    self.index_list.append(index)


class LinkSaver:
    def __init__(self, downloader=Downloader):
        self.url_list = downloader.url_list
        self.index_list = downloader.index_list

    def save_to_database(self):
        for url in self.url_list:
            pic = FunPic(piclink=url,
                         disabled=False)
            if self.url_list.index(url) in self.index_list:
                pic.info = 'good'
            else:
                pic.info = 'not good'
            db.session.add(pic)
            db.session.commit()
