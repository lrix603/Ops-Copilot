import os
import sys
import argparse
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

# 自动加载当前目录下的.env文件
load_dotenv()

# 1. 安全读取环境变量中的 API Key
API_KEY = os.environ.get("ZHIPU_API_KEY")
if not API_KEY:
    print("\033[91m[-] 错误：未找到 ZHIPU_API_KEY 环境变量。\033[0m")
    print("请确保当前目录下存在.env文件并配置了API_KEY")
    sys.exit(1)

URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def call_ai(prompt):
    """通用的 AI 请求封装 (适配 GLM-5.3 强制思考模式)"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "glm-5.3",                 # 接入最新模型
        "messages": [{"role": "user", "content": prompt}],
        "thinking": {"type": "enabled"},    # GLM-5.3 必须启用思考
        "reasoning_effort": "high",         # 开启高深度推理
        "temperature": 1.0
    }
    
    try:
        response = requests.post(URL, headers=headers, json=data)
        response.raise_for_status()  # 捕获 HTTP 异常
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"\033[91m[-] 调用 AI 失败: {e}\033[0m"

def troubleshoot(error_msg):
    """FDE 智能排障模式 (-e)"""
    prompt = f"""
    你是一个资深的 Linux 和 Docker 现场交付工程师（FDE）。
    我在客户现场遇到了以下报错信息：
    "{error_msg}"
    
    请帮我分析原因，并给出在 Linux 终端中可以直接执行的修复命令（用 Markdown 代码块输出）。
    要求：回复必须精简、直击要害，不要废话。
    """
    print("\n\033[96m[*] 启动 FDE 排障模式 (GLM-5.3 深度思考中)...\033[0m\n")
    # 用rich渲染Markdown
    response_text = call_ai(prompt)
    console = Console()
    md = Markdown(response_text)
    console.print(md)

def query_command(intent):
    """自然语言转命令模式 (-c)"""
    prompt = f"""
    你是一个 Linux 运维专家。用户想实现以下操作：
    "{intent}"
    
    请直接给出最标准的 Linux/Bash 命令，并严格遵循以下格式：
    1. 核心命令（用 Markdown 代码块包裹）
    2. 参数解释（每一个参数代表什么意思）
    3. 危险提示（如果该命令有删库、格式化或破坏风险，请用 ⚠️ 标出）
    """
    print("\n\033[96m[*] 启动命令生成模式 (GLM-5.3 深度思考中)...\033[0m\n")
    response_text = call_ai(prompt)
    console = Console()
    md = Markdown(response_text)
    console.print(md)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ops-Copilot: AI 驱动的 FDE 终端排障与命令助手")
    parser.add_argument("-e", "--error", type=str, help="输入报错信息进行排障")
    parser.add_argument("-c", "--cmd", type=str, help="用自然语言描述你想执行的命令")
    
    args = parser.parse_args()
    
    if args.error:
        troubleshoot(args.error)
    elif args.cmd:
        query_command(args.cmd)
    else:
        print("\033[93m用法:\033[0m")
        print("  排障模式: \033[92mpython3 ai_ops.py -e \"你的报错信息\"\033[0m")
        print("  命令查询: \033[92mpython3 ai_ops.py -c \"你想做什么操作\"\033[0m")
