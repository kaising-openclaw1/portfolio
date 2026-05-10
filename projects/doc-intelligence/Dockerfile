# Dockerfile - Doc Intelligence

FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY doc_intelligence/ ./doc_intelligence/

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "doc_intelligence.server:app", "--host", "0.0.0.0", "--port", "8000"]
