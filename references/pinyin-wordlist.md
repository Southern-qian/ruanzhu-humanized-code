# 拼音高频词表（拟人化命名用）

> 用法：按领域挑 15-25 个词作为本份作品的高频词，写进人设卡。
> 词表只是素材库——不是每个词都要用，更不要为了凑数硬塞。
> 审计脚本按这份词表统计拼音标识符占比，新增词请同步
> `scripts/humanize_audit.py` 里的 `PINYIN_WORDS`。

## 通用动作词

| 拼音 | 词 | 常见组合 |
|---|---|---|
| tianjia / zeng | 添加 / 增 | `tianjia_jilu` 新增记录 |
| shanchu / sc | 删除 | `sc_jilu`、`shanchu_row` |
| xiugai / xg | 修改 | `xg_mima` 改密码 |
| chaxun / cx | 查询 | `cx_jilu` 查记录 |
| baocun / bc | 保存 | `bc_biaodan` 存表单 |
| denglu / dl | 登录 | `dl_yonghu`、`denglu_ok` |
| tuichu | 退出 | `tuichu_sys` |
| daoru / daochu | 导入 / 导出 | `dc_excel` 导出 |
| suoding / jiesuo | 锁定 / 解锁 | `suoding_zhanghu` |
| tongji / tj | 统计 | `tj_shuju`、`tongji_yue` 月统计 |
| fenye / fy | 翻页 | `fy_da_`、`fenye_info` |
| shengcheng | 生成 | `sc_baobiao` 生成报表 |
| jisuan / js | 计算 | `js_zongjia` 算总价 |
| jiancha / jc | 检查 | `jc_hefa` 合法性检查 |
| tishi / ts | 提示 | `ts_xinxi` 提示信息 |
| quxiao | 取消 | `qx_dingdan` |
| tijiao | 提交 | `tj_biaodan` |

## 通用名词

| 拼音 | 词 | 常见组合 |
|---|---|---|
| yonghu / yh | 用户 | `yh_id`、`yonghu_ls` |
| mima / mm | 密码 | `mm_cuowu` 密码错误 |
| zhanghu / zh | 账户 | `zh_yue` 账户余额 |
| quanxian / qx | 权限 | `qx_pan` 权限判断 |
| jilu / jl | 记录 | `jl_ls`、`xin_jilu` |
| liebiao / lb | 列表 | `lb_ye` 列表页 |
| xiangqing / xq | 详情 | `xq_ye` 详情页 |
| shezhi / sz | 设置 | `sz_ye` 设置页 |
| biaodan / bd | 表单 | `bd_shuju` 表单数据 |
| shuju / sj | 数据 | `sj_yuan` 数据源 |
| mingcheng / mc | 名称 | `mc_chongfu` 名称重复 |
| leixing / lx | 类型 | `lx_ma` 类型码 |
| zhuangtai / zt | 状态 | `zt_zhi` 状态值 |
| riqi / rq | 日期 | `rq_fanwei` 日期范围 |
| shijian / sj2 | 时间 | `sj_cuo` 时间戳（注：sj 与"数据"缩写撞车，二选一） |
| shuliang / sl | 数量 | `sl_heji` 数量合计 |
| jine / danjia | 金额 / 单价 | `zong_jine` 总金额 |
| beizhu / bz | 备注 | `bz_xx` 备注信息 |
| neirong / nr | 内容 | `nr_changdu` 内容长度 |
| tupian / tp | 图片 | `tp_lu_jing` 图片路径 |
| suoyin / sy | 索引 | `sy_hao` 索引号 |
| dingdan / dd | 订单 | `dd_zhuangtai` |
| fujian / fj | 附件 | `fj_ls` |
| biaoqian / bq | 标签 | `bq_yun` 云标签 |
| fenlei / fl | 分类 | `fl_shu` 分类树 |

## 领域示例（按需扩充进人设卡）

| 领域 | 词例 |
|---|---|
| 水族 | `yanggang`(养缸) `huan_shui`(换水) `wei_shi`(喂食) `shui_zhi`(水质) |
| 育儿 | `weiyang`(喂养) `shuijiao`(睡觉) `nianling_y`(月龄) `tidian`(体测) |
| 财务 | `shou_zhi`(收支) `yusuan`(预算) `jiezhuan`(结转) `zhangmu`(账目) |
| 求职 | `mianjing`(面经) `tou_di`(投递) `yaoqing`(邀约) `fankui`(反馈) |
| 菜谱 | `shi_cai`(食材) `peng_ren`(烹饪) `pei_cai`(配菜) `wei_jing`(味型) |

## 拼写红线

1. 一份作品内**同一词只用一种拼法**（`jilu` 就别再出 `jl`，
   除非人设卡明确声明双轨且场景不重叠）。
2. 缩写避免歧义：`sj` 同时像"数据/时间/设计"——用缩写就要在
   人设卡里写死每个缩写的含义。
3. 别用带声调或非普通话拼法（审查员看不懂的方言拼音起反效果）。
4. `sj2` 这种带数字的消歧写法允许，但每份最多 1-2 处。
