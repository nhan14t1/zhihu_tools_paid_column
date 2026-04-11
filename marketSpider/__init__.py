import base64
import json
import logging
import os
import re
import sys

import requests
from lxml import etree

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import fontPreview


class MarketSpider:
    def __init__(self, header, output_dir=None, filename_prefix=None) -> None:
        self.header = header
        self.marketTitle = None
        self.marketFileStem = None
        self.glyfDict = {}
        self.url = None
        self.output_dir = output_dir
        self.filename_prefix = filename_prefix

    def sanitize_filename(self, name):
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", name).strip()
        return sanitized.rstrip(". ") or "untitled"

    def build_output_stem(self, title):
        safe_title = self.sanitize_filename(title)
        if self.filename_prefix:
            safe_title = f"{self.filename_prefix}-{safe_title}"
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            return os.path.join(self.output_dir, safe_title)
        return safe_title

    def cleanup_generated_files(self):
        if os.path.exists("font_preview.png"):
            os.remove("font_preview.png")
        if os.path.isdir("images"):
            for file_name in os.listdir("images"):
                file_path = os.path.join("images", file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            if not os.listdir("images"):
                os.rmdir("images")

    def getMarketHtml(self, url):
        self.url = url
        response = requests.get(url, verify=False, headers=self.header)
        try:
            with open("market.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            logging.info("文章请求成功！")
        except Exception as e:
            logging.error("文章请求失败：%s", str(e))

    def re_fetch_article(self):
        logging.info("重新请求文章...")
        self.getMarketHtml(self.url)
        self.getFontFile()
        self.getContent()

    def getFontFile(self, htmlFile="market.html"):
        with open(htmlFile, "r", encoding="utf-8") as f:
            html = f.read()
        fontFile = self.get_third_font_face(html)
        if fontFile == "":
            logging.error("未匹配到字体文件！")
            return
        parts = fontFile.split(",")
        if len(parts) != 2:
            logging.error("无效的字体数据URL！")
            return
        data = parts[1]
        try:
            data_bytes = base64.b64decode(data)
            with open("font.woff", "wb") as file:
                file.write(data_bytes)
            logging.info("字体文件下载成功！")
        except Exception as e:
            logging.error("字体文件下载失败: %s", str(e))

    def get_third_font_face(self, font_re):
        font_face_blocks = re.findall(r"@font-face\s*{[^}]*}", font_re)
        if len(font_face_blocks) >= 3:
            font_url = re.search(r"src:\s*url\(([^)]+)\)", font_face_blocks[2]).group(1)
            return font_url
        return ""

    def getContent(self, htmlFile="market.html") -> bool:
        with open(htmlFile, "r", encoding="utf-8") as f:
            html = f.read()

        if not html:
            logging.error("在获取文件的时候出错了！")
            return False

        content = etree.HTML(html)
        content = content.xpath('string(//*[@id="resolved"])')
        content = json.loads(content)
        manuscript_data = content["appContext"]["__connectedAutoFetch"]["manuscript"]["data"][
            "manuscriptData"
        ]
        contents = manuscript_data.get("pTagList", [])

        if not contents:
            manuscript_html = manuscript_data.get("manuscript", "")
            if manuscript_html:
                manuscript_root = etree.HTML(f"<body>{manuscript_html}</body>")
                paragraphs = manuscript_root.xpath("//p")
                contents = [
                    "".join(paragraph.xpath(".//text()")).replace("\xa0", " ").strip()
                    for paragraph in paragraphs
                ]
                contents = [item for item in contents if item]
                logging.info("pTagList 为空，已回退到 manuscript HTML 提取正文。")

        if not contents:
            logging.error("正文内容为空，未找到可用的 pTagList 或 manuscript。")
            return False

        self.marketTitle = manuscript_data["title"]
        self.marketFileStem = self.build_output_stem(self.marketTitle)
        with open(self.marketFileStem + ".temp", "w", encoding="utf-8") as f:
            for item in contents:
                f.write(item + "\n")
        logging.info("内容获取成功！")
        return True

    def replace_text(self, text, replacement_dict):
        result = []
        for char in text:
            if char in replacement_dict:
                result.append(replacement_dict[char])
            else:
                result.append(char)
        return "".join(result)

    def parse(self):
        font_preview = fontPreview.FontPreview()
        font_preview.set_market_spider(self)
        self.glyfDict = font_preview.preview("font.woff", "images", remove_files=False)
        logging.info(f"字体映射表: {self.glyfDict}")
        with open(self.marketFileStem + ".temp", "r", encoding="utf-8") as f:
            content = f.read()
        content = self.replace_text(content, self.glyfDict)
        with open(self.marketFileStem + ".txt", "w", encoding="utf-8") as f:
            f.write(content)
        logging.info("文章解析成功！")

    def spider(self, url):
        self.cleanup_generated_files()
        self.getMarketHtml(url)
        self.getFontFile()
        if self.getContent():
            self.parse()
