# 导入所需的模块
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt # 导入 Qt 核心模块中的枚举和常量
import sys
from datetime import datetime

# 创建应用主体
app = QApplication(sys.argv)

# 创建主窗口
window = QWidget()
window.setWindowTitle("日志时间序列自动生成脚本 - 主窗口")
window.resize(300,100) #宽，高


# 设置点击更新的小按钮
button = QPushButton()
button.setText("复制下一条")
button.setFixedHeight(100)

# 设置用于展示文本的标签
label0 = QLabel("（粘贴于文件开头：）",window)
label0.resize(50,40)
label = QLabel("",window)
label.resize(50,40)
label0.setTextFormat(Qt.TextFormat.PlainText)  # 强制设置为纯文本格式
label.setTextFormat(Qt.TextFormat.PlainText)  # 强制设置为纯文本格式

# 创建一个垂直布局管理器
layout = QVBoxLayout()
## 顺带着把前面的标签、按钮都放入此布局管理器
layout.addWidget(label0)
layout.addWidget(label)
layout.addWidget(button)
## 再把这么个布局赋予主窗口
window.setLayout(layout)

# 创建剪贴板对象
clipboard = QApplication.clipboard()

# 时间计算方法的定义(程序核心)
time0 = datetime.now().astimezone() ## time0表示上一次时间码，程序启动时第一次生成
time1 = time0 #程序当前时间。程序启动时与初始时间相等
weekdays = {
    0:"周一",
    1:"周二",
    2:"周三",
    3:"周四",
    4:"周五",
    5:"周六",
    6:"周日",
}

#用于初始化时间码的时段计算函数
def day_time_devide(time:datetime):
    '''
    day_time_devide 的 Docstring
    
    :param time: 用于将datetime转换为凌晨、上午、下午、夜晚四者之一
    :type time: datetime.datetime
    '''
    hour = time.hour
    if 0 <= hour and hour < 6:
        return "凌晨"
    elif 6 <= hour and hour < 12:
        return "上午"
    elif 12 <= hour and hour < 18:
        return "下午"
    elif 18 <= hour and hour < 24:
        return "夜晚"
    else:
        return "出错！"

# 初始化时间码！
## 得到初始的时间码
text0 = f'''# 电脑使用情况记述 <br> \n
> -- {time0.year}/{time0.month:0>2}/{time0.day:0>2} {weekdays[time0.weekday()]} {day_time_devide(time0)} *{time0.hour:0>2}:{time0.minute:0>2}* 创建 <br>
'''
## 通过label展示初始时间码
label.setText(text0)

def time2xxxx(time:datetime):
    '''
    time2xxxx 的 Docstring
    
    :param time: 将一个datetime对象转换为*00:00*格式的字符串时间戳
    :type time: datetime
    :return str
    '''
    h = time.hour
    m = time.minute
    return f"*{h:0>2}:{m:0>2}*"


def new_time_text():
    '''
    new_time 的 Docstring
    
    :param time: 返回基于当前时间运算得到的时间戳,带有mathjax箭头时间差
    '''
    global time1
    time2 = datetime.now().astimezone() # 获取当前时间，并临时保存。程序末尾传给time1
    delta_time = time2 - time1 # 计算时间差
    # 快速将时间差转换为时分秒
    m, s = divmod(delta_time.seconds, 60)
    h, m = divmod(m, 60)
    # 转换出箭头上的时间差字符！
    if h == 0:
        h_str = ""
    else:
        h_str = f"{h}h"
    if m == 0:
        m_str = ""
    else:
        m_str = f"{m}\'"
    if h_str == "" or m_str == "":
        if h_str == "" and m_str == "":
            delta_str = "1\'"
        else:
            delta_str = h_str + m_str
    else:
        delta_str = f"{h_str}\\ {m_str}"
    # 将时间点转换为时间戳
    time1_str = time2xxxx(time1)
    time2_str = time2xxxx(time2)
    # 更新time1
    time1 = time2
    # 返回
    print(delta_str,end=", ")
    return f"{time1_str}$\\large\\xrightarrow{{{delta_str}}}${time2_str}"


# 使按钮在被点击时完成更新标签文本
programme_awakening = True ## 如果程序是刚刚启动的话 的记号变量
def on_button_clicked(): ## 如果按钮被点击
    global programme_awakening
    ### 更新标签文本
    if programme_awakening:
        label0.setText("（粘贴于开首段落末尾字符后：）")
        text = f"\n* {new_time_text()}：\n\t"
        programme_awakening = False
    else:
        label0.setText("（粘贴于前一段落末尾字符后：）")
        text = f"\n<br>\n* {new_time_text()}：\n\t"
    
    label.setText(text+"\n") # 这里测试的话可以设为label.text()+text
    #将内容赋给剪贴板。大功告成！
    clipboard.setText(text)
    
## 设置信号与槽
button.clicked.connect(on_button_clicked)

# 显示窗口！
window.show()
clipboard.setText(text0)
#进入事件循环
sys.exit(app.exec())