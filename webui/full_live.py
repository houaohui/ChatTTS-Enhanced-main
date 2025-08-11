import gradio as gr
import time
import re
import os
from component_manager import register_component,get_component,update_component_value

from gen_pic import open_image

index_textbox = None

full_image_player = None
output_html2 = None
full_timer = None
need_delay_time=1

full_txt_content = '字幕'
full_image_path = r'D:\work\ChatTTS-Enhanced-main\ChatTTS-Enhanced-main\output_pic\zhe_tian\image.png'

def set_need_delay_time(val):
    global need_delay_time
    need_delay_time = val

def set_full_image(path):
    global full_image_path
    full_image_path = path
    return
    
def set_full_txt(txt):
    global full_txt_content
    full_txt_content = txt
    return

def update_full_image():
    global full_image_path
    return open_image(full_image_path)

index_content = '简介'

def set_index_content(txt):
    global index_content
    index_content = txt

def update_full_text():
    global full_txt_content, need_delay_time,output_html2,index_content
    html_content = f"""
    <div style="
        position: absolute;
        top: -100px;
        left: 50%;
        transform: translateX(-50%); /* 水平居中偏移 */
        z-index: 9999;
        padding: 2px 8px;
        text-align: center;
        background: rgba(5, 5, 5, 0.6); /* 半透明背景 */
        border-radius: 15px; /* 圆角 */
        backdrop-filter: blur(15px); /* 高斯模糊效果 */
        display: inline-block; /* 根据内容宽度调整 */
    ">
        {full_txt_content + '---' + f'<span style="background-color: #007bff; color: white; padding: 2px 4px; border-radius: 3px;">{index_content}</span>'}
    </div>
    """

    # full_timer.value = need_delay_time
    # print(f"update:{need_delay_time}")

    return html_content





def output_html2_obj():
    global output_html2
    return output_html2

def full_image_player_obj():
    global full_image_player
    return full_image_player


def render():
    global full_image_player, output_html2, full_timer, index_textbox
    
    # 添加一个隐藏的 div 元素来应用 CSS
    gr.HTML('<div style="width: 100px; height: 45px;"></div>')
    
    # 简要说明
    gr.HTML(f"""
            <div style="
                width: 250px; height: 45px; 
                # border: 2px solid red;
                position: absolute;
                top: 50px;
            ">
            <h1>《三体》全集⚡️⚡️</h1>
            <p><strong>作者:</strong> 刘慈欣</p>
            <p><strong>简介:</strong>《三体》是中国科幻作家刘慈欣创作的一部小说，原名《三体》，英文版翻译为《The Three-Body Problem》。这是《三体》三部曲的第一部，其他两部是《黑暗森林》和《死神永生》。这部小说是中国科幻文学的代表作之一，获得了极高的评价和多个奖项。</p>
            </div>
    """)

    # 章节指引
    gr.HTML(f"""
            <div style="
                width: 250px;
                # border: 2px solid red;
                position: absolute;
                top: 40px;
                right: -20px;
                overflow: hidden;
            ">
            <h1> 播放索引</h1>
            <p><strong>播放章节:</strong> 三体一</p>
<pre>
第1章 科学边界
第2章 台球
第3章 射手和农场主
第4章 三体、周文王、长夜
第5章 叶文洁
第6章 宇宙闪烁之一
第7章 疯狂年代
第8章 寂静的春天
第9章 红岸之一
第10章 宇宙闪烁之二
第11章 大史
第12章 三体、墨子、烈焰
第13章 红岸之二
第14章 红岸之三
第15章 红岸之四
第16章 三体、哥白尼、宇宙橄榄球、三日凌空
第17章 三体问题
第18章 三体、牛顿、冯·诺依曼、秦始皇、三日连珠
第19章 聚会
第20章 三体、爱因斯坦、单摆、大撕裂
第21章 三体、远征

</pre>
            </div>
    """)
    # 第22章 地球叛军
# 第23章 红岸之五
# 第24章 红岸之六
# 第25章 叛乱
# 第26章 雷志成、杨卫宁之死
# 第27章 无人忏悔
# 第28章 伊文斯
# 第29章 第二红岸基地
# 第30章 地球三体运动
# 第31章 两个质子
# 第32章 古筝行动
# 第33章 监听员
# 第34章 智子
# 第35章 虫子
# 第36章 尾声·遗址
    # index_textbox = gr.Textbox(value='>第1章 科学边界',elem_id="index_textbox",interactive = False,show_label= False)

    # with gr.Row():
    full_image_player = gr.Image(label="AI实时",elem_classes="full-width-image2",value=full_image_path, width='900px', height='100vh',show_download_button=False,show_fullscreen_button=False)

    output_html2 = gr.HTML(f"""
    <div style="
        position: absolute;
        top: -100px;
        left: 50%;
        transform: translateX(-50%); /* 水平居中偏移 */
        z-index: 9999;
        padding: 2px 8px;
        text-align: center;
        background: rgba(5, 5, 5, 0.6); /* 半透明背景 */
        border-radius: 15px; /* 圆角 */
        backdrop-filter: blur(15px); /* 高斯模糊效果 */
        display: inline-block; /* 根据内容宽度调整 */
        font-size: 20px; /* 增加字体大小 */
    ">
        {full_txt_content}
    </div>
    """)


    # from wording import get
    # output_mark_down = gr.Markdown(get('VersionDescription'))
    # def update_test():
    #     return get('VersionDescription')
    # # 1s刷新一次
    # full_timer = gr.Timer()
    # full_timer.tick(update_test, inputs=None, outputs=output_mark_down)
