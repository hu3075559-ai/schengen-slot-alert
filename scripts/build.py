# -*- coding: utf-8 -*-
"""Render the schengen-slot-alert static site into public/.

Usage: python3 scripts/build.py
Content lives in scripts/site_data.py and in the PAGES bodies below.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_data import SITE, COUNTRIES, CITIES, VISA_TYPES, PROVIDERS, FAQ, SOURCES_NOTE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "public")
TODAY = "2026-11-06"

GA_ID = "G-Q5SV4DD3W7"
GTAG = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '%s');
</script>
""" % (GA_ID, GA_ID)

HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
%GTAG%
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%TITLE%</title>
<meta name="description" content="%DESC%">
<link rel="canonical" href="%CANON%">
<meta property="og:type" content="%OGTYPE%">
<meta property="og:site_name" content="%SITENAME%">
<meta property="og:title" content="%TITLE%">
<meta property="og:description" content="%DESC%">
<meta property="og:url" content="%CANON%">
<meta property="og:image" content="%DOMAIN%/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/assets/style.css">
%JSONLD%
</head>
<body>
<header class="site-header">
  <a class="brand" href="/">%SITENAME%</a>
  <nav>
    <a href="/guide/appointment-process/">预约流程</a>
    <a href="/guide/slot-patterns/">放号规律</a>
    <a href="/guide/visa-centers/">受理机构</a>
    <a href="/faq/">常见问题</a>
  </nav>
</header>
<main>
"""

FOOT = """
</main>
<footer class="site-footer">
  <p>%SITENAME% · %TAGLINE%。只做放号信息提醒，不代抢、不代填表、不代预约，不收集任何证件信息。</p>
  <p><a href="/privacy/">隐私说明</a> · <a href="/faq/">常见问题</a> · <a href="https://gxccz.com/">gxccz 工具导航</a></p>
  <p>友情链接：<a href="https://en.gxccz.com/visitor-tools/">来华签证工具</a></p>
  <p>© 2026 gxccz.com · 站长QQ：65363885 · 联系邮箱 <a href="mailto:kefu@gxccz.com">kefu@gxccz.com</a> · <a href="https://gxccz.com/privacy/">隐私与条款</a></p>
</footer>
<script src="/assets/config.js"></script>
<script src="/assets/subscribe.js"></script>
</body>
</html>
"""


def page(path, title, desc, body, ogtype="website", jsonld=None):
    canon = SITE["domain"] + path
    html = HEAD.replace("%TITLE%", title).replace("%DESC%", desc)
    html = html.replace("%GTAG%", GTAG)
    html = html.replace("%CANON%", canon).replace("%OGTYPE%", ogtype)
    html = html.replace("%SITENAME%", SITE["name"]).replace("%DOMAIN%", SITE["domain"])
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">\n' + json.dumps(jsonld, ensure_ascii=False, indent=1) + "\n</script>"
    html = html.replace("%JSONLD%", ld)
    html += body
    html += FOOT.replace("%SITENAME%", SITE["name"]).replace("%TAGLINE%", SITE["tagline"])
    out = os.path.join(PUBLIC, path.lstrip("/"), "index.html") if path != "/" else os.path.join(PUBLIC, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def options(items, placeholder):
    opts = ['<option value="">%s</option>' % placeholder]
    for it in items:
        opts.append('<option value="%s">%s</option>' % (it, it))
    return "\n        ".join(opts)


FORM = """
<section class="card" id="subscribe">
  <h2>订阅放号提醒（验证期免费）</h2>
  <form class="subscribe-form" data-source="home-form" novalidate>
    <div class="grid">
      <label>目的国（主访国）
        <select name="country" required>
        %COUNTRY_OPTS%
        </select>
      </label>
      <label>递交城市（按常住地领区）
        <select name="city" required>
        %CITY_OPTS%
        </select>
      </label>
      <label>签证类型
        <select name="vtype" required>
        %VTYPE_OPTS%
        </select>
      </label>
      <label>计划出行月份（可选）
        <input type="month" name="travel_month">
      </label>
    </div>
    <label>接收提醒的邮箱
      <input type="email" name="email" required placeholder="you@example.com" autocomplete="email">
    </label>
    <label class="check">
      <input type="checkbox" name="paid_interest" value="yes">
      付费版筹备中：更高核查频率＋多组合同步监控，上线时优先通知我
    </label>
    <input type="text" name="hp" value="" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
    <button type="submit">订阅提醒</button>
    <p class="form-status" role="status"></p>
    <p class="fine">只收集邮箱与上述预约偏好，不收集护照号等任何证件信息。退订：回复任意提醒邮件注明「退订」。</p>
  </form>
</section>
"""

def form_html(source):
    return (FORM.replace("%COUNTRY_OPTS%", options(COUNTRIES, "请选择目的国"))
                .replace("%CITY_OPTS%", options(CITIES, "请选择递交城市"))
                .replace("%VTYPE_OPTS%", options(VISA_TYPES, "请选择签证类型"))
                .replace('data-source="home-form"', 'data-source="%s"' % source))


MAIL_MOCK = """
<section class="card">
  <h2>提醒邮件长这样（示例）</h2>
  <p class="fine">下面是一封提醒邮件的示意版式，仅作样式参考——不是真实放号通知。真实邮件只在你订阅的组合出现新时段时才发。</p>
  <div class="mail-mock">
    <p class="m-meta">发件人：申根号位提醒</p>
    <p class="m-meta"><strong>主题：法国 · 上海 · 旅游 — 检测到新的可预约时段</strong></p>
    <hr>
    <p>你好，你订阅的组合（法国 · 上海 · 旅游）检测到新的可预约时段。</p>
    <p>请尽快前往官方预约系统查看并自行预约，热门时段通常很快被约满。</p>
    <p><span class="m-cta">去官方系统查看 →</span></p>
    <p class="m-foot">这是一封提醒邮件，我们不代抢、不代预约。退订请直接回复本邮件注明「退订」。</p>
  </div>
</section>
"""

HOME_BODY = """
<section class="hero">
  <h1>申根签证预约位，一有放号就邮件提醒你</h1>
  <p class="lead">法国、德国、意大利等热门申根国家的递签预约经常约满。与其每天自己刷预约系统，不如交给我们盯：每个工作日核查你所选「国家＋城市」的放号情况，发现新的可预约时段，当天发邮件提醒，你再去官方渠道完成预约。</p>
</section>

<section class="card warn">
  <h2>先说清边界</h2>
  <ul>
    <li><strong>只提醒</strong>：我们不代抢号、不代填表、不代预约。预约名额与申请人信息绑定、不可转让，「代抢包中」多为黄牛，请勿上当。</li>
    <li><strong>核查频率</strong>：每个工作日人工＋半自动核查一次，不是 24 小时实时监控；周末与节假日放出的号，可能在下一个工作日才被核查到。</li>
    <li><strong>只收邮箱</strong>：订阅只需邮箱与预约偏好（国家、城市、类型、出行月份），不收集护照号等任何证件信息。</li>
  </ul>
</section>

%FORM%

<section class="card">
  <h2>怎么运作</h2>
  <ol class="steps">
    <li><strong>选组合</strong>：按你的主访国和常住地领区，选择目的国与递交城市，留下邮箱。</li>
    <li><strong>我们盯号</strong>：每个工作日核查该组合在官方预约系统（VFS Global / TLScontact / BLS 等）的放号情况。</li>
    <li><strong>有号通知</strong>：发现新的可预约时段，当天发邮件到你的邮箱；你第一时间去官方系统自行预约。</li>
  </ol>
</section>

%MAIL_MOCK%

<section class="card">
  <h2>先把时间账算清（官方口径）</h2>
  <ul class="data">
    <li>签证费：成人 <strong>90 欧元</strong>，6–12 岁儿童 45 欧元，6 岁以下免费（2024 年 6 月 11 日起执行，另付签证中心服务费）。</li>
    <li>递交窗口：最早可提前 <strong>6 个月</strong>递交，最晚须在出行前 <strong>15 天</strong>递交。</li>
    <li>审理时间：通常 <strong>15 个自然日</strong>出结果，个别情况可延长至 45 天。</li>
    <li>旅行医疗保险：保额不低于 <strong>3 万欧元</strong>，为申根签证法定要求。</li>
  </ul>
  <p class="fine">数据来源：欧盟委员会《签证法典》申根签证申请说明（核查日期：2026-11-06）。这意味着：预约位本身还要再往前留量——旺季时「约不到号」往往比「审理慢」更卡行程。</p>
</section>

<section class="card">
  <h2>申根预约攻略</h2>
  <ul class="links">
    <li><a href="/guide/appointment-process/">申根签证预约递交全流程</a>：从定主访国到取护照的完整步骤。</li>
    <li><a href="/guide/slot-patterns/">放号规律与刷号常识</a>：没有内部时刻表，只有这些真实规律。</li>
    <li><a href="/guide/visa-centers/">各国在华受理机构与领区常识</a>：你该去 VFS、TLScontact 还是 BLS？</li>
    <li><a href="/guide/no-appointment-slots/">申根签证预约不到号怎么办</a>：先分清是哪种「约不到」，再按五步走。</li>
    <li><a href="/guide/slot-release-time/">申根签证放号时间有规律吗</a>：没有统一时刻表，规律在号源的来源，不在钟点。</li>
    <li><a href="/guide/france-tlscontact-how-to-book/">法国申根签证预约 TLScontact 怎么约</a>：先填 France-Visas 表，再到 TLScontact 按领区约号。</li>
  </ul>
</section>
"""

GUIDE_PROCESS = """
<article>
<h1>申根签证预约递交全流程</h1>
<p class="lead">申根签证的难点常常不在材料，而在「约不到递交时间」。先把全流程走一遍，你就知道每个环节该提前多久动手。</p>

<h2>第一步：确定主访国</h2>
<p>向停留时间最长的申根国申请；如果在几个国家停留时间相同，向第一个入境的国家申请。申请错了国家，签证中心可能不予受理。一次行程只申请一个国家的申根签证，签出后可通行整个申根区。</p>

<h2>第二步：确认你的领区和递交城市</h2>
<p>各国在华按领区受理，原则上要按常住地所属领区选择递交城市，跨领区递交可能被拒收。同一国家在不同城市的号源紧张程度差别很大，但不能为了「哪里有号」随意跨领区。各机构的对应关系见<a href="/guide/visa-centers/">受理机构对照页</a>。</p>

<h2>第三步：在线填表与准备材料</h2>
<p>多数国家要求先在官方系统完成在线申请（如法国的 France-Visas、瑞士要求先在线填好申请表）才能预约递交时间。常规材料包括：护照、照片、行程单、机票酒店预订单、保险、在职/资金证明等，以目的国官方清单为准。</p>

<h2>第四步：预约递交时段</h2>
<p>在受理机构的预约系统（VFS Global / TLScontact / BLS 等）注册账号、选择城市与时段。热门领区在旺季（寒暑假、国庆、春节前）经常提前数周约满。最早可提前 6 个月递交，建议行程一确定就启动，不要等材料全齐了才想起来约号——号和材料可以并行准备。</p>

<h2>第五步：到中心递交并录指纹</h2>
<p>按预约时间提前约 15 分钟到达，递交材料、缴纳签证费与服务费、采集指纹。首次申请申根签证必须本人到场录指纹；59 个月内录过指纹的申请人，部分情形可免于再次采集（以各国规定为准）。</p>

<h2>第六步：等待审理与领取护照</h2>
<p>通常 15 个自然日出结果，个别情况可延长至 45 天。可选择自取或快递返还。注意：最晚递交时间是出行前 15 天，但那是没有给任何意外留余量的底线，不要按底线规划。</p>

<section class="card">
<h2>关键数字（官方口径）</h2>
<ul class="data">
  <li>签证费：成人 90 欧元 / 6–12 岁 45 欧元 / 6 岁以下免费（2024-06-11 起）。</li>
  <li>递交窗口：出行前 6 个月 ～ 15 天之间。</li>
  <li>审理：通常 15 天，最长可至 45 天。</li>
  <li>旅行医疗保险保额：不低于 3 万欧元。</li>
</ul>
<p class="fine">%SOURCES%</p>
</section>
<p><a href="/#subscribe">→ 回到首页订阅放号提醒</a></p>
</article>
"""

GUIDE_PATTERNS = """
<article>
<h1>申根签证放号规律与刷号常识</h1>
<p class="lead">先说实话：各签证中心<strong>没有公开发布的固定放号时间表</strong>。任何声称掌握「内部放号时刻」「包刷到号」的说法都不可靠。但号源紧张的成因和真实存在的规律，是可以讲清楚的。</p>

<h2>为什么热门领区总是约满</h2>
<ul>
  <li><strong>旺季集中</strong>：寒暑假、国庆、春节前是出行高峰，递交需求成倍放大，而受理窗口数量相对固定。</li>
  <li><strong>领区受理量不均</strong>：北京、上海、广州等大领区的申请量远高于其他城市，同一国家不同城市的紧张程度完全不同。</li>
  <li><strong>窗口期叠加</strong>：最早只能提前 6 个月递交，审理又要留出 15–45 天，实际可操作的时间带比想象中窄。</li>
</ul>

<h2>真实存在的规律</h2>
<ul>
  <li><strong>取消与改期会回流号位</strong>：他人取消或改期的时段会重新回到系统里，所以临近日期偶尔能刷到「捡漏」位——这是零星出现的，不是批量放号。</li>
  <li><strong>临时加场会成批放号</strong>：签证中心在旺季增加受理场次或人力时，会一次性放出一批新时段。这类放号没有预告，只能靠持续盯。</li>
  <li><strong>新月份/新周期开放时会放号</strong>：部分国家的系统按周期开放可预约日期，开放当日号相对充足，几天内就会被订完。</li>
  <li><strong>冷门国家/冷门城市明显宽松</strong>：如果行程灵活、主访国停留时间可以调整，换一个受理量小的国家申请，难度会低很多（但必须符合主访国规则，不能为了好约而造假行程）。</li>
</ul>

<h2>给你的可执行建议</h2>
<ol>
  <li>行程一确定就启动：官方允许提前 6 个月递交，越早动手，号越好约。</li>
  <li>材料与约号并行：不要等材料全齐才去刷号。</li>
  <li>经验口径：建议在出行前 45–60 天启动申请，给审理和意外留出余量。</li>
  <li>自己刷 + 订阅提醒双管齐下：有空时自己刷官方系统，同时订阅本站提醒，让工作日核查帮你兜底。</li>
</ol>

<h2>务必避开的坑</h2>
<ul>
  <li><strong>黄牛代抢</strong>：预约名额与申请人信息绑定、不可转让；买来的号可能因信息不一致被拒收，还附带个人信息泄露风险。</li>
  <li><strong>收费「内部渠道」</strong>：签证中心与使领馆多次提示，预约通过官方系统进行，除签证费与服务费外不应再向任何第三方付「抢号费」。</li>
  <li><strong>假行程凑主访国</strong>：为了好约而编造主访国行程，审理阶段被识破的后果是拒签并留记录。</li>
</ul>

<p class="fine">%SOURCES%</p>
<p><a href="/#subscribe">→ 回到首页订阅放号提醒</a></p>
</article>
"""

GUIDE_CENTERS = """
<article>
<h1>各国在华受理机构与领区常识</h1>
<p class="lead">申根各国在华的递交渠道并不统一：有的走 VFS Global，有的走 TLScontact，还有 BLS、GVCW 或领馆直收。先对上号，再去刷预约。</p>

<h2>受理机构对照表</h2>
<table class="tbl">
  <thead><tr><th>目的国</th><th>受理机构</th><th>说明</th></tr></thead>
  <tbody>
%PROVIDER_ROWS%
  </tbody>
</table>
<p class="fine">对照关系整理自各国使领馆公开页面（核查日期：2026-11-06），受理安排可能调整，以当期公告为准。</p>

<h2>领区的三条常识</h2>
<ul>
  <li><strong>按常住地选领区</strong>：原则上按你的常住地（工作/居住地）所属领区递交，跨领区递交可能被拒收，不要只看哪里有号。</li>
  <li><strong>各国领区划分不完全一致</strong>：同一个省份，在 A 国属上海领区、在 B 国可能属北京领区，逐国核对。</li>
  <li><strong>城市网点数量差别大</strong>：以德国为例，VFS 在华设有 15 个城市的签证中心；而部分国家只在少数城市设点，可能需要跨城递交。</li>
</ul>

<h2>官方入口（部分）</h2>
<ul>
  <li>西班牙（BLS 预约）：web.blscn.cn；西班牙驻华领事申根签证说明见西班牙外交部官网领事页面。</li>
  <li>德国：德国驻华使领馆官网（china.diplo.de）的签证问答页有最权威的流程与领区说明。</li>
  <li>瑞士：瑞士驻华使领馆官网（schweiz-china.eda.admin.ch）「应该去哪里申请申根签证」页面。</li>
  <li>法国：先在 France-Visas 完成在线申请，再经 TLScontact 预约递交。</li>
</ul>

<p class="fine">%SOURCES%</p>
<p><a href="/#subscribe">→ 回到首页订阅放号提醒</a></p>
</article>
"""

GUIDE_NO_SLOTS = """
<article>
<h1>申根签证预约不到号怎么办</h1>
<p class="lead">先说结论：约不到号时别急着找人「代抢」，先分清你遇到的是哪种「约不到」——多数情况要么是选错了城市或签证类别，要么是正赶上旺季号源紧张。按下面五步走：核对官方渠道 → 利用取消回流与加场放号 → 算清时间账 → 自己刷号加订阅提醒兜底。整个过程只走官方预约系统，不向任何第三方付「抢号费」。</p>

<h2>第一步：先分清你遇到的是哪种「约不到」</h2>
<ul>
  <li><strong>系统显示无可预约时段</strong>：最常见。说明该城市当前开放的日期都已被约满，不代表之后永远没号——取消回流与加场放号都会产生新时段。</li>
  <li><strong>城市或领区选错了</strong>：申根各国按领区受理，原则上按常住地所属领区选择递交城市。跨领区递交可能被拒收，不要只看「哪里有号」就换城市，换之前先核对领区划分（见<a href="/guide/visa-centers/">受理机构对照页</a>）。</li>
  <li><strong>在线申请没走完，进不了预约环节</strong>：多数国家要求先在官方系统完成在线申请（如法国的 France-Visas）才能预约递交时间。卡在填表环节会误以为「约不到号」，先把前置步骤走完。</li>
  <li><strong>签证类别选错了</strong>：旅游、商务、探亲等类别的号源是分开的，类别选错可能一直显示无号。按真实出行目的选择。</li>
</ul>

<h2>第二步：回到官方渠道再核对一遍</h2>
<ol>
  <li>从目的国使领馆官网的签证页面出发，点它给出的官方链接进入预约系统（VFS Global / TLScontact / BLS 等），不要从搜索引擎里的中介页面进入。</li>
  <li>逐项核对：目的国、递交城市、签证类别、申请人人数是否都选对了。</li>
  <li>看看当地系统是否提供官方等候名单：部分国家和地区的预约系统设有官方排队或等候机制，有就加入——这是官方渠道，比反复刷新更省力。</li>
  <li>确认账号信息无误：注册邮箱、手机号要能正常收信，提醒与确认信息都走这些渠道。</li>
</ol>

<h2>第三步：理解放号的真实规律</h2>
<p>各签证中心没有公开发布的固定放号时间表，所谓「内部放号时刻」「几点必放号」都不可靠。但以下三类新号源是真实存在的：</p>
<ul>
  <li><strong>取消与改期回流</strong>：他人取消或改期的时段会重新回到系统里，临近日期偶尔能刷到「捡漏」位——零星出现，不是批量放号。</li>
  <li><strong>临时加场批量放号</strong>：签证中心在旺季增加受理场次或人力时，会一次性放出一批新时段。这类放号没有预告，只能靠持续盯。</li>
  <li><strong>新周期开放放号</strong>：部分国家的系统按周期开放可预约日期，开放当日号相对充足，几天内就会被订完。</li>
</ul>
<p>更完整的规律分析见<a href="/guide/slot-patterns/">放号规律与刷号常识</a>。</p>

<h2>第四步：算一算时间账，行程太紧就改期</h2>
<p>约不到号有时不是号的问题，而是行程定得太紧。按官方口径倒推：最早可提前 6 个月递交，最晚须在出行前 15 天递交，审理通常 15 个自然日、个别情况可延长至 45 天。如果按出行日倒推已经逼近最晚递交时间，即使今天约到号也可能赶不上——这时最稳妥的办法是调整出行日期，把申请窗口拉长。经验口径：建议在出行前 45–60 天启动申请。</p>

<h2>第五步：自己刷号加订阅提醒，双管齐下</h2>
<ul>
  <li><strong>自己刷</strong>：有空时直接刷官方预约系统，重点关注取消回流位与新周期开放日。</li>
  <li><strong>订阅提醒兜底</strong>：在本站订阅你所选的「国家＋城市」组合，我们每个工作日人工＋半自动核查一次，发现新的可预约时段当天发邮件提醒，你再去官方系统自行预约。提醒只能帮你尽早知道，不能保证一定约得上；本站也不是 24 小时实时监控，周末与节假日放出的号可能在下一个工作日才被核查到。</li>
  <li><strong>行程灵活可考虑换主访国</strong>：冷门国家的受理量小、号明显宽松——但前提是符合主访国规则（停留最长或首入境），绝不能为了好约而编造行程。</li>
</ul>

<h2>务必避开的坑</h2>
<ul>
  <li><strong>黄牛代抢</strong>：预约名额与申请人信息绑定、不可转让；买来的号可能因信息不一致被签证中心拒收，还附带个人信息泄露风险。</li>
  <li><strong>收费「内部渠道」「包中」</strong>：签证中心与使领馆多次提示，预约通过官方系统进行，除签证费与服务费外不应再向任何第三方付「抢号费」。任何声称掌握内部放号时刻的说法都不可靠。</li>
  <li><strong>用机器人或脚本刷号</strong>：可能触发系统风控导致账号受限，得不偿失。</li>
</ul>

<section class="card">
<h2>关键数字（官方口径）</h2>
<ul class="data">
  <li>递交窗口：出行前 6 个月 ～ 15 天之间。</li>
  <li>审理时间：通常 15 个自然日，个别情况可延长至 45 天。</li>
  <li>签证费：成人 90 欧元 / 6–12 岁 45 欧元 / 6 岁以下免费（2024-06-11 起）。</li>
  <li>旅行医疗保险保额：不低于 3 万欧元。</li>
  <li>本站核查频率：每个工作日人工＋半自动核查一次，不是 24 小时实时监控。</li>
</ul>
<p class="fine">%SOURCES%</p>
</section>

<section class="card">
<h2>常见问题</h2>
<div class="faq-item"><h3>申根签证预约显示没有号，是不是就约不上了？</h3><p>不是。显示无号只代表当前开放的日期已被约满。取消回流、临时加场与新周期开放都会产生新时段，持续关注官方系统或订阅放号提醒，仍有机会约到。</p></div>
<div class="faq-item"><h3>换一个城市递交是不是更容易约到号？</h3><p>不同城市的号源紧张程度确实差别很大，但申根各国按领区受理，原则上要按常住地所属领区选择递交城市。跨领区递交可能被拒收，换城市前务必先核对领区划分，不要只看哪里有号。</p></div>
<div class="faq-item"><h3>找人代抢号靠谱吗？</h3><p>不靠谱。预约名额与申请人信息绑定、不可转让，买来的号可能因信息不一致被拒收，还有个人信息泄露风险。签证中心与使领馆多次提示：预约通过官方系统进行，不要向第三方付「抢号费」。</p></div>
<div class="faq-item"><h3>你们的放号提醒能保证我约到号吗？</h3><p>不能保证。提醒只能帮你尽早知道新时段出现，热门领区的号可能很快被订完，收到提醒后请第一时间去官方系统自行预约。本站每个工作日核查一次，不是 24 小时实时监控。</p></div>
</section>
<p><a href="/guide/appointment-process/">→ 先看预约递交全流程</a> · <a href="/#subscribe">→ 回到首页订阅放号提醒</a></p>
</article>
"""

GUIDE_RELEASE_TIME = """
<article>
<h1>申根签证放号时间有规律吗</h1>
<p class="lead">先说结论：没有统一的放号时刻表。VFS Global、TLScontact、BLS 等受理机构从未公开发布「每天几点放号」的固定时间，各国、各城市、各签证类别的开放节奏也不一样。真正有规律的不是钟点，而是号源的来源——新周期开放、旺季临时加场、他人取消回流，这三类号出现的时机是可以预判的。凡是声称「某点必放号」「内部时刻表」的说法，都不可靠，更不要为此向任何人付费。</p>

<h2>一、为什么没有统一的放号时间</h2>
<ul>
  <li><strong>受理机构不止一家</strong>：法国、荷兰走 TLScontact，西班牙走 BLS International，德国、意大利、瑞士等多数国家走 VFS Global，希腊走 GVCW，少数类别由使领馆直接受理（对照见<a href="/guide/visa-centers/">受理机构对照页</a>）。每家系统独立运行，不存在全申根统一的放号钟点。</li>
  <li><strong>同一机构各城市也不同</strong>：号源由各签证中心按本地受理能力与领区需求开放，北京、上海等大领区的紧张程度与小领区完全不同，开放节奏自然也不同。</li>
  <li><strong>官方从未公布时刻表</strong>：各使领馆与签证中心的公开说明只讲预约流程与递交窗口（最早提前 6 个月、最晚出行前 15 天），没有任何一家公布过每日放号的具体时点。网上流传的「凌晨放号」「整点放号」多为个人经验或中介话术，换个国家、换个城市就不成立。</li>
</ul>

<h2>二、真正的规律：号从哪来，什么时候来</h2>
<ul>
  <li><strong>新周期开放时批量出现</strong>：部分国家的系统按周期开放新的可预约日期，开放当日号相对充足，之后几天内被订完。规律是「盯新日期的开放」，不是「盯某个钟点」。</li>
  <li><strong>旺季加场时成批放号</strong>：寒暑假、国庆、春节前需求集中时，签证中心增加受理场次或人力，会一次性放出一批新时段。这类放号没有预告，出现时间取决于中心的排班决定。</li>
  <li><strong>取消与改期随时回流</strong>：他人取消或改期的时段会重新回到系统，零星、随机地出现，临近日期偶尔能刷到「捡漏」位。所谓「深夜刷到号」，多半刷到的就是这类回流位——是运气，不是时刻表。</li>
  <li><strong>部分系统有官方候补机制</strong>：少数国家或地区的预约系统设有官方等候名单，有空位时按登记顺序通知。当地有候补机制时，登记候补比反复刷新更省力，也更可靠。</li>
</ul>

<h2>三、按这个节奏刷号，比守钟点有用</h2>
<ol>
  <li>行程一确定就启动：官方允许提前 6 个月递交，越早进入系统，能碰到的新周期开放与加场就越多。</li>
  <li>先把前置步骤走完：多数国家要求先完成在线申请（如法国先在 France-Visas 填表）才能预约；账号提前注册好、信息提前填好，放号时才抢得过别人。完整步骤见<a href="/guide/appointment-process/">预约递交全流程</a>。</li>
  <li>材料与约号并行准备，不要等材料全齐才开始刷号。</li>
  <li>以天为单位持续关注，而不是守着某个整点反复刷新：新周期与加场都是以「批」出现的，持续在场比卡点更重要。</li>
  <li>自己刷加订阅提醒兜底：本站对你订阅的「国家＋城市」组合每个工作日人工＋半自动核查一次，发现新的可预约时段当天发邮件提醒。这不是 24 小时实时监控，也不能保证一定约得上；周末与节假日放出的号，可能在下一个工作日才被核查到。</li>
</ol>

<h2>四、这些「放号规律」不要信</h2>
<ul>
  <li><strong>「每天凌晨/整点必放号」</strong>：没有任何官方依据。不同机构、不同城市的系统各自运行，不存在统一钟点。</li>
  <li><strong>收费的「内部放号时间」</strong>：签证中心与使领馆多次提示，预约只通过官方系统进行，除签证费与服务费外不应向第三方付「抢号费」；卖「内部时刻」的和卖「代抢包中」的，是同一类生意。</li>
  <li><strong>用脚本或机器人高频刷号</strong>：可能触发系统风控导致账号受限，反而耽误正事。</li>
</ul>

<section class="card">
<h2>关键数字（官方口径）</h2>
<ul class="data">
  <li>递交窗口：出行前 6 个月 ～ 15 天之间。</li>
  <li>审理时间：通常 15 个自然日，个别情况可延长至 45 天。</li>
  <li>签证费：成人 90 欧元 / 6–12 岁 45 欧元 / 6 岁以下免费（2024-06-11 起）。</li>
  <li>本站核查频率：每个工作日人工＋半自动核查一次，不是 24 小时实时监控。</li>
</ul>
<p class="fine">%SOURCES%</p>
</section>

<section class="card">
<h2>常见问题</h2>
<div class="faq-item"><h3>申根签证放号时间有规律吗？</h3><p>没有统一的时刻表。VFS Global、TLScontact、BLS 等机构从未公布每日固定放号时间，各国各城市节奏不同。有规律的是号源来源：新周期开放、旺季加场会批量放号，他人取消会零星回流——盯这三类时机，比守某个钟点有用。</p></div>
<div class="faq-item"><h3>每天几点刷号最容易刷到？</h3><p>没有官方认可的「最佳时点」。取消回流位全天都可能随机出现，加场与新周期开放也没有预告。与其守整点，不如提前把账号与在线申请准备好，以天为单位持续关注，并用订阅提醒兜底。</p></div>
<div class="faq-item"><h3>有人说凌晨刷到了号，是不是凌晨真的会放号？</h3><p>凌晨刷到的多半是他人取消或改期回流的零星时段，这类号全天随机出现，只是深夜刷的人少、竞争小，才显得「凌晨有号」。它不是批量放号的时刻表，换一天、换一个城市就未必成立。</p></div>
<div class="faq-item"><h3>你们的放号提醒是自动实时监控吗？</h3><p>不是。本站目前没有自动实时监控：核查在每个工作日以人工＋半自动方式进行一次，发现新的可预约时段当天发邮件提醒。提醒只能帮你尽早知道，不能保证一定约得上；付费版（更高核查频率）正在筹备中，尚未上线。</p></div>
</section>
<p><a href="/guide/no-appointment-slots/">→ 约不到号时按这五步走</a> · <a href="/#subscribe">→ 回到首页订阅放号提醒</a></p>
</article>
"""


PRIVACY_BODY = """
<article>
<h1>隐私说明</h1>
<p>本站（%SITENAME%）只收集完成放号提醒所必需的最少信息：</p>
<ul>
  <li><strong>收集什么</strong>：你的邮箱，以及订阅时选择的预约偏好（目的国、递交城市、签证类型、计划出行月份）和是否愿意接收付费版上线通知。</li>
  <li><strong>绝不收集</strong>：护照号、身份证号等任何证件信息；请不要通过邮件或其他方式向我们发送这类信息。</li>
  <li><strong>用来做什么</strong>：仅用于核查你所订阅组合的放号情况并向你发送提醒邮件；付费版意向仅用于上线时通知。不出售、不与无关第三方共享订阅信息。</li>
  <li><strong>保存与删除</strong>：订阅信息保存在我们的订阅数据库中。回复任意一封提醒邮件注明「退订」，我们会删除你的订阅信息。</li>
</ul>
<p>本站为需求验证阶段的服务，核查在工作日以人工＋半自动方式进行，不承诺实时性与约号结果。</p>
</article>
"""

GUIDE_FR_TLS = """
<article>
<h1>法国申根签证预约 TLScontact 怎么约</h1>
<p class="lead">先说结论：法国在华签证递交走 TLScontact，预约分两步——先在法国官方 France-Visas 网站填好在线申请表，再到 TLScontact 官网注册账号、按领区选城市、选可预约时段。顺序不能反：没填表就约不上号。</p>

<h2>第一步：先在 France-Visas 填表</h2>
<p>打开法国官方签证网站 France-Visas（france-visas.gouv.fr），按向导完成在线申请表，系统会给出申请编号与应递交的签证中心。填表时按护照与行程如实填写，提交后打印申请表与回执，递交当天要带上。注意：France-Visas 是填表的地方，不是约号的地方；约号在第二步的 TLScontact 系统里完成。</p>

<h2>第二步：在 TLScontact 注册账号</h2>
<p>到 TLScontact 法国签证官网（visas-fr.tlscontact.com）注册账号，用注册邮箱登录。注册信息与申请人信息要一致，预约名额与申请人绑定、不可转让。账号提前注册好、信息提前填好，放号时才抢得过别人。</p>

<h2>第三步：按领区选城市，再选时段</h2>
<p>法国在华按领区受理，原则上按常住地所属领区选择递交城市，跨领区递交可能被拒收。选好城市后，系统显示当前开放的可预约日期与时段，选一个、确认预约，保存好预约确认信。热门领区在旺季经常提前数周约满，建议行程一确定就启动预约，号和材料可以并行准备。</p>

<h2>第四步：按预约时间到中心递交</h2>
<p>按预约时间提前约 15 分钟到达签证中心，递交材料、缴纳签证费与签证中心服务费、采集指纹。首次申请申根签证必须本人到场录指纹；59 个月内录过指纹的申请人，部分情形可免于再次采集（以法国官方规定为准）。</p>

<h2>第五步：等待审理与领取护照</h2>
<p>通常 15 个自然日出结果，个别情况可延长至 45 天。可选择自取或快递返还。最晚递交时间是出行前 15 天，但那是没有给任何意外留余量的底线，不要按底线规划。</p>

<section class="card">
<h2>关键数字（官方口径）</h2>
<ul class="data">
  <li>签证费：成人 90 欧元 / 6–12 岁 45 欧元 / 6 岁以下免费（2024-06-11 起，另付签证中心服务费，金额以 TLScontact 当期页面为准）。</li>
  <li>递交窗口：出行前 6 个月 ～ 15 天之间。</li>
  <li>审理：通常 15 天，最长可至 45 天。</li>
  <li>旅行医疗保险保额：不低于 3 万欧元。</li>
</ul>
<p class="fine">%SOURCES%</p>
</section>
<p><a href="/guide/appointment-process/">→ 先看预约递交全流程</a> · <a href="/guide/no-appointment-slots/">→ 约不到号时按这五步走</a> · <a href="/#subscribe">→ 回到首页订阅放号提醒</a></p>
</article>
"""



def article_ld(title, desc, path, date=None):
    d = date or TODAY
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "datePublished": d,
        "dateModified": d,
        "author": {"@type": "Organization", "name": SITE["name"]},
        "mainEntityOfPage": SITE["domain"] + path,
    }


def main():
    form = form_html("home-form")
    home_ld = {"@context": "https://schema.org", "@type": "WebSite",
               "name": SITE["name"], "url": SITE["domain"] + "/",
               "description": "申根签证预约位放号邮件提醒：每个工作日核查，只提醒不代抢。"}
    page("/", SITE["name"] + " | " + SITE["tagline"],
         "法国、德国、意大利等申根签证递签预约放号提醒：订阅国家+城市组合，每个工作日核查，有新的可预约时段当天邮件通知。只提醒，不代抢、不代预约，不收集证件信息。",
         HOME_BODY.replace("%FORM%", form).replace("%MAIL_MOCK%", MAIL_MOCK), jsonld=home_ld)

    page("/guide/appointment-process/", "申根签证预约递交全流程 | " + SITE["name"],
         "从确定主访国、领区、在线填表、预约递交时段到录指纹、取护照的完整流程与官方时间口径。",
         GUIDE_PROCESS.replace("%SOURCES%", SOURCES_NOTE) + form_html("guide-appointment-form"), ogtype="article",
         jsonld=article_ld("申根签证预约递交全流程", "申根签证预约递交的六个步骤与关键时间数字。", "/guide/appointment-process/"))

    page("/guide/slot-patterns/", "申根签证放号规律与刷号常识 | " + SITE["name"],
         "没有内部放号时刻表。讲清号源紧张的成因、回流位与加场放号等真实规律，以及黄牛代抢的风险。",
         GUIDE_PATTERNS.replace("%SOURCES%", SOURCES_NOTE) + form_html("guide-slots-form"), ogtype="article",
         jsonld=article_ld("申根签证放号规律与刷号常识", "号源紧张的成因与真实存在的放号规律。", "/guide/slot-patterns/"))

    rows = "\n".join(
        "    <tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (c, p, n) for c, p, n in PROVIDERS)
    page("/guide/visa-centers/", "各国在华受理机构与领区常识 | " + SITE["name"],
         "法国荷兰走 TLScontact、西班牙走 BLS、德国意大利等走 VFS Global：受理机构对照表与领区选择常识。",
         GUIDE_CENTERS.replace("%PROVIDER_ROWS%", rows).replace("%SOURCES%", SOURCES_NOTE)
         + form_html("guide-centers-form"),
         ogtype="article",
         jsonld=article_ld("各国在华受理机构与领区常识", "申根各国在华受理机构对照与领区常识。", "/guide/visa-centers/"))

    no_slots_faq = [
        ("申根签证预约显示没有号，是不是就约不上了？",
         "不是。显示无号只代表当前开放的日期已被约满。取消回流、临时加场与新周期开放都会产生新时段，持续关注官方系统或订阅放号提醒，仍有机会约到。"),
        ("换一个城市递交是不是更容易约到号？",
         "不同城市的号源紧张程度确实差别很大，但申根各国按领区受理，原则上要按常住地所属领区选择递交城市。跨领区递交可能被拒收，换城市前务必先核对领区划分，不要只看哪里有号。"),
        ("找人代抢号靠谱吗？",
         "不靠谱。预约名额与申请人信息绑定、不可转让，买来的号可能因信息不一致被拒收，还有个人信息泄露风险。签证中心与使领馆多次提示：预约通过官方系统进行，不要向第三方付「抢号费」。"),
        ("你们的放号提醒能保证我约到号吗？",
         "不能保证。提醒只能帮你尽早知道新时段出现，热门领区的号可能很快被订完，收到提醒后请第一时间去官方系统自行预约。本站每个工作日核查一次，不是 24 小时实时监控。"),
    ]
    no_slots_ld = {"@context": "https://schema.org", "@graph": [
        article_ld("申根签证预约不到号怎么办",
                   "约不到号时先分清是哪种「约不到」，再按官方渠道核对、利用取消回流与加场放号、算清时间账，最后用订阅提醒兜底。",
                   "/guide/no-appointment-slots/", date="2026-11-15"),
        {"@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in no_slots_faq]},
    ]}
    page("/guide/no-appointment-slots/", "申根签证预约不到号怎么办 | " + SITE["name"],
         "约不到申根签证递交号位时，先分清是哪种「约不到」，再按官方渠道核对、利用取消回流与加场放号、算清时间账，最后用订阅提醒兜底。只讲合规途径，不碰代抢。",
         GUIDE_NO_SLOTS.replace("%SOURCES%", SOURCES_NOTE) + form_html("guide-no-slots-form"), ogtype="article",
         jsonld=no_slots_ld)

    release_faq = [
        ("申根签证放号时间有规律吗？",
         "没有统一的时刻表。VFS Global、TLScontact、BLS 等机构从未公布每日固定放号时间，各国各城市节奏不同。有规律的是号源来源：新周期开放、旺季加场会批量放号，他人取消会零星回流——盯这三类时机，比守某个钟点有用。"),
        ("每天几点刷号最容易刷到？",
         "没有官方认可的「最佳时点」。取消回流位全天都可能随机出现，加场与新周期开放也没有预告。与其守整点，不如提前把账号与在线申请准备好，以天为单位持续关注，并用订阅提醒兜底。"),
        ("有人说凌晨刷到了号，是不是凌晨真的会放号？",
         "凌晨刷到的多半是他人取消或改期回流的零星时段，这类号全天随机出现，只是深夜刷的人少、竞争小，才显得「凌晨有号」。它不是批量放号的时刻表，换一天、换一个城市就未必成立。"),
        ("你们的放号提醒是自动实时监控吗？",
         "不是。本站目前没有自动实时监控：核查在每个工作日以人工＋半自动方式进行一次，发现新的可预约时段当天发邮件提醒。提醒只能帮你尽早知道，不能保证一定约得上；付费版（更高核查频率）正在筹备中，尚未上线。"),
    ]
    release_ld = {"@context": "https://schema.org", "@graph": [
        article_ld("申根签证放号时间有规律吗",
                   "没有统一的放号时刻表：VFS、TLScontact、BLS 从未公布每日固定放号时间。有规律的是号源来源——新周期开放、旺季加场批量放号、取消改期零星回流。",
                   "/guide/slot-release-time/", date="2026-11-17"),
        {"@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in release_faq]},
    ]}
    page("/guide/slot-release-time/", "申根签证放号时间有规律吗 | " + SITE["name"],
         "申根签证没有统一的放号时刻表，VFS、TLScontact、BLS 均未公布每日固定放号时间。有规律的是号源来源：新周期开放、旺季加场批量放号、取消改期零星回流。",
         GUIDE_RELEASE_TIME.replace("%SOURCES%", SOURCES_NOTE) + form_html("guide-release-time-form"), ogtype="article",
         jsonld=release_ld)

    fr_tls_faq = [
        ("法国签证是先填表还是先约号？",
         "先填表。先在法国官方 France-Visas 网站完成在线申请、拿到申请编号，再到 TLScontact 官网注册账号、按领区选城市约号。顺序不能反，没填表就约不上号。"),
        ("一定要在常住地所属领区的城市递交吗？",
         "原则上是。法国在华按领区受理，跨领区递交可能被拒收。不要只看「哪里有号」就换城市，换之前先核对领区划分。"),
        ("TLScontact 收服务费吗？",
         "收。签证费（成人 90 欧元）之外，另付签证中心服务费，金额以 TLScontact 官网当期页面为准。预约通过官网办理，不要向第三方付「抢号费」。"),
        ("你们的放号提醒是自动实时监控吗？",
         "不是。本站目前没有自动实时监控：核查在每个工作日以人工＋半自动方式进行一次，发现新的可预约时段当天发邮件提醒。提醒只能帮你尽早知道，不能保证一定约得上。"),
    ]
    fr_tls_ld = {"@context": "https://schema.org", "@graph": [
        article_ld("法国申根签证预约 TLScontact 怎么约",
                   "法国在华走 TLScontact：先在 France-Visas 填表，再到 TLScontact 注册、按领区选城市约号，五步讲清全流程与官方时间口径。",
                   "/guide/france-tlscontact-how-to-book/", date="2026-11-19"),
        {"@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fr_tls_faq]},
    ]}
    page("/guide/france-tlscontact-how-to-book/", "法国申根签证预约 TLScontact 怎么约 | " + SITE["name"],
         "法国申根签证在华走 TLScontact：先在 France-Visas 填表，再到 TLScontact 注册账号、按领区选城市约号，五步讲清全流程与官方时间口径。",
         GUIDE_FR_TLS.replace("%SOURCES%", SOURCES_NOTE) + form_html("guide-fr-tls-form"), ogtype="article",
         jsonld=fr_tls_ld)

    faq_items = "\n".join(
        '  <div class="faq-item"><h3>%s</h3><p>%s</p></div>' % (q, a) for q, a in FAQ)
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    page("/faq/", "常见问题 | " + SITE["name"],
         "收费、核查频率、能否代抢、退订方式等常见问题。",
         "<article>\n<h1>常见问题</h1>\n%s\n</article>" % faq_items + form_html("faq-form"), jsonld=faq_ld)

    page("/privacy/", "隐私说明 | " + SITE["name"],
         "本站只收集邮箱与预约偏好，不收集任何证件信息。",
         PRIVACY_BODY.replace("%SITENAME%", SITE["name"]))

    # 404
    nf = HEAD.replace("%TITLE%", "页面未找到 | " + SITE["name"]).replace("%DESC%", "页面未找到")
    nf = nf.replace("%GTAG%", GTAG)
    nf = nf.replace("%CANON%", SITE["domain"] + "/404.html").replace("%OGTYPE%", "website")
    nf = nf.replace("%SITENAME%", SITE["name"]).replace("%DOMAIN%", SITE["domain"]).replace("%JSONLD%", "")
    nf += '<section class="hero"><h1>404 · 页面未找到</h1><p class="lead">这个页面不存在。<a href="/">回到首页</a></p></section>'
    nf += FOOT.replace("%SITENAME%", SITE["name"]).replace("%TAGLINE%", SITE["tagline"])
    with open(os.path.join(PUBLIC, "404.html"), "w", encoding="utf-8") as f:
        f.write(nf)

    # sitemap / robots / llms
    urls = [("/", TODAY), ("/guide/appointment-process/", TODAY), ("/guide/slot-patterns/", TODAY),
            ("/guide/visa-centers/", TODAY), ("/guide/no-appointment-slots/", "2026-11-15"),
            ("/guide/slot-release-time/", "2026-11-17"),
            ("/guide/france-tlscontact-how-to-book/", "2026-11-19"),
            ("/faq/", TODAY), ("/privacy/", TODAY)]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, lm in urls:
        sm.append("  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>" % (SITE["domain"], u, lm))
    sm.append("</urlset>")
    with open(os.path.join(PUBLIC, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm) + "\n")
    with open(os.path.join(PUBLIC, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE["domain"])
    with open(os.path.join(PUBLIC, "llms.txt"), "w", encoding="utf-8") as f:
        f.write("# %s (%s)\n\n%s。面向中国申请人：订阅目的国+递交城市组合，"
                "每个工作日核查官方预约系统放号情况，有新的可预约时段即邮件提醒。"
                "只提醒，不代抢、不代填表、不代预约；不收集护照号等证件信息，只收邮箱与预约偏好。\n\n"
                "- 首页/订阅: %s/\n- 预约流程: %s/guide/appointment-process/\n"
                "- 放号规律: %s/guide/slot-patterns/\n- 受理机构: %s/guide/visa-centers/\n"
                "- 预约不到号怎么办: %s/guide/no-appointment-slots/\n"
                "- 放号时间有规律吗: %s/guide/slot-release-time/\n"
                "- 法国 TLScontact 怎么约: %s/guide/france-tlscontact-how-to-book/\n"
                "- 常见问题: %s/faq/\n- 隐私说明: %s/privacy/\n"
                % (SITE["name"], SITE["name_en"], SITE["tagline"], SITE["domain"],
                   SITE["domain"], SITE["domain"], SITE["domain"], SITE["domain"], SITE["domain"], SITE["domain"], SITE["domain"], SITE["domain"]))
    print("built", len(urls), "pages ->", PUBLIC)


if __name__ == "__main__":
    main()
