import base64
import os.path
from volcengine.visual.VisualService import VisualService

def get_next_image_filename(directory_path):
    # 确保目录路径存在
    if not os.path.isdir(directory_path):
        raise ValueError(f"目录路径 {directory_path} 不存在")

    # 获取目录中所有 .png 文件
    png_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.png')]
    
    # 计算当前的 .png 文件数量
    count = len(png_files)
    
    # 生成下一个图片文件的名称
    next_filename = f"image_{count + 1}.png"
    
    return next_filename

def open_image(file_path):
    from PIL import Image
    # 打开图像文件
    try:
        image = Image.open(file_path)
        return image
    except Exception as e:
        return str(e)  # 返回错误信息以便调试

def paint_dance(desc, current_play_srt_index, gen_index):
    visual_service = VisualService()
    visual_service.set_ak('VOLC_ACCESS_KEY')
    visual_service.set_sk('VOLC_ACCESS_KEY')
    
    output_folder = './output_pic/'

    # 通用v2.0-文生图
    form = {
        "req_key": "high_aes_general_v20",
        "prompt": desc.strip(),
        "model_version": "general_v2.0"
    }

    # resp = visual_service.high_aes_smart_drawing(form)
    # data = base64.b64decode(resp['data']['binary_data_base64'][0])
    data = None
    try:
        # 调用函数并处理响应
        resp = visual_service.high_aes_smart_drawing(form)
        
        # 确保响应中包含预期的数据
        if 'data' in resp and 'binary_data_base64' in resp['data']:
            # 解码 base64 数据
            data = base64.b64decode(resp['data']['binary_data_base64'][0])
        else:
            raise ValueError("响应中缺少 'data' 或 'binary_data_base64'")
    
    except KeyError as e:
        print(f"响应中缺少预期的键: {e}")
    except ValueError as e:
        print(f"值错误: {e}")
    except base64.binascii.Error as e:
        print(f"Base64 解码错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    
    if not data:
        return None
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # next file_name
    # file_name = get_next_image_filename(output_folder)
    file_name = f"image_{current_play_srt_index}_{gen_index}.png"
    
    # Define the output file path
    output_path = os.path.join(output_folder, file_name)
    
    with open(output_path, 'wb') as f:
        f.write(data)
    return output_path

# if __name__ == '__main__':
#     desc = '懒羊羊躺在床上看三体这本书'
#     output_path = './output_pic/'
#     paint_dance(desc, output_path)
