import json
import os
import sys
import re
from datetime import datetime

# 打包后用 exe 所在目录，作为脚本运行时使用脚本所在目录
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(_BASE_DIR, "data")
GROUPS_FILE = os.path.join(DATA_DIR, "groups.json")
SCORES_FILE = os.path.join(DATA_DIR, "scores.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")
REGISTRY_FILE = os.path.join(DATA_DIR, "registry.json")

#缓存
_total_cache = {}



def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_json(path, default):
    _ensure_dir()
    if not os.path.exists(path):
        _save_json(path, default)
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path, data):
    _ensure_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


#小组管理

def get_groups():
    return _load_json(GROUPS_FILE, [])


def save_groups(groups):
    _save_json(GROUPS_FILE, groups)


def add_group(name):
    groups = get_groups()
    if name in groups:
        return False, f"小组 '{name}' 已存在"
    groups.append(name)
    save_groups(groups)
    add_log("新增小组", f"新增小组: {name}")
    #为已有周次补0分
    scores = get_scores()
    for week in scores:
        if name not in scores[week]:
            scores[week][name] = 0
    save_scores(scores)
    invalidate_total_cache()
    return True, f"小组 '{name}' 已添加"


def remove_group(name):
    groups = get_groups()
    if name not in groups:
        return False, f"小组 '{name}' 不存在"
    groups.remove(name)
    save_groups(groups)
    add_log("删除小组", f"删除小组: {name}")
    #从分数中移除
    scores = get_scores()
    for week in scores:
        scores[week].pop(name, None)
    save_scores(scores)
    invalidate_total_cache()
    return True, f"小组 '{name}' 已删除"


def rename_group(old_name, new_name):
    groups = get_groups()
    if old_name not in groups:
        return False, f"小组 '{old_name}' 不存在"
    if new_name in groups:
        return False, f"小组 '{new_name}' 已存在"
    idx = groups.index(old_name)
    groups[idx] = new_name
    save_groups(groups)
    add_log("重命名小组", f"重命名: {old_name} → {new_name}")
    #更新分数中的名字
    scores = get_scores()
    for week in scores:
        if old_name in scores[week]:
            scores[week][new_name] = scores[week].pop(old_name)
    save_scores(scores)
    invalidate_total_cache()
    return True, f"已重命名: {old_name} → {new_name}"


#分数类

def get_scores():
    return _load_json(SCORES_FILE, {})


def save_scores(scores):
    _save_json(SCORES_FILE, scores)


def _parse_week_idx(name):
    m = re.match(r'^第(\d+)周$', name)
    if m:
        return int(m.group(1))
    return None


def get_weeks():
    scores = get_scores()
    return list(scores.keys())


def get_current_week():
    weeks = get_weeks()
    if not weeks:
        return None
    return weeks[-1]


def add_week():
    weeks = get_weeks()
    next_idx = len(weeks) + 1
    week_name = f"第{next_idx}周"

    scores = get_scores()
    if week_name in scores:
        return False, f"{week_name} 已存在"

    groups = get_groups()
    scores[week_name] = {g: 0 for g in groups}
    save_scores(scores)
    invalidate_total_cache()
    add_log("新增周次", f"新增周次: {week_name}")
    return True, f"{week_name} 已创建"


def add_score(group, week, value, reason=""):
    scores = get_scores()
    if week not in scores:
        return False, f"{week} 不存在"
    if group not in scores[week]:
        return False, f"小组 '{group}' 在 {week} 中不存在"

    old = scores[week][group]
    scores[week][group] = old + value
    save_scores(scores)
    invalidate_total_cache()

    sign = "+" if value >= 0 else ""
    detail = f"{group} {week} {sign}{value}"
    if reason:
        detail += f" ({reason})"
    add_log("修改分数", detail)
    return True, f"{group} {week}: {old} → {scores[week][group]}"


def get_group_total(group):

    if group in _total_cache:
        return _total_cache[group]
    scores = get_scores()
    total = 0
    for week in scores:
        total += scores[week].get(group, 0)
    _total_cache[group] = total
    return total


def invalidate_total_cache():
    """使总分缓存失效"""
    _total_cache.clear()


def get_highest_score_group():
    """获取总分最高的小组"""
    groups = get_groups()
    if not groups:
        return None, 0
    best = None
    best_score = float('-inf')
    for g in groups:
        total = get_group_total(g)
        if total > best_score:
            best_score = total
            best = g
    return best, best_score


#操作日志

def get_logs():
    return _load_json(LOGS_FILE, [])


def add_log(action, detail):
    logs = get_logs()
    logs.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "detail": detail
    })
    _save_json(LOGS_FILE, logs)


def clear_logs():
    _save_json(LOGS_FILE, [])


#注册表

def get_registry():
    if not os.path.exists(REGISTRY_FILE):
        registry_creater()
    return _load_json(REGISTRY_FILE, [])
    

def save_registry(registry_data):
    return _save_json(REGISTRY_FILE, registry_data)

def get_models():
    registry = get_registry()
    models_list = registry.get("models", [])
    attr_dict = {item["model_name"]: item for item in registry.get("Attribute", [])}
    result = []
    for name in models_list:
        if name not in attr_dict:
            continue
        attr = attr_dict[name]
        class_name = attr.get("model_class", "")
        #旧版registry没有model_class字段，尝试按文件名推断
        if not class_name:
            module_name = attr.get("model_path", "").replace(".py", "")
            class_name = module_name.split("_")[0].title() + "".join(
                w.title() for w in module_name.split("_")[1:]
            ) + "Page" if module_name else ""
        result.append({
            "name": name,
            "module": attr.get("model_path", "").replace(".py", ""),
            "class_name": class_name,
        })
    return result

def registry_creater():
    create = {
        "models" : ["分数","小组","趋势","关于"],
        "Attribute" : [
            {
                "model_name" : "分数",
                "writer" : "Axlewire",
                "descriptions" : "用于增减分数以及周次。",
                "model_path" : "score_page.py",
                "model_class" : "ScorePage"
            },
            {
                "model_name" : "小组",
                "writer" : "Axlewire",
                "descriptions" : "用于管理小组成员以及小组。",
                "model_path" : "group_page.py",
                "model_class" : "GroupPage"
            },
            {
                "model_name" : "趋势",
                "writer" : "Axlewire",
                "descriptions" : "用于查看分数统计。",
                "model_path" : "trend_page.py",
                "model_class" : "TrendPage"
            },
            {
                "model_name" : "关于",
                "writer" : "Axlewire",
                "descriptions" : "用于查看关于本项目的信息以及配置自定义项。",
                "model_path" : "about.py",
                "model_class" : "AboutPage"
            }

        ]
    }
    _save_json(REGISTRY_FILE,create)


#初始化

def init_data():
    init_flag = os.path.join(DATA_DIR, ".initialized")
    if os.path.exists(init_flag):
        return 
    #示例数据
    save_groups(["第一组", "第二组", "第三组", "第四组", "第五组", "第六组", "第七组", "第八组"])
    scores = {"第1周": {"第一组": 0, "第二组": 0, "第三组": 0, "第四组": 0, "第五组": 0, "第六组": 0, "第七组": 0, "第八组": 0}}
    save_scores(scores)
    registry_creater()
    add_log("系统初始化", "创建示例小组和第一周数据")
    #写入初始化标识
    with open(init_flag, "w", encoding="utf-8") as f:
        f.write("1")
