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
  <p><a href="/privacy/">隐私说明</a> · <a href="/faq/">常见问题</a></p>
  <p>更多出行工具：<a href="https://chinatransitvisa.pages.dev/">外国人来华工具（240 小时过境免签校验 · 离境退税计算）</a> · <a href="https://gxccz.com/">gxccz 工具导航</a></p>
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


def article_ld(title, desc, path):
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "datePublished": TODAY,
        "dateModified": TODAY,
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
    urls = ["/", "/guide/appointment-process/", "/guide/slot-patterns/",
            "/guide/visa-centers/", "/faq/", "/privacy/"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append("  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>" % (SITE["domain"], u, TODAY))
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
                "- 常见问题: %s/faq/\n- 隐私说明: %s/privacy/\n"
                % (SITE["name"], SITE["name_en"], SITE["tagline"], SITE["domain"],
                   SITE["domain"], SITE["domain"], SITE["domain"], SITE["domain"], SITE["domain"]))
    print("built", len(urls), "pages ->", PUBLIC)


if __name__ == "__main__":
    main()
