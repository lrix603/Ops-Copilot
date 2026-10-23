# Ops-Copilot (AI 驱动的 FDE 终端排障与命令助手)

## 项目背景
在 FDE（现场交付工程师）日常工作中，面对海量且生僻的 Linux/Docker 底层报错，以及繁杂的命令参数，极易卡壳。本项目接入智谱 **GLM-5.3** 旗舰大模型，打造终端侧 AI 辅助工具，大幅降低排障门槛，提升交付效率。

## 核心功能
- **Web 端可视化**：基于 Streamlit 构建，脱离终端限制，提供现代化交互界面。
- **多模态排障**：支持上传报错截图（Base64 编码），调用 GLM 视觉模型直接识别图中报错。
- **零信任环境探针**：默认纯对话模式；需显式授权后，工具才会以只读方式探测当前环境（目录、Docker、内存）供 AI 参考，杜绝敏感数据泄露。
- **Human-in-the-loop 拦截**：内置危险命令黑名单（如 `rm -rf`），AI 生成的命令必须经过人类二次确认才可执行，防止 AI 幻觉引发删库灾难。
- **离线降级方案**：内置 FDE 常用命令速查表，无网络或 AI 宕机时亦可作为本地运维手册。

##技术栈与工程实践
- **Python 3**：使用 `argparse` 构建专业 CLI 界面。
- **模型选型**：接入智谱 **GLM-5.3**，利用其增强的网络安全与终端操作推理能力，精准定位故障。
- **参数调优**：针对 GLM-5.3 强制思考模式，设置 `thinking={"type": "enabled"}` 与 `reasoning_effort="high"`，确保输出逻辑严谨。
- **安全合规**：API Key 采用 `os.environ` 从环境变量读取，杜绝硬编码导致的密钥泄漏风险。

## 如何使用

1. 配置密钥：在项目根目录创建 `.env` 文件，填入 `ZHIPU_API_KEY=你的真实API_KEY`。
2. 安装依赖：`pip install -r requirements.txt`
3. 启动服务：`streamlit run app.py`
4. 打开浏览器访问 `http://localhost:8501`。

## 效果展示

1. Web界面（智能排障和命令提示）
   <img width="2560" height="1122" alt="system1" src="https://github.com/user-attachments/assets/26a7cb09-3175-4856-9e97-08cfd492e7f8" />

   <img width="2231" height="1060" alt="system2" src="https://github.com/user-attachments/assets/22584e9b-2364-43bc-9e31-92b6320bfdfb" />

2. 授权AI探测当前环境
   <img width="2197" height="1022" alt="AI授权" src="https://github.com/user-attachments/assets/ecfc2fdd-c613-436f-9864-b53f5bdd2c2b" />

3. 命令提示后，可以直接代替执行，危险命令会警告，防止AI幻觉
   <img width="1139" height="1012" alt="run" src="https://github.com/user-attachments/assets/bff8bbce-c765-4ff4-bd23-873a5f07b7fd" />

   <img width="2402" height="1063" alt="Security" src="https://github.com/user-attachments/assets/51cf5f16-ddb0-4e1d-b588-847c4b849ba4" />

4. 放置常用命令速查表
   <img width="1111" height="1110" alt="prompt" src="https://github.com/user-attachments/assets/af88ad62-da15-4109-9e38-b909451ffcb3" />
