from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import time
import shutil
from pathlib import Path

# gloable var
started = False
driver = None
options = None

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
    global driver,options
    options = Options()
    # options.add_argument("--headless")  # 运行时不显示浏览器窗口
    options.add_argument("user-data-dir=C:/Users/16997/AppData/Local/Google/Chrome/User Data")  # 替换为实际的用户数据目录路径

    # 初始化 WebDriver（以 Chrome 为例）
    driver = webdriver.Chrome(options=options)

    # 打开目标网页
    driver.get('https://aihh.hzlesu.cn/h5/painting/make.html')  # 替换成你要访问的页面



def gen_pic_sele(desc, play_srt_index, gen_index):
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
        print('请完成登录操作并按 Enter 键继续...')
        
        # 可选：在登录后重新检查
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(login_avatar_locator)
            )
            input('用户已成功登录 Enter 键继续...')
        except:
            print('登录超时或未成功登录')
        return None



    # 接收用户输入的数据
    user_input = desc

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

    # 创建显式等待对象
    wait = WebDriverWait(driver, 30)  # 设置最长等待时间为 30 秒

    try:
        # 使用显式等待检查 img 元素是否存在
        img = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".-top-content > img")))
        print("Image element exists.")
    except TimeoutException:
        print("Image element does not exist within the given time.")
        return None
    
    # 获取 img 的 src 属性
    src = img.get_attribute("src")

    # 检查 src 是否为空
    if src:
        if src.strip():  # 确保 src 不是空字符串
            print(f"Image src is not empty: {src}")
        else:
            print("Image src is an empty string")
            return None
    else:
        print("Image src attribute is not present")
        return None


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
    destination_directory = './output_pic/zhe_tian/'

    return move_and_rename_png(source_directory, destination_directory, play_srt_index, gen_index)

