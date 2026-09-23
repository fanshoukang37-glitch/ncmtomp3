# NCM to MP3 / FLAC

[中文说明](#中文说明) | [English](#english)

批量把网易云音乐的 `.ncm` 加密文件还原成普通音频文件，支持递归扫描整个文件夹。

A batch converter that turns NetEase Cloud Music `.ncm` files back into ordinary
audio files, scanning the whole folder tree.

---

## 中文说明

### 简介

`ncm2mp3` 是一个把 `.ncm` 文件批量解密还原成普通音频的小工具。指定一个文件夹，
它会自动递归找出里面所有的 `.ncm`，逐个解密还原，输出到原文件所在位置。

### 特性

- **单文件 exe，免安装**：打包后是一个独立 exe，目标机器不需要装 Python 或任何依赖。
- **递归扫描**：文件夹、多层子文件夹都能一次处理完。
- **自动识别真实格式**：靠解密后的文件头判断，是 mp3 就输出 `.mp3`，是 flac 无损就输出 `.flac`，不会出现扩展名和内容对不上的情况。
- **单个文件出错不影响其余**：某个文件损坏或格式异常只会报错并跳过，其余文件继续处理。
- **不覆盖已有文件**：如果目标文件已存在，会跳过该文件并**保留**原 `.ncm`，不会误删或覆盖。
- **只在成功后删除**：原 `.ncm` 仅在解密成功且文件写入完成后才删除。
- **结束时暂停**：双击或拖拽运行时会停在结果界面，窗口不会一闪而过。

### 使用方法

**方式一：拖拽运行（推荐）**

1. 把装着 `.ncm` 的文件夹直接拖到 `ncm2mp3.exe` 图标上松手；
2. 等它跑完，看最后的统计结果；
3. 按回车退出。

**方式二：双击运行**

1. 双击 `ncm2mp3.exe`；
2. 把文件夹路径（或单个 `.ncm` 文件）拖进窗口，回车；
3. 也可以手动输入路径，路径带空格时可以用引号包起来。

**方式三：命令行**

```bat
ncm2mp3.exe "D:\Music\VipSongsDownload"
ncm2mp3.exe "D:\Music\A" "D:\Music\B"          :: 一次传多个路径
ncm2mp3.exe "D:\Music" --no-pause               :: 处理完直接退出，不等待回车
```

命令行参数：

| 参数 | 说明 |
| --- | --- |
| `<路径>...` | 一个或多个文件夹 / `.ncm` 文件。不给参数则进入交互式输入。 |
| `--no-pause` | 结束后不等待回车，适合脚本或批处理里调用。 |

退出码：`0` 全部成功；`1` 没找到文件或被手动中断；`2` 有文件转换失败。

### 输出说明

假设原文件是 `D:\Music\某首歌.ncm`：

- 内容实际是 mp3 → 生成 `D:\Music\某首歌.mp3`
- 内容实际是 flac → 生成 `D:\Music\某首歌.flac`
- 生成成功后，原 `D:\Music\某首歌.ncm` 被删除
- 如果 `D:\Music\某首歌.mp3` 已经存在，则跳过，原 `.ncm` **保留**

转换过程中的临时文件以 `.ncm_tmp` 结尾，正常结束时不会残留。

### 从源码构建

需要 Python 3.8 或更高版本。

```bash
pip install pycryptodome pyinstaller
pyinstaller --onefile --console --name ncm2mp3 ncm2mp3.py
```

生成的可执行文件在 `dist/ncm2mp3.exe`。

不打包也可以直接跑：

```bash
python ncm2mp3.py "D:\Music"
```

### 工作原理

`.ncm` 是网易云音乐客户端在本地保存的加密容器，结构大致为：

1. 文件头 magic `CTENFDAM`；
2. 一段被异或混淆后再经 AES-128-ECB 加密的密钥，解密后用来构造一个 RC4 风格的密钥盒；
3. 元信息块（曲名、歌手、专辑、真实格式等），同样是异或 + Base64 + AES；
4. 专辑封面图；
5. 音频数据本体，逐字节与密钥盒生成的密钥流异或还原。

本工具按上述结构逐块还原，不重新编码音频，因此**没有二次音质损失**——
原来是什么码率，出来就还是什么码率。

### 免责声明

本项目是一个纯粹的文件格式转换工具，**不提供、不存储、不内置、不分发任何音频内容**。

**使用范围**

- 仅限处理你自己合法获取的音乐文件（自行购买、已开通会员，或已获得权利人授权）。
- 转换结果**仅供个人学习、研究与本地备份**使用，不得用于任何形式的商业用途。
- 不得将转换后的音频上传、分享或传播到任何平台，也不得用于公开演出、直播、
  混音、二次创作发布等场景。
- 不得用于规避版权方的付费与授权机制，或实施任何侵犯著作权及相关权利的行为。

**非商业使用声明**

本项目**明确禁止商业使用**。任何以营利为目的的使用——包括但不限于销售本工具或
其衍生版本、提供付费转换服务、将其捆绑进商业产品、或借本项目引流变现——均未获得
授权，作者保留追究相关责任的权利。

**责任限制**

- 本工具按「现状」提供，不附带任何明示或默示的担保，包括但不限于适销性、特定
  用途适用性及不侵权担保。
- 使用本工具产生的全部风险由使用者自行承担。因使用或无法使用本工具而导致的任何
  数据丢失、文件损坏、设备故障、法律纠纷或其他损失，作者概不负责。
- 使用者应自行确认其使用行为符合所在国家 / 地区的法律法规。因使用者违规使用而
  引发的一切法律责任，由使用者本人独立承担。

**请支持正版**：如果你喜欢这些音乐，请在正规平台购买或续费会员，让创作者获得应有
的回报。

---

## English

### What it is

`ncm2mp3` batch-decrypts NetEase Cloud Music `.ncm` files into ordinary audio
files. Point it at a folder and it recursively finds every `.ncm` inside,
decrypts each one, and writes the result next to the original.

### Features

- **Single-file exe, no install**: the packaged build is one standalone
  executable. No Python or third-party dependency needed on the target machine.
- **Recursive scan**: handles a folder, or any number of nested subfolders, in
  one run.
- **Real format detection**: the output extension comes from the decrypted
  file header, so an mp3 payload becomes `.mp3` and a lossless flac payload
  becomes `.flac`. The extension always matches the content.
- **Per-file error isolation**: a corrupt or unexpected file is reported and
  skipped; every other file still gets processed.
- **Never overwrites**: if the target file already exists, that file is skipped
  and its `.ncm` source is **kept** untouched.
- **Deletes only after success**: the original `.ncm` is removed only once
  decryption and writing have both completed.
- **Pauses when done**: when launched by double-click or drag-and-drop, the
  window stays open so you can read the summary.

### Usage

**Option 1: drag and drop (recommended)**

1. Drag the folder containing your `.ncm` files onto `ncm2mp3.exe`.
2. Wait for the summary.
3. Press Enter to exit.

**Option 2: double-click**

1. Double-click `ncm2mp3.exe`.
2. Drag a folder path (or a single `.ncm` file) into the window and press Enter.
3. You can also type the path manually; quote it if it contains spaces.

**Option 3: command line**

```bat
ncm2mp3.exe "D:\Music\VipSongsDownload"
ncm2mp3.exe "D:\Music\A" "D:\Music\B"          :: multiple paths at once
ncm2mp3.exe "D:\Music" --no-pause               :: exit without waiting for Enter
```

Arguments:

| Argument | Description |
| --- | --- |
| `<path>...` | One or more folders or `.ncm` files. With no argument, an interactive prompt is shown. |
| `--no-pause` | Do not wait for Enter at the end. Useful for scripts and batch files. |

Exit codes: `0` all succeeded; `1` nothing found or interrupted; `2` at least
one file failed.

### Output

Given a source file `D:\Music\song.ncm`:

- mp3 payload → produces `D:\Music\song.mp3`
- flac payload → produces `D:\Music\song.flac`
- on success, the original `D:\Music\song.ncm` is deleted
- if `D:\Music\song.mp3` already exists, the file is skipped and the `.ncm`
  is **kept**

Temporary files end with `.ncm_tmp` and are always cleaned up.

### Building from source

Requires Python 3.8 or newer.

```bash
pip install pycryptodome pyinstaller
pyinstaller --onefile --console --name ncm2mp3 ncm2mp3.py
```

The executable is written to `dist/ncm2mp3.exe`.

You can also run it directly without packaging:

```bash
python ncm2mp3.py "D:\Music"
```

### How it works

`.ncm` is the encrypted container the NetEase Cloud Music client stores locally.
Roughly, its layout is:

1. An 8-byte magic header, `CTENFDAM`.
2. An AES-128-ECB encrypted, XOR-obfuscated key. Once decrypted it is used to
   build an RC4-style key box.
3. A metadata block (title, artist, album, real format, ...), also
   XOR + Base64 + AES.
4. The embedded album cover image.
5. The audio payload itself, restored by XORing it with the keystream produced
   from the key box.

This tool reverses that structure block by block. It never re-encodes the
audio, so there is **no generation loss** — the output has exactly the same
bitrate as the source.

### Disclaimer

This project is a plain file-format conversion tool. It does **not** provide,
host, bundle, or distribute any audio content.

**Permitted scope**

- Use it only on music files you have legally obtained (purchased yourself,
  downloaded through your own paid subscription, or otherwise properly
  licensed).
- The converted output is intended **solely for personal study, research, and
  local backup**, and must not be used for any commercial purpose.
- Do not upload, share, or distribute the converted audio on any platform, and
  do not use it for public performance, live streaming, remixing, or
  republishing derivative works.
- Do not use this tool to circumvent a rights holder's paid access or licensing
  mechanisms, or to commit any act that infringes copyright or related rights.

**Non-commercial notice**

This project is **explicitly non-commercial**. Any for-profit use — including
but not limited to selling this tool or a derivative of it, offering a paid
conversion service, bundling it into a commercial product, or monetizing
traffic generated by this project — is not authorized. The author reserves all
rights to pursue such use.

**Limitation of liability**

- This software is provided "as is", without warranty of any kind, express or
  implied, including but not limited to the warranties of merchantability,
  fitness for a particular purpose, and non-infringement.
- You assume all risk arising from the use of this tool. The author is not
  liable for any data loss, file corruption, hardware failure, legal dispute,
  or other damage resulting from the use of, or inability to use, this
  software.
- You are responsible for confirming that your use complies with the laws and
  regulations of your jurisdiction. Any legal liability arising from your
  misuse of this tool rests with you alone.

**Please support the official release**: if you enjoy the music, buy it or keep
your subscription active on the legitimate platform so the creators are paid.
