import os
import streamlit as st
import requests
from dotenv import load_dotenv
import platform
import subprocess  # 用于执行系统命令
import re          # 用于提取 Markdown 代码块
import base64
import subprocess

# 加载环境变量
load_dotenv()
API_KEY = os.environ.get("ZHIPU_API_KEY")
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 页面基础配置
st.set_page_config(page_title="Ops-Copilot", page_icon="🤖", layout="centered")

# 核心调用大模型的函数（升级支持图片）
def call_ai(prompt, base64_image=None):
    if not API_KEY:
        return "❌ 错误：未找到 ZHIPU_API_KEY，请检查 .env 文件。"
    
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    # 构建消息内容
    content = [{"type": "text", "text": prompt}]
    if base64_image:
        # 如果有图片，把图片拼进消息里
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })

    data = {
        "model": "glm-5.3", # 注意：如果 glm-5.3 不支持视觉，可换成 "glm-4v"
        "messages": [{"role": "user", "content": content}],
        "thinking": {"type": "enabled"},
        "reasoning_effort": "high"
    }
    
    try:
        response = requests.post(URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ 调用 AI 失败: {e}"

# 💡 新增：真实的系统环境探针（只读、安全）
def get_environment_context():
    context = "【当前系统环境上下文】\n"
    try:
        # 1. 获取当前工作目录和文件列表
        pwd = os.getcwd()
        files = subprocess.run("ls -F", shell=True, capture_output=True, text=True).stdout.strip()
        context += f"- 当前工作目录: {pwd}\n"
        context += f"- 目录下可见文件/文件夹:\n{files[:500]}\n" # 限制500字符防超长

        # 2. 获取 Docker 运行状态（如果装了Docker）
        docker_ps = subprocess.run("docker ps --format '{{.Names}} ({{.Image}})' 2>/dev/null", shell=True, capture_output=True, text=True).stdout.strip()
        if docker_ps:
            context += f"- 当前运行中的 Docker 容器:\n{docker_ps[:500]}\n"
        
        # 3. 获取系统内存简要信息
        free_mem = subprocess.run("free -h | grep Mem", shell=True, capture_output=True, text=True).stdout.strip()
        if free_mem:
            context += f"- 内存使用情况: {free_mem}\n"

    except Exception as e:
        context += f"- (获取环境信息时出现异常: {e})\n"
    
    return context

# 🚨 新增：安全执行命令的函数（带黑名单拦截）
def run_command_safe(command):
    # 1. 危险命令黑名单拦截
    dangerous_patterns = [r"rm\s+-rf", r"mkfs", r"dd\s+if=", r"shutdown", r"reboot", r">\s*/dev/sd"]
    for pattern in dangerous_patterns:
        if re.search(pattern, command):
            return False, "🚨 严重警告：检测到高危/破坏性命令，已被系统安全策略拦截！请手动核实后在终端执行。"

    # 2. 真正的执行过程
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout if result.stdout else result.stderr
        if not output:
            output = "命令执行完成，无输出返回。"
        return True, output
    except Exception as e:
        return False, f"执行出错: {e}"

# --- 侧边栏 ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/robot-3.png", width=80)
    st.title("Ops-Copilot")
    st.markdown("AI 驱动的 FDE 现场助手")
    st.divider()
    
    mode = st.radio("选择工作模式", ["🛠️ 智能排障 (Troubleshoot)", "💻 命令生成 (NL2Shell)"])
    st.divider()
    
    st.markdown("### 🔒 安全授权中心")
    allow_context = st.toggle("允许 AI 读取当前系统环境")
    st.caption("开启后，AI 将结合当前服务器环境提供更精准的建议。")
    st.divider()
    st.caption("Powered by GLM-5.3")
# 辅助函数：渲染 AI 结果 + 提取命令 + 执行按钮
def render_result_and_actions(result_text, unique_id):
    st.markdown(result_text)
    
    # 提取 ```bash 和 ``` 之间的内容
    commands = re.findall(r'```bash\n(.*?)\n```', result_text, re.DOTALL)
    if commands:
        st.divider()
        st.markdown("### ⚙️ 系统拦截与执行中心")
        for i, cmd in enumerate(commands):
            cmd = cmd.strip()
            if not cmd: continue
            
            st.code(cmd, language="bash")
            
            # 定义当前命令的各个状态 Key
            btn_key = f"apply_{unique_id}_{i}"
            confirm_key = f"confirm_{unique_id}_{i}"
            result_key = f"result_{unique_id}_{i}"
            
            # 1. 点击“申请执行”
            if st.button(f"▶ 申请执行该命令", key=btn_key):
                st.session_state[confirm_key] = True
                # 如果之前有结果，清空旧结果
                if result_key in st.session_state:
                    del st.session_state[result_key]
            
            # 2. 如果处于“申请”状态，显示确认框和“确认执行”按钮
            if st.session_state.get(confirm_key, False):
                st.warning(f"⚠️ **安全确认**：你确定要在当前环境执行以下命令吗？\n\n`{cmd}`")
                
                if st.button("✅ 确认执行", key=f"exec_{unique_id}_{i}", type="primary"):
                    # 执行命令
                    success, output = run_command_safe(cmd)
                    # 把结果存入 session_state，防止页面刷新丢失
                    st.session_state[result_key] = (success, output)
                    # 关闭确认框
                    st.session_state[confirm_key] = False
                    st.rerun() # 强制刷新页面，让界面立刻更新
            
            # 3. 如果该命令有执行结果，渲染出来
            if result_key in st.session_state:
                success, output = st.session_state[result_key]
                if success:
                    st.success("✅ 执行成功！终端输出如下：")
                    st.code(output, language="text")
                else:
                    st.error(output)

# --- 主界面渲染 ---
if mode == "🛠️ 智能排障 (Troubleshoot)":
    st.header("🛠️ 终端智能排障")
    
    if allow_context:
        st.success("✅ 已授权读取环境上下文，AI 将提供更精准的排障方案。")
    else:
        st.info("ℹ️ 当前为纯对话模式，请尽量提供详细的报错信息。")
        
    error_input = st.text_area("请粘贴报错信息", height=150, placeholder="例如：docker: permission denied...")
    
    # 💡 新增：图片上传功能
    uploaded_file = st.file_uploader("或者上传报错截图 (PNG/JPG)", type=["png", "jpg", "jpeg"])
    base64_img = None
    if uploaded_file is not None:
        st.image(uploaded_file, caption="已上传的报错截图", width=400)
        # 将图片转为 Base64 编码
        base64_img = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    
    if st.button("开始分析", type="primary"):
        # 只要有文本或者有图片，就允许分析
        if error_input or uploaded_file:
            with st.spinner("GLM-5.3 深度思考中..."):
                system_context = ""
                if allow_context:
                      system_context = get_environment_context()                
                prompt = f"""
                你是一个资深的 Linux 和 Docker 现场交付工程师（FDE）。
                {system_context}
                我遇到了以下报错（见文本或图片）：
                "{error_input}"
                请帮我分析原因，并给出修复命令（用 Markdown 代码块输出）。要求精简、直击要害。
                """
                # 把 base64_img 传给函数
                result = call_ai(prompt, base64_image=base64_img)
                st.session_state["troubleshoot_result"] = result
        else:
            st.warning("请至少输入文字或上传一张图片！")
                
    if "troubleshoot_result" in st.session_state:
        st.success("分析完成！")
        render_result_and_actions(st.session_state["troubleshoot_result"], "troubleshoot")

elif mode == "💻 命令生成 (NL2Shell)":
    st.header("💻 自然语言转命令")
    
    if allow_context:
        st.success("✅ 已授权读取环境上下文。")
    else:
        st.info("ℹ️ 当前为纯对话模式。")
        
    intent_input = st.text_input("你想执行什么操作？", placeholder="例如：查看当前占用内存最高的前五个进程")
    
    if st.button("生成命令", type="primary"):
        if intent_input:
            with st.spinner("GLM-5.3 深度思考中..."):
                system_context = ""
                if allow_context:
                      system_context = get_environment_context()                
                prompt = f"""
                你是一个 Linux 运维专家。
                {system_context}
                用户想实现以下操作：
                "{intent_input}"
                请直接给出最标准的 Linux 命令，并严格遵循以下格式：
                1. 核心命令（用 Markdown 代码块包裹）
                2. 参数解释
                3. 危险提示（如果有删库风险，用 ⚠️ 标出）
                """
                # 💡 核心修改：把结果存入 session_state
                st.session_state["nl2shell_result"] = call_ai(prompt)
                
    # 💡 核心修改：只要记忆库里有结果，就一直渲染
    if "nl2shell_result" in st.session_state:
        st.success("生成完成！")
        render_result_and_actions(st.session_state["nl2shell_result"], "nl2shell")
    # 💡 新增：常用命令速查表（放在页面最下方）
    # ==========================================
    st.divider()
    with st.expander("📖 点击展开：FDE 常用 Linux/Docker 运维命令速查表"):
        st.markdown("""
        **📁 文件与目录**
        * `ls -lh`：查看目录下的文件大小与权限
        * `du -sh *`：查看当前目录各文件/文件夹大小
        * `find . -name "*.log"`：查找当前目录所有 .log 文件

        **📊 系统资源**
        * `top` / `htop`：实时查看 CPU/内存占用
        * `free -h`：查看内存使用情况
        * `df -h`：查看磁盘空间占用
        * `ps aux | grep <关键字>`：查找特定进程

        **🌐 网络排查**
        * `ss -tulnp`：查看端口监听及对应进程（取代老旧的 netstat）
        * `ping <IP>`：测试网络连通性
        * `curl -I <URL>`：查看 HTTP 响应头
        * `tcpdump -i any port 80`：抓包排障

        **🐳 Docker 核心**
        * `docker ps -a`：查看所有容器（包括已停止的）
        * `docker logs -f <ID>`：实时滚动查看容器日志
        * `docker exec -it <ID> bash`：进入容器内部
        * `docker stats`：查看容器 CPU/内存资源占用
        """)
