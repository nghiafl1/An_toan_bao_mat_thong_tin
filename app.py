import base64
import os
from typing import List
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# --- THÊM MỚI: Import thư viện đọc file Word ---
try:
    from docx import Document
except ImportError:
    Document = None  # Xử lý trường hợp người dùng chưa cài thư viện

# ================= AES CONSTANTS & HELPERS =================

S_BOX = [
    # 0    1    2    3    4    5    6    7    8    9    A    B    C    D    E    F
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
]

INV_S_BOX = [
    0x52,0x09,0x6A,0xD5,0x30,0x36,0xA5,0x38,0xBF,0x40,0xA3,0x9E,0x81,0xF3,0xD7,0xFB,
    0x7C,0xE3,0x39,0x82,0x9B,0x2F,0xFF,0x87,0x34,0x8E,0x43,0x44,0xC4,0xDE,0xE9,0xCB,
    0x54,0x7B,0x94,0x32,0xA6,0xC2,0x23,0x3D,0xEE,0x4C,0x95,0x0B,0x42,0xFA,0xC3,0x4E,
    0x08,0x2E,0xA1,0x66,0x28,0xD9,0x24,0xB2,0x76,0x5B,0xA2,0x49,0x6D,0x8B,0xD1,0x25,
    0x72,0xF8,0xF6,0x64,0x86,0x68,0x98,0x16,0xD4,0xA4,0x5C,0xCC,0x5D,0x65,0xB6,0x92,
    0x6C,0x70,0x48,0x50,0xFD,0xED,0xB9,0xDA,0x5E,0x15,0x46,0x57,0xA7,0x8D,0x9D,0x84,
    0x90,0xD8,0xAB,0x00,0x8C,0xBC,0xD3,0x0A,0xF7,0xE4,0x58,0x05,0xB8,0xB3,0x45,0x06,
    0xD0,0x2C,0x1E,0x8F,0xCA,0x3F,0x0F,0x02,0xC1,0xAF,0xBD,0x03,0x01,0x13,0x8A,0x6B,
    0x3A,0x91,0x11,0x41,0x4F,0x67,0xDC,0xEA,0x97,0xF2,0xCF,0xCE,0xF0,0xB4,0xE6,0x73,
    0x96,0xAC,0x74,0x22,0xE7,0xAD,0x35,0x85,0xE2,0xF9,0x37,0xE8,0x1C,0x75,0xDF,0x6E,
    0x47,0xF1,0x1A,0x71,0x1D,0x29,0xC5,0x89,0x6F,0xB7,0x62,0x0E,0xAA,0x18,0xBE,0x1B,
    0xFC,0x56,0x3E,0x4B,0xC6,0xD2,0x79,0x20,0x9A,0xDB,0xC0,0xFE,0x78,0xCD,0x5A,0xF4,
    0x1F,0xDD,0xA8,0x33,0x88,0x07,0xC7,0x31,0xB1,0x12,0x10,0x59,0x27,0x80,0xEC,0x5F,
    0x60,0x51,0x7F,0xA9,0x19,0xB5,0x4A,0x0D,0x2D,0xE5,0x7A,0x9F,0x93,0xC9,0x9C,0xEF,
    0xA0,0xE0,0x3B,0x4D,0xAE,0x2A,0xF5,0xB0,0xC8,0xEB,0xBB,0x3C,0x83,0x53,0x99,0x61,
    0x17,0x2B,0x04,0x7E,0xBA,0x77,0xD6,0x26,0xE1,0x69,0x14,0x63,0x55,0x21,0x0C,0x7D
]

RCON = [
    0x00000000,
    0x01000000,0x02000000,0x04000000,0x08000000,0x10000000,0x20000000,0x40000000,
    0x80000000,0x1b000000,0x36000000, # enough for AES-256 expansion rounds
]

Nb = 4
Nk = 8   # 256-bit key -> 8 words
Nr = 14  # number of rounds for AES-256

def bytes2matrix(b: bytes) -> List[List[int]]:
    # AES state is 4x4 bytes, column-major
    return [[b[row + 4*col] for col in range(4)] for row in range(4)]

def matrix2bytes(matrix: List[List[int]]) -> bytes:
    return bytes([matrix[row][col] for col in range(4) for row in range(4)])

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

# ----------------- GF(2^8) multiply -----------------
def xtime(a: int) -> int:
    return ((a << 1) & 0xFF) ^ (0x1B if (a & 0x80) else 0x00)

def gf_mul(a: int, b: int) -> int:
    res = 0
    for i in range(8):
        if b & 1:
            res ^= a
        hi_bit_set = a & 0x80
        a = (a << 1) & 0xFF
        if hi_bit_set:
            a ^= 0x1B
        b >>= 1
    return res

# ================= KEY EXPANSION =================
def word_from_bytes(b: bytes) -> int:
    return (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3]

def bytes_from_word(w: int) -> bytes:
    return bytes([(w >> 24) & 0xFF, (w >> 16) & 0xFF, (w >> 8) & 0xFF, w & 0xFF])

def sub_word(w: int) -> int:
    b = bytes_from_word(w)
    return word_from_bytes(bytes([S_BOX[x] for x in b]))

def rot_word(w: int) -> int:
    b = bytes_from_word(w)
    return word_from_bytes(bytes([b[1], b[2], b[3], b[0]]))

def expand_key(key: bytes) -> List[int]:
    # returns list of 4-byte words (as ints), total Nb*(Nr+1) words = 4*(Nr+1)
    assert len(key) == 4 * Nk
    w = [word_from_bytes(key[4*i:4*i+4]) for i in range(Nk)]
    i = Nk
    while len(w) < Nb * (Nr + 1):
        temp = w[-1]
        if i % Nk == 0:
            temp = sub_word(rot_word(temp)) ^ RCON[i // Nk]
        elif Nk > 6 and (i % Nk) == 4:
            temp = sub_word(temp)
        w.append(w[-Nk] ^ temp)
        i += 1
    return w

def round_key_from_words(words: List[int], round_idx: int) -> List[List[int]]:
    # produce 4x4 matrix for the round (AddRoundKey)
    start = round_idx * Nb
    key_bytes = b''.join(bytes_from_word(w) for w in words[start:start+Nb])
    return bytes2matrix(key_bytes)

# ================= AES TRANSFORMS =================
def add_round_key(state: List[List[int]], round_key: List[List[int]]):
    for r in range(4):
        for c in range(4):
            state[r][c] ^= round_key[r][c]

def sub_bytes(state: List[List[int]]):
    for r in range(4):
        for c in range(4):
            state[r][c] = S_BOX[state[r][c]]

def inv_sub_bytes(state: List[List[int]]):
    for r in range(4):
        for c in range(4):
            state[r][c] = INV_S_BOX[state[r][c]]

def shift_rows(state: List[List[int]]):
    # row r is rotated left by r
    for r in range(1, 4):
        state[r] = state[r][r:] + state[r][:r]

def inv_shift_rows(state: List[List[int]]):
    for r in range(1, 4):
        state[r] = state[r][-r:] + state[r][:-r]

def mix_single_column(col: List[int]) -> List[int]:
    a = col[:]  # copy
    return [
        gf_mul(a[0],2) ^ gf_mul(a[1],3) ^ a[2] ^ a[3],
        a[0] ^ gf_mul(a[1],2) ^ gf_mul(a[2],3) ^ a[3],
        a[0] ^ a[1] ^ gf_mul(a[2],2) ^ gf_mul(a[3],3),
        gf_mul(a[0],3) ^ a[1] ^ a[2] ^ gf_mul(a[3],2)
    ]

def inv_mix_single_column(col: List[int]) -> List[int]:
    a = col[:]
    return [
        gf_mul(a[0],0x0e) ^ gf_mul(a[1],0x0b) ^ gf_mul(a[2],0x0d) ^ gf_mul(a[3],0x09),
        gf_mul(a[0],0x09) ^ gf_mul(a[1],0x0e) ^ gf_mul(a[2],0x0b) ^ gf_mul(a[3],0x0d),
        gf_mul(a[0],0x0d) ^ gf_mul(a[1],0x09) ^ gf_mul(a[2],0x0e) ^ gf_mul(a[3],0x0b),
        gf_mul(a[0],0x0b) ^ gf_mul(a[1],0x0d) ^ gf_mul(a[2],0x09) ^ gf_mul(a[3],0x0e)
    ]

def mix_columns(state: List[List[int]]):
    # operate column by column
    for c in range(4):
        col = [state[r][c] for r in range(4)]
        mixed = mix_single_column(col)
        for r in range(4):
            state[r][c] = mixed[r]

def inv_mix_columns(state: List[List[int]]):
    for c in range(4):
        col = [state[r][c] for r in range(4)]
        mixed = inv_mix_single_column(col)
        for r in range(4):
            state[r][c] = mixed[r]

# ================= BLOCK ENCRYPT / DECRYPT =================
def encrypt_block(block: bytes, round_keys: List[int]) -> bytes:
    state = bytes2matrix(block)
    add_round_key(state, round_key_from_words(round_keys, 0))

    for rnd in range(1, Nr):
        sub_bytes(state)
        shift_rows(state)
        mix_columns(state)
        add_round_key(state, round_key_from_words(round_keys, rnd))

    # final round (no mix_columns)
    sub_bytes(state)
    shift_rows(state)
    add_round_key(state, round_key_from_words(round_keys, Nr))

    return matrix2bytes(state)

def decrypt_block(block: bytes, round_keys: List[int]) -> bytes:
    state = bytes2matrix(block)
    add_round_key(state, round_key_from_words(round_keys, Nr))
    inv_shift_rows(state)
    inv_sub_bytes(state)

    for rnd in range(Nr-1, 0, -1):
        add_round_key(state, round_key_from_words(round_keys, rnd))
        inv_mix_columns(state)
        inv_shift_rows(state)
        inv_sub_bytes(state)

    add_round_key(state, round_key_from_words(round_keys, 0))
    return matrix2bytes(state)

# ================= PADDING (PKCS7) =================
def pkcs7_pad(data: bytes) -> bytes:
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len]) * pad_len

def pkcs7_unpad(data: bytes) -> bytes:
    if len(data) == 0 or len(data) % 16 != 0:
        raise ValueError("Invalid padded data length")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Invalid padding")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid PKCS7 padding bytes")
    return data[:-pad_len]

# ================= KEY DERIVATION (PBKDF2) =================
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,              # 256-bit key
        salt=salt,
        iterations=200_000,
    )
    return kdf.derive(password.encode("utf-8"))

# ================= MODE: CBC (using our block cipher) =================
def aes256_encrypt_cbc(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    if len(iv) != 16:
        raise ValueError("IV must be 16 bytes for CBC")
    round_keys = expand_key(key)
    padded = pkcs7_pad(plaintext)
    ciphertext = b""
    prev = iv
    for i in range(0, len(padded), 16):
        block = padded[i:i+16]
        block = xor_bytes(block, prev)
        enc = encrypt_block(block, round_keys)
        ciphertext += enc
        prev = enc
    return ciphertext

def aes256_decrypt_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    if len(iv) != 16:
        raise ValueError("IV must be 16 bytes for CBC")
    if len(ciphertext) % 16 != 0:
        raise ValueError("Invalid ciphertext length")
    round_keys = expand_key(key)
    plaintext_padded = b""
    prev = iv
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        dec = decrypt_block(block, round_keys)
        plaintext_padded += xor_bytes(dec, prev)
        prev = block
    return pkcs7_unpad(plaintext_padded)

# ==================== PUBLIC FUNCTIONS (used by GUI) ====================
def encrypt_text(plaintext: str, password: str) -> str:
    salt = os.urandom(16)
    key = derive_key(password, salt)        # 32 bytes
    iv = os.urandom(16)                     # 16-byte IV for CBC
    ciphertext = aes256_encrypt_cbc(plaintext.encode("utf-8"), key, iv)
    combined = salt + iv + ciphertext
    return base64.b64encode(combined).decode("utf-8")

def decrypt_text(cipher_b64: str, password: str) -> str:
    combined = base64.b64decode(cipher_b64)
    if len(combined) < 32:
        raise ValueError("Dữ liệu không hợp lệ")
    salt = combined[:16]
    iv = combined[16:32]
    ciphertext = combined[32:]
    key = derive_key(password, salt)
    plaintext = aes256_decrypt_cbc(ciphertext, key, iv)
    return plaintext.decode("utf-8")

# ==================== GUI ====================
class AESApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 AES-256 Encryptor")
        self.setFixedSize(900, 650)
        self.setStyleSheet("""
            QWidget {
                background-color: #202124;
                color: #E8EAED;
                font-family: 'Segoe UI';
            }
            QPushButton {
                background-color: #3C4043;
                color: white;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #5F6368;
            }
            QLineEdit, QTextEdit {
                background-color: #303134;
                border: 1px solid #5F6368;
                border-radius: 6px;
                color: #E8EAED;
                font-size: 14px;
            }
            QLabel {
                font-weight: bold;
                font-size: 15px;
            }
        """)

        layout = QVBoxLayout(self)

        title = QLabel("MÃ HÓA & GIẢI MÃ AES-256")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)

        layout.addWidget(QLabel("Văn bản:"))
        self.text_input = QTextEdit()
        layout.addWidget(self.text_input)

        layout.addWidget(QLabel("Mật khẩu:"))

        pw_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.toggle_pw_btn = QPushButton("👁")
        self.toggle_pw_btn.setFixedWidth(40)
        self.toggle_pw_btn.setCheckable(True)
        self.toggle_pw_btn.setToolTip("Hiện / Ẩn mật khẩu")
        self.toggle_pw_btn.setStyleSheet("""
            QPushButton {
                background-color: #3C4043;
                color: white;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #5F6368;
            }
        """)

        pw_layout.addWidget(self.password_input)
        pw_layout.addWidget(self.toggle_pw_btn)
        layout.addLayout(pw_layout)

        self.toggle_pw_btn.toggled.connect(self.toggle_password_visibility)

        layout.addWidget(QLabel("Kết quả:"))
        self.result_box = QTextEdit()
        layout.addWidget(self.result_box)

        button_layout = QHBoxLayout()

        self.open_btn = QPushButton("📂 Đọc file")
        self.encrypt_btn = QPushButton("🔒 Mã hóa")
        self.decrypt_btn = QPushButton("🔓 Giải mã")
        self.save_btn = QPushButton("💾 Lưu file")

        for btn in [self.open_btn, self.encrypt_btn, self.decrypt_btn, self.save_btn]:
            btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        self.open_btn.clicked.connect(self.open_file)
        self.save_btn.clicked.connect(self.save_file)
        self.encrypt_btn.clicked.connect(self.encrypt_action)
        self.decrypt_btn.clicked.connect(self.decrypt_action)

    # --- SỬA ĐỔI HÀM NÀY ĐỂ ĐỌC FILE WORD ---
    def open_file(self):
        # Cho phép chọn cả .txt và .docx
        file_filter = "All Files (*);;Text Files (*.txt);;Word Documents (*.docx)"
        path, _ = QFileDialog.getOpenFileName(self, "Chọn file văn bản", "", file_filter)
        
        if path:
            try:
                # Nếu là file Word (.docx)
                if path.endswith(".docx"):
                    if Document is None:
                        QMessageBox.warning(self, "Lỗi thiếu thư viện", "Bạn chưa cài đặt thư viện 'python-docx'.\nVui lòng chạy lệnh: pip install python-docx")
                        return
                        
                    doc = Document(path)
                    # Nối các đoạn văn bản lại với nhau
                    full_text = []
                    for para in doc.paragraphs:
                        full_text.append(para.text)
                    self.text_input.setPlainText('\n'.join(full_text))
                    
                # Nếu là file text (.txt)
                else:
                    with open(path, "r", encoding="utf-8") as f:
                        self.text_input.setPlainText(f.read())
                        
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể đọc file:\n{e}")

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Lưu file", "", "Text Files (*.txt)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.result_box.toPlainText())
                QMessageBox.information(self, "Thành công", "Đã lưu file thành công!")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu file:\n{e}")

    def encrypt_action(self):
        text = self.text_input.toPlainText().strip()
        password = self.password_input.text().strip()
        if not text or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập văn bản và mật khẩu!")
            return
        try:
            result = encrypt_text(text, password)
            self.result_box.setPlainText(result)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def decrypt_action(self):
        text = self.text_input.toPlainText().strip()
        password = self.password_input.text().strip()
        if not text or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập nội dung mã hóa và mật khẩu!")
            return
        try:
            result = decrypt_text(text, password)
            self.result_box.setPlainText(result)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Giải mã thất bại: {e}")

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_pw_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_pw_btn.setText("👁")

if __name__ == "__main__":
    app = QApplication([])
    window = AESApp()
    window.show()
    app.exec()