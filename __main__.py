import requests
import os
import time
import re
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, wait
from retrying import retry

def get_m3u8_url(url):
    session = requests.Session()
    # 访问首页获取cookie
    # session.get("https://www.yzzs113.com/", headers=headers)
    # url = "https://www.yzzs113.com/114play/20172-2-1/"
    response = session.get(url, headers=headers)
    response.encoding = "UTF-8"
    data = response.text
    # 正则抓取上面的源代码中的m3u8的url
    m3u8_uri = re.search('"url":"(.+?index.m3u8)"', data).group(1).replace('\\', '')
    # 写入文件 分析当前的页面源代码
    with open('index.html', 'wb') as f:
        # 写入response.content bytes二进制类型
        f.write(response.content)
    # 请求可以获取index.m3u8文件
    response = session.get(m3u8_uri, headers=headers)
    with open('m2u8_uri.text', 'wb') as f:
        # 写入response.content bytes二进制类型
        f.write(response.content)
    response.encoding = 'UTF-8'
    data = response.text
    # 拆分返回的内容获取真整的index.m3u8文件的url
    # 注意 一定要strip
    url = data.split('/', 3)[-1].strip()
    print(data)
    print('m2u8_uri', m3u8_uri)
    print('url', url)
    print(urljoin(m3u8_uri, url))
    url = urljoin(m3u8_uri, url)
    return url

@retry(stop_max_attempt_number=3)
def down_video(url, i):
    '''
    下载ts文件
    :param url:
    :param i:
    :return:
    '''
    # print(url)
    # 下载ts文件
    # try:
    resp = requests.get(url, headers=headers)
    with open(os.path.join(path, str(i)+'.ts'), mode="wb") as f3:
        f3.write(resp.content)
    assert resp.status_code == 200

def download_all_videos(url, path):
    # 请求m3u8文件进行下载
    resp = requests.get(url, headers=headers)
    with open("index.m3u8", mode="w", encoding="utf-8") as f:
        f.write(resp.content.decode('UTF-8'))# 下载所有ts文件
    if not os.path.exists(path):
        os.mkdir(path)
    # 开启线程 准备下载
    pool = ThreadPoolExecutor(max_workers=50)
    # 1. 读取文件
    tasks = []
    i = 0
    with open("index.m3u8", mode="r", encoding="utf-8") as f:
        for line in f:
            # 如果不是url 则走下次循环
            if line.startswith("#"):
                continue
            print(line, i)
            # 开启线程
            tasks.append(pool.submit(down_video, line.strip(), i))
            i += 1
    print(i)
    # 统一等待
    wait(tasks)
    # 如果阻塞可以给一个超时参数
    # wait(tasks, timeout=1800)

def do_m3u8_url(path, m3u8_filename="index.m3u8"):
    # 这里还没处理key的问题
    if not os.path.exists(path):
        os.mkdir(path)
    # else:
    # shutil.rmtree(path)
    # os.mkdir(path)
    with open(m3u8_filename, mode="r", encoding="utf-8") as f:
        data = f.readlines()

    fw = open(os.path.join(path, m3u8_filename), 'w', encoding="utf-8")
    abs_path = os.getcwd()
    i = 0
    for line in data:
        # 如果不是url 则走下次循环
        if line.startswith("#"):
            fw.write(line)
        else:
            fw.write(f'{abs_path}/{path}/{i}.ts\n')
            i += 1

def merge(path, filename='output'):
    '''
    进行ts文件合并 解决视频音频不同步的问题 建议使用这种
    :param filePath:
    :return:
    '''
    os.chdir(path)
    cmd = f'ffmpeg -i index.m3u8 -c copy {filename}.mp4'
    os.system(cmd)

if __name__ == '__main__':
    headers = {"User-Agent": "Mozilla/4.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
    # 电影的url 返回index.m3u8的url地址
    url = get_m3u8_url("https://www.yzzs114.com/114play/20172-2-1/")
    # # ts文件存储目录
    path = 'ts'
    # 下载m3u8文件以及ts文件
    download_all_videos(url, path)
    do_m3u8_url(path)
    # 文件合并
    merge(path, '西西里的美丽传说')
    print('over')