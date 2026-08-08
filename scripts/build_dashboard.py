#!/usr/bin/env python3
"""Build standalone candidate and employer HTML from a job-intelligence run."""

import argparse
import base64
import csv
import html
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ID = re.compile(r"\b(?:SRC|SMP|BRAND|CAM|TOOL|EXP|AST|FIT|CLM|ANS|GAP|OPS|CON)-\d{3}\b")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TYPE_LABELS = {
    "benchmark_brand": "对标品牌", "campaign": "营销活动", "program": "合作项目",
    "creator": "创作者", "account": "账号", "content": "内容", "prospect": "潜在客户",
    "ad": "广告", "listing": "商品页面", "tool_or_platform": "工具/平台",
    "expert_case": "专家案例", "discussion": "公开讨论", "policy": "政策/规则",
    "source_asset": "原始资料",
}
ROLE_LABELS = {
    "official": "官方来源", "native_behavior": "平台原生行为", "candidate_claim": "候选人陈述",
    "user_supplied_job": "用户提供岗位", "user_voice": "用户声音", "practitioner_voice": "从业者经验",
    "authoritative": "权威资料", "reporting": "媒体报道", "vendor": "服务商资料", "ai_lead": "AI 线索",
}


def locate_dirs(run_root):
    run_root = run_root.resolve()
    if (run_root / "outputs").is_dir():
        return run_root / "outputs", run_root / "work"
    return run_root, run_root.parent / "work"


def safe_url(value):
    try:
        parsed = urlparse(value)
        return value if parsed.scheme in {"http", "https"} and parsed.netloc else ""
    except ValueError:
        return ""


def render_inline(text):
    escaped = html.escape(text, quote=True)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda m: f'<a href="{html.escape(safe_url(html.unescape(m.group(2))), quote=True)}" target="_blank" rel="noopener noreferrer">{m.group(1)}</a>',
        escaped,
    )
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
    return escaped


def render_markdown(text):
    lines = text.splitlines()
    out, paragraph, list_type = [], [], None
    in_code, code_lines = False, []

    def flush_paragraph():
        if paragraph:
            out.append(f"<p>{render_inline(' '.join(part.strip() for part in paragraph))}</p>")
            paragraph.clear()

    def close_list():
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    index = 0
    while index < len(lines):
        line = lines[index]
        if line.strip().startswith("```"):
            flush_paragraph(); close_list()
            if in_code:
                out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines, in_code = [], False
            else:
                in_code = True
            index += 1; continue
        if in_code:
            code_lines.append(line); index += 1; continue
        heading = HEADING.match(line)
        if heading:
            flush_paragraph(); close_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{render_inline(heading.group(2))}</h{level}>")
            index += 1; continue
        if line.startswith("|") and index + 1 < len(lines) and re.match(r"^\|?\s*:?-+", lines[index + 1]):
            flush_paragraph(); close_list()
            headers = [cell.strip() for cell in line.strip().strip("|").split("|")]
            index += 2
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                index += 1
            head = "".join(f"<th>{render_inline(cell)}</th>" for cell in headers)
            body = "".join("<tr>" + "".join(f"<td>{render_inline(cell)}</td>" for cell in row) + "</tr>" for row in rows)
            out.append(f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
            continue
        item = re.match(r"^\s*([-*+] |\d+[.)] )(.*)$", line)
        if item:
            flush_paragraph()
            wanted = "ol" if item.group(1)[0].isdigit() else "ul"
            if list_type != wanted:
                close_list(); out.append(f"<{wanted}>"); list_type = wanted
            out.append(f"<li>{render_inline(item.group(2))}</li>")
            index += 1; continue
        if line.startswith(">"):
            flush_paragraph(); close_list()
            quote = line.lstrip("> ")
            out.append(f"<blockquote>{render_inline(quote)}</blockquote>")
            index += 1; continue
        if re.match(r"^\s*---+\s*$", line):
            flush_paragraph(); close_list(); out.append("<hr>"); index += 1; continue
        if not line.strip():
            flush_paragraph(); close_list(); index += 1; continue
        paragraph.append(line)
        index += 1
    flush_paragraph(); close_list()
    if in_code:
        out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    return "\n".join(out)


def extract_section(text, needle):
    lines = text.splitlines()
    start, level = None, None
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if match and needle.lower() in match.group(2).lower():
            start, level = index, len(match.group(1)); break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = HEADING.match(lines[index])
        if match and len(match.group(1)) <= level:
            end = index; break
    return "\n".join(lines[start:end])


def document_title(filename, text):
    for line in text.splitlines():
        match = HEADING.match(line)
        if match and len(match.group(1)) == 1:
            return re.sub(r"[*_`]+", "", match.group(2)).strip()
    return filename.removesuffix(".md").replace("_", " ").title()


def read_rows(csv_path):
    with csv_path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_screenshots(package_root, work_dir, evidence_urls):
    manifest_path = work_dir / "evidence-screenshots.json"
    if not manifest_path.exists():
        return [], [f"missing screenshot manifest: {manifest_path}"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"invalid screenshot manifest: {exc}"]
    screenshots, failures = [], []
    mime_by_suffix = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
    for index, item in enumerate(manifest.get("screenshots", []), 1):
        if not item.get("include_in_role_brief"):
            continue
        if item.get("public_safe") is not True:
            failures.append(f"screenshot {index} must set public_safe to true")
            continue
        record_id = item.get("record_id", "")
        if record_id not in evidence_urls:
            failures.append(f"screenshot {index} record_id is absent from evidence CSV: {record_id!r}")
            continue
        relative = Path(item.get("file", ""))
        image_path = (package_root / relative).resolve()
        try:
            image_path.relative_to(package_root.resolve())
        except ValueError:
            failures.append(f"screenshot {index} escapes run root: {relative}")
            continue
        mime = mime_by_suffix.get(image_path.suffix.lower())
        if not mime:
            failures.append(f"screenshot {index} unsupported format: {relative}")
            continue
        if not image_path.exists():
            failures.append(f"screenshot {index} file missing: {image_path}")
            continue
        url = safe_url(item.get("source_url", ""))
        observed = item.get("observed_date", "")
        if not url:
            failures.append(f"screenshot {index} missing direct source_url")
        elif url != evidence_urls[record_id]:
            failures.append(f"screenshot {index} source_url does not match its evidence record")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", observed):
            failures.append(f"screenshot {index} invalid observed_date: {observed!r}")
        if not item.get("caption") or not item.get("source_name"):
            failures.append(f"screenshot {index} needs source_name and human-readable caption")
        data = base64.b64encode(image_path.read_bytes()).decode("ascii")
        screenshots.append({**item, "source_url": url, "data_uri": f"data:{mime};base64,{data}"})
    if len(screenshots) < 2:
        failures.append("role opportunity brief requires at least two public-safe evidence screenshots")
    return screenshots, failures


def metric_card(value, label):
    return f'<div class="metric-card"><div class="metric-value">{html.escape(str(value))}</div><div class="metric-label">{html.escape(label)}</div></div>'


def panel(panel_id, title, subtitle, content, active=False):
    klass = "panel active" if active else "panel"
    return f'<section class="{klass}" id="{panel_id}"><div class="section-heading"><div><h2>{html.escape(title)}</h2><p>{html.escape(subtitle)}</p></div></div>{content}</section>'


def make_candidate_html(title, company, role, markdown_files, rows):
    cheatsheet = markdown_files.get("INTERVIEW_CHEATSHEET.md", "")
    priority = extract_section(cheatsheet, "面试前 10 分钟") or extract_section(cheatsheet, "10 minute")
    fallback = extract_section(cheatsheet, "如果只剩 3 分钟") or extract_section(cheatsheet, "3 minute")
    router = extract_section(cheatsheet, "乱序提问导航") or extract_section(cheatsheet, "out-of-order")
    if not priority:
        priority = "## 面试前 10 分钟\n请先完成 P0/P1 优先级内容。"
    if not router:
        router = "## 乱序提问导航\n请按面试官意图补全导航。"

    memory_html = (
        '<div class="priority-grid">'
        f'<article class="priority-card p0"><span class="label">P0 · 必须记住</span>{render_markdown(priority)}</article>'
        f'<article class="priority-card p1"><span class="label">3 分钟版本</span>{render_markdown(fallback or "只保留公司、岗位、三个锚点和三个问题。")}</article>'
        '<article class="priority-card p2"><span class="label">P2 · 需要时再查</span><h3>不用背完整研究报告</h3><p>竞品、样本、来源和长答案都在后面的可视化页签中。先掌握能够迁移到不同问题的答案锚点。</p><button class="nav-btn" data-open-panel="evidence">查看证据地图</button></article>'
        '</div><article class="prose">' + render_markdown(router) + '</article>'
    )

    type_count = len({row.get("sample_type") for row in rows if row.get("sample_type")})
    source_count = len({row.get("source_role") for row in rows if row.get("source_role")})
    high_count = sum(row.get("confidence") == "high" for row in rows)
    market_count = len({row.get("market") for row in rows if row.get("market")})
    metrics = "".join([
        metric_card(len(rows), "研究记录"), metric_card(type_count, "证据类型"),
        metric_card(high_count, "高可信记录"), metric_card(market_count, "覆盖市场"),
    ])

    evidence_html = f'''
      <div class="chart-grid">
        <article class="chart-card"><h3>证据类型</h3><div data-chart="type"></div></article>
        <article class="chart-card"><h3>来源角色</h3><div data-chart="role"></div></article>
        <article class="chart-card"><h3>市场覆盖</h3><div data-chart="market"></div></article>
      </div>
      <div class="filters">
        <input data-filter="search" type="search" placeholder="搜索品牌、平台、机制或结论" aria-label="搜索证据">
        <select data-filter="type" aria-label="筛选证据类型"><option value="">全部类型</option></select>
        <select data-filter="role" aria-label="筛选来源角色"><option value="">全部来源</option></select>
        <select data-filter="confidence" aria-label="筛选可信度"><option value="">全部可信度</option><option value="high">高</option><option value="medium">中</option><option value="low">低</option></select>
      </div>
      <p data-evidence-count></p>
      <div class="table-wrap"><table class="data-table"><thead><tr><th>样本</th><th>市场/平台</th><th>直接观察</th><th>可迁移启发</th><th>可信度</th><th>来源</th></tr></thead><tbody data-evidence-body></tbody></table></div>'''

    document_panels = []
    for filename, text in markdown_files.items():
        if filename in {"INTERVIEW_CHEATSHEET.md", "GLOSSARY.md", "ROLE_OPPORTUNITY_BRIEF.md"}:
            continue
        label = document_title(filename, text)
        document_panels.append(panel("doc-" + re.sub(r"[^a-z0-9]+", "-", filename.lower()).strip("-"), label, "完整内容", f'<article class="prose">{render_markdown(text)}</article>'))

    cheat_panel = panel("cheatsheet", "完整面试小抄", "需要细节时再看，不要求顺序背诵", f'<article class="prose">{render_markdown(cheatsheet)}</article>')
    glossary_text = markdown_files.get("GLOSSARY.md", "# 术语表\n本次尚未提供术语表。")
    glossary_panel = panel("glossary", "术语表", "缩写第一次出现时先看人话解释", f'<article class="prose">{render_markdown(glossary_text)}</article>')
    candidate_panels = [
        panel("memory", "先记住这些", "优先级和乱序应答入口", memory_html, True),
        panel("evidence", "可视化证据地图", "把品牌、平台、市场与来源整理成容易浏览的视图", evidence_html),
        cheat_panel, *document_panels, glossary_panel,
    ]

    nav = [
        ("memory", "先记住这些"), ("evidence", "证据地图"), ("cheatsheet", "完整小抄"),
    ]
    nav += [(re.sub(r"[^a-z0-9]+", "-", "doc-" + name.lower()).strip("-"), document_title(name, text)) for name, text in markdown_files.items() if name not in {"INTERVIEW_CHEATSHEET.md", "GLOSSARY.md", "ROLE_OPPORTUNITY_BRIEF.md"}]
    nav.append(("glossary", "术语表"))
    nav_html = "".join(f'<button class="nav-btn{" active" if index == 0 else ""}" data-target="{target}">{html.escape(label)}</button>' for index, (target, label) in enumerate(nav))
    css = (ROOT / "assets/dashboard-theme.css").read_text(encoding="utf-8")
    js = (ROOT / "assets/dashboard.js").read_text(encoding="utf-8")
    rows_json = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    types_json = json.dumps(TYPE_LABELS, ensure_ascii=False)
    roles_json = json.dumps(ROLE_LABELS, ensure_ascii=False)
    return f'''<!doctype html>
<html lang="zh-CN" data-dashboard-version="0.3.0"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{css}</style></head>
<body><div class="app-shell"><header class="topbar"><div class="brandline"><div class="brandmark">E</div><div><h1>{html.escape(title)}</h1><p>{html.escape(company)} · {html.escape(role)}</p></div></div><div class="top-actions"><button class="ghost-btn" data-export-pdf aria-label="导出为 PDF">导出 PDF</button></div></header>
<section class="hero"><div class="eyebrow">求职情报 · 面试准备</div><h2>先抓住能赢下面试的重点，再进入完整研究。</h2><p>这是一份面向求职者的单页入口：优先级、乱序问答、证据地图、完整材料和术语解释都在这里。</p><div class="metric-grid">{metrics}</div></section>
<div class="content-layout"><nav class="sidebar" aria-label="页面导航">{nav_html}</nav><main class="main">{''.join(candidate_panels)}</main></div><footer class="footer">Eliot Global Job Intelligence · 求职情报与面试准备</footer></div>
<script>window.EVIDENCE_ROWS={rows_json};window.TYPE_LABELS={types_json};window.ROLE_LABELS={roles_json};</script><script>{js}</script></body></html>'''


def make_role_brief_html(title, company, role, author, prepared_date, source_text, screenshots):
    clean_text = AUDIT_ID.sub("", source_text)
    clean_text = re.sub(r"^#\s+.+?\n+", "", clean_text, count=1)
    gallery = "".join(
        f'<figure class="evidence-shot"><img src="{shot["data_uri"]}" alt="{html.escape(shot["caption"], quote=True)}">'
        f'<figcaption><strong>{html.escape(shot["caption"])}</strong>'
        f'<span>{html.escape(shot["source_name"])} · {html.escape(shot["observed_date"])}</span>'
        f'<a href="{html.escape(shot["source_url"], quote=True)}" target="_blank" rel="noopener noreferrer">查看来源 ↗</a>'
        '</figcaption></figure>'
        for shot in screenshots
    )
    css = (ROOT / "assets/dashboard-theme.css").read_text(encoding="utf-8")
    meta = " · ".join(part for part in [f"Prepared by {author}" if author else "", prepared_date] if part)
    return f'''<!doctype html><html lang="zh-CN" data-dashboard-version="0.3.0"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{css}</style></head><body class="brief-page">
<header class="brief-topbar"><div class="brief-brand"><strong>{html.escape(company)}</strong><span>{html.escape(role)}</span></div><button class="ghost-btn" data-export-pdf onclick="window.print()" aria-label="导出为 PDF">导出 PDF</button></header>
<section class="brief-hero"><div class="brief-hero-inner"><div class="brief-kicker">Role opportunity brief</div><h1>{html.escape(title)}</h1><p class="lead">市场信号、对标机制与 30 天验证路径</p><div class="brief-meta">{html.escape(meta)}</div></div></section>
<main class="brief-content"><section class="evidence-stage"><h2>关键证据快照</h2><p>用原始页面呈现支撑判断的核心信号。</p><div class="evidence-gallery">{gallery}</div></section><article class="prose brief-copy">{render_markdown(clean_text)}</article></main>
<footer class="brief-footer">{html.escape(meta)}</footer></body></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--title", default="求职情报与面试准备中心")
    parser.add_argument("--company", default="目标公司")
    parser.add_argument("--role", default="目标岗位")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--role-brief-source", type=Path)
    parser.add_argument("--role-brief-output", type=Path)
    parser.add_argument("--brief-title")
    parser.add_argument("--author", default="")
    parser.add_argument("--prepared-date", default=date.today().isoformat())
    args = parser.parse_args()
    output_dir, work_dir = locate_dirs(args.run_root)
    required = [output_dir / "JOB_INTELLIGENCE_BRIEF.md", output_dir / "INTERVIEW_CHEATSHEET.md", output_dir / "EVIDENCE_AND_BENCHMARKS.csv"]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print(json.dumps({"passed": False, "missing": missing}, ensure_ascii=False, indent=2))
        return 1
    markdown_files = {path.name: path.read_text(encoding="utf-8") for path in sorted(output_dir.glob("*.md"))}
    rows = read_rows(required[2])
    role_brief_source = args.role_brief_source or output_dir / "ROLE_OPPORTUNITY_BRIEF.md"
    role_brief_output = args.role_brief_output or output_dir / "ROLE_OPPORTUNITY_BRIEF.html"
    role_brief_exists = role_brief_source.exists()
    package_root = args.run_root.resolve()
    if package_root.name == "outputs":
        package_root = package_root.parent
    evidence_urls = {row.get("record_id", ""): row.get("url", "") for row in rows}
    screenshots, screenshot_failures = (load_screenshots(package_root, work_dir, evidence_urls) if role_brief_exists else ([], []))
    if screenshot_failures:
        print(json.dumps({"passed": False, "screenshot_failures": screenshot_failures}, ensure_ascii=False, indent=2))
        return 1
    candidate_output = args.output or output_dir / "JOB_SEARCH_DASHBOARD.html"
    candidate_output.write_text(make_candidate_html(args.title, args.company, args.role, markdown_files, rows), encoding="utf-8")
    generated = [str(candidate_output)]
    if role_brief_exists:
        brief_title = args.brief_title or f"{args.company} · {args.role} 机会简报"
        role_brief_output.write_text(make_role_brief_html(brief_title, args.company, args.role, args.author, args.prepared_date, role_brief_source.read_text(encoding="utf-8"), screenshots), encoding="utf-8")
        generated.append(str(role_brief_output))
    print(json.dumps({"builder": "eliot-global-job-intelligence/dashboard", "generated": generated, "evidence_rows": len(rows), "role_brief_screenshots": len(screenshots), "passed": True}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
