# AI Resume Master - 智能简历分析与人岗匹配系统

> 基于 **阿里云 Serverless (FC)** + **FastAPI** + **LLM (通义千问)** + **Redis** 构建的现代化招聘辅助工具。

[![Deployment Status](https://img.shields.io/badge/Deployment-Live-success)](https://[你的GitHub用户名].github.io/ai-resume-analyzer/frontend/index.html)
[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Cloud](https://img.shields.io/badge/Cloud-Aliyun%20Serverless-orange)](https://www.aliyun.com/product/fc)

## 在线演示 (Live Demo)
 **[点击此处体验完整功能](https://leess1214.github.io/AI-powered-intelligent-resume-analysis-system/frontend/index.html)**

*(注：后端部署于阿里云函数计算，前端托管于 GitHub Pages。支持上传 PDF 格式简历进行测试。)*

---
## 项目介绍 (Introduction)

在招聘流程中，HR 往往面临海量简历筛选的痛点。本项目旨在利用 **Generative AI (生成式 AI)** 的自然语言处理能力，实现对非结构化简历文档（PDF）的自动化解析与结构化提取。

此外，系统支持输入**职位描述 (JD)**，利用 LLM 对候选人进行多维度的**人岗匹配打分**，并引入 **Redis 缓存机制** 优化重复查询的性能与成本。
## 核心特性 (Key Features)

- **智能 PDF 解析**：使用 `pdfplumber` 高保真提取 PDF 文本，通过清洗算法去除冗余字符。
- **AI 结构化提取**：基于 Prompt Engineering，从非结构化文本中精准提取姓名、技能栈、学历、工作年限等关键信息。
- **人岗匹配评分**：根据用户输入的 JD，AI 自动分析候选人优势与劣势，并给出 0-100 的匹配度评分。
- **高性能缓存 (Redis)**：
  - 实现文件内容指纹 (MD5) 计算。
  - 集成 **Upstash Redis**，对已分析过的简历+JD组合进行缓存。
  - **效果**：重复查询响应时间从 **5s+ 降低至 <200ms**，大幅节省 AI Token 成本。
- **Serverless 部署**：
  - 利用阿里云 FC 3.0 实现毫秒级弹性伸缩。
  - 解决 `manylinux` 环境下的 Python 依赖打包兼容性问题。
  - 配置 CORS 策略解决跨域安全限制。

## 技术栈(Tech Stack)
| **模块**     | **技术选型**         | **说明**                          |
| ------------ | -------------------- | --------------------------------- |
| **Backend**  | Python 3.10, FastAPI | 高性能异步 Web 框架               |
| **Compute**  | Alibaba Cloud FC     | Serverless 无服务器计算           |
| **AI Model** | Qwen-Plus (通义千问) | 通过 DashScope API 调用           |
| **Cache**    | Upstash (Redis)      | Serverless Redis，用于结果缓存    |
| **Storage**  | Ephemeral Storage    | 临时文件流处理 (内存处理，不落盘) |
| **Frontend** | HTML5, Tailwind CSS  | 轻量级单页应用 (SPA)              |
| **DevOps**   | Git, GitHub Pages    | 代码版本控制与静态托管            |
## 系统架构 (Architecture)

本项目采用云原生 Serverless 架构，实现了**计算与存储分离**、**前后端分离**。

```text
+-----------------+       +-------------------+       +-------------------------+
|  User (Browser) | ----> |    GitHub Pages   | ----> |   Aliyun API Gateway    |
+-----------------+       | (Frontend Hosting)|       |      (Entry Point)      |
                          +-------------------+       +------------+------------+
                                                                   |
                                                                   v
                                                      +-------------------------+
                                                      |  Aliyun Function Compute|
                                                      |      (Python 3.10)      |
                                                      +------------+------------+
                                                                   |
            +------------------------------------------------------+---------------------+
            |                                                      |                     |
            v                                                      v                     |
+-----------------------+                            +-------------------------+         |
|   Redis Cache         | <----(1. Check Hash)-----  |      Logic Controller   |         |
|   (Upstash)           | -----(2. Cache Hit?)---->  |      (FastAPI)          |         |
+-----------------------+                            +-----------+-------------+         |
                                                                 |                       |
                                                                 | (3. Cache Miss)       |
                                                                 v                       |
                                                     +-------------------------+         |
                                                     |    PDF Parser & Clean   |         |
                                                     +-----------+-------------+         |
                                                                 |                       |
                                                                 v                       |
                                                     +-------------------------+         |
                                                     |        LLM Service      |         |
                                                     |    (Qwen-Plus API)      | <-------+
                                                     +-------------------------+
```




## 本地开发与运行(Local Development)
如果你希望在本地运行本项目进行调试或二次开发，请参考以下步骤：
### 1.环境准备
- Python 3.10
### 2.克隆仓库
```bash
git clone [https://github.com/](https://github.com/)[你的GitHub用户名]/ai-resume-analyzer.git
cd ai-resume-analyzer
```
### 3.安装依赖
```bash
# 安装依赖
pip install -r requirements.txt
```
### 4.配置环境变量
```bash
# 必填：阿里云百炼 (DashScope) API Key
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# 必填：Redis 连接字符串 (格式: rediss://default:密码@地址:端口)
# 注意：Upstash 必须使用 rediss:// 协议
REDIS_URL=rediss://default:xxxxxxxxxxxx@xxxxx.upstash.io:6379

# 可选：模型名称 (默认 qwen-plus)
AI_MODEL_NAME=qwen-plus
```
### 5.启动后端服务
```bash
python main.py
```
### 6.启动前端
1.找到 frontend/index.html 文件。

2.将 API_URL 修改为本地地址：
```JavaScript
const API_URL = "[http://127.0.0.1:8000/api/analyze](http://127.0.0.1:8000/api/analyze)";
```
3.双击打开 index.html 即可开始测试。
