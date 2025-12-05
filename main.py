from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from utils import parse_pdf_to_text
from ai_service import analyze_resume

app = FastAPI(title="AI 智能简历分析系统")

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
    """
    核心接口：
    1. 接收 PDF 文件
    2. (可选) 接收职位描述文本
    3. 返回解析结果和评分
    """
    # 1. 验证文件类型
    if not file.filename.endswith(".pdf"):
        return {"error": "仅支持 PDF 文件"}

    # 2. 读取并解析 PDF
    file_bytes = await file.read()
    text_content = parse_pdf_to_text(file_bytes)

    if not text_content:
        return {"error": "无法从 PDF 中提取文本，可能是扫描件"}

    # 3. 调用 AI 进行分析
    # 注意：这里是同步调用，如果并发高建议放入 Celery 任务队列
    # 但对于面试演示，直接调用即可
    result = analyze_resume(text_content, job_description)

    return {
        "filename": file.filename,
        "success": True,
        "data": result
    }


if __name__ == "__main__":
    import uvicorn

    # 启动命令：python main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)