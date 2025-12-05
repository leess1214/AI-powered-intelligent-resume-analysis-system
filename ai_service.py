import json
from config import settings
# 如果使用阿里云通义千问，由于它兼容 OpenAI SDK，我们可以直接用 openai 库
# 只需修改 base_url 即可 (阿里云通常是 https://dashscope.aliyuncs.com/compatible-mode/v1)
from openai import OpenAI

client = None
if not settings.MOCK_MODE:
    client = OpenAI(
        api_key=settings.API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        # 阿里云 Endpoint 示例
    )


def analyze_resume(resume_text: str, job_description: str = None):
    """
    调用 AI 对简历进行分析。
    """
    if settings.MOCK_MODE:
        return _mock_response(job_description is not None)

    # 1. 构建 Prompt
    # 基础任务：提取信息
    system_instruction = """
    你是一个资深的招聘专家和简历解析助手。
    你的任务是提取简历关键信息，并输出为严格的 JSON 格式。
    不要输出任何 Markdown 标记（如 ```json），只输出纯 JSON 字符串。
    """

    user_prompt = f"""
    简历内容如下：
    {resume_text[:4000]} 

    请提取以下字段：
    - basic_info: {{ name, phone, email, university, degree }}
    - skills: [列出技能关键词]
    - summary: 一句话总结该候选人的特点
    """

    # 进阶任务：如果有职位描述，增加评分逻辑
    if job_description:
        user_prompt += f"""

        同时，请根据以下职位描述对简历进行打分：
        职位描述：{job_description[:2000]}

        请在 JSON 中额外增加以下字段：
        - match_score: (0-100的整数)
        - match_analysis: (简短的匹配度分析，说明加分项和减分项)
        """

    try:
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # 低温度保证输出稳定
            response_format={"type": "json_object"}  # 强制 JSON (部分模型支持)
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"AI 调用失败: {e}")
        return {"error": "AI分析服务暂时不可用"}


def _mock_response(include_score=False):
    """
    模拟数据，用于开发测试
    """
    data = {
        "basic_info": {
            "name": "张三",
            "phone": "13800138000",
            "email": "zhangsan@example.com",
            "university": "某知名大学",
            "degree": "硕士"
        },
        "skills": ["Python", "FastAPI", "Machine Learning", "Redis"],
        "summary": "具备扎实数学基础和后端开发能力的应届硕士生。"
    }
    if include_score:
        data["match_score"] = 85
        data[
            "match_analysis"] = "候选人技能栈与职位高度匹配，特别是在Python后端方面。但在实际高并发项目经验上稍显不足。"
    return data