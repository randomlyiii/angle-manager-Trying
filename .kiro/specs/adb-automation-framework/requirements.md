# 需求文档 - ADB 自动化测试框架

## 简介

ADB 自动化测试框架是一个基于 Python 开发的自动化测试工具，用于通过 ADB（Android Debug Bridge）连接和控制 MuMu 模拟器，执行图像识别、模板匹配和自动化任务。该框架提供图形化配置界面，支持游戏自动化测试、应用自动化操作和重复性任务自动执行。

## 术语表

- **ADB_Controller**: ADB 设备控制器，负责与 Android 设备/模拟器通信
- **Image_Matcher**: 图像匹配器，负责图像识别和模板匹配
- **Task_Executor**: 任务执行器，负责调度和执行自动化任务
- **Config_Manager**: 配置管理器，负责统一配置文件的读写
- **GUI_Window**: 图形用户界面窗口，提供可视化配置和控制
- **MuMu_Launcher**: MuMu 模拟器启动器，负责自动启动模拟器
- **ADB_Doctor**: ADB 诊断工具，负责诊断和修复连接问题
- **Config_Migrator**: 配置迁移工具，负责旧配置文件迁移
- **Template**: 模板图像，用于在屏幕截图中查找匹配的图像
- **Screenshot**: 屏幕截图，从设备捕获的当前屏幕图像
- **Task**: 任务，由多个步骤组成的自动化操作序列
- **Step**: 步骤，任务中的单个操作单元
- **Device**: 设备，指 Android 模拟器或真实设备
- **Port**: 端口，ADB 连接使用的网络端口号
- **Confidence**: 置信度，模板匹配的相似度分数（0-1）

## 需求

### 需求 1: ADB 设备连接管理

**用户故事:** 作为测试人员，我希望系统能够自动连接和管理 ADB 设备，以便我可以控制模拟器执行自动化操作。

#### 验收标准

1. THE ADB_Controller SHALL 通过指定的 IP 地址和端口连接到 Device
2. WHEN 连接失败时，THE ADB_Controller SHALL 重试连接最多配置的重试次数
3. WHEN 连接超时时，THE ADB_Controller SHALL 在配置的超时时间后终止连接尝试
4. THE ADB_Controller SHALL 验证 Device 连接状态并返回连接结果
5. WHEN Device 屏幕处于休眠状态时，THE ADB_Controller SHALL 唤醒 Device 屏幕
6. THE ADB_Controller SHALL 获取并返回 Device 的屏幕尺寸信息

### 需求 2: MuMu 模拟器自动启动

**用户故事:** 作为测试人员，我希望系统能够自动启动 MuMu 模拟器，以便我不需要手动启动模拟器。

#### 验收标准

1. WHEN 启用自动启动功能时，THE MuMu_Launcher SHALL 启动指定路径的 MuMu 模拟器
2. THE MuMu_Launcher SHALL 根据配置的端口号计算模拟器实例索引
3. THE MuMu_Launcher SHALL 等待模拟器端口开始监听，最长等待 120 秒
4. WHEN 模拟器已在运行时，THE MuMu_Launcher SHALL 跳过启动步骤并直接连接
5. THE MuMu_Launcher SHALL 在启动前结束所有冲突的 ADB 进程
6. WHEN 模拟器启动失败时，THE MuMu_Launcher SHALL 返回失败状态并记录错误信息

### 需求 3: 屏幕截图捕获

**用户故事:** 作为测试人员，我希望系统能够捕获设备屏幕截图，以便进行图像识别和分析。

#### 验收标准

1. THE ADB_Controller SHALL 从 Device 捕获当前屏幕图像
2. THE ADB_Controller SHALL 将 Screenshot 保存到配置的文件路径
3. WHEN 截图目录不存在时，THE ADB_Controller SHALL 创建必要的目录结构
4. THE ADB_Controller SHALL 在截图完成后验证文件是否成功创建
5. WHEN 截图失败时，THE ADB_Controller SHALL 返回失败状态

### 需求 4: 图像模板匹配

**用户故事:** 作为测试人员，我希望系统能够在屏幕截图中查找指定的模板图像，以便识别界面元素。

#### 验收标准

1. THE Image_Matcher SHALL 在 Screenshot 中查找指定的 Template
2. THE Image_Matcher SHALL 使用 OpenCV 的 TM_CCOEFF_NORMED 算法进行模板匹配
3. WHEN 匹配置信度大于或等于配置的阈值时，THE Image_Matcher SHALL 返回匹配成功结果
4. THE Image_Matcher SHALL 返回匹配位置的中心坐标、左上角坐标、尺寸和置信度
5. THE Image_Matcher SHALL 支持查找所有匹配的 Template 实例
6. THE Image_Matcher SHALL 支持保存带有匹配标记的调试图像

### 需求 5: 设备交互操作

**用户故事:** 作为测试人员，我希望系统能够模拟点击和滑动操作，以便自动控制设备界面。

#### 验收标准

1. THE ADB_Controller SHALL 在 Device 的指定坐标执行点击操作
2. THE ADB_Controller SHALL 在点击操作后等待配置的延迟时间
3. THE ADB_Controller SHALL 在 Device 上执行从起点到终点的滑动操作
4. THE ADB_Controller SHALL 支持配置滑动操作的持续时间
5. WHEN 操作执行失败时，THE ADB_Controller SHALL 返回失败状态

### 需求 6: 自动化任务执行

**用户故事:** 作为测试人员，我希望系统能够按照预定义的步骤执行自动化任务，以便完成复杂的测试流程。

#### 验收标准

1. THE Task_Executor SHALL 从配置文件加载任务定义
2. THE Task_Executor SHALL 按顺序执行任务中的每个 Step
3. THE Task_Executor SHALL 支持"查找并点击"、"等待"和"截图"三种步骤类型
4. WHEN 执行"查找并点击"步骤时，THE Task_Executor SHALL 重复截图和匹配直到找到 Template 或超时
5. WHEN 任务被禁用时，THE Task_Executor SHALL 跳过该任务
6. WHEN 步骤执行失败时，THE Task_Executor SHALL 终止当前任务并返回失败状态
7. THE Task_Executor SHALL 记录所有任务执行的详细日志

### 需求 7: 统一配置管理

**用户故事:** 作为测试人员，我希望所有配置集中在一个文件中，以便统一管理和维护。

#### 验收标准

1. THE Config_Manager SHALL 从 config.json 文件读取所有模块的配置
2. THE Config_Manager SHALL 支持 ADB、模拟器、OCR 和任务四个配置分组
3. WHEN 配置文件不存在时，THE Config_Manager SHALL 返回空配置对象
4. THE Config_Manager SHALL 使用 UTF-8 编码读写配置文件
5. THE Config_Manager SHALL 以 JSON 格式保存配置，缩进为 2 个空格

### 需求 8: 图形化配置界面

**用户故事:** 作为测试人员，我希望通过图形界面配置和控制程序，以便更方便地使用系统。

#### 验收标准

1. THE GUI_Window SHALL 提供 ADB 路径、MuMu 路径和连接端口的配置输入
2. THE GUI_Window SHALL 支持通过文件浏览对话框选择可执行文件路径
3. THE GUI_Window SHALL 提供保存配置、测试连接和 ADB 诊断三个功能按钮
4. THE GUI_Window SHALL 提供启动和停止程序的控制按钮
5. THE GUI_Window SHALL 在滚动文本区域实时显示运行日志
6. THE GUI_Window SHALL 在程序运行时锁定配置输入，防止修改
7. THE GUI_Window SHALL 显示当前程序运行状态（未运行、运行中、已完成、已停止、错误）
8. WHEN 用户点击启动按钮时，THE GUI_Window SHALL 验证必填配置项并在新线程中运行主程序
9. WHEN 用户点击停止按钮时，THE GUI_Window SHALL 设置停止标志并终止任务执行
10. WHEN 用户关闭窗口且程序正在运行时，THE GUI_Window SHALL 提示用户确认退出

### 需求 9: ADB 连接诊断和修复

**用户故事:** 作为测试人员，我希望系统能够自动诊断和修复 ADB 连接问题，以便快速解决连接故障。

#### 验收标准

1. THE ADB_Doctor SHALL 检测 MuMu 模拟器版本（6、9 或 12）
2. THE ADB_Doctor SHALL 根据模拟器版本确定默认 ADB 端口
3. THE ADB_Doctor SHALL 结束所有冲突的 ADB 进程
4. THE ADB_Doctor SHALL 检查目标端口的占用情况并显示占用进程信息
5. WHEN 具有管理员权限时，THE ADB_Doctor SHALL 检查并配置 Windows 防火墙规则
6. THE ADB_Doctor SHALL 查找并使用 MuMu 自带的 ADB 工具
7. THE ADB_Doctor SHALL 重启 ADB 服务（kill-server 和 start-server）
8. THE ADB_Doctor SHALL 尝试连接设备并验证连接状态
9. WHEN 诊断步骤失败时，THE ADB_Doctor SHALL 提供可能的原因和解决方案
10. THE ADB_Doctor SHALL 通过回调函数输出诊断过程的详细日志

### 需求 11: 日志记录系统

**用户故事:** 作为测试人员，我希望系统记录详细的运行日志，以便追踪问题和分析执行过程。

#### 验收标准

1. THE Task_Executor SHALL 将日志同时输出到文件和控制台
2. THE Task_Executor SHALL 使用日期命名日志文件（格式：task_YYYYMMDD.log）
3. THE Task_Executor SHALL 将日志文件保存到 data 目录
4. THE Task_Executor SHALL 记录任务开始、步骤执行、成功、失败和完成事件
5. THE Task_Executor SHALL 在日志中包含时间戳、日志级别和消息内容
6. THE Task_Executor SHALL 使用 UTF-8 编码写入日志文件

### 需求 12: 错误处理和重试机制

**用户故事:** 作为测试人员，我希望系统能够处理临时错误并自动重试，以便提高测试的稳定性。

#### 验收标准

1. WHEN ADB 命令执行超时时，THE ADB_Controller SHALL 在配置的超时时间后终止命令
2. WHEN 连接失败时，THE ADB_Controller SHALL 重试最多配置的重试次数
3. WHEN 截图失败时，THE Task_Executor SHALL 等待后重试
4. WHEN 模板匹配失败时，THE Task_Executor SHALL 在超时前持续重试
5. WHEN 步骤执行失败且未达到最大重试次数时，THE Task_Executor SHALL 等待后重试
6. WHEN 异常发生时，THE System SHALL 捕获异常、记录错误信息并返回失败状态

### 需求 13: 配置验证

**用户故事:** 作为测试人员，我希望系统能够验证配置的有效性，以便在启动前发现配置错误。

#### 验收标准

1. WHEN 用户启动程序时，THE GUI_Window SHALL 验证 ADB 路径、MuMu 路径和端口号是否已配置
2. THE GUI_Window SHALL 验证端口号是否为 1024-65535 范围内的有效整数
3. THE GUI_Window SHALL 验证 ADB 工具和 MuMu 模拟器文件是否存在
4. WHEN 配置验证失败时，THE GUI_Window SHALL 显示错误消息并阻止程序启动
5. WHEN 配置验证成功时，THE GUI_Window SHALL 自动保存配置并启动程序

### 需求 14: 多实例支持

**用户故事:** 作为测试人员，我希望系统能够连接不同的 MuMu 模拟器实例，以便同时测试多个环境。

#### 验收标准

1. THE System SHALL 支持通过端口号区分不同的模拟器实例
2. THE MuMu_Launcher SHALL 根据端口号计算模拟器索引（公式：(端口 - 16384) / 32）
3. THE ADB_Controller SHALL 支持通过设备名称指定连接的特定设备
4. WHEN 配置了设备名称时，THE ADB_Controller SHALL 在所有 ADB 命令中使用 -s 参数指定设备

### 需求 15: 模板管理

**用户故事:** 作为测试人员，我希望系统能够从指定目录加载模板图像，以便组织和管理测试资源。

#### 验收标准

1. THE Image_Matcher SHALL 从配置的模板目录加载 Template 文件
2. THE Image_Matcher SHALL 支持 PNG、JPG 等常见图像格式
3. WHEN Template 文件不存在时，THE Image_Matcher SHALL 返回 None 并记录警告
4. THE Image_Matcher SHALL 使用相对于模板目录的文件名引用 Template

### 需求 16: 调试支持

**用户故事:** 作为开发人员，我希望系统能够保存调试信息，以便分析匹配失败的原因。

#### 验收标准

1. THE Image_Matcher SHALL 支持保存带有匹配标记的调试图像
2. THE Image_Matcher SHALL 在调试图像上绘制匹配区域的矩形框
3. THE Image_Matcher SHALL 在调试图像上标记匹配位置的中心点
4. THE Image_Matcher SHALL 将调试图像保存到 debug 目录
5. WHEN 调试目录不存在时，THE Image_Matcher SHALL 创建必要的目录结构

### 需求 17: 线程安全

**用户故事:** 作为开发人员，我希望 GUI 操作不会阻塞主线程，以便界面保持响应。

#### 验收标准

1. THE GUI_Window SHALL 在独立线程中执行主程序逻辑
2. THE GUI_Window SHALL 使用 daemon 线程避免阻止程序退出
3. THE GUI_Window SHALL 使用 root.after 方法从工作线程更新 UI 组件
4. THE GUI_Window SHALL 使用停止标志（stop_flag）实现线程间通信
5. THE GUI_Window SHALL 在程序运行时禁用启动按钮，防止重复启动

### 需求 18: 资源清理

**用户故事:** 作为系统管理员，我希望程序能够正确清理资源，以便避免资源泄漏。

#### 验收标准

1. WHEN 程序终止时，THE System SHALL 停止所有正在执行的任务
2. WHEN 用户关闭窗口时，THE GUI_Window SHALL 检查程序运行状态并提示确认
3. THE ADB_Controller SHALL 在命令执行超时时终止子进程
4. THE System SHALL 确保临时文件和缓存文件被正确创建和管理

### 需求 19: 跨平台兼容性

**用户故事:** 作为开发人员，我希望系统能够在 Windows 平台上稳定运行，以便支持主要用户群体。

#### 验收标准

1. THE System SHALL 在 Windows 操作系统上运行
2. THE System SHALL 使用 Windows 路径分隔符处理文件路径
3. THE ADB_Controller SHALL 使用 shell=True 执行 Windows 命令
4. THE MuMu_Launcher SHALL 支持查找 Windows 桌面快捷方式
5. WHEN 使用 pywin32 库时，THE System SHALL 处理库不可用的情况

### 需求 20: 性能要求

**用户故事:** 作为测试人员，我希望系统能够快速响应操作，以便提高测试效率。

#### 验收标准

1. THE ADB_Controller SHALL 在 30 秒内完成设备连接
2. THE ADB_Controller SHALL 在 5 秒内完成单次截图操作
3. THE Image_Matcher SHALL 在 2 秒内完成单次模板匹配
4. THE Task_Executor SHALL 在配置的任务间隔时间后开始下一个任务
5. THE GUI_Window SHALL 在 1 秒内响应用户的按钮点击操作
