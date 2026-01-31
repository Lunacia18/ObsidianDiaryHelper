# PySide6 + QML 迁移指南

## 1. 项目现状分析

现有代码 `Obsidian_Diary_main.py` 是一个基于 PyQt6 的 GUI 工具，用于生成 Obsidian 日记的时间戳。尽管功能可用，但存在以下问题：

- **代码结构单一**：所有逻辑（UI、时间计算、剪贴板操作）都写在一个文件中，超过 150 行。
- **全局变量滥用**：使用 `global` 关键字管理状态，增加复杂度。
- **命名不规范**：函数名如 `day_time_devide`（拼写错误）、`time2xxxx` 不符合 PEP 8。
- **缺乏错误处理**：未处理剪贴板访问失败、时间计算异常等情况。
- **硬编码字符串**：界面文本、时间格式固定，不易修改。
- **依赖 PyQt6**：使用 GPL 许可，对分发有要求。

## 2. PySide6 + QML 的优势

### 2.1 为什么选择 PySide6？
- **官方绑定**：PySide6 是 Qt 官方 Python 绑定，许可为 LGPL，商业友好。
- **与 PyQt6 API 高度兼容**：大多数代码只需修改导入语句即可迁移。
- **活跃维护**：由 Qt 公司直接支持，更新及时。

### 2.2 为什么引入 QML？
- **声明式 UI**：用简洁的 QML 语言描述界面，分离 UI 与业务逻辑。
- **现代设计**：支持动画、渐变、响应式布局，视觉效果更佳。
- **易于维护**：UI 修改无需重新编译 Python 代码，只需编辑 QML 文件。
- **跨平台**：QML 界面在不同操作系统上表现一致。

### 2.3 迁移后的预期收益
- 代码结构清晰，易于扩展新功能。
- UI 与逻辑解耦，便于团队协作。
- 提供更美观、现代化的用户界面。
- 降低许可风险，方便分发。

## 3. 迁移策略（分步骤实施）

### 第一阶段：准备环境
1. 安装 PySide6：`uv add pyside6`
2. 创建项目目录结构（见第 4 节）。
3. 备份现有代码。

### 第二阶段：替换 PyQt6 为 PySide6
1. 修改导入语句：
   ```python
   # from PyQt6.QtWidgets import ... 
   # 改为
   from PySide6.QtWidgets import ...
   ```
2. 检查 API 差异（如信号槽语法，基本一致）。
3. 更新 `pyproject.toml` 依赖。

### 第三阶段：拆分业务逻辑
1. 将时间计算函数提取到独立模块 `time_utils.py`。
2. 将剪贴板操作封装到 `clipboard_manager.py`。
3. 创建 `TimeManager` 类管理时间状态，消除全局变量。

### 第四阶段：设计 QML 界面
1. 编写主窗口 QML 文件（`MainWindow.qml`）。
2. 在 Python 中加载 QML 引擎。
3. 将 `TimeManager` 暴露给 QML 上下文。

### 第五阶段：集成测试
1. 确保功能与原有版本一致。
2. 添加简单的单元测试。
3. 打包验证。

## 4. 文件结构建议

```
obsidiandiaryhelper/
├── src/
│   ├── obsidiandiaryhelper/
│   │   ├── __init__.py
│   │   ├── main.py              # 程序入口
│   │   ├── timemanager.py       # 时间管理类
│   │   ├── time_utils.py        # 时间计算函数
│   │   ├── clipboard_manager.py # 剪贴板操作
│   │   └── config.py            # 配置管理
│   └── qml/
│       ├── MainWindow.qml       # 主窗口界面
│       ├── Button.qml           # 自定义按钮
│       └── TimeLabel.qml        # 时间显示标签
├── tests/
│   ├── test_time_utils.py
│   └── test_timemanager.py
├── data/
│   └── config.json              # 配置文件
├── dist/                        # 打包输出
├── docs/                        # 文档
├── pyproject.toml
└── README.md
```

## 5. 核心代码示例

### 5.1 TimeManager 类（Python 后端）

```python
# timemanager.py
from datetime import datetime
from typing import Tuple

class TimeManager:
    """管理时间状态，生成时间戳字符串"""
    
    def __init__(self):
        self.start_time = datetime.now().astimezone()
        self.last_time = self.start_time
        self.is_first_click = True
        
    def get_time_period(self, dt: datetime) -> str:
        """返回时段描述：凌晨、上午、下午、夜晚"""
        hour = dt.hour
        if 0 <= hour < 6:
            return "凌晨"
        elif 6 <= hour < 12:
            return "上午"
        elif 12 <= hour < 18:
            return "下午"
        elif 18 <= hour < 24:
            return "夜晚"
        else:
            return "未知"
    
    def format_time_stamp(self, dt: datetime) -> str:
        """格式化为 *HH:MM*"""
        return f"*{dt.hour:02d}:{dt.minute:02d}*"
    
    def generate_time_text(self) -> Tuple[str, str]:
        """
        生成新的时间戳文本
        返回 (显示文本, 剪贴板文本)
        """
        now = datetime.now().astimezone()
        delta = now - self.last_time
        
        # 计算时间差描述
        total_minutes = int(delta.total_seconds() // 60)
        if total_minutes == 0:
            delta_str = "0'"
        else:
            hours, minutes = divmod(total_minutes, 60)
            parts = []
            if hours:
                parts.append(f"{hours}h")
            if minutes:
                parts.append(f"{minutes}'")
            delta_str = " ".join(parts)
        
        # 生成箭头字符串
        prev_stamp = self.format_time_stamp(self.last_time)
        curr_stamp = self.format_time_stamp(now)
        arrow_text = f"{prev_stamp}$\\large\\xrightarrow{{{delta_str}}}${curr_stamp}"
        
        # 更新状态
        self.last_time = now
        display_text = f"* {arrow_text}：\n\t"
        clipboard_text = display_text
        
        if self.is_first_click:
            self.is_first_click = False
            prefix = "（粘贴于开首段落末尾字符后：）"
        else:
            prefix = "（粘贴于前一段落末尾字符后：）"
            clipboard_text = f"\n<br>\n{clipboard_text}"
        
        return prefix, display_text, clipboard_text
```

### 5.2 QML 界面示例

```qml
// MainWindow.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: window
    width: 400
    height: 200
    title: "Obsidian 日记时间助手"
    color: "#f5f5f5"
    
    // 暴露给 QML 的 TimeManager 实例
    property var timeManager
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 10
        
        Label {
            id: instructionLabel
            text: "（粘贴于文件开头：）"
            font.pixelSize: 14
            color: "#666"
        }
        
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            color: "white"
            border.color: "#ddd"
            radius: 8
            
            ScrollView {
                anchors.fill: parent
                anchors.margins: 8
                
                TextArea {
                    id: timeLabel
                    text: timeManager.initialText
                    font.family: "Consolas, Monaco, monospace"
                    font.pixelSize: 13
                    readOnly: true
                    wrapMode: Text.Wrap
                }
            }
        }
        
        Button {
            id: generateButton
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            text: "复制下一条"
            font.pixelSize: 16
            font.bold: true
            background: Rectangle {
                color: generateButton.down ? "#4a90e2" : "#5a9de6"
                radius: 8
            }
            contentItem: Text {
                text: generateButton.text
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            
            onClicked: {
                var result = timeManager.generateTimeText()
                instructionLabel.text = result.prefix
                timeLabel.text = result.displayText
                // 剪贴板操作由 Python 后端处理
            }
        }
    }
}
```

### 5.3 Python 主程序（加载 QML）

```python
# main.py
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QUrl, QObject, Slot, Property, Signal
from timemanager import TimeManager

class Bridge(QObject):
    """连接 Python 与 QML 的桥梁"""
    
    def __init__(self, time_manager):
        super().__init__()
        self._time_manager = time_manager
        
    @Property(str, constant=True)
    def initialText(self):
        """返回初始时间文本"""
        dt = self._time_manager.start_time
        period = self._time_manager.get_time_period(dt)
        return f"""# 电脑使用情况记述 <br>
> -- {dt.year}/{dt.month:02d}/{dt.day:02d} {self._weekday(dt)} {period} *{dt.hour:02d}:{dt.minute:02d}* 创建 <br>"""
    
    @Slot(result="QVariant")
    def generateTimeText(self):
        """生成时间文本，返回包含 prefix、displayText、clipboardText 的对象"""
        prefix, display, clipboard = self._time_manager.generate_time_text()
        # 这里可以调用剪贴板操作
        from clipboard_manager import set_clipboard_text
        set_clipboard_text(clipboard)
        
        return {
            "prefix": prefix,
            "displayText": display,
            "clipboardText": clipboard
        }
    
    def _weekday(self, dt):
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return weekdays[dt.weekday()]

def main():
    app = QApplication(sys.argv)
    
    # 创建时间管理器
    time_manager = TimeManager()
    
    # 创建 QML 视图
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    
    # 创建桥梁并暴露给 QML
    bridge = Bridge(time_manager)
    view.rootContext().setContextProperty("timeManager", bridge)
    
    # 加载 QML 文件
    qml_file = Path(__file__).parent / "qml" / "MainWindow.qml"
    view.setSource(QUrl.fromLocalFile(str(qml_file)))
    
    if view.status() == QQuickView.Error:
        sys.exit(-1)
    
    view.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
```

## 6. 学习资源推荐

### 6.1 官方文档
- **PySide6 官方文档**：https://doc.qt.io/qt-6/pyside6-index.html
- **QML 语言参考**：https://doc.qt.io/qt-6/qtqml-index.html
- **Qt for Python 示例**：https://doc.qt.io/qt-6/qtforpython-examples.html

### 6.2 中文教程
- **Qt 官方中文社区**：https://www.qt.io/zh-cn/
- **PySide6 入门教程**：https://zhuanlan.zhihu.com/p/64642254
- **QML 快速上手**：https://blog.csdn.net/qq_40194498/article/details/119890190

### 6.3 视频课程
- **Bilibili 搜索 "PySide6 教程"**：多个系列免费视频
- **Udemy "PySide6 Masterclass"**：英文付费课程，深度完整

### 6.4 参考书籍
- **《PySide6 GUI 编程指南》**（电子版）
- **《QML 与 Qt Quick 核心编程》**

## 7. 开发环境配置

### 7.1 安装 Python 3.8+
```bash
# 检查 Python 版本
python --version

# 使用 uv 管理虚拟环境（推荐）
pip install uv
```

### 7.2 创建项目并安装依赖
```bash
# 创建项目目录
mkdir obsidiandiaryhelper
cd obsidiandiaryhelper

# 初始化 uv 项目
uv init

# 添加 PySide6 依赖
uv add pyside6

# 添加开发工具
uv add --dev pytest black flake8
```

### 7.3 配置 VSCode 开发环境
1. 安装扩展：
   - **Python**（Microsoft）
   - **Qt for Python**（Qt）
   - **QML**（Qt）

2. 创建 `.vscode/settings.json`：
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "files.associations": {
        "*.qml": "qml"
    }
}
```

### 7.4 运行测试
```bash
# 运行 Python 后端测试
uv run pytest tests/

# 启动 QML 界面
uv run python src/obsidiandiaryhelper/main.py
```

## 8. 难点与解决方案

### 8.1 Python 与 QML 数据交换
**难点**：QML 不能直接调用 Python 类的方法。
**解决方案**：
- 创建 `Bridge` 类继承 `QObject`，使用 `@Slot` 装饰器暴露方法。
- 使用 `setContextProperty` 将对象注入 QML 上下文。
- 对于复杂数据，返回 `QVariant` 或 `QVariantMap`。

### 8.2 QML 界面布局
**难点**：不熟悉 QML 的布局系统（ColumnLayout、RowLayout 等）。
**解决方案**：
- 先从简单布局开始，逐步添加复杂组件。
- 使用 Qt Designer 的 QML 模式可视化设计界面。
- 参考官方示例中的布局代码。

### 8.3 剪贴板操作
**难点**：QML 中访问系统剪贴板需要平台特定代码。
**解决方案**：
- 在 Python 后端实现剪贴板操作，通过桥梁暴露给 QML。
- 使用 `PySide6.QtGui.QClipboard`，与原有代码类似。

### 8.4 打包分发
**难点**：PySide6 + QML 应用打包体积较大。
**解决方案**：
- 使用 `pyinstaller` 并指定 QML 文件：
  ```bash
  pyinstaller --name ObsidianDiaryHelper ^
              --add-data "src/qml;qml" ^
              src/obsidiandiaryhelper/main.py
  ```
- 使用 `Nuitka` 编译为 C 扩展，减少体积。
- 利用 Qt 的部署工具 `windeployqt`（Windows）。

## 9. 测试建议

### 9.1 单元测试
```python
# tests/test_time_utils.py
import pytest
from datetime import datetime
from obsidiandiaryhelper.time_utils import get_time_period

def test_get_time_period():
    # 测试凌晨时段
    dt = datetime(2024, 1, 1, 3, 0)  # 凌晨 3 点
    assert get_time_period(dt) == "凌晨"
    
    # 测试边界情况
    dt = datetime(2024, 1, 1, 6, 0)  # 上午 6 点
    assert get_time_period(dt) == "上午"
```

### 9.2 集成测试
```python
# tests/test_integration.py
def test_full_workflow():
    # 模拟点击按钮，检查剪贴板内容
    pass
```

### 9.3 UI 测试
- 使用 **Qt Test Framework** 进行 UI 自动化测试。
- 或使用 **pytest-qt** 插件模拟用户交互。

### 9.4 剪贴板测试
```python
# 模拟剪贴板操作，避免实际系统依赖
from unittest.mock import Mock, patch

def test_clipboard_set():
    with patch('PySide6.QtWidgets.QApplication.clipboard') as mock_clipboard:
        # 测试剪贴板设置
        pass
```

## 10. 总结

迁移到 PySide6 + QML 不仅能解决现有代码的结构问题，还能为项目带来以下好处：

1. **代码质量提升**：模块化设计，易于维护和测试。
2. **界面现代化**：QML 提供更美观、响应式的 UI。
3. **许可友好**：LGPL 许可降低分发限制。
4. **扩展性强**：便于添加新功能如主题切换、插件系统。

建议按照本文的迁移策略分步实施，先完成 PySide6 替换，再逐步引入 QML 界面。在迁移过程中，保持原有功能可用性，每完成一个阶段都进行充分测试。

---

**文档版本**：1.0  
**更新日期**：2026-01-31  
**适用对象**：Python 新手、GUI 开发者、Obsidian 用户  

> 注意：本文档仅为迁移指南，实际实施时请根据具体需求调整。如有疑问，欢迎查阅推荐的学习资源或提交 Issue。