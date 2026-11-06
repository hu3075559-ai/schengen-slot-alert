# schengen-slot-alert

申根签证预约位放号提醒（需求验证版），静态站，Cloudflare Pages 托管：
https://schengen-slot-alert.pages.dev

- `/` 首页：价值主张＋订阅表单（国家/城市/签证类型/邮箱）＋边界说明
- `/guide/appointment-process/` 预约递交全流程
- `/guide/slot-patterns/` 放号规律与刷号常识
- `/guide/visa-centers/` 各国在华受理机构对照
- `/faq/`、`/privacy/`

## 口径（硬）

- 只提醒、不代抢、不代填表、不代预约（代抢属黄牛）；不收集护照号等证件信息，
  只收邮箱与预约偏好。
- 核查口径：每个工作日人工＋半自动核查一次，不是 24 小时实时监控，文案须如实。
- 本轮不收款：付费版仅在表单里收集意向勾选（对标 Schengenappointments £7.99
  买断，为二期定价参考，不在站上标价）。

## Layout / publishing

只有 `public/` 发布：Pages 项目 destination_dir=public。内容源在
`scripts/site_data.py`（国家/城市/FAQ/受理机构）与 `scripts/build.py`
（页面正文）。改内容后跑 `python3 scripts/build.py` 重新生成 public/，
再经 gh.py 推送，Pages 自动部署。

订阅落库走 leads-api（POST https://lunasign.me/api/leads，site=schengen-alert，
偏好写入 note 字段），与 china-visitor-tools 等站同一服务。
