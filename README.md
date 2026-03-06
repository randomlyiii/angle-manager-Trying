# ADB模拟器自动连接工具

自动启动MuMu模拟器并建立ADB连接的简单工具。

## 功能

- 自动启动MuMu模拟器
- 自动连接ADB设备
- 自动隐藏模拟器管理器窗口
- 自动唤醒设备屏幕

## 安装依赖

```bash
pip install -r requirements.txt
```

或运行：
```bash
DependencySetup_依赖库安装.bat
```

## 配置

编辑 `config/adb_config.json` 文件：

```json
{
  "adb_path": "E:\\MuMuPlayer-12.0\\shell\\adb.exe",
  "mumu_path": "E:\\MuMuPlayer-12.0\\nx_device\\12.0\\shell\\MuMuNxDevice.exe",
  "mumu_index": 0,
  "connection_timeout": 30
}
```

- `adb_path`: ADB工具路径
- `mumu_path`: MuMu模拟器启动程序路径
- `mumu_index`: 模拟器索引（0表示第一个模拟器）
- `connection_timeout`: 连接超时时间（秒）

## 运行

```bash
python Python/main.py
```

## 项目结构

```
├── Python/
│   ├── main.py              # 主程序入口
│   └── adb/
│       └── adb_controller.py # ADB控制器
├── config/
│   └── adb_config.json      # ADB配置文件
└── requirements.txt         # Python依赖
```
