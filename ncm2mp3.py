# -*- coding: utf-8 -*-
"""把文件夹里所有的 .ncm 批量解密还原成 mp3 / flac。

用法：
    双击运行，把文件夹（或单个 .ncm 文件）拖进窗口回车；
    或者命令行 ncm2mp3.exe "D:\\Music" [--no-pause]
转换成功后原 .ncm 会被删除；.ncm 内部是 flac 的会输出 .flac。
"""

import base64
import binascii
import json
import os
import struct
import sys

from Crypto.Cipher import AES

MAGIC = b"CTENFDAM"
CORE_KEY = binascii.a2b_hex("687A4852416D736F356B496E62617857")
META_KEY = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
CHUNK = 0x8000
TMP_SUFFIX = ".ncm_tmp"


class NcmError(Exception):
    """ncm 文件损坏或格式不认识。"""


def _unpad(data):
    pad = data[-1]
    return data[:-pad] if 0 < pad <= 16 else data


def _xor(data, value):
    return bytes(b ^ value for b in data)


def _read_key_box(f):
    """读取并解密 RC4 风格的密钥盒。"""
    f.seek(2, os.SEEK_CUR)
    key_length = struct.unpack("<I", f.read(4))[0]
    key = _xor(f.read(key_length), 0x64)
    key = AES.new(CORE_KEY, AES.MODE_ECB).decrypt(key)
    key = _unpad(key)[17:]  # 去掉 "neteasecloudmusic" 前缀

    box = bytearray(range(256))
    last = 0
    offset = 0
    for i in range(256):
        swap = box[i]
        last = (swap + last + key[offset]) & 0xFF
        offset = (offset + 1) % len(key)
        box[i] = box[last]
        box[last] = swap
    return box


def _read_meta(f):
    meta_length = struct.unpack("<I", f.read(4))[0]
    blob = _xor(f.read(meta_length), 0x63)
    blob = base64.b64decode(blob[22:])  # 去掉 "163 key(Don't modify):"
    blob = AES.new(META_KEY, AES.MODE_ECB).decrypt(blob)
    text = _unpad(blob).decode("utf-8")[6:]  # 去掉 "music:"
    try:
        return json.loads(text)
    except ValueError:
        return {}


def _skip_cover(f):
    f.seek(4 + 5, os.SEEK_CUR)  # crc32 + 5 字节间隔
    cover_size = struct.unpack("<I", f.read(4))[0]
    f.seek(cover_size, os.SEEK_CUR)


def _decode_to(src_path, dst_path):
    """把 src_path 解密写入 dst_path，返回内嵌的元信息。"""
    with open(src_path, "rb") as f:
        if f.read(8) != MAGIC:
            raise NcmError("不是有效的 NCM 文件")
        key_box = _read_key_box(f)
        meta = _read_meta(f)
        _skip_cover(f)

        with open(dst_path, "wb") as out:
            while True:
                chunk = bytearray(f.read(CHUNK))
                size = len(chunk)
                if size == 0:
                    break
                for i in range(1, size + 1):
                    j = i & 0xFF
                    chunk[i - 1] ^= key_box[
                        (key_box[j] + key_box[(key_box[j] + j) & 0xFF]) & 0xFF
                    ]
                out.write(chunk)
    return meta


def _detect_ext(path, meta):
    """优先看真实文件头，其次看元信息里的 format。"""
    with open(path, "rb") as f:
        head = f.read(4)
    if head == b"fLaC":
        return ".flac"
    if head[:3] == b"ID3" or head[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return ".mp3"
    fmt = str(meta.get("format", "")).lower()
    return ".flac" if fmt == "flac" else ".mp3"


def convert_file(src_path):
    """转换单个文件，返回 (状态, 目标路径)。状态为 ok / skip。"""
    base = src_path[: -len(".ncm")]
    tmp_path = base + TMP_SUFFIX
    try:
        meta = _decode_to(src_path, tmp_path)
        if os.path.getsize(tmp_path) == 0:
            raise NcmError("解密结果为空")
        dst_path = base + _detect_ext(tmp_path, meta)
        if os.path.exists(dst_path):
            return "skip", dst_path
        os.replace(tmp_path, dst_path)
        os.remove(src_path)
        return "ok", dst_path
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def collect(target):
    if os.path.isfile(target):
        return [target] if target.lower().endswith(".ncm") else []
    found = []
    for root, dirs, files in os.walk(target):
        dirs.sort()
        for name in sorted(files):
            if name.lower().endswith(".ncm"):
                found.append(os.path.join(root, name))
    return found


def main(argv):
    no_pause = "--no-pause" in argv
    targets = [a for a in argv if not a.startswith("--")]

    if not targets:
        print("把包含 .ncm 的文件夹（或单个 .ncm 文件）拖进这个窗口，然后回车。")
        raw = input("路径: ").strip().strip('"')
        if not raw:
            return 1
        targets = [raw]

    files = []
    for target in targets:
        if not os.path.exists(target):
            print("[跳过] 路径不存在：%s" % target)
            continue
        files.extend(collect(target))

    if not files:
        print("没有找到任何 .ncm 文件。")
        return 1

    total = len(files)
    print("共找到 %d 个 .ncm 文件，开始转换……\n" % total)
    ok = skipped = failed = 0
    for index, path in enumerate(files, 1):
        name = os.path.basename(path)
        try:
            status, dst_path = convert_file(path)
        except Exception as exc:  # 单个文件出错不影响其余文件
            failed += 1
            print("[%d/%d] 失败   %s   (%s)" % (index, total, name, exc))
            continue
        if status == "skip":
            skipped += 1
            print("[%d/%d] 已存在，跳过   %s" % (index, total, os.path.basename(dst_path)))
        else:
            ok += 1
            print("[%d/%d] 完成   %s" % (index, total, os.path.basename(dst_path)))

    print("\n全部结束：成功 %d 个，跳过 %d 个，失败 %d 个。" % (ok, skipped, failed))
    if skipped:
        print("被跳过的文件因为目标文件已存在，原 .ncm 已保留。")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    try:
        code = main(sys.argv[1:])
    except KeyboardInterrupt:
        print("\n已中断。")
        code = 1
    if "--no-pause" not in sys.argv:
        try:
            input("\n按回车键退出……")
        except (EOFError, KeyboardInterrupt):
            pass
    sys.exit(code)
