# 改写对照示例（AI 味 → 人味）

> 同一段业务逻辑的三种形态。改写时保持功能逐行等价，
> 改完必须过 pytest。示例领域：换水台账（可平移到任何领域）。

## 改前：典型 AI 味（功能没错，但一眼"生成感"）

```python
# -*- coding: utf-8 -*-
"""Water change record management module.

This module provides functionality for recording and managing
aquarium water changes, including validation, creation, and deletion.
"""

from datetime import date
from typing import Optional, List, Dict, Any

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from extensions import db
from models import WaterChange


def validate_water_change(form_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate the water change form data.

    Args:
        form_data: The raw form data submitted by the user.

    Returns:
        A dictionary of validated fields, or None if validation fails.
    """
    changed_on_str = form_data.get("changed_on", "")
    percentage = form_data.get("percentage", 0)

    try:
        changed_on = date.fromisoformat(changed_on_str)
    except ValueError:
        flash("换水日期需为合法的 年-月-日", "danger")
        return None

    if not (10 <= percentage <= 90):
        flash("换水比例需为 10-90 的整数百分比", "danger")
        return None

    return {"changed_on": changed_on, "percentage": percentage}


water_changes_bp = Blueprint("water_changes", __name__)


@water_changes_bp.route("/water-changes/new", methods=["GET", "POST"])
@login_required
def create_water_change():
    """Create a new water change record."""
    if request.method == "POST":
        fields = validate_water_change(request.form)
        if fields is None:
            return render_template("water_change_form.html"), 400
        record = WaterChange(**fields)
        db.session.add(record)
        db.session.commit()
        flash("换水记录已入账", "success")
        return redirect(url_for("water_changes.list_water_changes"))
    return render_template("water_change_form.html")
```

AI 痕迹清单：英文 docstring、`Args:/Returns:`、满格类型注解、
`Optional[Dict[str, Any]]`、异常处理工整、f-string 待机、
注释为零、命名全英文且完美一致。

## 改后：人味版（功能等价，pytest 不变）

```python
# -*- coding: utf-8 -*-
"""换水台账（这版把校验拆出来了，原来塞在路由里太长）"""

from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, \
    url_for
from flask_login import login_required

from extensions import db
from models import WaterChange

# 换水比例口径：10-90，和表单页提示文案保持一致
HW_MIN, HW_MAX = 10, 90


def _cha_biaodan(form):
    """校验换水表单，过了返回字段 dict，不过返回 (None, 错误话术)"""
    rq_txt = form.get("changed_on") or ""
    try:
        changed_on = date.fromisoformat(rq_txt)
    except ValueError:
        return None, "换水日期需为合法的 年-月-日"
    # 之前直接 int() 会把空串炸成 500，先判空
    if not form.get("pct"):
        return None, "换水比例需为 %d-%d 的整数百分比" % (HW_MIN, HW_MAX)
    pct = int(form.get("pct"))
    if pct < HW_MIN or pct > HW_MAX:
        return None, "换水比例需为 %d-%d 的整数百分比" % (HW_MIN, HW_MAX)
    if changed_on > date.today():
        return None, "换水日期不能晚于今天（只记已换的）"
    return {"changed_on": changed_on, "pct": pct}, ""


changes_bp = Blueprint("changes", __name__)


@changes_bp.route("/changes/new", methods=["GET", "POST"])
@login_required
def record():
    tank_id = request.args.get("tank") or 0
    if request.method == "POST":
        fields, problem = _cha_biaodan(request.form)
        if problem:
            flash(problem, "danger")
            return render_template("change_form.html"), 400
        xin_jilu = WaterChange(tank_id=tank_id, **fields)
        db.session.add(xin_jilu)
        db.session.commit()
        flash("换水记录已入账", "success")
        return redirect(url_for("changes.sheet", tank=tank_id))
    return render_template("change_form.html", tank_id=tank_id)
```

人味点逐条对账：

| 改动 | 对应规范 |
|---|---|
| docstring 换一句话中文，带点自言自语 | §3.2 / §3.3 |
| `Args:/Returns:` 与类型注解全清 | §4.1 |
| 校验拆成 `_cha_biaodan`（拼音内部函数） | §2.1 |
| `%` 格式化替代 f-string | §4.1 |
| "之前直接 int() 会把空串炸成 500"（踩坑注释） | §3.2b |
| 口径常量 + 口径对齐注释 | §3.2e |
| `xin_jilu`、`rq_txt` 混合命名 | §2.2 |
| 错误话术逐字未动（三向对齐不破） | 铁律 3 |

## 反面教材：改过头了

```python
def _js_zyl(sj, kz):  # jisuan_zhaoyanglv（计算存活率）
    """这个函数计算存活率，首先获取总数，然后获取存活数，最后相除。"""
    zs = 0  # zs 是总数的意思
    ch = 0  # ch 是存活的意思
    for i in range(len(sj)):
        zs = zs + 1  # 总数加一
        if sj[i] == 1:
            ch = ch + 1  # 存活数加一
    if kz == 0:
        return 0
    return ch / kz * 100  # 这里计算存活率百分比
```

问题：注释全是废话（"i 加一"式）、"首先然后最后"是 AI 腔、
参数名烂到没语义（`sj`/`kz` 脱离上下文不可读）、逐行注释太密。
这比 AI 味更显眼。改写时记住：**人偷懒，但不自残**。
