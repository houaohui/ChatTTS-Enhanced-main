import gradio as gr
from wording import get
import batch_option
import text_options
import seed_option
import aduio_option
import enhance_option
import output_option
import config_option
import live_paly
import pic_play
import full_live
from webuiutils import read_config, get_server_config

main_page = None
live_page = None
# tab visibale
tab_visible = True


# 自定义 CSS 样式去掉 Tab 组件的边框
css_code = """
.input-textarea {
    font-size: 30px; color: red; 
}

body, html {
    margin: 0;
    padding: 0;
    height: 100%;
}

/* 隐藏 Webkit 浏览器中的滚动条 */
body::-webkit-scrollbar {
  display: none; /* 隐藏滚动条 */
}

body {
  overflow: scroll; /* 保留滚动功能 */
  -ms-overflow-style: auto; /* 只适用于 Internet Explorer 和 Edge */
}


.full-width-image img {
    object-fit: cover;
    width: 100%;
    height: 100%;
}

.full-width-image2 img {
    object-fit: cover;
    width: 100%;
    height: 100%;
}

.full-width-image2 {
  margin: 0 auto;
}

# 章节导航
.index_textbox {
    width: 200px;
    background-color: black;
    position: absolute;
    top: 20px;
    right: -20px;
}

#custom-tab-content {
    border: none !important;
    box-shadow: none !important;
}

footer {
    visibility: hidden;
}
"""

theme = gr.themes.Soft().set(
    input_text_size = "*text_lg",
    input_text_weight = "500",
    block_border_color_dark = "#242424",
)

def main():
    global tab_1,tab_2,tab_3
    
    with gr.Blocks(css=css_code, theme=theme,fill_width=True,fill_height=True) as main_page:
        with gr.Tab("Component 1", visible=tab_visible, elem_id="custom-tab-content"): #标签页1
            gr.Markdown(get('Title'))
            gr.Markdown(get('VersionDescription'))
            with gr.Row():
                with gr.Column():
                    batch_option.render()
                    with gr.Row():
                        gr.Markdown(get('TextOptionsTitle'))
                    text_options.render()
                    with gr.Row():
                        gr.Markdown(get('SeedOptionsTitle'))
                    seed_option.render()
                    with gr.Row():
                        gr.Markdown(get('AudioOptionsTitle'))
                    aduio_option.render()
                    with gr.Row():
                        gr.Markdown(get('AudioEnhancementTitle'))
                    enhance_option.render()

                with gr.Column():
                    output_option.render()
                    gr.Markdown(get('configmanager'))
                    config_option.render()
                    with gr.Accordion(get('HelpTitle'), open=False):
                        gr.Markdown(get('HelpContent'))
                        with gr.Row():
                            gr.Markdown(" ")
                        with gr.Row():
                            gr.Markdown(" ")
                    with gr.Row():
                        gr.Markdown('🔧项目地址:https://github.com/CCmahua/ChatTTS-Enhanced')
        
        with gr.Tab("Component 2", visible=tab_visible, elem_id="custom-tab-content"): #标签页2
            with gr.Row():
                with gr.Column():
                    live_paly.render()
        with gr.Tab("Component 3", visible=tab_visible, elem_id="custom-tab-content"): #标签页3
            
            full_live.render() # 这两个顺序不能倒

        with gr.Tab("Component 4", visible=tab_visible, elem_id="custom-tab-content"): #标签页3
            with gr.Column():
                    pic_play.render()



        batch_option.listen()
        text_options.listen()
        seed_option.listen()
        aduio_option.listen()
        enhance_option.listen()
        output_option.listen()
        live_paly.listen()

        config = read_config('config.ini')
        custom_server, ip_address, port = get_server_config(config)

        if custom_server:
            main_page.launch(share=False, inbrowser=True, server_name=ip_address, server_port=port)
        else:
            main_page.launch(share=False, inbrowser=True)   



if __name__ == '__main__':
    main()