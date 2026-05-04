#!/usr/bin/env python3
"""
DEOBFUSCATOR - CHỈ DÙNG THƯ VIỆN MẶC ĐỊNH
Không cần pip install gì cả!
"""

import base64
import zlib
import re
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def extract_payload():
    """Lấy payload từ file thtool.py"""
    log("Đang đọc file...")
    
    with open('thtool.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Tìm payload (chuỗi bytes dài nhất)
    pattern = r"b'([^']+)'"
    matches = re.findall(pattern, content)
    
    if not matches:
        pattern = r'b"([^"]+)"'
        matches = re.findall(pattern, content)
    
    if not matches:
        log("ERROR: Không tìm thấy payload!")
        return None
    
    payload = max(matches, key=len)
    log(f"Tìm thấy payload: {len(payload)} ký tự")
    return payload.encode('utf-8')

def try_decode(data):
    """Thử các cách giải mã (chỉ dùng thư viện mặc định)"""
    
    # 1. Thử Ascii85
    try:
        result = base64.a85decode(data)
        log(f"  ✓ Ascii85: {len(data)} -> {len(result)} bytes")
        return result, "Ascii85"
    except:
        pass
    
    # 2. Thử Base64
    try:
        result = base64.b64decode(data)
        log(f"  ✓ Base64: {len(data)} -> {len(result)} bytes")
        return result, "Base64"
    except:
        pass
    
    # 3. Thử URL-safe Base64
    try:
        result = base64.urlsafe_b64decode(data)
        log(f"  ✓ URL-safe Base64: {len(data)} -> {len(result)} bytes")
        return result, "URL-Base64"
    except:
        pass
    
    # 4. Thử giải nén zlib
    try:
        if data[:2] in [b'\x78\x9c', b'\x78\xda', b'\x78\x01']:
            result = zlib.decompress(data)
            log(f"  ✓ zlib: {len(data)} -> {len(result)} bytes")
            return result, "zlib"
    except:
        pass
    
    return data, None

def deep_decode(data):
    """Giải mã đệ quy"""
    current = data
    round_num = 0
    history = []
    
    log("Bắt đầu giải mã các lớp...")
    
    while round_num < 20:
        round_num += 1
        log(f"\n--- Lớp {round_num} ---")
        
        decoded, method = try_decode(current)
        
        if method is None:
            log("  Không thể giải mã thêm")
            break
        
        history.append(f"Lớp {round_num}: {method}")
        current = decoded
    
    log(f"\n✅ Đã giải mã {len(history)} lớp!")
    return current, history

def save_results(data, history):
    """Lưu kết quả"""
    log("\nLưu kết quả...")
    
    # Lưu lịch sử
    with open('deobfuscation_report.txt', 'w') as f:
        f.write("LỊCH SỬ GIẢI MÃ\n")
        f.write("=" * 50 + "\n")
        for h in history:
            f.write(f"{h}\n")
        f.write("\n")
    
    # Kiểm tra loại kết quả
    try:
        text = data.decode('utf-8')
        # Là text
        with open('decoded_payload.py', 'w', encoding='utf-8') as f:
            f.write(text)
        log("✅ Đã lưu decoded_payload.py")
        
        # In preview
        print("\n" + "=" * 60)
        print("PREVIEW (500 ký tự đầu):")
        print("=" * 60)
        print(text[:500])
        
    except UnicodeDecodeError:
        # Là binary
        ext = '.exe' if data[:2] == b'MZ' else '.bin'
        with open(f'decoded_payload{ext}', 'wb') as f:
            f.write(data)
        log(f"✅ Đã lưu decoded_payload{ext}")
        
        # In signature
        if data[:2] == b'MZ':
            print("\n🔴 PHÁT HIỆN WINDOWS EXECUTABLE!")
        elif data[:4] == b'\x7fELF':
            print("\n🔴 PHÁT HIỆN LINUX EXECUTABLE!")
        else:
            print("\n⚠️ Binary không xác định")

def main():
    print("=" * 60)
    print("DEOBFUSCATOR - GIẢI MÃ THTOOL.PY")
    print("=" * 60)
    
    # Trích xuất
    payload = extract_payload()
    if not payload:
        print("❌ Thất bại!")
        return
    
    # Giải mã
    result, history = deep_decode(payload)
    
    # Lưu kết quả
    save_results(result, history)
    
    print("\n" + "=" * 60)
    print("✅ HOÀN TẤT! VÀO ARTIFACTS ĐỂ TẢI KẾT QUẢ")
    print("=" * 60)

if __name__ == "__main__":
    main()
