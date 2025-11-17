# 打包说明

## 方法一：使用批处理脚本（推荐）

双击运行 `build.bat` 即可自动打包。

## 方法二：手动打包

### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

### 2. 执行打包命令

```bash
pyinstaller --onefile --windowed --name=MySQLExporter main.py
```

### 3. 找到生成的 EXE

打包完成后，可执行文件位于：
```
dist\MySQLExporter.exe
```

## 打包参数说明

- `--onefile`: 打包成单个 EXE 文件
- `--windowed`: 不显示控制台窗口（GUI 程序）
- `--name`: 指定输出的 EXE 文件名
- `--add-data`: 添加额外文件（如 README）
- `--hidden-import`: 确保某些模块被正确打包

## 注意事项

1. 打包后的 EXE 文件较大（约 100-150MB），这是正常现象
2. 首次运行可能需要几秒钟加载
3. 配置文件 `dby_config.json` 会在 EXE 所在目录创建（隐藏文件）
4. 打包后的程序可以在其他 Windows 电脑上直接运行，无需安装 Python

## 缩小 EXE 体积（可选）

如果需要缩小体积，可以使用 UPX 压缩：

```bash
# 安装 UPX
# 下载：https://github.com/upx/upx/releases

pyinstaller --onefile --windowed --name=MySQLExporter --upx-dir=<UPX路径> main.py
```

## 测试打包后的程序

1. 进入 `dist` 目录
2. 双击运行 `MySQLExporter.exe`
3. 测试所有功能是否正常
