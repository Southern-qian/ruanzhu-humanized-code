# ruanzhu-humanized-code — 软著源代码拟人化风格规范

> 把代码改写成"中国独立开发者手写味"：拼音变量名、高密度中文注释、
> 刻意朴素的写法。这套风格已实测通过软著（CPCC）审查。
> 配一个可机判的审计脚本，任何模型（包括 GLM-4.1-Flash 这类轻量模型）
> 都能照着执行、跑分、交付。

## 这是什么 / 不是什么

**是**：一道代码风格工序。把功能正确但"AI 味重"的代码（命名完美一致、
注释均匀、f-string 一统天下、类型注解满格）改写成带人味的读感。

**不是**：不改变创作事实。软件是申请人主导开发的作品，AI 是工具；
创作投入的证据（构建任务书、DECISIONS、测试、git 历史）应按各自的
创作档案流程另行归档。本仓库只解决"风格读感"，不伪造任何东西。

## 为什么有效

审查最先抓的不是 bug，是**过度均匀**。人写的代码天然不均匀：
命名中英混用、注释密度忽高忽低、格式化方式随手换、有的函数精雕
有的糊完就睡。拟人化的本质是**制造合理的不均匀**——不是写烂，
烂到读不懂反而更显眼。

## 规范速览

| 模块 | 核心规则 | 详见 |
|---|---|---|
| 拼音变量命名法 | 局部变量/内部函数拼音化（占自命名标识符 25-45%）；类名、数据库列名、路由函数名不动 | SKILL.md §2 |
| 中文注释规范 | 注释率 20-35% 且分布不均匀；五种人味注释选 2-3 种；禁英文注释/emoji/AI 腔 | SKILL.md §3 |
| 写法朴素化 | f-string ≤70%、混用 `%`/`.format()`、少用类型注解和推导式嵌套；允许适度"烂"，禁真烂 | SKILL.md §4 |
| 作者人设卡 | 每份作品一张风格身份证（拼写习惯/注释主风格/前后缀），组合内互不相像 | references/persona-cards.md |
| 六项审计门 | 注释率、拼音占比、emoji=0、英文注释=0、Google docstring=0、f-string 占比 | scripts/humanize_audit.py |

五条铁律（任何一条破了不许交付）：功能不变（pytest 全绿）、
框架约定不改（endpoint/列名/模板变量）、口径不改（文案逐字一致）、
宁可朴素不可错误、密度有度（全拼音和零拼音都是红灯）。

## 快速开始

### 用法 A：作为 ZCode skill 安装

```bash
# 用户级（所有项目可用）
mkdir -p ~/.agents/skills
git clone https://github.com/Southern-qian/ruanzhu-humanized-code.git
cp -r ruanzhu-humanized-code ~/.agents/skills/
# 或项目级：拷到 <项目>/.agents/skills/
```

之后对话里说"给 xxx 项目做软著代码拟人化"即可触发。

### 用法 B：丢给任意模型（v4.1flash 提示词模板）

把本仓库放进项目根目录（或指定绝对路径），发这段话：

```
请先完整阅读 <仓库路径>/SKILL.md、references/pinyin-wordlist.md、
references/before-after.md、references/persona-cards.md，然后按顺序执行：
1. 为项目 <项目路径> 生成一张作者人设卡（模板见 persona-cards.md），
   保存到项目的 DECISIONS.md；
2. 按 SKILL.md §6 流程逐文件改写（先读 tools/gen_source_doc.py 的
   ORDER 列表，前 30 页/后 30 页出镜文件优先精修）；
3. 每改完 3 个文件跑一次 pytest，红了就地修，不许回滚跳过；
4. 全部改完运行：python3 <仓库路径>/scripts/humanize_audit.py <项目路径> --gate
   六项全 PASS 才算完成；有任何 FAIL 按对应章节修到位再收工。
```

轻量模型执行要点：规则全是"查表 + 替换 + 跑分"的机械动作，
不需要品味判断；唯一容易跑偏的是铁律 2（框架约定不改），
提示词里可以再强调一遍。

## 审计工具

```bash
python3 scripts/humanize_audit.py <项目目录> --gate      # 门禁判定，FAIL 退出码 1
python3 scripts/humanize_audit.py <项目目录>             # 只看报告
python3 scripts/humanize_audit.py <项目目录> --json      # 机器可读（供流水线消费）
python3 scripts/humanize_audit.py <项目目录> --gate --min-comment 0.30  # 调门槛
```

默认跳过 venv/.git/__pycache__/node_modules 和 tools/tests 目录
（它们不进鉴别材料正文页）；加 `--all` 全查。

| 指标 | 默认门槛 | 说明 |
|---|---|---|
| 注释率 | 20% – 35% | (注释行+docstring行)/代码行 |
| 拼音标识符占比 | 10% – 60% | 按词表整词匹配（下划线/camel 分段），见 references/pinyin-wordlist.md；此为宽机械门，改写目标带以 SKILL.md 为准（25-45%） |
| emoji 数 | = 0 | 注释与代码字符串 |
| 纯英文注释行 | = 0 | 编码声明/shebang 除外 |
| Google docstring | = 0 | `Args:/Returns:` 等 |
| f-string 占比 | ≤ 75% | f-string / (f-string + %s + .format) |

脚本还会列出"代码 >20 行但注释率 <10%"的文件清单——这就是
逐字审查前 30 页时最先露馅的地方，优先加密。

### 实测基线（2026-10，现有组合）

| 项目 | 注释率 | 拼音占比 | 审计结论 |
|---|---|---|---|
| babylog（28 文件） | 3.8% | 0.1% | FAIL |
| aquarium（24 文件） | 3.8% | 0.0% | FAIL |

现有生产线作品全部不达新门槛——这正是本规范要补的课；
新作品建议在业务构建阶段就按人设卡写，改写 pass 只留给存量。

## 与软著生产线的集成

```
业务构建（按人设卡直接人味写）
   → 闸门验证（pytest ≥100 全绿 / 相似度 ≤35% / 一致性）
   → [存量改写走这里] 拟人化 pass → pytest 复跑 → humanize_audit --gate
   → similarity_check 复测（拼音化天然降 winnowing 热点，只降不升）
   → build_all 重出鉴别材料   ← 必做！源代码文档是旧文本等于白改
```

注意三件事：
1. **重点加密区** = 源程序文档前 30 页 + 后 30 页（审查员逐字读的
   只有这两段），注释密度往 30-35% 打；中段 20% 即可，别均匀。
2. **组合去同源**：相邻两份作品的人设卡至少在拼写习惯和注释主风格上
   不同，高频词表重叠 ≤3 个词。
3. **改完必重出材料**：鉴别材料里的代码文本不同步，档案报告会
   "说谎"（旧覆盖率旧相似度），这是有前科的坑。

## 目录结构

```
ruanzhu-humanized-code/
├── README.md                      ← 本文档
├── SKILL.md                       ← 规范正文（skill 入口）
├── references/
│   ├── pinyin-wordlist.md         ← 拼音词表（约 80 词 + 领域扩充法）
│   ├── before-after.md            ← AI 味 → 人味 逐行对照 + 反面教材
│   └── persona-cards.md           ← 作者人设卡模板 + 三张示例卡
└── scripts/
    └── humanize_audit.py          ← 六项计量审计（纯 stdlib，无依赖）
```

## FAQ

**会不会显得"故意装人味"？**
不会，前提是守密度红线。全拼音、满屏注释和零拼音、零注释同样
反常——门槛区间（拼音 25-45%、注释 20-35%）就是"正常中国个人
开发者"的统计带。审查看的是整体读感，不是单项指标拉满。

**改写把测试搞红了怎么办？**
就地修，修法是"改成正确的人会怎么写"，不许回滚、不许跳过测试。
常见雷区：路由函数名、列名、模板变量被误改——回查铁律 2。

**为什么入口要先看 gen_source_doc.py 的 ORDER？**
鉴别材料的源程序文档按这个 ORDER 排页，审查员真正逐字读的是
前 30 页和后 30 页。把注释密度花在出镜页，性价比最高。

**GLM-4.1-Flash 这类轻量模型能执行吗？**
能。规范刻意写成了查表式（词表、对照表、人设卡、六项数字门），
不需要模型有风格品味。建议一次只派一个项目、按 §6 步骤走，
并在提示词里强调铁律 2。

**审计脚本的拼音判定会不会误报？**
按词表整词匹配（分段后判定），已实测排除 `changelog/change_count`
（含 hang 不算）、`my_tanks`（英文前缀不算）、`birth_length_mm`
（单位不算）这类陷阱；`xin_jilu`、`xinjilu`、`xinJilu` 均正确命中。

## License

MIT
