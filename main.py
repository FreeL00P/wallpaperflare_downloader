import requests
from lxml import html
from urllib.parse import quote

def get_html(url):
    try:
        response = requests.get(url)
        # 如果请求成功 (status code 200)
        if response.status_code == 200:
            return response.text
        else:
            print(url)
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def parse_html(html_content):
    if html_content is not None:
        # 使用lxml的html模块解析HTML
        #print(html_content)
        tree = html.fromstring(html_content)

        # 使用XPath选择器提取你需要的数据
        pre_imgs = tree.xpath('//*[@id="gallery"]/li')
        pre_imgs_list=[]
        for pre_img in pre_imgs:
            pre_imgs_list.append(pre_img.xpath('./figure/a/@href')[0])
        # 返回解析后的数据
        return pre_imgs_list
    else:
        return None
def get_pre_img_url(urls):
    # 原图链接集合
    img_urls=[]
    img_url_alt={}
    for url in urls:
        url=url+"/download"
        html_content = get_html(url)
        if html_content is not None:
            # 使用lxml的html模块解析HTML
            #print(html_content)
            tree = html.fromstring(html_content)

            # 使用XPath选择器提取你需要的数据
            img_url = tree.xpath('//*[@id="show_img"]/@src')
            img_alt = tree.xpath('//*[@id="show_img"]/@alt')[0]
            img_url_alt={img_url[0]:img_alt}
            # print(img_url_alt)
            img_urls.append(img_url_alt)
        else:
            continue
        img_url_alt={}
    return img_urls

def main():
    # 定义要爬取的网址
    url = 'https://www.wallpaperflare.com/search?wallpaper='
    try:
        wallpaper_key=input("请输入壁纸关键字：")
        start_page=int(input("输入起始页码："))
        end_page=int(input("输入结束页码："))
    except:
        print("输入错误！")
        exit()
    for i in range(start_page,end_page+1):
        url = url + quote(wallpaper_key) + '&page=' + str(i)
        print(url)
        # 发送请求并获取HTML内容
        html_content = get_html(url)
        # 解析HTML内容,得到的是图片的下载页面
        pre_img_urls = parse_html(html_content)
        print(pre_img_urls)
        # 获取图片的原图
        img_urls=get_pre_img_url(pre_img_urls)
        print(img_urls)

if __name__ == "__main__":
    main()
