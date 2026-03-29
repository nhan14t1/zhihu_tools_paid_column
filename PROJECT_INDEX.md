# Project Index: ZhiHu Tools

## 📋 Project Overview

**Project Name:** ZhiHu Tools
**Description:** 知乎盐选文章获取工具 (Zhihu Yanxuan Content Extraction Tool)
**Language:** Python
**License:** Open Source
**Repository:** https://github.com/onewhitethreee/zhihu_tools

### Purpose
A specialized tool designed to extract content from Zhihu Yanxuan (盐选) articles. Since 2022-2023, Zhihu platform has implemented web structure changes and anti-crawling mechanisms, restricting Yanxuan content to mobile apps only. This project provides an effective solution to overcome these technical barriers.

---

## 🏗️ Project Architecture

### Directory Structure
```
zhihu_tools/
├── .github/
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md          # Bug report template
│       └── feature_request.md     # Feature request template
├── .git/                          # Git repository data
├── venv/                          # Virtual Python environment
├── answerSpider/                  # Question/Answer extraction module
│   ├── __init__.py
│   └── __pycache__/
├── config/                        # Configuration management
│   ├── __init__.py
│   ├── __pycache__/
│   └── option.py                  # Command-line & menu options handler
├── ddddocr/                       # OCR functionality component
│   ├── __init__.py
│   ├── common.onnx                # ONNX model for OCR
│   ├── common_det.onnx            # Detection model
│   ├── common_old.onnx            # Legacy model
│   ├── logo.png
│   ├── README.md
│   └── requirements.txt
├── fakeUserAgent/                 # User-Agent management
│   ├── __init__.py
│   ├── __pycache__/
│   └── user_agents.json           # Collection of User-Agent strings
├── fontPreview/                   # Font decoding & rendering solution
│   ├── __init__.py
│   └── __pycache__/
├── main/                          # Core execution scripts
│   ├── spider.py                  # Main spider controller
│   └── __pycache__/
├── marketSpider/                  # Market content extraction module
│   ├── __init__.py
│   └── __pycache__/
├── .gitignore                     # Git ignore rules
├── config.ini                     # Configuration file (cookies, User-Agent)
├── README.md                      # Project documentation
└── requirements.txt               # Python dependencies
```

---

## 🔧 Core Components

### 1. **Main Spider** ([main/spider.py](main/spider.py))
**Class:** `zhihuSpider`

**Responsibilities:**
- Main application controller
- Menu system and user interaction
- Configuration loading
- Header management (Cookie + User-Agent)
- Routing to different extraction modes

**Key Methods:**
- `__init__()`: Initialize configuration and headers
- `getOptionChoise()`: Route user selection to appropriate handler
- `optionChoise1()`: Extract single question (⏳ In Development)
- `optionChoise2()`: Extract book chapter (✅ Completed)
- `optionChoise3()`: Extract full book (⏳ In Development)
- `optionChoise4()`: Keyword-based search (⏳ In Development)
- `commandChoise()`: Handle command-line arguments

**Usage:**
```bash
python main/spider.py
```

### 2. **Market Spider** ([marketSpider/__init__.py](marketSpider/__init__.py))
**Class:** `MarketSpider`

**Responsibilities:**
- Extract content from Zhihu Market links
- Download and decode custom fonts
- Parse HTML content using XPath
- Replace obfuscated characters

**Key Methods:**
- `getMarketHtml(url)`: Fetch article HTML
- `re_fetch_article()`: Re-request article on failure
- `getFontFile()`: Extract and decode base64 font file
- `get_third_font_face()`: Parse CSS @font-face rules
- `getContent()`: Extract article content and title
- `replace_text()`: Replace obfuscated characters
- `parse()`: Font preview and OCR processing
- `spider(url)`: Main extraction workflow

**Supported URL Format:**
```
https://www.zhihu.com/market/paid_column/1702723501155422208/section/1788920608135983104
```

### 3. **Font Preview** ([fontPreview/__init__.py](fontPreview/__init__.py))
**Class:** `FontPreview`, `FontDocument`

**Responsibilities:**
- Parse WOFF font files using fontTools
- Generate glyph preview images
- OCR character recognition using ddddocr
- Build character mapping dictionary
- Font correction and validation

**Key Methods:**
- `open_font()`: Load font file
- `parse_font()`: Extract glyph metadata
- `generate_image()`: Create full font preview
- `generate_single_character_image()`: Create individual glyph images
- `recognize_image()`: OCR character recognition with retry logic
- `fill_font_dict()`: Fill missing characters
- `correct_font_dict()`: Correct common OCR errors
- `preview()`: Complete font processing workflow

**Dependencies:**
- fontTools (font parsing)
- Pillow (image generation)
- ddddocr (OCR)

### 4. **Fake UserAgent** ([fakeUserAgent/__init__.py](fakeUserAgent/__init__.py))
**Class:** `fakeUserAgent`

**Responsibilities:**
- Manage collection of User-Agent strings
- Random User-Agent selection
- Platform-based User-Agent organization

**Key Methods:**
- `loadUserAgent()`: Load from user_agents.json
- `getRandomPlatform()`: Select random platform
- `getRandomUserAgent()`: Get random User-Agent string

**Data Source:** [fakeUserAgent/user_agents.json](fakeUserAgent/user_agents.json)

### 5. **Config Option** ([config/option.py](config/option.py))
**Class:** `option`

**Responsibilities:**
- Command-line argument parsing
- Menu system
- Input validation

**Key Methods:**
- `menu()`: Display menu options
- `getCommand()`: Parse command-line arguments
- `getOption()`: Get user menu selection
- `main()`: Main option handling logic

### 6. **Answer Spider** ([answerSpider/__init__.py](answerSpider/__init__.py))
**Status:** ⏳ In Development

**Purpose:** Extract content from question-type links

---

## 📦 Dependencies

### Core Dependencies ([requirements.txt](requirements.txt))
```
fonttools==4.53.1          # Font file parsing
lxml==5.2.2                # HTML/XML parsing
numpy==1.26.4              # Numerical computing
onnxruntime==1.18.1        # ONNX model runtime
opencv_python_headless==4.10.0.84  # Image processing
Pillow==10.4.0             # Image manipulation
Requests==2.32.3           # HTTP requests
```

### OCR Dependencies ([ddddocr/requirements.txt](ddddocr/requirements.txt))
- Additional OCR-specific packages

---

## ⚙️ Configuration

### Configuration File ([config.ini](config.ini))
```ini
[DEFAULT]
Cookie=<your_zhihu_cookie>
User-Agent=Mozilla/5.0 (Linux; Android 14; ...)
Host=zhihu.com
```

**Required Setup:**
1. Valid Zhihu Yanxuan membership account
2. Cookie from network inspection tools
3. Mobile User-Agent string

---

## 🚀 Development Roadmap

| Feature | Status |
|---------|--------|
| Dynamic User-Agent Generation | ✅ Completed |
| Font Decoding & Rendering | ✅ Completed |
| Single Question Extraction | ⏳ In Development |
| Market Link Extraction | ✅ Completed |
| Full Book Extraction | ⏳ In Development |
| GUI Implementation | ⏳ Planned |
| Keyword-based Search | ⏳ Planned |

---

## 📝 Usage Examples

### Basic Usage
```bash
# Interactive mode
python main/spider.py

# Follow menu prompts:
# 1. Extract single question
# 2. Extract book chapter
# 3. Extract full book
# 4. Keyword search
# 0. Exit
```

### Example Workflow (Option 2)
```python
from main.spider import zhihuSpider

spider = zhihuSpider()
spider._zhihuSpider__option = "2"
url = "https://www.zhihu.com/market/paid_column/..."
spider.getOptionChoise()
```

---

## 🔐 Security & Legal Considerations

### Authentication
- Requires valid Zhihu Yanxuan membership
- Cookie-based authentication
- Mobile User-Agent required

### Legal Notice
⚠️ **This tool is designed for personal archiving of legally accessible Yanxuan content.** Users are responsible for ensuring their use complies with Zhihu's Terms of Service and applicable laws.

---

## 🐛 Troubleshooting

### Common Issues

**Module Import Errors**
```bash
pip install -r requirements.txt
```

**Content Extraction Failure**
- Verify active Zhihu Yanxuan membership
- Check Cookie validity in config.ini
- Ensure User-Agent is mobile-format
- Try different User-Agent options

**OCR Recognition Errors**
- Automatic retry mechanism (3 attempts)
- Falls back to default character ("一")
- Check font file integrity

---

## 📚 Technical Highlights

### Font Obfuscation Solution
1. **Extract**: Download base64-encoded WOFF font from CSS
2. **Parse**: Use fontTools to extract glyph mappings
3. **Generate**: Create individual character images
4. **Recognize**: Use ddddocr for character recognition
5. **Map**: Build character replacement dictionary
6. **Replace**: Substitute obfuscated characters in content

### Anti-Crawling Countermeasures
- Random User-Agent rotation
- Mobile headers simulation
- Cookie-based authentication
- Automatic retry on failure
- Font decoding for obfuscated text

---

## 🤝 Contributing

**Contribution Guidelines:**
1. Fork the repository
2. Create a feature branch
3. Submit documented Pull Request

**Issue Templates:**
- [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)
- [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)

---

## 📧 Contact

**For specific requirements:**
Send quote + requirements to: twaapot@gmail.com

---

## 📅 Project History

### Recent Updates
- **2025-03-08**: Bug fixes by [@Xmug](https://github.com/Xmug)
- **2024-04-20**: Code refactoring and architecture optimization

### Git Status
- **Current Branch:** main
- **Uncommitted Changes:**
  - Modified: [config.ini](config.ini)
  - Modified: [requirements.txt](requirements.txt)
  - New: [.gitignore](.gitignore)

### Recent Commits
- `bde0ee9` Update issue templates
- `4a71a88` Update README.md
- `eabd6d6` Update README.md
- `92d836d` Bug fixes (PR by @Xmug)
- `932d6d0` Update README.md

---

## 📄 File Summary

### Python Modules (7 files)
- [main/spider.py](main/spider.py) - Main application controller
- [config/option.py](config/option.py) - Configuration handler
- [marketSpider/__init__.py](marketSpider/__init__.py) - Market content extractor
- [fontPreview/__init__.py](fontPreview/__init__.py) - Font processor
- [fakeUserAgent/__init__.py](fakeUserAgent/__init__.py) - User-Agent manager
- [answerSpider/__init__.py](answerSpider/__init__.py) - Answer extractor (WIP)
- [ddddocr/__init__.py](ddddocr/__init__.py) - OCR wrapper

### Configuration Files (3 files)
- [config.ini](config.ini) - Application configuration
- [requirements.txt](requirements.txt) - Python dependencies
- [.gitignore](.gitignore) - Git ignore rules

### Documentation (4 files)
- [README.md](README.md) - Project documentation
- [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md)
- [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)
- [ddddocr/README.md](ddddocr/README.md)

### Data Files (1 file)
- [fakeUserAgent/user_agents.json](fakeUserAgent/user_agents.json) - User-Agent database

### ML Models (3 files)
- [ddddocr/common.onnx](ddddocr/common.onnx)
- [ddddocr/common_det.onnx](ddddocr/common_det.onnx)
- [ddddocr/common_old.onnx](ddddocr/common_old.onnx)

### Images (1 file)
- [ddddocr/logo.png](ddddocr/logo.png)

---

## 🔍 Code Statistics

- **Total Python Files:** 7
- **Total Lines of Code:** ~500+ (excluding venv)
- **Main Language:** Python 3.x
- **Supported Platforms:** Windows, Linux, macOS
- **Virtual Environment:** venv (configured)

---

*Index generated on: 2026-03-29*
*Project Version: Development*
*Python Version: 3.11+*
