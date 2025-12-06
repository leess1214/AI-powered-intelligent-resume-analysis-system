# ai_service.py
import json
from openai import OpenAI
from config import settings


def analyze_resume(resume_text: str, job_description: str = None):
    """
    调用阿里云通义千问进行简历分析
    """
    # 1. 如果还在 Mock 模式或者没有 Key，返回假数据（防止报错）
    if settings.MOCK_MODE or not settings.API_KEY:
        print("警告：正在使用 Mock 数据，请检查 API_KEY 是否配置")
        return _mock_response(job_description is not None)

    # 2. 初始化客户端 (使用 OpenAI SDK 连接阿里云)
    client = OpenAI(
        api_key=settings.API_KEY,
        base_url=settings.BASE_URL
    )

    # 3. 构造 System Prompt (人设)
    system_prompt = """
    你是一个拥有20年经验的资深技术招聘专家。
    你的任务是精准提取简历信息，并根据职位描述(JD)进行客观评分。

    【重要指令】
    1. 必须返回严格的 JSON 格式数据。
    2. 不要包含 markdown 标记（如 ```json），只返回纯文本 JSON。
    3. 如果简历中找不到某项信息，该字段填 "未提及"。
    """

    # 4. 构造 User Prompt (任务)
    # 为了节省 Token 和防止上下文超长，截取简历前 3000 字
    user_prompt = f"""
    请分析以下简历内容：

    【简历文本开始】
    {resume_text[:3000]}
    【简历文本结束】

    请输出以下 JSON 结构的数据：
    {{
        "basic_info": {{
            "name": "姓名",
            "phone": "电话",
            "email": "邮箱",
            "education": "最高学历/毕业院校",
            "years_of_experience": "工作年限(数字或估算)"
        }},
        "skills": ["技能1", "技能2", "技能3"],
        "summary": "50字以内的候选人能力总结"
    }}
    """

    # 5. 如果有 JD，增加评分逻辑
    if job_description:
        user_prompt += f"""

        【职位描述 (JD)】
        {job_description[:1500]}

        请在刚才的 JSON 中额外增加以下字段：
        "match_score": (0-100之间的整数评分),
        "match_analysis": "简短评价人岗匹配度，指出优势和不足(100字以内)"
        """

    try:
        # 6. 发起调用
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            temperature=0.1  # 温度设低一点，让输出更稳定
        )

        # 7. 解析结果
        content = response.choices[0].message.content
        # 清洗一下可能存在的 markdown 符号
        content = content.replace("```json", "").replace("```", "").strip()

        return json.loads(content)

    except Exception as e:
        print(f"AI 调用失败: {e}")
        # 如果真挂了，返回一个带错误信息的 JSON，而不是让程序崩溃
        return {
            "basic_info": {"name": "AI解析失败"},
            "summary": f"服务暂时不可用: {str(e)}",
            "skills": []
        }


def _mock_response(include_score=False):
    # 保留 mock 函数作为备用
    data = {
        "basic_info": {"name": "测试用户(Mock)", "email": "test@mock.com"},
        "skills": ["Mock Skill 1", "Mock Skill 2"],
        "summary": "这是本地测试数据，说明 API Key 未生效。"
    }
    if include_score:
        data["match_score"] = 88
        data["match_analysis"] = "测试模式匹配分析。"
    return data
