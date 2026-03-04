# 自动化测试工具

基于Python的ADB自动化测试框架，支持MuMu模拟器连接、图像识别和自动化任务执行。

## 项目结构

```
项目根目录
├── cache/          # 缓存目录，存放临时截图、识别缓存
├── config/         # 配置目录，存放ADB连接参数、识图模板配置、任务规则配置
├── data/           # 数据目录，存放任务运行日志、操作记录
├── debug/          # 调试目录，存放调试日志、截图对比文件
├── externals/      # 外部依赖目录，存放ADB工具包
├── Python/         # Python核心源码目录
│   ├── adb/        # ADB连接与设备操作模块
│   ├── ocr/        # 图像识别、模板匹配核心模块
│   ├── task/       # 自动化任务调度与执行模块
│   └── main.py     # 项目主程序入口
├── resource/       # 资源目录，存放识图模板图片
├── requirements.txt
├── DependencySetup_依赖库安装.bat
└── README.md
```

## 快速开始

### 1. 安装依赖

运行依赖安装脚本：
```bash
DependencySetup_依赖库安装.bat
```

或手动安装：
```bash
pip install -r requirements.txt
```

### 2. 配置ADB

1. 下载Android Platform Tools: https://developer.android.com/tools/releases/platform-tools
2. 解压到 `externals/adb/` 目录
3. 修改 `config/adb_config.json` 配置设备信息

### 3. 准备模板图片

将需要识别的按钮、图标等截图放入 `resource/templates/` 目录

### 4. 配置任务

编辑 `config/task_config.json` 配置自动化任务流程

### 5. 运行程序

```bash
python Python/main.py
```

## 配置说明

### ADB配置 (config/adb_config.json)

```json
{
  "device_name": "emulator-5554",  // 设备名称，通过adb devices查看
  "adb_path": "externals/adb/adb.exe",  // ADB工具路径
  "connection_timeout": 30,  // 连接超时时间
  "retry_times": 3,  // 重试次数
  "screenshot_path": "cache/screenshot.png"  // 截图保存路径
}
```

### 任务配置 (config/task_config.json)

```json
{
  "task_interval": 1.0,  // 任务间隔时间
  "max_retry": 3,  // 最大重试次数
  "click_delay": 0.5,  // 点击延迟
  "tasks": [
    {
      "name": "示例任务",
      "enabled": true,
      "steps": [
        {
          "action": "find_and_click",  // 查找并点击
          "template": "button_example.png",  // 模板图片名称
          "timeout": 10  // 超时时间
        }
      ]
    }
  ]
}
```

## 支持的操作

- `find_and_click`: 查找模板并点击
- `wait`: 等待指定时间
- `screenshot`: 截取屏幕

## 注意事项

1. 确保MuMu模拟器已启动并开启ADB调试
2. 模板图片建议使用PNG格式，尺寸不宜过大
3. 识别阈值可在 `config/ocr_config.json` 中调整
4. 日志文件保存在 `data/` 目录下

## 常见问题

### 无法连接设备

1. 检查模拟器是否启动
2. 运行 `adb devices` 查看设备列表
3. 确认 `config/adb_config.json` 中的设备名称正确

### 识别不到模板

1. 检查模板图片是否清晰
2. 降低识别阈值 (ocr_config.json中的template_match_threshold)
3. 查看 `debug/` 目录下的调试图片

## 许可证

MIT License
