from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re
import time
import shutil
from pathlib import Path

# gloable var
started = False
driver = None

def move_and_rename_png(src_dir, dest_dir, play_srt_index, gen_index):
    # 确保源目录和目标目录存在
    if not os.path.isdir(src_dir):
        raise FileNotFoundError(f"Source directory {src_dir} does not exist.")
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)

    # 获取源目录中所有的 .png 文件
    png_files = list(Path(src_dir).glob('*.png'))
    
    if not png_files:
        print("No .png files found in the source directory.")
        return

    # 获取最新的 .png 文件
    latest_file = max(png_files, key=os.path.getmtime)

    # 定义新的文件名
    new_file_name = f"image_{play_srt_index}_{gen_index}.png"
    dest_file_path = Path(dest_dir) / new_file_name

    # 剪切文件到目标目录，并重命名
    shutil.move(latest_file, dest_file_path)

    print(f"Moved {latest_file} to {dest_file_path}")
    return dest_file_path



# 设置 Options
def sele_init():
    global driver
    options = Options()
    options.add_argument("user-data-dir=C:/Users/16997/AppData/Local/Google/Chrome/User Data")  # 替换为实际的用户数据目录路径

    # 初始化 WebDriver（以 Chrome 为例）
    driver = webdriver.Chrome(options=options)

    # 打开目标网页
    driver.get('https://aihh.hzlesu.cn/h5/painting/make.html')  # 替换成你要访问的页面



def gen_pic_sele(play_srt_index, gen_index):
    global started
    # 初始化
    if not started:
        sele_init()
        started = True
    
    # 定义检查登录状态的元素特征
    login_avatar_locator = (By.XPATH, "//img[@src='https://aihh.hzlesu.cn/h5/painting/static/img/user_avatar.png']")

    print('检测登录状态...')
    try:
        # 等待直到登录头像元素出现或达到超时
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(login_avatar_locator)
        )
        print('已登陆')
    except:
        print('未检测到登录状态或登录头像元素未出现')

        # 提示用户登录
        input('请完成登录操作并按 Enter 键继续...')
        
        # 可选：在登录后重新检查
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(login_avatar_locator)
            )
            input('用户已成功登录 Enter 键继续...')
        except:
            print('登录超时或未成功登录')



    # 接收用户输入的数据
    user_input = input('请输入画面描述的关键词: ')

    # 定义 textarea 和提交按钮的定位
    textarea_locator = (By.CSS_SELECTOR, "textarea.form-control.form-control-sm")
    submit_button_locator = (By.CSS_SELECTOR, "button.btn.btn-primary.exec-generate-btn")

    try:
        # 定位到 textarea 元素并输入数据
        textarea = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(textarea_locator)
        )
        textarea.clear()
        textarea.send_keys(user_input)
        
        # 定位到提交按钮并点击
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(submit_button_locator)
        )
        submit_button.click()
        
        print('数据已输入并提交，等待生成')

    except Exception as e:
        print(f'操作失败: {e}')


    # 定义下载按钮的定位
    download_button_locator = (By.XPATH, "//img[@src='static/img/icon-download-lg.png']")

    try:
        # 等待直到下载按钮元素出现或达到超时
        download_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(download_button_locator)
        )
        # 点击下载按钮
        download_button.click()
        print('开始下载')

    except Exception as e:
        print(f'下载按钮操作失败: {e}')
    time.sleep(1)
    
    try:
        # 等待直到登录头像元素出现或达到超时
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(login_avatar_locator)
        )
        print('下载完成')
    except:
        print('下载超时')

    # 替换以下路径为你的源目录和目标目录
    source_directory = r'C:\Users\16997\Downloads'
    destination_directory = './output_pic/'

    return move_and_rename_png(source_directory, destination_directory, play_srt_index, gen_index)


current_play_srt_index = 100  # 示例值，替换为实际值
gen_index = 1  # 示例值，替换为实际值

# gen_pic_sele(current_play_srt_index, gen_index)

# 中文数字到阿拉伯数字的转换函数
def chinese_to_arabic(chinese_num):
    chinese_digits = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
                      '六': 6, '七': 7, '八': 8, '九': 9}
    return chinese_digits.get(chinese_num, None)

# # 提取章节并转换中文数字为阿拉伯数字
# def extract_chapter(text):
#     print(f"extract_chapter: {text}")

#     # 使用正则表达式匹配 "第n章" 的格式，其中 n 是单个汉字
#     pattern = r'第([\u4e00-\u9fa5])章'
    
#     # 使用 re.findall 提取所有匹配的章节信息
#     matches = re.findall(pattern, text)
    
#     # 将中文数字转换为阿拉伯数字并生成匹配的章节信息列表
#     chapters = []
#     for match in matches:
#         arabic_num = chinese_to_arabic(match)
#         if arabic_num is not None:
#             chapters.append(f'第{arabic_num}章')
    
#     # 判断是否找到匹配的章节信息
#     if chapters:
#         print(f"chapters: {chapters}")
#         return chapters
#     else:
#         return None

# 提取章节并转换中文数字为阿拉伯数字
def extract_chapter(text):
    # 使用正则表达式匹配 "第n章" 的格式，其中 n 是单个汉字
    pattern = r'第([\u4e00-\u9fa5])章(.+)'
    
    # 使用 re.search 提取第一个匹配的章节信息及其后面的所有内容
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        chinese_number = match.group(1)
        chapter_content = match.group(2)
        
        # 转换中文数字到阿拉伯数字
        arabic_number = chinese_to_arabic(chinese_number)
        
        if arabic_number is not None:
            chapter_info = f"第{arabic_number}章 {chapter_content}"
        else:
            chapter_info = f"第{chinese_number}章 {chapter_content}"
        
        return chapter_info
    else:
        return None
    
    
# 示例用法
text = "前言部分\n第七章这是章节内容的开始。这里是章节的具体内容，可能会有很多文字。"
chapter_content = extract_chapter(text)
print(f"{chapter_content}")


input("continue")

driver.quit()