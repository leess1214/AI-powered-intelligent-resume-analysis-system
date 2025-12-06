from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from utils import parse_pdf_to_text
from ai_service import analyze_resume

import hashlib
import json
import redis
from config import settings

app = FastAPI(title="AI 智能简历分析系统")

# 初始化 Redis 客户端
# decode_responses=True 让取出来的数据直接是字符串，不是 bytes
redis_client = None
if settings.REDIS_URL:
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        print("Redis 连接成功")
    except Exception as e:
        print(f"Redis 连接失败: {e}")

# 配置跨域资源共享 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源访问（生产环境应限制为你的前端域名）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Service is running"}


@app.post("/api/analyze")
async def analyze_endpoint(
        file: UploadFile = File(...),
        job_description: str = Form(None)
):
    if not file.filename.endswith(".pdf"):
        return {"error": "仅支持 PDF 文件"}

    # 1. 读取文件二进制数据
    file_bytes = await file.read()

    # ================= 缓存逻辑开始 =================
    # 2. 计算文件指纹 (MD5)
    # 如果有 JD，JD 变了评分也会变，所以指纹要包含 JD 的内容
    md5_hash = hashlib.md5(file_bytes).hexdigest()
    if job_description:
        # 把 JD 也加进哈希计算，确保不同的 JD 产生不同的缓存
        md5_hash = hashlib.md5(
            (md5_hash + job_description).encode()).hexdigest()

    cache_key = f"resume_analysis:{md5_hash}"

    # 3. 查缓存
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                print(f"🌟 命中缓存: {cache_key}")
                # 直接返回缓存的数据 (注意：Redis存的是字符串，要转回 Dict)
                return {
                    "filename": file.filename,
                    "success": True,
                    "data": json.loads(cached_data),
                    "source": "cache"  # 标记一下来源，方便前端展示
                }
        except Exception as e:
            print(f"读缓存出错: {e}")
    # ================= 缓存逻辑结束 =================

    # 4. 如果没命中，走原来的老路
    text_content = parse_pdf_to_text(file_bytes)
    if not text_content:
        return {"error": "无法从 PDF 中提取文本"}

    result = analyze_resume(text_content, job_description)

    # ================= 写入缓存 =================
    if redis_client and result:
        try:
            # ex=3600 表示缓存 1 小时后过期
            redis_client.set(cache_key, json.dumps(result), ex=3600)
            print(f"💾 已写入缓存: {cache_key}")
        except Exception as e:
            print(f"写缓存出错: {e}")
    # ===========================================

    return {
        "filename": file.filename,
        "success": True,
        "data": result,
        "source": "ai_generation"
    }





# @app.post("/api/analyze")
# async def analyze_endpoint(
#         file: UploadFile = File(...),
#         job_description: str = Form(None)
# ):
#     """
#     核心接口：
#     1. 接收 PDF 文件
#     2. (可选) 接收职位描述文本
#     3. 返回解析结果和评分
#     """
#     # 1. 验证文件类型
#     if not file.filename.endswith(".pdf"):
#         return {"error": "仅支持 PDF 文件"}
#
#     # 2. 读取并解析 PDF
#     file_bytes = await file.read()
#     text_content = parse_pdf_to_text(file_bytes)
#
#     if not text_content:
#         return {"error": "无法从 PDF 中提取文本，可能是扫描件"}
#
#     # 3. 调用 AI 进行分析
#     # 注意：这里是同步调用，如果并发高建议放入 Celery 任务队列
#     # 但对于面试演示，直接调用即可
#     result = analyze_resume(text_content, job_description)
#
#     return {
#         "filename": file.filename,
#         "success": True,
#         "data": result
#     }





if __name__ == "__main__":
    import uvicorn

    # 启动命令：python main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
