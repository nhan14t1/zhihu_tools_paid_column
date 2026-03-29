# Samples Folder

Đặt các hình ảnh PNG của các ký tự đặc biệt (dấu câu) vào folder này.

## Định dạng tên file:

```
ký tự.png
```

Ví dụ:
- `「.png` - Dấu mở ngoặc kép
- `」.png` - Dấu đóng ngoặc kép
- `！.png` - Dấu chấm than
- `：.png` - Dấu hai chấm
- `？.png` - Dấu chấm hỏi
- `…`.png - Dấu ba chấm
- `。.png` - Dấu chấm tròn

## Cách lấy hình ảnh:

1. Chạy chương trình crawl một lần
2. Vào folder `/images/`
3. Tìm file PNG tương ứng với ký tự cần (ví dụ: `300C.png` cho dấu 「)
4. Copy file đó vào folder `/samples/` và đổi tên thành `「.png`

## Lưu ý:

- Chỉ đặt các ký tự đặc biệt/dấu câu vào đây
- Không đặt chữ Hán (chữ Hán sẽ được tự động map bằng OCR)
- Ảnh nên có kích thước 200x200 pixels (như files trong /images/)
