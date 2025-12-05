import pdfplumber
import io
import re


def parse_pdf_to_text(file_bytes: bytes) -> str:
    """
    接收文件的二进制流，返回清洗后的纯文本。
    """
    text_content = []

    try:
        # 使用 io.BytesIO 将二进制流转换为类似文件的对象
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
    except Exception as e:
        print(f"PDF解析错误: {e}")
        return ""

    # 合并文本
    full_text = "\n".join(text_content)

    # 数据清洗：去除多余的连续空白字符，保留基本段落结构
    # 这里的正则意味着：把连续的空格变成一个空格，但保留换行
    # 注意：根据实际 PDF 情况，有时需要把换行符也去掉，这里保留是为了分段清晰
    clean_text = re.sub(r'[ \t]+', ' ', full_text).strip()

    return clean_text