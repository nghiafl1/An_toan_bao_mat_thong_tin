✨ Tính năng chính
Mã hóa mạnh mẽ: Sử dụng thuật toán AES-256 bit tự triển khai (manual implementation of AES blocks) phục vụ mục đích học tập và nghiên cứu.

Chế độ CBC: Sử dụng Vector khởi tạo (IV) ngẫu nhiên cho mỗi lần mã hóa để đảm bảo an toàn.

Dẫn xuất khóa an toàn: Sử dụng PBKDF2HMAC (với SHA-256) và Salt ngẫu nhiên để tạo khóa 256-bit từ mật khẩu người dùng.

Hỗ trợ đa định dạng:

Nhập văn bản trực tiếp.

Đọc file văn bản thuần (.txt).

Mới: Đọc nội dung từ file Microsoft Word (.docx).

Giao diện hiện đại: Giao diện tối (Dark Theme) được xây dựng bằng PySide6 (Qt for Python).

Lưu trữ: Dễ dàng lưu kết quả mã hóa/giải mã ra file .txt.

🛠️ Yêu cầu cài đặt
Để chạy được chương trình, bạn cần cài đặt Python 3.x và các thư viện sau:

PySide6: Để hiển thị giao diện.

cryptography: Để sử dụng hàm băm và dẫn xuất khóa (KDF).

python-docx: Để đọc file Word.

Cài đặt qua pip
Mở terminal hoặc Command Prompt và chạy lệnh sau:
pip install PySide6 cryptography python-docx

🚀 Hướng dẫn sử dụng
Mã hóa (Encrypt):

Nhập văn bản vào ô "Văn bản" hoặc nhấn nút 📂 Đọc file để chọn file .txt hoặc .docx.

Nhập mật khẩu vào ô "Mật khẩu".

Nhấn nút 🔒 Mã hóa.

Kết quả (chuỗi Base64) sẽ hiện ở ô "Kết quả".

Giải mã (Decrypt):

Paste chuỗi mã hóa (Base64) vào ô "Văn bản" (hoặc đọc từ file đã lưu).

Nhập đúng mật khẩu đã dùng để mã hóa.

Nhấn nút 🔓 Giải mã.

Nội dung gốc sẽ hiện ra ở ô "Kết quả".

Lưu kết quả:

Sau khi mã hóa hoặc giải mã, nhấn 💾 Lưu file để lưu nội dung từ ô kết quả ra máy.

🧠 Cơ chế hoạt động (Technical Details)
Key Expansion: Mở rộng khóa từ 256-bit ban đầu thành các khóa vòng (Round Keys).

Cấu trúc dữ liệu đầu ra: Chuỗi kết quả được mã hóa Base64 bao gồm 3 phần ghép lại: [Salt (16 bytes)] + [IV (16 bytes)] + [Ciphertext] Điều này giúp quá trình giải mã tự động trích xuất Salt và IV mà không cần người dùng phải nhớ.

Padding: Sử dụng chuẩn PKCS#7 để đảm bảo dữ liệu đầu vào chia hết cho kích thước khối (16 bytes).