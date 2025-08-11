import gradio as gr
import os
import re
import glob
import threading
import time
from wording import get
from component_manager import register_component,get_component,update_component_value
from typing import Optional
import os
import sys
import shutil
sys.path.append(os.getcwd())
from utils.files_utils import open_folder
from utils.path_utils import get_path
from processors.audio_processor import audio_pre_processor
from processors.params.process_params import AudioPreProcessParams,TextProcessParams,EnhanceProcessParams
from processors.text_processor import batch_or_split_text
from processors.model_processor import load_chat_tts
from pic_play import load_and_parse_srt,set_gen_image_flag

def copy_file(src_path, dst_path):
    # 检查源文件是否存在
    if not os.path.isfile(src_path):
        print(f"Source file {src_path} does not exist.")
        return
    
    # 确保目标目录存在，如果不存在则创建它
    dst_dir = os.path.dirname(dst_path)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    
    # 复制文件
    try:
        shutil.copy(src_path, dst_path)
        print(f"File copied from {src_path} to {dst_path}")
    except Exception as e:
        print(f"Error copying file: {e}")


def generate_audio(txtfile):

    CHAT=load_chat_tts()

    text_process_params = TextProcessParams(
    batch_processing = True,
    txt_file = txtfile,
    split_text_flag = get_component('split_text_checkbox').value,
    text = get_component('text_input').value,
    segment_length = get_component('segment_length_slider').value
    )

    text_segments = batch_or_split_text(text_process_params)



    audio_pre_Process_Params = AudioPreProcessParams(
    text_segments = text_segments,
    audio_profile_path = get_component('audio_seed_input').value,# 这里先写成固定的，后面改成动态的
    speed_slider = get_component('speed_slider').value,
    temperature = get_component('temperature_slider').value,
    top_P = get_component('top_p_slider').value,
    top_K = get_component('top_k_slider').value,
    refine_oral=get_component('oral_slider').value,
    refine_laugh=get_component('laugh_slider').value,
    refine_break=get_component('break_slider').value,
    refine_text_flag = get_component('refine_text_checkbox').value,
    nums2text_switch = get_component('nums2text_checkbox').value,
    concatenate_audio=get_component('concatenate_audio_checkbox').value,
    emb_upload=get_component('emb_upload_checkbox').value,
    emb_upload_path=get_component('emb_upload_input').value,
    srt_flag=True,
    batch_processing=True
    )
    enhance_parms = EnhanceProcessParams(
        enhance_audio=get_component('enhance_audio_checkbox').value,
        denoise_audio=get_component('denoise_audio_checkbox').value,
        nfe=get_component('nfe_slider').value,
        solver=get_component('solver_dropdown').value,
        tau=get_component('tau_slider').value,
    )
    original_audio_output,enhanced_audio_output, text = audio_pre_processor(audio_pre_Process_Params,enhance_parms,CHAT)
    
    # ################### copy final  ############### 
    file_name = os.path.splitext(os.path.basename(txtfile))[0]
    out_con_audio=os.path.join(get_path('OUTPUT_DIR'), file_name, '合并')
    concatenated_audio_path = os.path.join(out_con_audio, f"{file_name}_合并.wav")

    # add
    final_file_dir = get_component('final_output_box').value
    print(f"final_file_dir:{final_file_dir}")
    if final_file_dir:
        final_out_con_audio=os.path.join(get_path('OUTPUT_DIR'), final_file_dir)
        # 判断路径是否为文件夹
        if not os.path.isdir(final_out_con_audio):
            print(f"The path {final_out_con_audio} is not a directory.")
        # 确保目录存在，如果不存在则创建
        os.makedirs(final_out_con_audio, exist_ok=True)
        final_concatenated_audio_path = os.path.join(final_out_con_audio, f"{file_name}_合并.wav")
        # copy
        copy_file(concatenated_audio_path,final_concatenated_audio_path)

        # 复制srt文件
        srt_path = os.path.join(get_path('OUTPUT_DIR'), file_name, f'{file_name}.srt')
        final_srt_path = os.path.join(final_out_con_audio, f'{file_name}.srt')
        # copy
        copy_file(srt_path,final_srt_path)
    else:
        print("Final output directory is not set.")

    
    



# 提取文件名称中的数字，用于排序
def extract_number(filename):
    match = re.search(r'(\d+)', filename)
    return int(match.group()) if match else 0


class AudioGenerator:
    def __init__(self):
        self.current_gen_index = 0
        self.txt_files = []
        self.stop_button_flag = False
        self.stop_finish_falg = False
        self.state_box = None
        self.folder_path = None
        self.started = False
    
    def set_state_box(self, state_box):
        self.state_box = state_box
        self.state_box.value = "TEST"

    def update_state_box(self):
        return self.state_box.value
    
    def write_state_box(self, value):
        self.state_box.value = value
        print(value)
        return value
        

    def check_path_valid(self, folder_path):
        if folder_path and os.path.isdir(folder_path):
            return True
        self.write_state_box("Invalid folder path")
        return False

    def gen_next(self):
        if not self.check_path_valid(self.folder_path):
            return
        while self.current_gen_index < len(self.txt_files):
            if self.stop_button_flag:
                index = self.current_gen_index - 1
                index = index if index >= 0 else 0
                self.write_state_box(f"{self.txt_files[index]} 生成完成，已停止！")
                self.stop_finish_falg = True
                self.started = False
                break
            
            txtFile = os.path.join(self.folder_path,self.txt_files[self.current_gen_index])
            self.write_state_box(f"正在生成: {txtFile}")
            # 模拟生成过程
            # time.sleep(3)
            generate_audio(txtFile)

            self.current_gen_index += 1

        if self.current_gen_index == len(self.txt_files):
            self.write_state_box("生成完成!")

    def stop_gen(self):
        if self.stop_finish_falg == True:
            return self.write_state_box("已经停止")
        if not self.check_path_valid(self.folder_path):
            return self.update_state_box()
        self.stop_button_flag = True
        return self.write_state_box(f"等待 {self.txt_files[self.current_gen_index]} 生成结束...")
    
    def resume_gen(self):
        if self.started == True:
            return self.update_state_box()
        self.started = True
        self.stop_finish_falg = False
        self.stop_button_flag = False
        threading.Thread(target=self.gen_next).start()
        return self.update_state_box()
    
    # 跳转到指定的文件生成
    def goto_gen(self, index, folder_path):
        try:
            index = int(index)
        except ValueError:
            return "invalid index"
        # check folder path
        self.folder_path = folder_path
        if not self.check_path_valid(self.folder_path):
            return "Invalid folder path"
        
        self.txt_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if self.txt_files:
            self.txt_files = sorted(self.txt_files, key=extract_number)
        else: 
            return "cant find txt files"

        # 赋值索引值
        if not isinstance(index, int) or index <= 0 or index > len(self.txt_files):
            return "index out of range"
        else:
            self.current_gen_index = index - 1

        if self.started == True:
            return self.update_state_box()
        self.started = True
        self.stop_finish_falg = False
        self.stop_button_flag = False

        threading.Thread(target=self.gen_next).start()
        return self.write_state_box(f"跳转到{self.txt_files[self.current_gen_index]}")

    def start_gen_audio(self, folder_path):
        self.folder_path = folder_path
        if not self.check_path_valid(folder_path):
            return "Invalid folder path"
        if self.started == True:
            return "已经在生成了,重新生成,先暂停"
        if os.path.isdir(folder_path):
            self.txt_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            if self.txt_files:
                self.txt_files = sorted(self.txt_files, key=extract_number)
                self.current_gen_index = 0
                self.started = True
                self.stop_button_flag = False
                self.stop_finish_falg = False
                self.state_box.value = f"Total {len(self.txt_files)} files found and listed."
                threading.Thread(target=self.gen_next).start()
                return self.state_box.value
            else:
                return "No files found in the folder."
        else:
            return "Invalid folder path."


# 播放器
# 获取文件夹中音频文件列表 
def get_audio_files(folder_path):
    print(f"Selected folder: {folder_path}")
    if os.path.isdir(folder_path):
        files = glob.glob(os.path.join(folder_path, "*.wav"))  # Assuming audio files are .mp3
        files.sort(key=extract_number)  # Sort files alphabetically
        print("Files in the folder:")
        for file in files:
            print(file)
        print(f"Total {len(files)} files found and listed.")
        return files
    return []

def get_audio_file_path(folder_path, file_index):
    files = get_audio_files(folder_path)
    if 0 <= file_index < len(files):
        return os.path.join(folder_path, files[file_index])
    return None

def update_index(index, delta, max_index):
    new_index = index + delta
    if 0 <= new_index <= max_index:
        return new_index
    return index

audio_gen=None
final_output_box: Optional[gr.Textbox] = None


def render():
    global folder_input,select_box,state_box,audio_gen,final_output_box
    gr.Markdown('### 批量生成音频')
    gr.Markdown('使用前面设置的参数')
    audio_gen = AudioGenerator()
    
    with gr.Row():
        folder_input = gr.Textbox(label="TXT文件列表")
        final_output_box = gr.Textbox(label="输出文件夹名称(在output目录下)",value="three_body")

    with gr.Row():
        state_box = gr.Textbox(label="状态信息", autoscroll=True, every=1.0)
        audio_gen.set_state_box(state_box)  # 设置 state_box
        
    
    with gr.Row():
        start_gen_audio_button = gr.Button("开始/重新生成", variant="primary")
        stop_gen_audio_button = gr.Button("停止生成", variant="primary")
        continue_gen_audio_button = gr.Button("继续生成", variant="primary")
        goto_gen_box = gr.Textbox(label="跳转生成-从1开始")
        goto_gen_box.submit(audio_gen.goto_gen, inputs=[goto_gen_box,folder_input], outputs=state_box)
    
    # 1s刷新一次
    timer = gr.Timer()
    timer.tick(audio_gen.update_state_box, inputs=None, outputs=state_box)
    start_gen_audio_button.click(audio_gen.start_gen_audio, inputs=folder_input, outputs=state_box)
    stop_gen_audio_button.click(audio_gen.stop_gen, inputs=None, outputs=state_box)
    continue_gen_audio_button.click(audio_gen.resume_gen, inputs=None, outputs=state_box)



    # 音频播放控制 ############################
    global dir_play_input,audio_files,current_index
    gr.Markdown('### 批量播放音频')
    
    with gr.Row():
        dir_play_input = gr.Textbox(value=r"D:\work\ChatTTS-Enhanced-main\ChatTTS-Enhanced-main\output_audio\three_body",label="音频播放目录")
        status_text  = gr.Textbox(label="播放状态", interactive=False)
    audio_player = gr.Audio(label="Audio Player", autoplay=True)
    

    with gr.Row():
        play_button = gr.Button("PLAY", variant="primary")
        prev_button = gr.Button("Previous")
        next_button = gr.Button("Next")
    with gr.Row():
        jump_index_input = gr.Textbox(label="Jump to Index")
        jump_button = gr.Button("Jump")

    def play_audio_action(folder_path):
        global current_index, audio_files
        audio_files = get_audio_files(folder_path)
        if audio_files:
            current_index = 0
            print(f"index:{current_index}")
            load_and_parse_srt(current_index) # 加载字幕
            file_path = get_audio_file_path(folder_path, current_index)
            return file_path, f"正在播放: {file_path}"
        return None, "No audio files found."

    def play_previous(folder_path):
        global current_index,dir_play_input,audio_files
        if audio_files:
            current_index = update_index(current_index, -1, len(audio_files) - 1)
            print(f"index:{current_index}")
            load_and_parse_srt(current_index) # 加载字幕
            file_path = get_audio_file_path(folder_path, current_index)
            return file_path, f"正在播放: {file_path}"
        return None, "No audio files found."

    def play_next(folder_path):
        global current_index,dir_play_input,audio_files
        audio_files = get_audio_files(folder_path)
        if audio_files:
            current_index = update_index(current_index, 1, len(audio_files) - 1)
            print(f"index:{current_index}")
            file_path = get_audio_file_path(folder_path, current_index)
            load_and_parse_srt(current_index) # 加载字幕
            return file_path, f"正在播放: {file_path} index:{current_index} total:{len(audio_files)}"
        return None, "No audio files found."

    def jump_to_index(index,folder_path):
        global current_index,dir_play_input
        if audio_files:
            index = int(index)
            if 0 <= index < len(audio_files):
                current_index = index
                file_path = get_audio_file_path(folder_path, current_index)
                load_and_parse_srt(current_index) # 加载字幕
                return file_path, f"正在播放: {file_path}"
        return None, "Invalid index."


    # 顺序播放
    audio_player.stop(play_next,inputs=dir_play_input,outputs=[audio_player, status_text])
    # 图片生成控制
    audio_player.play(lambda: set_gen_image_flag(True))
    audio_player.pause(lambda: set_gen_image_flag(False))
    
    play_button.click(play_audio_action, inputs=dir_play_input, outputs=[audio_player, status_text])
    prev_button.click(play_previous, inputs=dir_play_input, outputs=[audio_player, status_text])
    next_button.click(play_next, inputs=dir_play_input, outputs=[audio_player, status_text])
    jump_button.click(jump_to_index, inputs=[jump_index_input,dir_play_input], outputs=[audio_player, status_text])

    register_component("final_output_box", final_output_box)

def listen():
    final_output_box.change(lambda value: update_component_value("final_output_box", value), inputs=final_output_box,
                          outputs=[])
