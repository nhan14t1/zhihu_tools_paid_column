# Zhihu Market Crawl Debug Guide

Tai lieu nay ghi lai cac quy luat va kinh nghiem sua loi cho chuc nang crawl truyen Zhihu bang:

```bash
python main/spider.py
```

Sau do chon menu item `2`.

Muc tieu cua tai lieu:
- Giai thich luong chay hien tai
- Ghi lai nhung diem de vo khi Zhihu thay doi nho
- Dua ra quy trinh debug nhanh de sua lai ma khong can phan tich tu dau

## 1. Luong chay hien tai

File chinh:
- `main/spider.py`
- `marketSpider/__init__.py`
- `fontPreview/__init__.py`

Luot chay:
1. `MarketSpider.spider(url)` duoc goi.
2. Chuong trinh xoa file sinh ra cua lan truoc:
   - `font_preview.png`
   - thu muc `images/`
3. Request bai viet va luu vao `market.html`.
4. Trich `font.woff` tu CSS `@font-face` trong `market.html`.
5. Trich noi dung bai viet va ghi vao file `*.txt.temp`.
6. Phan tich `font.woff`, sinh:
   - `font_preview.png`
   - cac anh glyph trong `images/`
7. OCR/match de tao `glyfDict`.
8. Replace ky tu trong file `*.txt.temp` va ghi ra `*.txt`.

## 2. Cac file quan trong khi debug

Khi co loi, day la 4 nhom file can giu lai:

- `market.html`
- `font.woff`
- `font_preview.png`
- thu muc `images/`

Va neu can kiem tra ket qua:
- `*.txt.temp`
- `*.txt`

Y nghia:

### `market.html`
- Chua payload goc tra ve tu Zhihu
- Day la noi can kiem tra dau tien neu file `.txt.temp` rong

### `font_preview.png`
- Anh tong hop tat ca glyph cua font obfuscation trong lan request hien tai
- Dung de nhin bang mat xem cac ma dang map toi ky tu nao

### `images/*.png`
- Moi file la mot glyph don
- Ten file la ma Unicode gia trong lan request hien tai, vi du `300D.png`, `FF1F.png`
- Ma nay thay doi theo tung lan crawl, khong on dinh

### `samples/*.png`
- Bo anh mau cho dau cau/ky tu dac biet de hay OCR nham
- Ten file phai la chinh ky tu that, vi du:
  - `「.png`
  - `」.png`
  - `？.png`
  - `！.png`
  - `：.png`
- Dong `U+xxxx` ben duoi trong sample co the sai ma khong van de
- Logic hien tai crop bo dong ma, chi so sanh hinh dang glyph

## 3. Cac van de da gap va cach da sua

### Van de A: `AttributeError: 'NoneType' object has no attribute 're_fetch_article'`

Nguyen nhan cu:
- `MarketSpider.parse()` tao `FontPreview()`
- Sau do da set `market_spider`
- Nhung `FontPreview.preview()` lai tu tao mot `FontPreview()` moi
- Ket qua la mat state va `market_spider = None`

Cach sua:
- `preview()` phai dung chinh `self`, khong duoc tao instance moi

### Van de B: Chay xong khong con `font_preview.png` va `images/`

Nguyen nhan cu:
- `preview(..., remove_files=True)` xoa output sau khi parse

Cach sua:
- Xoa file cu o dau moi lan crawl
- Giu output sau khi crawl xong de debug

Hien tai:
- Lan crawl moi se cleanup file cu truoc
- Output moi duoc giu lai

### Van de C: File `*.txt.temp` rong

Nguyen nhan:
- Truoc day code doc `manuscriptData["pTagList"]`
- Co luc Zhihu tra `pTagList = []`
- Nhung noi dung that lai nam trong `manuscriptData["manuscript"]`

Cach sua:
- Neu `pTagList` rong, fallback sang parse HTML trong `manuscript`

Dau hieu nhan biet:
- Log van bao `内容获取成功！`
- Nhung file `.temp` co do dai `0`
- Trong `market.html`, tim duoc:
  - `pTagList":[]`
  - nhung `manuscript":"<p>...</p>..."` lai co du lieu

### Van de D: Chu Han dung, nhung dau cau sai

Nguyen nhan:
- OCR nhan chu Han kha tot
- Nhung cac dau cau va ky tu it net de bi nham thanh:
  - chu Han khac
  - Latin (`r`, `l`)
  - so (`2`)
  - ky tu khac (`-`)

Cach sua hien tai:
1. Crop bo phan `U+xxxx` ben duoi anh glyph
2. Tao nhieu variant anh de OCR
3. Danh dau ket qua OCR dang nghi, vi du:
   - rong
   - dai hon 1 ky tu
   - Latin/so/ky tu don net
4. Neu dang nghi thi fallback sang so khop anh dac biet
5. So khop uu tien `samples/` truoc
6. Neu khong co sample thi moi dung render bang font he thong
7. Neu sample match rat manh thi duoc override ca khi OCR tra ve chu Han

Vi du loi da gap:
- `」` bi nham thanh `上`

Cach da xu ly:
- Them sample override threshold de neu hinh dang rat giong `」` thi ep ket qua thanh `」`

## 4. Quy trinh debug nhanh khi Zhihu doi nho

Neu sau nay chuong trinh lai loi, lam theo dung thu tu nay.

### Buoc 1: Kiem tra `market.html`

Can tra loi 3 cau hoi:

1. Co request thanh cong khong?
2. Trich duoc `font.woff` khong?
3. Noi dung nam o dau?

Can tim trong `market.html`:
- `id="resolved"`
- `manuscriptData`
- `pTagList`
- `manuscript`
- `@font-face`

Neu `pTagList` rong:
- Kiem tra `manuscript`
- Neu `manuscript` co noi dung, parser phai fallback sang day

Neu ca `pTagList` va `manuscript` deu rong:
- Kha nang cao Zhihu doi payload
- Can tim field moi trong `manuscriptData`

### Buoc 2: Kiem tra `font_preview.png`

Mo file nay va doi chieu:
- O vuong nao la dau cau
- O vuong nao la chu Han
- Ma U+ nao dang tro den glyph nao trong lan request nay

Neu thay bang mat ma log map sai:
- Loi nam o OCR/matching, khong phai o request

### Buoc 3: Kiem tra `images/`

Mo cac file dang nghi, nhat la:
- `300C.png`
- `300D.png`
- `3002.png`
- `FF01.png`
- `FF1A.png`
- `FF1F.png`

Can xac dinh:
- Glyph that la gi
- OCR dang tra ve gi
- Sample co ton tai cho glyph do khong

### Buoc 4: Kiem tra `samples/`

Neu dau cau moi lai hay nham:
1. Chay crawl 1 lan
2. Tim file glyph dung trong `images/`
3. Copy vao `samples/`
4. Doi ten thanh ky tu that, vi du `」.png`

Luu y:
- Khong can sua dong `U+xxxx`
- Khong can Photoshop xoa ma o ben duoi, vi code da crop bo

### Buoc 5: Kiem tra file ket qua

So sanh:
- `*.txt.temp`: noi dung truoc khi thay ky tu
- `*.txt`: noi dung sau khi thay ky tu

Neu `.temp` da dung ma `.txt` sai:
- Loi nam o mapping

Neu `.temp` da rong:
- Loi nam o parser noi dung

## 5. Nhung diem de vo nhat trong code

### `marketSpider/__init__.py`

Cho de vo:
- `get_third_font_face()`
- `getContent()`
- `parse()`
- `cleanup_generated_files()`

Neu Zhihu doi HTML/CSS:
- rat co the phai sua `get_third_font_face()`

Neu Zhihu doi payload JSON:
- rat co the phai sua `getContent()`

### `fontPreview/__init__.py`

Cho de vo:
- `_extract_glyph_image()`
- `_is_suspicious_result()`
- `_load_sample_references()`
- `_get_best_special_match()`
- `recognize_image()`

Neu dau cau bi nham:
- uu tien sua trong khu vuc nay

## 6. Cach mo rong bo `samples`

Nen bo sung sample cho cac ky tu de nham sau:
- `「`
- `」`
- `？`
- `！`
- `：`
- `。`

Co the bo sung them neu sau nay gap:
- `，`
- `、`
- `；`
- `（`
- `）`
- `《`
- `》`
- `“`
- `”`
- `…`

Nguyen tac dat ten:
- Ten file phai la ky tu that
- Vi du `。.png`, `，.png`, `（.png`

## 7. Dau hieu de biet dang hong o dau

### Truong hop 1: Log dung, file `.txt` rong
- Kiem tra `*.txt.temp`
- Neu `.temp` rong: parser noi dung hong
- Neu `.temp` co du lieu: replace/mapping hong

### Truong hop 2: Chu Han dung, dau cau sai
- OCR chu Han van on
- Fallback/sample cho dau cau chua du
- Uu tien bo sung `samples/`

### Truong hop 3: Ca chu Han cung sai hang loat
- Co the:
  - OCR fail tren toan bo font
  - crop glyph sai
  - `font.woff` da doi kieu
  - trich nham `@font-face`

### Truong hop 4: Khong sinh `font.woff` hoac `images/`
- Kiem tra `@font-face`
- Kiem tra `get_third_font_face()`
- Kiem tra `fontFile.split(",")`

## 8. Cach sua toi thieu neu server doi nho

Neu co loi nho trong tuong lai, uu tien sua theo thu tu:

1. Sua parser noi dung trong `getContent()`
2. Sua parser font trong `get_third_font_face()`
3. Them hoac cap nhat `samples/`
4. Dieu chinh nguong so khop trong `fontPreview/__init__.py`
5. Chi sua OCR chu Han neu that su can thiet

Ly do:
- Loi thuong gap nhat la doi payload JSON va nham dau cau
- Chu Han hien tai da on hon nhieu so voi dau cau

## 9. Checklist khi bao loi moi

Khi can debug mot lan loi moi, hay luu lai:

- URL da crawl
- log day du
- `market.html`
- `font.woff`
- `font_preview.png`
- thu muc `images/`
- thu muc `samples/`
- file `.temp`
- file `.txt`

Neu co day du bo nay, gan nhu chac chan se phan tich va sua lai duoc nhanh.

