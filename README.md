# AxleScore

一个轻量（real？）的课堂小组评分工具，基于 PyQt5 构建，以悬浮窗形式常驻桌面，方便教师实时加减分、查看趋势。

## 功能

- **分数管理** — 按周次对小组进行加分/减分，支持填写原因，实时查看排名与累计总分
- **小组管理** — 添加、删除、重命名小组，自动统计排行榜
- **趋势图表** — 单周柱状图与双周对比图，直观展示各组分数变化
- **悬浮窗** — 无边框窗口，可拖拽移动，支持收起/展开
- **操作日志** — 记录所有分数变更与小组操作，可随时查看和清空


## 依赖

- Python 3.7+
- PyQt5
- matplotlib
- numpy

## 安装与运行

```bash
pip install PyQt5 matplotlib numpy
python floating_window.py
```

首次运行会自动创建 `data/` 目录并初始化示例数据。


## 许可证
本项目基于 **GNU General Public License v3.0** 开源。  
详见 [LICENSE](LICENSE) 文件。

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)