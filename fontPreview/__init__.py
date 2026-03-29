import io
import logging
import math
import os
import re
import shutil
import sys

from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import ddddocr

try:
    RESAMPLING_LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLING_LANCZOS = Image.LANCZOS


class FontDocument:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)


class FontPreview:
    SAMPLE_DIR = "samples"
    SAMPLE_OVERRIDE_THRESHOLD = 32
    SPECIAL_CHARACTERS = [
        "\uFF1F",
        "\uFF01",
        "\uFF1A",
        "\u3002",
        "\u300C",
        "\u300D",
        "\u300A",
        "\u300B",
        "\uFF08",
        "\uFF09",
        "\uFF0C",
        "\u3001",
        "\uFF1B",
        "\u201C",
        "\u201D",
        "\u2018",
        "\u2019",
        "\u2026",
        "\u00B7",
    ]

    def __init__(self):
        self.font_meta = []
        self.font_dict = {}
        self.market_spider = None
        self._sample_cache = None

    def set_market_spider(self, market_spider):
        self.market_spider = market_spider

    def open_font(self, file_path):
        return FontDocument(file_path)

    def parse_font(self, document):
        try:
            font = TTFont(document.file_path)
            cmap = font.getBestCmap()

            self.font_meta = []
            for unicode_val, glyph_name in cmap.items():
                try:
                    Unicode[unicode_val]
                except KeyError:
                    pass

                glyph_info = {
                    "name": glyph_name,
                    "unicode": f"U+{unicode_val:04X}",
                    "unicode_value": unicode_val,
                    "character": chr(unicode_val),
                }
                self.font_meta.append(glyph_info)

            return font
        except Exception as e:
            raise Exception(f"Error parsing font: {str(e)}")

    def _load_unicode_font(self, size):
        for font_name in ["arial.ttf", "msyh.ttc", "msyhbd.ttc", "simsun.ttc"]:
            try:
                return ImageFont.truetype(font_name, size=size)
            except OSError:
                continue
        return ImageFont.load_default()

    def generate_image(self, font_file_path):
        glyph_size = 100
        glyphs_per_row = 10
        padding = 10

        num_glyphs = len(self.font_meta)
        num_rows = (num_glyphs + glyphs_per_row - 1) // glyphs_per_row
        img_width = (glyph_size + padding) * glyphs_per_row + padding
        img_height = (glyph_size + padding) * num_rows + padding

        image = Image.new("RGB", (img_width, img_height), color="white")
        draw = ImageDraw.Draw(image)

        try:
            preview_font = ImageFont.truetype(font_file_path, size=60)
        except IOError:
            preview_font = ImageFont.load_default()

        unicode_font = self._load_unicode_font(12)

        for i, glyph in enumerate(self.font_meta):
            row = i // glyphs_per_row
            col = i % glyphs_per_row
            x = col * (glyph_size + padding) + padding
            y = row * (glyph_size + padding) + padding

            draw.rectangle([x, y, x + glyph_size, y + glyph_size], outline="black")
            draw.text(
                (x + glyph_size // 2, y + glyph_size // 2 - 15),
                glyph["character"],
                font=preview_font,
                fill="black",
                anchor="mm",
            )
            draw.text(
                (x + glyph_size // 2, y + glyph_size - 15),
                glyph["unicode"],
                font=unicode_font,
                fill="black",
                anchor="mm",
            )

        return image

    def generate_single_character_image(self, font_file_path, glyph_info, size=200):
        image = Image.new("RGB", (size, size), color="white")
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype(font_file_path, size=size // 2)
        except IOError:
            font = ImageFont.load_default()

        draw.text(
            (size // 2, size // 2 - size // 8),
            glyph_info["character"],
            font=font,
            fill="black",
            anchor="mm",
        )

        unicode_font = self._load_unicode_font(size // 10)
        draw.text(
            (size // 2, size - size // 10),
            glyph_info["unicode"],
            font=unicode_font,
            fill="black",
            anchor="mm",
        )

        return image

    def save_image(self, image, output_path):
        image.save(output_path)

    def _serialize_image(self, image):
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def _get_binary_bbox(self, image, max_height_ratio=1.0):
        gray = image.convert("L")
        width, height = gray.size
        cropped_height = max(1, int(height * max_height_ratio))
        pixels = gray.load()
        min_x, min_y, max_x, max_y = width, cropped_height, -1, -1

        for y in range(cropped_height):
            for x in range(width):
                if pixels[x, y] < 220:
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

        if max_x == -1 or max_y == -1:
            return None
        return (min_x, min_y, max_x + 1, max_y + 1)

    def _extract_glyph_image(self, image):
        bbox = self._get_binary_bbox(image, max_height_ratio=0.72)
        if bbox is None:
            bbox = self._get_binary_bbox(image, max_height_ratio=1.0)
        if bbox is None:
            return image.convert("L")

        glyph = image.crop(bbox).convert("L")
        glyph = ImageOps.expand(glyph, border=24, fill=255)
        return glyph.resize((160, 160), RESAMPLING_LANCZOS)

    def _build_ocr_variants(self, image):
        glyph = self._extract_glyph_image(image)
        variants = [image.convert("L"), glyph]

        inverted = ImageOps.invert(glyph)
        bbox = inverted.getbbox()
        if bbox is not None:
            tight = glyph.crop(bbox)
            tight = ImageOps.expand(tight, border=32, fill=255)
            variants.append(tight.resize((180, 180), RESAMPLING_LANCZOS))

        return variants

    def _load_reference_font(self, size):
        for font_name in ["msyh.ttc", "msyhbd.ttc", "simhei.ttf", "simsun.ttc", "arial.ttf"]:
            try:
                return ImageFont.truetype(font_name, size=size)
            except OSError:
                continue
        return ImageFont.load_default()

    def _normalize_for_match(self, image, size=96):
        glyph = self._extract_glyph_image(image)
        bbox = ImageOps.invert(glyph).getbbox()
        if bbox is not None:
            glyph = glyph.crop(bbox)

        canvas = Image.new("L", (size, size), 255)
        scale = min((size - 16) / max(1, glyph.width), (size - 16) / max(1, glyph.height))
        resized = glyph.resize(
            (max(1, int(glyph.width * scale)), max(1, int(glyph.height * scale))),
            RESAMPLING_LANCZOS,
        )
        offset = ((size - resized.width) // 2, (size - resized.height) // 2)
        canvas.paste(resized, offset)
        return canvas

    def _render_reference_character(self, character, size=96):
        canvas = Image.new("L", (size, size), 255)
        draw = ImageDraw.Draw(canvas)
        font = self._load_reference_font(size // 2)
        draw.text((size // 2, size // 2), character, font=font, fill=0, anchor="mm")
        return self._normalize_for_match(canvas, size=size)

    def _load_sample_references(self, size=96):
        if self._sample_cache is not None:
            return self._sample_cache

        sample_map = {}
        if os.path.isdir(self.SAMPLE_DIR):
            for file_name in os.listdir(self.SAMPLE_DIR):
                file_path = os.path.join(self.SAMPLE_DIR, file_name)
                if not os.path.isfile(file_path):
                    continue

                character, extension = os.path.splitext(file_name)
                if not character or extension.lower() not in {".png", ".jpg", ".jpeg", ".bmp"}:
                    continue

                try:
                    with Image.open(file_path) as sample_image:
                        sample_map[character] = self._normalize_for_match(sample_image, size=size)
                except OSError:
                    logging.warning(f"无法读取样本图片: {file_path}")

        self._sample_cache = sample_map
        return self._sample_cache

    def _get_best_special_match(self, image):
        normalized = self._normalize_for_match(image)
        best_char = None
        best_score = None
        references = self._load_sample_references(size=normalized.size[0])

        if not references:
            references = {
                character: self._render_reference_character(character, size=normalized.size[0])
                for character in self.SPECIAL_CHARACTERS
            }

        for character, reference in references.items():
            diff = ImageChops.difference(normalized, reference)
            histogram = diff.histogram()
            total_pixels = normalized.size[0] * normalized.size[1]
            squared_sum = sum(value * ((index % 256) ** 2) for index, value in enumerate(histogram))
            score = math.sqrt(squared_sum / total_pixels)

            if best_score is None or score < best_score:
                best_char = character
                best_score = score

        return best_char, best_score

    def _match_special_character(self, image):
        best_char, best_score = self._get_best_special_match(image)
        if best_score is not None and best_score <= 75:
            logging.info(f"特殊字符兜底匹配成功: {best_char} (score={best_score:.2f})")
            return best_char
        return None

    def _is_suspicious_result(self, result):
        if not result:
            return True
        if len(result) != 1:
            return True
        if re.fullmatch(r"[A-Za-z0-9\-_=+*/\\|~`]", result):
            return True
        return False

    def generate_all_single_character_images(self, font_file_path, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for glyph_info in self.font_meta:
            image = self.generate_single_character_image(font_file_path, glyph_info)
            output_path = os.path.join(output_dir, f"{glyph_info['unicode'].split('+')[1]}.png")
            self.save_image(image, output_path)

    def recognize_image(self, image_path):
        ocr = ddddocr.DdddOcr(show_ad=False)
        ocr.set_ranges(7)
        images = sorted(os.listdir(image_path))
        sample_characters = set(self._load_sample_references().keys())

        for image_name in images:
            image_file = os.path.join(image_path, image_name)
            with Image.open(image_file) as glyph_image:
                variants = self._build_ocr_variants(glyph_image)

            result = ""
            for variant in variants:
                result = ocr.classification(self._serialize_image(variant)).strip()
                if result:
                    break

            with Image.open(image_file) as glyph_image:
                best_special_char, best_special_score = self._get_best_special_match(glyph_image)

            if (
                best_special_char
                and best_special_score is not None
                and best_special_score <= self.SAMPLE_OVERRIDE_THRESHOLD
            ):
                result = best_special_char

            if self._is_suspicious_result(result) or result in sample_characters:
                special_result = None
                if best_special_char and best_special_score is not None and best_special_score <= 75:
                    special_result = best_special_char
                if special_result:
                    result = special_result

            if not result:
                logging.error(f"图片 {image_name} 识别结果为空，无法建立字体映射")
                raise ValueError(f"无法识别字符图片: {image_name}")

            self.font_dict[chr(int(image_name.split(".")[0], 16))] = result

    def remove_files(self, path):
        if os.path.exists("font_preview.png"):
            os.remove("font_preview.png")
        shutil.rmtree(path)

    def fill_font_dict(self):
        for key, value in self.font_dict.items():
            if value == "":
                self.font_dict[key] = "\u4E00"

    def correct_font_dict(self):
        for key, value in self.font_dict.items():
            if value == "\u4E8C":
                self.font_dict[key] = "\u4E00"
                logging.info("字体映射表已检查并修正。")

    def preview(self, font_file_path, output_dir, remove_files=True):
        font_document = self.open_font(font_file_path)
        self.parse_font(font_document)
        image = self.generate_image(font_file_path)
        self.save_image(image, "font_preview.png")
        self.generate_all_single_character_images(font_file_path, output_dir)
        self.recognize_image(output_dir)
        if remove_files:
            self.remove_files(output_dir)
        self.fill_font_dict()
        self.correct_font_dict()
        return self.font_dict
