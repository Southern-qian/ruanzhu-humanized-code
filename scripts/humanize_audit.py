#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""humanize_audit.py — 软著源代码拟人化程度审计

对项目 .py 源码做六项计量，判定是否达到"手写味"门槛：
  1. 注释率          (注释行+docstring行)/代码行，默认门槛 20%-35%
  2. 拼音标识符占比  含拼音词根的标识符出现次数占比，默认 10%-60%
  3. emoji 数        必须为 0
  4. 纯英文注释行数  必须为 0
  5. Google docstring（Args:/Returns: 等）出现次数，必须为 0
  6. f-string 占比   f-string/(f-string+%s+.format)，默认 <=75%

用法：
  python3 humanize_audit.py <项目目录> --gate
  python3 humanize_audit.py <项目目录> --json
  python3 humanize_audit.py <项目目录> --gate --min-comment 0.30 --exclude tools

默认跳过 venv/.git/__pycache__/node_modules，以及 tools、tests 目录
（它们不进鉴别材料正文页）。要全查加 --all。

退出码：0=通过，1=有门槛未过，2=用法错误。
"""

import argparse
import json
import os
import re
import sys

# 拼音词根表：与 references/pinyin-wordlist.md 保持同步
PINYIN_WORDS = set("""
tianjia zengjia shanchu xiugai chaxun baocun denglu tuichu daoru daochu
suoding jiesuo tongji fenye shengcheng jisuan jiancha tishi quxiao tijiao
yonghu mima zhanghu quanxian jilu liebiao xiangqing shezhi biaodan shuju
mingcheng leixing zhuangtai riqi shijian shuliang jine danjia beizhu
neirong tupian suoyin dingdan fujian biaoqian fenlei yongjin yue
xin zong quan ge tian ri
jl yh tj sc xg cx bc dl zh qx fl bq fj sy dd fy ts js jc
bd rq mc lx zt sl bz nr tp yj ye hang lieyanggang huanshui weishi shuizhi weiyang shuijiao nianling tidian
shouzhi yusuan jiezhuan zhangmu mianjing toudi yaoqing fankui
shicai pengren peicai weijing gangwei gongsi jindu beiwang rili
""".split())

PY_KEYWORDS = set("""
False None True and as assert async await break class continue def del
elif else except finally for from global if import in is lambda nonlocal
not or pass raise return try while with yield
self cls int str float bool dict list set tuple len range print
""".split())

IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
CAMEL_RE = re.compile(r"[A-Z]+(?![a-z])|[A-Z][a-z]*|[a-z]+")
EMOJI_RE = re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]")
GOOGLE_DOC_RE = re.compile(r"^\s*(Args|Returns|Raises|Parameters|Yields|Attributes)\s*:", re.M)
FSTRING_RE = re.compile(r"[fF](['\"])")
PCT_FMT_RE = re.compile(r"%[sdif]|%\(")
FORMAT_RE = re.compile(r"\.format\(")

# 多音节拼音词（>=2 字母）可无缝拼接判定：xinjilu = xin + jilu
LONG_WORDS = {w for w in PINYIN_WORDS if len(w) >= 2}


def _word_splits(seg, parts=None):
    """seg 能否被 PINYIN_WORDS 里的词（各 >=2 字母）恰好拼成；返回切法数"""
    if parts is None:
        parts = []
    if not seg:
        return 1 if len(parts) >= 2 else 0
    total = 0
    for i in range(2, len(seg) + 1):
        if seg[:i] in LONG_WORDS:
            total += _word_splits(seg[i:], parts + [seg[:i]])
    return total


def is_pinyin_name(name):
    """标识符是否拼音味：任一下划线/camel 分段是词表词或可由词表词拼成"""
    segs = []
    for raw in name.split("_"):
        segs.extend(s.lower() for s in CAMEL_RE.findall(raw) if s)
    for seg in segs:
        if seg in PINYIN_WORDS or _word_splits(seg):
            return True
    return False

SKIP_DIRS_DEFAULT = {"venv", ".git", "__pycache__", "node_modules",
                     "tools", "tests", "migrations", "scripts",
                     ".pytest_cache", "dist", "build"}


def read_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()
    except OSError:
        return []


def classify_lines(lines):
    """把文件行分成 docstring 行和非 docstring 行（简单三引号状态机）"""
    in_doc = False
    quote = None
    doc_rows, code_rows = set(), set()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if in_doc:
            doc_rows.add(idx)
            if quote and quote in line:
                in_doc = False
            continue
        # 单行 docstring（"""xxx"""）也算 docstring 行
        for q in ('"""', "'''"):
            if stripped.startswith(q) and stripped.count(q) >= 2 and len(stripped) > 6:
                doc_rows.add(idx)
                break
            if q in line:
                in_doc = True
                quote = q
                doc_rows.add(idx)
                break
        else:
            code_rows.add(idx)
    return doc_rows, code_rows


def audit_file(path):
    lines = read_lines(path)
    doc_rows, _ = classify_lines(lines)
    stats = {
        "file": path,
        "total": len(lines),
        "comment": 0,
        "docstring": len(doc_rows),
        "code": 0,
        "ident_total": 0,
        "ident_pinyin": 0,
        "emoji": 0,
        "en_comment": 0,
        "google_doc": len(GOOGLE_DOC_RE.findall("\n".join(lines))),
        "fstring": 0,
        "pct_fmt": 0,
        "dot_format": 0,
        "optional_hits": 0,
        "arrow_hints": 0,
    }
    pinyin_seen = set()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if idx in doc_rows:
            continue
        if stripped.startswith("#"):
            stats["comment"] += 1
            body = stripped[1:].strip()
            # 编码声明/shebang 是约定行，不算英文注释
            if ("coding:" in body or body.startswith("!/")
                    or re.match(r"-\*-[\s\w.:-]*-\*-$", body)):
                continue
            # 纯英文注释：ascii 且含字母、长度可观
            if body and body.isascii() and re.search(r"[A-Za-z]{3,}", body):
                stats["en_comment"] += 1
            continue
        if not stripped:
            continue
        stats["code"] += 1
        stats["emoji"] += len(EMOJI_RE.findall(line))
        stats["fstring"] += len(FSTRING_RE.findall(line))
        stats["pct_fmt"] += len(PCT_FMT_RE.findall(line))
        stats["dot_format"] += len(FORMAT_RE.findall(line))
        stats["optional_hits"] += line.count("Optional[")
        stats["arrow_hints"] += line.count("-> ")
        for name in IDENT_RE.findall(line):
            if name in PY_KEYWORDS:
                continue
            stats["ident_total"] += 1
            if is_pinyin_name(name):
                stats["ident_pinyin"] += 1
                pinyin_seen.add(name)
    stats["pinyin_names"] = sorted(pinyin_seen)[:20]
    return stats


def find_py_files(root, include_all):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        parts = set(rel.split(os.sep))
        if not include_all and parts & SKIP_DIRS_DEFAULT:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames
                       if d not in {"venv", ".git", "__pycache__", "node_modules"}]
        for fn in filenames:
            if fn.endswith(".py"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="软著源代码拟人化审计")
    ap.add_argument("root", help="项目目录或单个 .py 文件")
    ap.add_argument("--gate", action="store_true", help="按门槛判定并决定退出码")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--all", action="store_true", help="包含 tools/tests 等目录")
    ap.add_argument("--min-comment", type=float, default=0.20)
    ap.add_argument("--max-comment", type=float, default=0.35)
    ap.add_argument("--pinyin-low", type=float, default=0.10)
    ap.add_argument("--pinyin-high", type=float, default=0.60)
    ap.add_argument("--max-fstring", type=float, default=0.75)
    args = ap.parse_args(argv)

    if os.path.isfile(args.root):
        files = [args.root]
    elif os.path.isdir(args.root):
        files = find_py_files(args.root, args.all)
    else:
        print("路径不存在: %s" % args.root, file=sys.stderr)
        return 2
    if not files:
        print("没找到 .py 文件", file=sys.stderr)
        return 2

    results = [audit_file(f) for f in files]
    agg = {k: sum(r[k] for r in results)
           for k in ("total", "comment", "docstring", "code", "ident_total",
                     "ident_pinyin", "emoji", "en_comment", "google_doc",
                     "fstring", "pct_fmt", "dot_format", "optional_hits",
                     "arrow_hints")}
    annotated = agg["comment"] + agg["docstring"]
    agg["comment_ratio"] = round(annotated / max(agg["code"], 1), 3)
    agg["pinyin_ratio"] = round(agg["ident_pinyin"] / max(agg["ident_total"], 1), 3)
    fmt_total = agg["fstring"] + agg["pct_fmt"] + agg["dot_format"]
    agg["fstring_ratio"] = round(agg["fstring"] / fmt_total, 3) if fmt_total else None

    checks = [
        ("注释率 %.1f%% 在 [%.0f%%, %.0f%%]" % (
            agg["comment_ratio"] * 100, args.min_comment * 100,
            args.max_comment * 100),
         args.min_comment <= agg["comment_ratio"] <= args.max_comment),
        ("拼音标识符占比 %.1f%% 在 [%.0f%%, %.0f%%]" % (
            agg["pinyin_ratio"] * 100, args.pinyin_low * 100,
            args.pinyin_high * 100),
         args.pinyin_low <= agg["pinyin_ratio"] <= args.pinyin_high),
        ("emoji 数 = 0", agg["emoji"] == 0),
        ("纯英文注释 = 0", agg["en_comment"] == 0),
        ("Google docstring = 0", agg["google_doc"] == 0),
        ("f-string 占比 <= %.0f%%" % (args.max_fstring * 100),
         agg["fstring_ratio"] is None or agg["fstring_ratio"] <= args.max_fstring),
    ]

    if args.json:
        print(json.dumps({
            "aggregate": agg,
            "checks": [{"item": c[0], "pass": c[1]} for c in checks],
            "files": [{k: r[k] for k in r if k != "pinyin_names"} for r in results],
            "pinyin_names_sample": {r["file"]: r["pinyin_names"]
                                    for r in results if r["pinyin_names"]},
        }, ensure_ascii=False, indent=1))
    else:
        print("=" * 60)
        print("拟人化审计：%s（%d 个文件）" % (args.root, len(results)))
        print("=" * 60)
        print("注释行 %d + docstring %d / 代码行 %d = 注释率 %.1f%%"
              % (agg["comment"], agg["docstring"], agg["code"],
                 agg["comment_ratio"] * 100))
        print("拼音标识符 %d / %d = %.1f%%（样例：%s）"
              % (agg["ident_pinyin"], agg["ident_total"],
                 agg["pinyin_ratio"] * 100,
                 "、".join(results[0]["pinyin_names"][:6]) or "无"))
        print("emoji=%d  英文注释=%d  Google docstring=%d" % (
            agg["emoji"], agg["en_comment"], agg["google_doc"]))
        print("格式化：f-string %d / %s / .format %d，f-string 占比 %s"
              % (agg["fstring"], agg["pct_fmt"], agg["dot_format"],
                 ("%.0f%%" % (agg["fstring_ratio"] * 100))
                 if agg["fstring_ratio"] is not None else "无"))
        print("类型注解痕迹：Optional[ %d 处，-> %d 处" % (
            agg["optional_hits"], agg["arrow_hints"]))
        print("-" * 60)
        for item, ok in checks:
            print("  %s %s" % ("PASS" if ok else "FAIL", item))
        print("-" * 60)
        low_files = [r for r in results
                     if r["code"] > 20 and
                     (r["comment"] + r["docstring"]) / max(r["code"], 1) < 0.10]
        if low_files:
            print("重点提示（以下文件代码>20行但注释率<10%，优先加密）：")
            for r in low_files[:8]:
                print("   %s（%d 行代码，%d 条注释）"
                      % (os.path.relpath(r["file"], args.root), r["code"],
                         r["comment"] + r["docstring"]))

    if args.gate:
        ok = all(c[1] for c in checks)
        if not args.json:
            print("审计结论：%s" % ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
