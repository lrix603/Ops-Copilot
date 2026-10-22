# Ops-Copilot (AI 驱动的 FDE 终端排障与命令助手)

## 项目背景
在 FDE（现场交付工程师）日常工作中，面对海量且生僻的 Linux/Docker 底层报错，以及繁杂的命令参数，极易卡壳。本项目接入智谱 **GLM-5.3** 旗舰大模型，打造终端侧 AI 辅助工具，大幅降低排障门槛，提升交付效率。

## 核心功能
- **智能排障 (`-e`)**：输入终端报错，AI 自动剖析根因并输出修复命令。
- **自然语言转命令 (`-c`)**：输入需求，AI 自动生成标准 Linux 命令并解释参数。
- **安全护栏**：针对生成的高危命令（如 `rm -rf`），AI 会自动输出 ⚠️ 警告。

##技术栈与工程实践
- **Python 3**：使用 `argparse` 构建专业 CLI 界面。
- **模型选型**：接入智谱 **GLM-5.3**，利用其增强的网络安全与终端操作推理能力，精准定位故障。
- **参数调优**：针对 GLM-5.3 强制思考模式，设置 `thinking={"type": "enabled"}` 与 `reasoning_effort="high"`，确保输出逻辑严谨。
- **安全合规**：API Key 采用 `os.environ` 从环境变量读取，杜绝硬编码导致的密钥泄漏风险。

## 如何使用

1. 在同级目录下创建一个名为`.evn`的文件。
2. 配置你的智谱 API Key在env文件中：
   ```bash
   ZHIPU_API_KEY=你的真实API_KEY
   ```
3. 运行排障模式：
   ```bash
   python3 ai_ops.py -e "docker: permission denied while trying to connect..."
   ```
   <img width="1109" height="1296" alt="figure1" src="https://github.com/user-attachments/assets/09db69fb-3953-421f-b926-7c8270845bf0" />

4. 运行命令翻译模式:
   ```bash
   python3 ai_ops.py -c "查看当前系统内内存占用排名前五的进程"
   ```
   <img width="1723" height="1465" alt="figure2" src="https://github.com/user-attachments/assets/6b284d52-9ab4-4c93-8626-4a595be988d0" />

