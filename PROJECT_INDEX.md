# Project Index: ZhiHu Tools

## Project Overview

**Project Name:** ZhiHu Tools  
**Description:** Tool for extracting Zhihu Yanxuan / Market story content  
**Language:** Python  
**Repository:** https://github.com/onewhitethreee/zhihu_tools

### Purpose
This project is used to crawl paid Zhihu market stories, decode obfuscated fonts, recover the correct Chinese text, and save the result as local text files.

The currently stable workflow is:
- Run `python main/spider.py`
- Choose menu item `2` to crawl one URL
- Choose menu item `5` to crawl many URLs from `urls.csv`

---

## Project Architecture

### Directory Structure
```text
zhihu_tools/
├── answerSpider/                  # Question/answer crawler (not implemented)
├── config/                        # Config helpers
├── ddddocr/                       # OCR engine and ONNX models
├── fakeUserAgent/                 # Random User-Agent helper
├── fontPreview/                   # Font decoding and glyph recognition
├── images/                        # Runtime glyph images from current crawl
├── main/                          # Entry scripts
├── marketSpider/                  # Zhihu market crawler
├── output/                        # Batch crawl output files
├── samples/                       # Punctuation sample images
├── .gitignore
├── config.ini
├── font.woff                      # Runtime font from current crawl
├── font_preview.png               # Runtime font preview image
├── market.html                    # Runtime HTML from current crawl
├── PROJECT_INDEX.md               # This file
├── README.md
├── requirements.txt
├── urls.csv                       # Batch crawl input list
└── ZHIHU_MARKET_DEBUG_GUIDE.md    # Detailed debugging guide
```

### Important Runtime Files
- `market.html`: raw Zhihu response for the latest crawl
- `font.woff`: custom obfuscation font extracted from the page
- `font_preview.png`: preview grid of all glyphs in the current font
- `images/*.png`: one glyph image per character for the current crawl
- `samples/*.png`: trusted punctuation samples used to correct OCR mistakes

---

## Core Components

### 1. Main Spider
**File:** [main/spider.py](main/spider.py)  
**Class:** `zhihuSpider`

**Responsibilities:**
- Load config and headers
- Show interactive menu
- Route execution to the selected crawl mode
- Run batch crawl from `urls.csv`
- Insert random delay between batch requests

**Implemented Menu Items:**
- `2`: Crawl a single market chapter URL
- `5`: Crawl many URLs from `urls.csv`

**Current Menu:**
```text
1. Single question extraction
2. Single market chapter crawl
3. Full book extraction
4. Keyword crawl
5. Batch crawl urls.csv
0. Exit
```

**Key Methods:**
- `getOptionChoise()`: dispatch menu selection
- `optionChoise2()`: single URL crawl
- `optionChoise5()`: batch crawl from CSV
- `commandChoise()`: return current option

**Batch Crawl Behavior:**
- Reads `urls.csv`
- Expected row format: `ID,URL`
- Skips empty or invalid rows with warning logs
- Saves output to `output/`
- Uses random delay between requests

**Delay Settings:**
- `BATCH_DELAY_MIN_SECONDS = 3`
- `BATCH_DELAY_MAX_SECONDS = 8`

### 2. Market Spider
**File:** [marketSpider/__init__.py](marketSpider/__init__.py)  
**Class:** `MarketSpider`

**Responsibilities:**
- Request Zhihu market pages
- Extract and decode the runtime font
- Extract story content
- Save `.temp` and `.txt`
- Support output directory and filename prefix for batch mode

**Key Methods:**
- `__init__(header, output_dir=None, filename_prefix=None)`
- `sanitize_filename()`
- `build_output_stem()`
- `cleanup_generated_files()`
- `getMarketHtml(url)`
- `getFontFile()`
- `get_third_font_face()`
- `getContent()`
- `replace_text()`
- `parse()`
- `spider(url)`

**Current Output Rules:**
- Menu item `2`:
  - saves to project root
  - filename based on story title
- Menu item `5`:
  - saves to `output/`
  - filename format: `ID-Title`
  - example: `065-Story Title.txt`

**Content Extraction Strategy:**
1. Parse `#resolved` JSON from `market.html`
2. Read `manuscriptData["pTagList"]`
3. If `pTagList` is empty, fallback to `manuscriptData["manuscript"]`
4. Save extracted lines to `.temp`
5. Replace obfuscated glyphs and save final `.txt`

### 3. Font Preview
**File:** [fontPreview/__init__.py](fontPreview/__init__.py)  
**Classes:** `FontPreview`, `FontDocument`

**Responsibilities:**
- Parse `font.woff`
- Generate glyph preview images
- OCR glyph images
- Build character mapping dictionary
- Correct punctuation OCR errors with sample matching

**Key Methods:**
- `open_font()`
- `parse_font()`
- `generate_image()`
- `generate_single_character_image()`
- `generate_all_single_character_images()`
- `recognize_image()`
- `fill_font_dict()`
- `correct_font_dict()`
- `preview()`

**Punctuation Recovery Strategy:**
- Crop away the `U+xxxx` label area
- OCR normal Han glyphs
- Detect suspicious OCR results
- Compare punctuation glyphs against real images in `samples/`
- Allow strong sample matches to override OCR

This is why punctuation such as `？`, `！`, `：`, `「`, `」` is now much more stable.

### 4. Fake UserAgent
**File:** [fakeUserAgent/__init__.py](fakeUserAgent/__init__.py)

**Responsibilities:**
- Load user-agent list
- Choose random platform / user-agent
- Help reduce request fingerprint repetition

### 5. Config
**Files:**
- [config/__init__.py](config/__init__.py)
- [config/option.py](config/option.py)

**Responsibilities:**
- Read `config.ini`
- Provide Cookie / User-Agent / Host
- Legacy menu helper code still exists in `config/option.py`

### 6. Debug Guide
**File:** [ZHIHU_MARKET_DEBUG_GUIDE.md](ZHIHU_MARKET_DEBUG_GUIDE.md)

This file contains:
- known Zhihu structure changes
- how to inspect `market.html`
- how to inspect `font_preview.png` and `images/`
- how to add/update punctuation samples
- how to debug future breakages quickly

---

## Input and Output Formats

### Single Crawl Input
Interactive input from menu item `2`:
```text
https://www.zhihu.com/market/paid_column/.../section/...
```

### Batch Crawl Input
**File:** [urls.csv](urls.csv)

**Format:**
```csv
065,https://www.zhihu.com/market/paid_column/1702723501155422208/section/1788920608135983104
066,https://www.zhihu.com/market/paid_column/1702723501155422208/section/1788920608135983105
```

### Batch Crawl Output
Saved to `output/`:
```text
output/
  065-Story Title.temp
  065-Story Title.txt
  066-Another Story.temp
  066-Another Story.txt
```

---

## Dependencies

### Core Dependencies
From [requirements.txt](requirements.txt):
- `fonttools`
- `lxml`
- `numpy`
- `onnxruntime`
- `opencv_python_headless`
- `Pillow`
- `Requests`

### OCR Runtime
From `ddddocr/`:
- ONNX OCR models
- OCR wrapper code

---

## Current Features

| Feature | Status |
|---|---|
| Random User-Agent generation | Completed |
| Zhihu market chapter crawl | Completed |
| Font decoding and glyph mapping | Completed |
| Punctuation sample matching | Completed |
| Batch crawl from `urls.csv` | Completed |
| Random delay between batch URLs | Completed |
| Single question extraction | Not implemented |
| Full book extraction | Not implemented |
| Keyword crawl | Not implemented |

---

## Current Workflow Summary

### Option 2: Single Crawl
1. Ask user for URL
2. Request page
3. Save `market.html`
4. Extract `font.woff`
5. Extract content into `.temp`
6. Generate glyph images
7. OCR and build mapping
8. Replace text and save final `.txt`

### Option 5: Batch Crawl
1. Read all rows from `urls.csv`
2. Validate `ID,URL`
3. Crawl each URL in order
4. Save each result to `output/ID-Title.*`
5. Wait random delay before next URL

---

## Anti-Crawling Countermeasures

Current mitigations in the project:
- Cookie-based authenticated access
- Mobile-style User-Agent
- Random extra User-Agent suffix from local database
- Runtime font decoding
- Punctuation correction using sample glyphs
- Random delay between batch requests

---

## Troubleshooting

### If `.temp` is empty
- Check `market.html`
- Inspect `manuscriptData`
- Verify whether `pTagList` is empty
- Verify whether content is still present in `manuscript`

### If Han characters are mostly correct but punctuation is wrong
- Inspect `images/`
- Inspect `font_preview.png`
- Add or update images in `samples/`
- Re-run crawl

### If batch crawl does not start
- Ensure [urls.csv](urls.csv) exists
- Ensure each row has `ID,URL`

### If Zhihu changes page structure again
- Start with [ZHIHU_MARKET_DEBUG_GUIDE.md](ZHIHU_MARKET_DEBUG_GUIDE.md)

---

## File Summary

### Main Python Modules
- [main/spider.py](main/spider.py) - interactive menu and batch crawl
- [marketSpider/__init__.py](marketSpider/__init__.py) - Zhihu market crawler
- [fontPreview/__init__.py](fontPreview/__init__.py) - font parsing and glyph matching
- [fakeUserAgent/__init__.py](fakeUserAgent/__init__.py) - user-agent helper
- [config/__init__.py](config/__init__.py) - config reader
- [config/option.py](config/option.py) - legacy option helper
- [answerSpider/__init__.py](answerSpider/__init__.py) - placeholder module
- [ddddocr/__init__.py](ddddocr/__init__.py) - OCR wrapper

### Documentation
- [README.md](README.md)
- [PROJECT_INDEX.md](PROJECT_INDEX.md)
- [ZHIHU_MARKET_DEBUG_GUIDE.md](ZHIHU_MARKET_DEBUG_GUIDE.md)

### Runtime / Data
- [urls.csv](urls.csv) - batch input
- `output/` - batch output
- `samples/` - punctuation samples
- `images/` - latest generated glyph images

---

## Notes

- `PROJECT_INDEX.md` should reflect the actual working implementation, not the original upstream state.
- The most important recent additions are:
  - menu item `5`
  - `urls.csv` batch input
  - `output/ID-Title.txt` naming
  - random delay between batch requests
  - punctuation correction using `samples/`

---

*Index updated on: 2026-04-12*  
*Project version: Development*  
*Python version target: 3.x*
