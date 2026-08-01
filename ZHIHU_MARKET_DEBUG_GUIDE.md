# Zhihu Market Crawl Debug Guide

Tài liệu này ghi lại các quy luật và kinh nghiệm sửa lỗi cho chức năng crawl truyện Zhihu bằng:

```bash
python main/spider.py
```

Sau đó chọn menu item `2`.

Mục tiêu của tài liệu:
- Giải thích luồng chạy hiện tại
- Ghi lại những điểm dễ vỡ khi Zhihu thay đổi nhỏ
- Đưa ra quy trình debug nhanh để sửa lại mà không cần phân tích từ đầu

## 1. Luồng chạy hiện tại

File chính:
- `main/spider.py`
- `marketSpider/__init__.py`
- `fontPreview/__init__.py`

Luot chạy:
1. `MarketSpider.spider(url)` được gọi.
2. Chương trình xóa file sinh ra của lần trước:
   - `font_preview.png`
   - thư mục `images/`
3. Request bài viết và lưu vào `market.html`.
4. Trích `font.woff` từ CSS `@font-face` trong `market.html`.
5. Trích nội dung bài viết và ghi vào file `*.txt.temp`.
6. Phân tích `font.woff`, sinh:
   - `font_preview.png`
   - các ảnh glyph trong `images/`
7. OCR/match để tạo `glyfDict`.
8. Replace ký tự trong file `*.txt.temp` và ghi ra `*.txt`.

## 2. Các file quan trọng khi debug

Khi có lỗi, đây là 4 nhóm file cần giữ lại:

- `market.html`
- `font.woff`
- `font_preview.png`
- thư mục `images/`

Và nếu cần kiểm tra kết quả:
- `*.txt.temp`
- `*.txt`

Ý nghĩa:

### `market.html`
- Chứa payload gốc trả về từ Zhihu
- Đây là nơi cần kiểm tra đầu tiên nếu file `.txt.temp` rỗng

### `font_preview.png`
- Ảnh tổng hợp tất cả glyph của font obfuscation trong lần request hiện tại
- Dùng để nhìn bằng mắt xem các mã đang map tới ký tự nào

### `images/*.png`
- Mỗi file là một glyph đơn
- Tên file là mã Unicode giả trong lần request hiện tại, ví dụ `300D.png`, `FF1F.png`
- Mã này thay đổi theo từng lần crawl, không ổn định

### `samples/*.png`
- Bộ ảnh mẫu cho dấu câu/ký tự đặc biệt để hay OCR nhầm
- Tên file phải chính là ký tự thật, ví dụ:
  - `「.png`
  - `」.png`
  - `？.png`
  - `！.png`
  - `：.png`
- Dòng `U+xxxx` bên dưới trong sample có thể sai mà không vấn đề
- Logic hiện tại crop bỏ dòng mã, chỉ so sánh hình dạng glyph

## 3. Các vấn đề đã gặp và cách đã sửa

### Vấn đề A: `AttributeError: 'NoneType' object has no attribute 're_fetch_article'`

Nguyên nhân cũ:
- `MarketSpider.parse()` tạo `FontPreview()`
- Sau đó đã set `market_spider`
- Nhưng `FontPreview.preview()` lại tự tạo một `FontPreview()` mới
- Kết quả là mất state và `market_spider = None`

Cách sửa:
- `preview()` phải dùng chính `self`, không được tạo instance mới

### Vấn đề B: Chay xong không còn `font_preview.png` và `images/`

Nguyên nhân cũ:
- `preview(..., remove_files=True)` xóa output sau khi parse

Cách sửa:
- Xóa file cũ ở đầu mỗi lần crawl
- Giữ output sau khi crawl xong để debug

Hiện tại:
- Lần crawl mới sẽ cleanup file cũ trước
- Output mới được giữ lại

### Vấn đề C: File `*.txt.temp` rỗng

Nguyên nhân:
- Trước ngày code đọc `manuscriptData["pTagList"]`
- Có lúc Zhihu trả `pTagList = []`
- Nhưng nội dung thật lại nằm trong `manuscriptData["manuscript"]`

Cách sửa:
- Nếu `pTagList` rỗng, fallback sang parse HTML trong `manuscript`

Dấu hiệu nhận biết:
- Log vẫn báo `内容获取成功！`
- Nhưng file `.temp` có độ dài `0`
- Trong `market.html`, tìm được:
  - `pTagList":[]`
  - nhưng `manuscript":"<p>...</p>..."` lại có dữ liệu

### Vấn đề D: Chữ Hán đúng, nhưng dấu câu sai

Nguyên nhân:
- OCR nhận chữ Hán khá tốt
- Nhưng các dấu câu và ký tự ít nét thì bị nhầm thành:
  - chữ Hán khác
  - Latin (`r`, `l`)
  - số (`2`)
  - ký tự khác (`-`)

Cách sửa hiện tại:
1. Crop bỏ phần `U+xxxx` bên dưới ảnh glyph
2. Tạo nhiều variant ảnh để OCR
3. Đánh dấu kết quả OCR đáng nghi, ví dụ:
   - rỗng
   - dài hơn 1 ký tự
   - Latin/số/ký tự đơn nét
4. Nếu đáng nghi thì fallback sang so khớp ảnh đặc biệt
5. So khớp ưu tiên `samples/` trước
6. Nếu không có sample thì mới dùng render bằng font hệ thống
7. Nếu sample match rất mạnh thì được override cả khi OCR trả về chữ Hán

Ví dụ lỗi đã gặp:
- `」` bị nhầm thành `上`

Cách đã xử lý:
- Thêm sample override threshold để nếu hình dạng rất giống `」` thì ép kết quả thành `」`

## 4. Quy trình debug nhanh khi Zhihu đổi nhỏ

Nếu sau này chương trình lại lỗi, làm theo đúng thứ tự này.

### Bước 1: Kiểm tra `market.html`

Cần trả lời 3 câu hỏi:

1. Có request thành công không?
2. Trích được `font.woff` không?
3. Nội dung nằm ở đâu?

Cần tìm trong `market.html`:
- `id="resolved"`
- `manuscriptData`
- `pTagList`
- `manuscript`
- `@font-face`

Nếu `pTagList` rỗng:
- Kiểm tra `manuscript`
- Nếu `manuscript` có nội dung, parser phải fallback sang đây

Nếu cả `pTagList` và `manuscript` đều rỗng:
- Khả năng cao Zhihu đổi payload
- Cần tìm field mới trong `manuscriptData`

### Bước 2: Kiểm tra `font_preview.png`

Mở file này và đối chiếu:
- Ô vuông nào là dấu câu
- Ô vuông nào là chữ Hán
- Mã U+ nào đang trỏ đến glyph nào trong lần request này

Nếu thấy bằng mắt mà log map sai:
- Lỗi nằm ở OCR/matching, không phải ở request

### Bước 3: Kiểm tra `images/`

Mở các file đáng nghi, nhất là:
- `300C.png`
- `300D.png`
- `3002.png`
- `FF01.png`
- `FF1A.png`
- `FF1F.png`

Cần xác định:
- Glyph thật là gì
- OCR đang trả về gì
- Sample có tồn tại cho glyph đó không

### Bước 4: Kiểm tra `samples/`

Nếu dấu câu mới lại hay nhầm:
1. Chạy crawl 1 lần
2. Tìm file glyph đúng trong `images/`
3. Copy vào `samples/`
4. Đổi tên thành ký tự thật, ví dụ `」.png`

Lưu ý:
- Không cần sửa dòng `U+xxxx`
- Không cần Photoshop xóa mã ở bên dưới, vì code đã crop bỏ

### Bước 5: Kiểm tra file kết quả

So sánh:
- `*.txt.temp`: nội dung trước khi thay ký tự
- `*.txt`: nội dung sau khi thay ký tự

Nếu `.temp` đã đúng mà `.txt` sai:
- Lỗi nằm ở mapping

Nếu `.temp` đã rỗng:
- Lỗi nằm ở parser nội dung

## 5. Những điểm dễ vỡ nhất trong code

### `marketSpider/__init__.py`

Chỗ dễ vỡ:
- `get_third_font_face()`
- `getContent()`
- `parse()`
- `cleanup_generated_files()`

Nếu Zhihu đổi HTML/CSS:
- Rất có thể phải sửa `get_third_font_face()`

Nếu Zhihu đổi payload JSON:
- Rất có thể phải sửa `getContent()`

### `fontPreview/__init__.py`

Chỗ dễ vỡ:
- `_extract_glyph_image()`
- `_is_suspicious_result()`
- `_load_sample_references()`
- `_get_best_special_match()`
- `recognize_image()`

Nếu dấu câu bị nhầm:
- Ưu tiên sửa trong khu vực này

## 6. Cách mở rộng bộ `samples`

Nên bổ sung sample cho các ký tự dễ nhầm sau:
- `「`
- `」`
- `？`
- `！`
- `：`
- `。`

Có thể bổ sung thêm nếu sau này gặp:
- `，`
- `、`
- `；`
- `（`
- `）`
- `《`
- `》`
- `"`
- `"`
- `…`

Nguyên tắc đặt tên:
- Tên file phải là ký tự thật
- Ví dụ `。.png`, `，.png`, `（.png`

## 7. Dấu hiệu để biết đang hỏng ở đâu

### Trường hợp 1: Log đúng, file `.txt` rỗng
- Kiểm tra `*.txt.temp`
- Nếu `.temp` rỗng: parser nội dung hỏng
- Nếu `.temp` có dữ liệu: replace/mapping hỏng

### Trường hợp 2: Chữ Hán đúng, dấu câu sai
- OCR chữ Hán vẫn ổn
- Fallback/sample cho dấu câu chưa đủ
- Ưu tiên bổ sung `samples/`

### Trường hợp 3: Cả chữ Hán cũng sai hàng loạt
- Có thể:
  - OCR fail trên toàn bộ font
  - crop glyph sai
  - `font.woff` đã đổi kiểu
  - trích nhầm `@font-face`

### Trường hợp 4: Không sinh `font.woff` hoặc `images/`
- Kiểm tra `@font-face`
- Kiểm tra `get_third_font_face()`
- Kiểm tra `fontFile.split(",")`

## 8. Cách sửa tối thiểu nếu server đổi nhỏ

Nếu có lỗi nhỏ trong tương lai, ưu tiên sửa theo thứ tự:

1. Sửa parser nội dung trong `getContent()`
2. Sửa parser font trong `get_third_font_face()`
3. Thêm hoặc cập nhật `samples/`
4. Điều chỉnh ngưỡng so khớp trong `fontPreview/__init__.py`
5. Chỉ sửa OCR chữ Hán nếu thật sự cần thiết

Lý do:
- Lỗi thường gặp nhất là đổi payload JSON và nhầm dấu câu
- Chữ Hán hiện tại đã ổn hơn nhiều so với dấu câu

## 9. Checklist khi báo lỗi mới

Khi cần debug một lần lỗi mới, hãy giữ lại:

- URL đã crawl
- Log đầy đủ
- `market.html`
- `font.woff`
- `font_preview.png`
- thư mục `images/`
- thư mục `samples/`
- file `.temp`
- file `.txt`

Nếu có đầy đủ bộ này, gần như chắc chắn sẽ phân tích và sửa lại được nhanh.

