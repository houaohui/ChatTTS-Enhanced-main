import gradio as gr
import time
import re
import os



# 解析 .srt 文件内容
def parse_srt(srt_content):
    pattern = r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\d+\n|$)"
    matches = re.findall(pattern, srt_content, re.DOTALL)
    parsed_srt = []
    for match in matches:
        start_time = match[1]
        end_time = match[2]
        text = match[3].replace('\n', ' ').strip()
        # print(f"S:{start_time} E:{end_time} T:{text}")
        # print('')
        parsed_srt.append((start_time, end_time, text))
    return parsed_srt

# 将时间格式转换为秒
def time_to_seconds(time_str):
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

# 初始化全局变量
parsed_srt = []
# 当前正在播放的索引值 从0开始
current_play_srt_index = 0
# 语音片段内的index 从0开始
current_index = 0
start_time = None
textbox = None

from full_live import update_full_text,update_full_image,set_full_image,set_full_txt,set_index_content
from full_live import full_image_player_obj,output_html2_obj ,set_need_delay_time,update_full_text

# 中文数字到阿拉伯数字的转换函数
def chinese_to_arabic(chinese_num):
    chinese_digits = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
                      '六': 6, '七': 7, '八': 8, '九': 9}
    return chinese_digits.get(chinese_num, None)

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

# 定时器回调函数，更新 Textbox 的内容
def update_textbox_content():
    global current_index, start_time, textbox
    if current_index >= len(parsed_srt):
        return textbox.value # 如果已经显示完所有字幕，停止更新
    
    # 获取当前播放时间
    elapsed_time = time.time() - start_time
    start_time_seconds = time_to_seconds(parsed_srt[current_index][0])
    # print(f"elapsed_time:{elapsed_time}")
    # print(f"start_time:{start_time_seconds}")
    set_need_delay_time(start_time_seconds - elapsed_time)
    # 如果当前时间到达字幕的开始时间，更新内容
    if elapsed_time >= start_time_seconds:
        text = parsed_srt[current_index][2]
        found_chapter = extract_chapter(text)
        if found_chapter:
            set_index_content(found_chapter)
        set_full_txt(text)
        current_index += 1
        textbox.value = textbox.value if textbox.value is not None else ""
        textbox.value = textbox.value + "\n\n" + text
        print(f"len_txt:{len(textbox.value)}")
        if len(textbox.value) > 2000:
            textbox.value = textbox.value[-500:]
    return textbox.value

# 从指定目录中按数字排序，读取第index个 .srt 文件并解析
def load_and_parse_srt(index):
    global parsed_srt, current_index, start_time, current_play_srt_index
    
    # 当前正在播放的索引值
    current_play_srt_index = index
    # 指定目录路径（可以替换为你的实际路径）
    directory_path = r"D:\work\ChatTTS-Enhanced-main\ChatTTS-Enhanced-main\output_audio\zhe_tian"

    # 查找目录中的所有 .srt 文件
    srt_files = [f for f in os.listdir(directory_path) if f.endswith('.srt')]
    
    if not srt_files:
        return []  # 如果没有找到 .srt 文件，返回空列表
    
    # 按文件名的数字部分排序
    srt_files.sort(key=lambda f: int(re.findall(r'\d+', f)[0]) if re.findall(r'\d+', f) else float('inf'))
    
    # 选择排序后的第一个文件
    first_srt_file = os.path.join(directory_path, srt_files[index])
    print(first_srt_file)
    
    with open(first_srt_file, 'r', encoding='utf-8') as f:
        srt_content = f.read()
    
    # 解析并重置相关变量
    parsed_srt = parse_srt(srt_content)
    current_index = 0
    start_time = time.time()

    return parsed_srt

def find_first_long_subtitle_from_index(parsed_srt, start_index, max_length):
    # 确保起始索引在有效范围内
    if start_index < 0 or start_index >= len(parsed_srt):
        print("start_index 超出范围")
        return [None, None]
    
    for i in range(start_index, len(parsed_srt)):
        _, _, text = parsed_srt[i]
        if len(text) > max_length:
            return [i,text]  # 找到第一个符合条件的字幕并返回 返回字母对应的索引值，和字符
    
    return [None, None]  # 如果没有找到符合条件的字幕，返回 None

def find_cached_image(gen_index, current_play_srt_index):
    # 指定目录路径
    directory_path = r"D:\work\ChatTTS-Enhanced-main\ChatTTS-Enhanced-main\output_pic\zhe_tian"
    
    # 生成文件路径
    cached_image = os.path.join(directory_path, f"image_{current_play_srt_index}_{gen_index}.png")
    
    # 检查文件是否存在
    if os.path.exists(cached_image):
        return cached_image
    else:
        return None  # 或者可以返回其他适当的提示信息，如 "File not found"


from gen_pic import paint_dance,open_image
from sele_gen_pic import gen_pic_sele
gen_pic_ok = False
gen_picing = False
image_player = None
now_image_path = r"D:\work\ChatTTS-Enhanced-main\ChatTTS-Enhanced-main\output_pic\zhe_tian\image.png"
# 是否开始生成图片
gen_image_flag= False

def set_gen_image_flag(en):
    global gen_image_flag
    gen_image_flag = en
    if gen_image_flag:
        print("enable gen image")
    else:
        print("disable gen image")

# 生成图片
def gen_pic():
    global parsed_srt,current_index,gen_pic_ok,gen_picing,now_image_path
    global current_play_srt_index
    # 音频没有开始播放
    if not gen_image_flag:
        return open_image(now_image_path),update_full_image()
    print('gen image start')
    if gen_picing:
        print("gen...")
        return open_image(now_image_path),update_full_image()
    gen_picing = True
    gen_pic_ok = False
    while not gen_pic_ok:
        # 这里判断图片是否已经生成，如果已经生成，使用已经生成的图片进行播放
        # 需要变量，当前的语音片段index，当前的语音片段对应的图片的index
        gen_index,txt = find_first_long_subtitle_from_index(parsed_srt, current_index, 50)
        # 根据gen_index 和 current_play_srt_index 来找到对应的图像文件名称
        cached_image = find_cached_image(gen_index,current_play_srt_index)
        if cached_image:
            gen_pic_ok = True
            gen_picing = False
            now_image_path = cached_image
            print(f"find cached image:{cached_image}")
            break
        else:
            print("no cached image found")

        if txt: 
            print(f"start gen pic... txt:{txt}")
            # gen_image_path = paint_dance(txt, current_play_srt_index, gen_index) #根据 current_play_srt_index, gen_index生成图片名称
            gen_image_path = gen_pic_sele(txt, current_play_srt_index, gen_index) #根据 current_play_srt_index, gen_index生成图片名称
            if gen_image_path:
                now_image_path = gen_image_path  # 显示生成的图片
                print("gen pic success!!!")
                gen_pic_ok = True
                gen_picing = False
                break
            else:
                print("gen faild retry...")
        else:
            print("no find txt retry...")
        if not gen_image_flag:
            gen_pic_ok = True
            gen_picing = False
            print("stoped.")
            break
        time.sleep(5)
    set_full_image(now_image_path)
    return open_image(now_image_path), update_full_image()


def render():
    global textbox, image_player
    with gr.Column():
        
        # 添加一个隐藏的 div 元素来应用 CSS
        gr.HTML('<div style="width: 100px; height: 45px;"></div>')

        with gr.Row():  
            with gr.Row():
                # 显示图片
                image_player = gr.Image(label="AI实时",elem_classes="full-width-image",value=now_image_path, height='92vh',show_download_button=False,show_fullscreen_button=False)
            with gr.Column():
                # 输入框和按钮
                textbox = gr.Textbox(label="字幕显示", elem_id="subtitle_textbox",interactive = False,lines=17,max_lines=17,autoscroll=True)
                gr.Markdown('# 《三体》全集⚡️⚡️')
                gr.Markdown('作者: 刘慈欣')
                gr.Markdown('简介:《三体》是中国科幻作家刘慈欣创作的一部小说，原名《三体》，英文版翻译为《The Three-Body Problem》。这是《三体》三部曲的第一部，其他两部是《黑暗森林》和《死神永生》。这部小说是中国科幻文学的代表作之一，获得了极高的评价和多个奖项。')
                gr.Markdown('正在播放章节: 三体1')
                # start_button = gr.Button("Start")

                # start_button.click(load_and_parse_srt, inputs=None, outputs=None)
                # 1s刷新一次

                # 使用这种方式可以避免报错
                output_html2 = output_html2_obj()
                full_image_player = full_image_player_obj()

                timer = gr.Timer()
                timer.tick(update_textbox_content, inputs=None, outputs=[textbox])

                # 30s刷新一次
                timer_pic = gr.Timer(value=12)
                timer_pic.tick(gen_pic, inputs=None, outputs=[image_player,full_image_player])

                # 当值改变时触发
                textbox.change(update_full_text, inputs=None, outputs=[output_html2])
