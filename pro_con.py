import uuid

import os

import re

import requests
from lxml import html
from urllib.parse import quote
import threading
from queue import Queue

wallpaper_key = input("请输入壁纸关键字：")

# 创建队列
url_queue = Queue()
pre_img_url_queue = Queue()

def get_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            #print(url)
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def parse_html(html_content):
    if html_content is not None:
        tree = html.fromstring(html_content)
        pre_imgs = tree.xpath('//*[@id="gallery"]/li')
        # pre_imgs_list = []
        for pre_img in pre_imgs:
            # pre_imgs_list.append(pre_img.xpath('./figure/a/@href')[0])
            #print(pre_img.xpath('./figure/a/@href')[0])
            pre_img_url_queue.put(pre_img.xpath('./figure/a/@href')[0])
        #return  pre_img.xpath('./figure/a/@href')[0]

    else:
        return None

def get_pre_img_url(url):
    url = url + "/download"
    html_content = get_html(url)
    img_url_alt={}
    if html_content is not None:
        tree = html.fromstring(html_content)
        img_url = tree.xpath('//*[@id="show_img"]/@src')
        img_alt = tree.xpath('//*[@id="show_img"]/@alt')[0]
        img_url_alt = {img_url[0]: img_alt}
    return img_url_alt

def download_image(url, save_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"Image downloaded successfully to {save_path}")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def producer():
    while True:
        try:
            url = url_queue.get()
            html_content = get_html(url)
            parse_html(html_content)
            #pre_img_urls = parse_html(html_content)
            #pre_img_url_queue.put(pre_img_urls)
        finally:
            url_queue.task_done()

def consumer():
    while True:
        try:
            pre_img_urls = pre_img_url_queue.get()
            img_url_alt = get_pre_img_url(pre_img_urls)
            for img_url, img_alt in img_url_alt.items():
                img_alt = safeFilename(img_alt)
                main_path = f"D:/壁纸/欧根/{wallpaper_key}"  # 文件保存路径，如果不存在就会被重建
                if not os.path.exists(main_path):  # 如果路径不存在
                    os.makedirs(main_path)
                uid = str(uuid.uuid4())
                suid = ''.join(uid.split('-'))
                save_path = f'{main_path}/{img_alt}{suid[1:6]}.jpg'  # 修改为实际保存路径和文件名
                download_image(img_url, save_path)
        finally:
            pre_img_url_queue.task_done()
def safeFilename(filename, replace=''):
    return re.sub(re.compile(
        '[/\\\:*?"<>|]')
        , replace,
        filename
    )
def main():
    url = 'https://www.wallpaperflare.com/search?wallpaper='
    try:
        start_page = int(input("输入起始页码："))
        end_page = int(input("输入结束页码："))
    except:
        print("输入错误！")
        exit()

    # 创建生产者线程
    for _ in range(1):
        t = threading.Thread(target=producer)
        t.daemon = True
        t.start()

    # 创建消费者线程
    for _ in range(10):
        t = threading.Thread(target=consumer)
        t.daemon = True
        t.start()

    # 将URL添加到队列
    for i in range(start_page, end_page + 1):
        url = url + quote(wallpaper_key) + '&page=' + str(i)
        url_queue.put(url)
        if  i==end_page+1:
            exit()

    # 等待所有URL被处理
    url_queue.join()
    pre_img_url_queue.join()

if __name__ == "__main__":
    main()
