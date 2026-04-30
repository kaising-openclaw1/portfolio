#!/usr/bin/env python3
"""
网页数据抓取示例
功能：抓取网页内容，提取结构化数据
"""

import requests
from bs4 import BeautifulSoup
import json

def scrape_website(url, selectors):
    """抓取网页并提取数据"""
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = {}
    for key, selector in selectors.items():
        element = soup.select_one(selector)
        data[key] = element.text.strip() if element else None
    
    return data

if __name__ == "__main__":
    # 示例用法
    selectors = {
        "title": "h1",
        "content": ".article-content"
    }
    # result = scrape_website("https://example.com", selectors)
    print("数据抓取模块就绪")
