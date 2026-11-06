/* Subscribe form (.subscribe-form) -> leads service.
 * Collects email + appointment preferences only. Never document data. */
(function () {
  function noteOf(form) {
    function v(name) {
      var el = form.querySelector('[name="' + name + '"]');
      return el ? (el.value || "").trim() : "";
    }
    var parts = [];
    if (v("country")) parts.push("国家=" + v("country"));
    if (v("city")) parts.push("城市=" + v("city"));
    if (v("vtype")) parts.push("类型=" + v("vtype"));
    if (v("travel_month")) parts.push("出行月份=" + v("travel_month"));
    var paid = form.querySelector('[name="paid_interest"]');
    parts.push("付费版意向=" + (paid && paid.checked ? "是" : "否"));
    return parts.join("; ");
  }
  function bind(form) {
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var status = form.querySelector(".form-status");
      var emailEl = form.querySelector('input[name="email"]');
      var email = (emailEl.value || "").trim();
      if (!email) { status.textContent = "请先填写邮箱。"; return; }
      if (!form.querySelector('[name="country"]').value ||
          !form.querySelector('[name="city"]').value ||
          !form.querySelector('[name="vtype"]').value) {
        status.textContent = "请先选好目的国、递交城市和签证类型。"; return;
      }
      status.textContent = "正在订阅...";
      fetch(window.SSA_CONFIG.leadsEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          site: window.SSA_CONFIG.leadsSite,
          email: email,
          source: form.getAttribute("data-source") || "",
          note: noteOf(form),
          hp: (form.querySelector('[name="hp"]') || {}).value || ""
        })
      }).then(function (r) { return r.json(); })
        .then(function (d) {
          if (d && d.ok && d.status === "subscribed") {
            status.textContent = "订阅成功。每个工作日我们会核查你选的组合，有放号当天邮件通知你。";
            form.reset();
          } else if (d && d.ok && d.status === "already") {
            status.textContent = "这个邮箱已经订阅过这个站点了（同一组合如需修改偏好，请回复提醒邮件）。";
          } else {
            status.textContent = "提交失败，请稍后再试。";
          }
        })
        .catch(function () {
          status.textContent = "提交失败，请检查网络后重试。";
        });
    });
  }
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".subscribe-form").forEach(bind);
  });
})();
