# MAA 项目架构参考文档

> 本文档基于 Maa-Project_Completed 项目分析，为 adb-automation-framework 提供架构设计参考

## 文档概述

本文档记录了 MAA (MaaAssistantArknights) 项目的整体架构、目录结构、配置管理策略和关键设计模式，作为 adb-automation-framework 项目开发的参考依据。

---

## 1. 项目整体架构

### 1.1 核心组件

MAA 项目采用模块化架构，主要包含以下核心组件：

```
MAA 核心架构
├── MaaCore.dll          # 核心逻辑库（图像识别、任务调度）
├── MaaUtils.dll         # 工具库（日志、配置管理）
├── MaaWin32ControlUnit.dll  # Windows 控制单元（输入模拟）
├── MAA.exe              # GUI 主程序
└── Python API           # Python 接口封装
```

### 1.2 技术栈

- **图像识别**: OpenCV (opencv_world4_maa.dll)
- **OCR**: PaddleOCR + FastDeploy (fastdeploy_ppocr_maa.dll)
- **深度学习**: ONNX Runtime (onnxruntime_maa.dll)
- **GUI**: WPF (.NET)
- **控制方式**: ADB + Minitouch/Maatouch
- **日志**: Serilog

---

## 2. 目录结构设计

### 2.1 标准目录布局

```
项目根目录/
├── cache/              # 缓存目录（动态数据）
│   ├── avatars/        # 头像缓存
│   ├── gui/            # GUI 相关缓存
│   ├── resource/       # 资源增量更新缓存
│   ├── version/        # 版本信息缓存
│   ├── etag.json       # HTTP ETag 缓存
│   └── last_modified.json  # 资源最后修改时间
│
├── config/             # 配置目录（用户配置）
│   ├── gui.json        # 主配置文件
│   ├── gui.json.bak    # 配置备份
│   └── backup/         # 历史配置备份
│
├── data/               # 数据目录（持久化数据）
│   ├── Achievement.json    # 成就数据
│   └── DepotData.json      # 仓库数据
│
├── debug/              # 调试目录（日志和截图）
│   ├── asst.log        # 核心日志
│   ├── gui.log         # GUI 日志
│   ├── drops/          # 掉落识别截图
│   ├── infrast/        # 基建识别截图
│   ├── interface/      # 界面识别截图
│   └── [其他分类]/     # 按功能分类的调试截图
│
├── externals/          # 外部依赖库
│   └── [第三方 DLL]
│
├── resource/           # 资源目录（只读资源）
│   ├── global/         # 多服务器资源
│   ├── platform_diff/  # 平台差异资源
│   ├── tasks/          # 任务定义
│   ├── template/       # 图像模板
│   ├── minitouch/      # Minitouch 二进制
│   ├── PaddleOCR/      # OCR 模型
│   ├── onnx/           # ONNX 模型
│   ├── config.json     # 资源配置
│   ├── stages.json     # 关卡数据
│   ├── recruitment.json # 公招数据
│   └── version.json    # 资源版本
│
└── Python/             # Python API
    ├── asst/           # Python 包
    └── sample.py       # 示例代码
```

### 2.2 目录设计原则

1. **职责分离**: 配置、数据、缓存、日志分离
2. **可清理性**: cache/ 和 debug/ 可安全删除
3. **备份机制**: 关键配置自动备份（.bak, .old）
4. **分类组织**: 调试文件按功能分类存储
5. **增量更新**: 支持资源增量更新（cache/resource/）

---

## 3. 配置管理系统

### 3.1 配置文件架构

MAA 采用分层配置架构：

```
配置层次
├── 全局配置 (Global)          # 跨配置共享
│   ├── GUI 设置
│   ├── 热键设置
│   └── 定时器设置
│
└── 配置方案 (Configurations)  # 多配置支持
    ├── Default              # 默认配置
    ├── [自定义配置1]
    └── [自定义配置2]
```

### 3.2 配置文件格式 (gui.json)

```json
{
  "Configurations": {
    "Default": {
      "Connect.AdbPath": "路径",
      "Connect.Address": "127.0.0.1:16384",
      "Connect.ConnectConfig": "MuMuEmulator12",
      "Connect.TouchMode": "maatouch",
      "Start.ClientType": "Bilibili",
      // ... 其他配置项
    }
  },
  "Current": "Default",  // 当前激活的配置
  "Global": {
    "GUI.Localization": "zh-cn",
    "GUI.UseTray": "True",
    // ... 全局配置项
  }
}
```

### 3.3 配置命名规范

采用分层命名法：`模块.子模块.配置项`

示例：
- `Connect.AdbPath` - 连接模块的 ADB 路径
- `Start.ClientType` - 启动模块的客户端类型
- `Roguelike.DeploymentWithPause` - 肉鸽模块的暂停部署

### 3.4 配置迁移机制

- 自动检测配置版本
- 向后兼容旧配置
- 自动迁移到新格式
- 保留旧配置备份（.old）

---

## 4. 连接配置系统

### 4.1 连接配置架构 (resource/config.json)

MAA 支持多种模拟器和连接方式，通过配置继承实现：

```json
{
  "connection": [
    {
      "configName": "General",  // 基础配置
      "devices": "[Adb] devices",
      "connect": "[Adb] connect [AdbSerial]",
      "screencapRawWithGzip": "[Adb] -s [AdbSerial] exec-out \"screencap | gzip -1\"",
      "click": "[Adb] -s [AdbSerial] shell input tap [x] [y]",
      // ... 其他命令模板
    },
    {
      "configName": "MuMuEmulator12",  // 继承基础配置
      "baseConfig": "General",
      "orientation": "[Adb] -s [AdbSerial] shell \"dumpsys input | grep SurfaceOrientation | tail -n 1 | grep -m 1 -o -E [0-9]\""
    },
    {
      "configName": "BlueStacks",
      "baseConfig": "General"
    }
    // ... 其他模拟器配置
  ]
}
```

### 4.2 命令模板系统

使用占位符实现命令模板化：

- `[Adb]` - ADB 可执行文件路径
- `[AdbSerial]` - 设备序列号
- `[x]`, `[y]` - 坐标参数
- `[PackageName]` - 应用包名
- `[NcAddress]`, `[NcPort]` - Netcat 参数

### 4.3 截图方式优先级

1. **screencapRawByNC** - 通过 Netcat 传输原始数据（最快）
2. **screencapRawWithGzip** - Gzip 压缩传输（平衡）
3. **screencapEncode** - PNG 编码传输（兼容性最好）

---

## 5. 缓存管理策略

### 5.1 ETag 缓存机制 (cache/etag.json)

```json
{
  "https://api.maa.plus/.../tasks.json": "\"69a2a060-a55\"",
  "https://api.maa.plus/.../StageActivity.json": "\"6932d2c9-5147\""
}
```

**工作原理**:
1. 请求资源时携带 ETag
2. 服务器返回 304 Not Modified 则使用缓存
3. 返回 200 则更新缓存和 ETag

### 5.2 资源版本管理 (resource/version.json)

```json
{
  "activity": {
    "name": "矢量突破#2 巫术之夜",
    "time": 1771920000  // Unix 时间戳
  },
  "gacha": {
    "pool": "劫尽古今",
    "time": 1770678000
  },
  "last_updated": "2026-03-03 08:33:20.000"
}
```

### 5.3 增量资源更新

```
主资源 (resource/)
  ↓ 加载
增量资源 (cache/resource/)
  ↓ 覆盖
最终资源
```

支持场景：
- 活动关卡数据更新
- 外服资源增量
- 临时修复补丁

---

## 6. 日志和调试系统

### 6.1 日志分级

```
[TRC] Trace   - 详细跟踪信息（模板匹配分数）
[DBG] Debug   - 调试信息
[INF] Info    - 一般信息
[WRN] Warning - 警告
[ERR] Error   - 错误
[FTL] Fatal   - 致命错误
```

### 6.2 日志格式

```
[时间][级别][进程ID][线程ID] 消息内容
[2026-03-04 10:14:25.162][TRC][Px3148][Tx2510] match_templ | Bskill_man_exp3.png score: 0.892383
```

### 6.3 调试截图分类

```
debug/
├── drops/      # 掉落识别
├── infrast/    # 基建识别
├── interface/  # 界面识别
├── map/        # 地图识别
├── recruit/    # 公招识别
├── roguelike/  # 肉鸽识别
└── other/      # 其他
```

**命名规范**: `YYYY.MM.DD-HH.MM.SS.mmm_raw.png`

### 6.4 日志轮转

- `asst.log` - 当前日志
- `asst.bak.log` - 上一次日志
- 自动清理旧日志

---

## 7. Python API 设计

### 7.1 API 架构

```python
from asst.asst import Asst
from asst.emulator import Bluestacks
from asst.updater import Updater

# 资源加载
Asst.load(path=path)
Asst.load(path=path, incremental_path=incremental_path)

# 实例创建
asst = Asst(callback=my_callback)

# 任务执行
asst.append_task('StartUp')
asst.start()
```

### 7.2 回调机制

```python
@Asst.CallBackType
def my_callback(msg, details, arg):
    m = Message(msg)
    d = json.loads(details.decode("utf-8"))
    # 处理消息
```

### 7.3 增量资源加载

支持两种增量资源场景：
1. **外服资源**: 加载 `resource/global/YoStarEN`
2. **活动资源**: 加载 `cache/resource/tasks.json`

---

## 8. 资源组织模式

### 8.1 任务定义 (resource/tasks/)

按功能模块组织任务定义文件：
- `StartUp.json` - 启动任务
- `Fight.json` - 战斗任务
- `Infrast.json` - 基建任务
- `Recruit.json` - 公招任务
- `Roguelike.json` - 肉鸽任务

### 8.2 图像模板 (resource/template/)

按识别对象分类：
- 界面元素模板
- 按钮模板
- 图标模板
- OCR 辅助模板

### 8.3 多服务器支持

```
resource/
├── [基础资源]
└── global/
    ├── YoStarEN/   # 英服
    ├── YoStarJP/   # 日服
    └── YoStarKR/   # 韩服
```

---

## 9. 关键设计模式

### 9.1 配置继承模式

```json
{
  "configName": "MuMuEmulator12",
  "baseConfig": "General",
  // 只覆盖需要修改的配置
}
```

**优点**:
- 减少重复配置
- 便于维护
- 支持配置复用

### 9.2 命令模板模式

```json
{
  "click": "[Adb] -s [AdbSerial] shell input tap [x] [y]"
}
```

**优点**:
- 统一命令格式
- 支持参数替换
- 便于扩展新设备

### 9.3 增量更新模式

```
基础资源 + 增量资源 = 最终资源
```

**优点**:
- 减少下载量
- 支持快速修复
- 多服务器支持

### 9.4 分层配置模式

```
Global (全局) + Configuration (方案) = 最终配置
```

**优点**:
- 多配置切换
- 共享全局设置
- 配置隔离

---

## 10. 性能优化策略

### 10.1 截图优化

```json
{
  "taskDelay": 500,  // 识别延迟（毫秒）
  "SSSFightScreencapInterval": 0,      // 保全战斗截图间隔
  "RoguelikeFightScreencapInterval": 100,  // 肉鸽战斗截图间隔
  "CopilotFightScreencapInterval": 0   // 抄作业战斗截图间隔
}
```

### 10.2 控制延迟

```json
{
  "controlDelayRange": [0, 0],  // 点击随机延时 [最小, 最大]
  "adbSwipeDurationMultiplier": 10.0,  // 滑动延迟倍数
  "adbSwipeXDistanceMultiplier": 0.8   // 滑动距离倍数
}
```

### 10.3 缓存策略

- HTTP ETag 缓存
- 图像模板缓存
- OCR 结果缓存
- 配置文件缓存

---

## 11. 错误处理和容错

### 11.1 配置备份

- 自动创建 `.bak` 备份
- 保留 `.old` 历史版本
- 配置迁移失败回滚

### 11.2 日志记录

- 多级别日志
- 进程/线程信息
- 调试截图保存
- 日志文件轮转

### 11.3 连接重试

```json
{
  "Connect.RetryOnDisconnected": "True",
  "Connect.AllowADBRestart": "True",
  "Connect.AllowADBHardRestart": "True"
}
```

---

## 12. 扩展性设计

### 12.1 模拟器支持扩展

通过添加新的连接配置支持新模拟器：

```json
{
  "configName": "NewEmulator",
  "baseConfig": "General",
  // 覆盖特定命令
}
```

### 12.2 多服务器支持

通过增量资源支持新服务器：

```
resource/global/NewServer/
├── tasks/
├── template/
└── config.json
```

### 12.3 插件化架构

- Python API 封装
- 回调机制
- 任务链扩展

---

## 13. 安全性考虑

### 13.1 配置安全

- 敏感信息加密存储
- 配置文件权限控制
- 备份文件管理

### 13.2 连接安全

- ADB 连接验证
- 设备 UUID 识别
- 连接超时控制

### 13.3 数据上报

```json
{
  "penguinReport": {
    "url": "https://penguin-stats.io/PenguinStats/api/v2/report"
  },
  "yituliuReport": {
    "recruitUrl": "https://backend.yituliu.cn/maa/upload/recruit"
  }
}
```

---

## 14. 对 adb-automation-framework 的建议

### 14.1 架构建议

1. **采用模块化设计**: 核心库 + 工具库 + 控制单元
2. **分离配置和数据**: 参考 MAA 的目录结构
3. **实现配置继承**: 减少重复配置
4. **支持增量更新**: 便于快速修复和扩展

### 14.2 配置管理建议

1. **分层配置**: Global + Configurations
2. **命名规范**: 模块.子模块.配置项
3. **自动备份**: .bak 和 .old 机制
4. **配置迁移**: 版本兼容性处理

### 14.3 日志系统建议

1. **分级日志**: TRC/DBG/INF/WRN/ERR/FTL
2. **结构化日志**: 时间/级别/进程/线程
3. **调试截图**: 按功能分类存储
4. **日志轮转**: 自动清理旧日志

### 14.4 缓存策略建议

1. **HTTP 缓存**: ETag + Last-Modified
2. **可清理设计**: cache/ 目录可安全删除
3. **增量更新**: 支持资源增量加载

### 14.5 扩展性建议

1. **配置继承**: baseConfig 机制
2. **命令模板**: 占位符替换
3. **插件化**: Python API 封装
4. **多平台支持**: 平台差异资源

---

## 15. 参考资源

### 15.1 关键文件

- `config/gui.json` - 主配置文件
- `resource/config.json` - 连接配置
- `cache/etag.json` - 缓存管理
- `resource/version.json` - 版本信息
- `Python/sample.py` - API 示例

### 15.2 核心目录

- `cache/` - 缓存和临时文件
- `config/` - 用户配置
- `debug/` - 日志和调试截图
- `resource/` - 只读资源
- `externals/` - 第三方依赖

---

## 附录：配置项速查表

### A.1 连接配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| Connect.AdbPath | ADB 路径 | `E:\MuMu\adb.exe` |
| Connect.Address | 连接地址 | `127.0.0.1:16384` |
| Connect.ConnectConfig | 连接配置名 | `MuMuEmulator12` |
| Connect.TouchMode | 触控模式 | `maatouch` |

### A.2 启动配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| Start.ClientType | 客户端类型 | `Bilibili` |
| Start.StartGame | 是否启动游戏 | `True` |
| Start.EmulatorPath | 模拟器路径 | `E:\MuMu\MuMuNxDevice.exe` |

### A.3 性能配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| taskDelay | 识别延迟（毫秒） | 500 |
| controlDelayRange | 点击延时范围 | [0, 0] |
| adbSwipeDurationMultiplier | 滑动延迟倍数 | 10.0 |

---

**文档版本**: 1.0  
**创建日期**: 2026-03-04  
**基于项目**: Maa-Project_Completed  
**目标项目**: adb-automation-framework
