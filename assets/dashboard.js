(() => {
  const state = { rows: window.EVIDENCE_ROWS || [] };
  const typeLabels = window.TYPE_LABELS || {};
  const roleLabels = window.ROLE_LABELS || {};
  const confidenceLabels = { high: "高", medium: "中", low: "低" };

  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;").replaceAll("'", "&#039;");

  function activate(id) {
    document.querySelectorAll(".panel").forEach((panel) => panel.classList.toggle("active", panel.id === id));
    document.querySelectorAll(".nav-btn").forEach((button) => button.classList.toggle("active", button.dataset.target === id));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  document.querySelectorAll(".nav-btn").forEach((button) => button.addEventListener("click", () => activate(button.dataset.target)));
  document.querySelectorAll("[data-open-panel]").forEach((button) => button.addEventListener("click", () => activate(button.dataset.openPanel)));
  document.querySelector("[data-export-pdf]")?.addEventListener("click", () => window.print());

  const by = (key) => state.rows.reduce((acc, row) => {
    const value = row[key] || "未标注";
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});

  function renderBars(target, values, labels = {}) {
    const node = document.querySelector(target);
    if (!node) return;
    const entries = Object.entries(values).sort((a, b) => b[1] - a[1]).slice(0, 7);
    const max = Math.max(1, ...entries.map(([, count]) => count));
    node.innerHTML = entries.map(([label, count]) => `
      <div class="bar-row">
        <span>${escapeHtml(labels[label] || label)}</span>
        <div class="bar-track"><div class="bar-fill" style="width:${Math.round(count / max * 100)}%"></div></div>
        <strong>${count}</strong>
      </div>`).join("");
  }

  renderBars("[data-chart=type]", by("sample_type"), typeLabels);
  renderBars("[data-chart=role]", by("source_role"), roleLabels);
  renderBars("[data-chart=market]", by("market"));

  const search = document.querySelector("[data-filter=search]");
  const type = document.querySelector("[data-filter=type]");
  const role = document.querySelector("[data-filter=role]");
  const confidence = document.querySelector("[data-filter=confidence]");
  const tableBody = document.querySelector("[data-evidence-body]");
  const count = document.querySelector("[data-evidence-count]");

  function optionValues(key, labels) {
    return [...new Set(state.rows.map((row) => row[key]).filter(Boolean))]
      .sort().map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(labels[value] || value)}</option>`).join("");
  }
  if (type) type.insertAdjacentHTML("beforeend", optionValues("sample_type", typeLabels));
  if (role) role.insertAdjacentHTML("beforeend", optionValues("source_role", roleLabels));

  function renderEvidence() {
    if (!tableBody) return;
    const q = (search?.value || "").trim().toLowerCase();
    const rows = state.rows.filter((row) => {
      const haystack = Object.values(row).join(" ").toLowerCase();
      return (!q || haystack.includes(q)) && (!type?.value || row.sample_type === type.value)
        && (!role?.value || row.source_role === role.value)
        && (!confidence?.value || row.confidence === confidence.value);
    });
    if (count) count.textContent = `显示 ${rows.length} / ${state.rows.length} 条`;
    tableBody.innerHTML = rows.length ? rows.map((row, index) => `
      <tr data-record-id="${escapeHtml(row.record_id)}">
        <td><strong>${escapeHtml(row.name || `证据 ${index + 1}`)}</strong><br><span class="badge">${escapeHtml(typeLabels[row.sample_type] || row.sample_type)}</span></td>
        <td>${escapeHtml(row.market || "—")}<br><small>${escapeHtml(row.platform || "")}</small></td>
        <td>${escapeHtml(row.direct_evidence || "—")}</td>
        <td>${escapeHtml(row.transfer_lesson || row.interview_use || "—")}</td>
        <td><span class="confidence-${escapeHtml(row.confidence)}">${escapeHtml(confidenceLabels[row.confidence] || row.confidence)}</span></td>
        <td>${row.url ? `<a href="${escapeHtml(row.url)}" target="_blank" rel="noopener noreferrer">打开来源</a>` : "—"}</td>
      </tr>`).join("") : '<tr><td colspan="6" class="empty">没有匹配的证据。请调整筛选条件。</td></tr>';
  }
  [search, type, role, confidence].filter(Boolean).forEach((node) => node.addEventListener(node === search ? "input" : "change", renderEvidence));
  renderEvidence();
})();
