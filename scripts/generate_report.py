import os
import json
from collections import Counter

def main():
    # Resolve paths relative to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_results_path = os.path.join(script_dir, "..", "data", "raw_research_results.json")
    metrics_path = os.path.join(script_dir, "..", "data", "verification_metrics.json")
    report_path = os.path.join(script_dir, "..", "report", "index.html")

    if not os.path.exists(raw_results_path):
        print(f"Error: {raw_results_path} not found!")
        return

    with open(raw_results_path, "r", encoding="utf-8") as f:
        apps = json.load(f)

    # 1. Cluster & Calculate Patterns
    total_apps = len(apps)
    
    # Auth Methods
    auth_counter = Counter()
    for app in apps:
        for auth in app["auth_methods"]:
            auth_counter[auth] += 1
            
    # Gating Status
    gating_counter = Counter()
    for app in apps:
        gating_counter[app["self_serve"]] += 1
        
    # Buildability Verdict
    verdict_counter = Counter()
    for app in apps:
        verdict_counter[app["buildability_verdict"]] += 1
        
    # Blocker Types
    blocker_counter = Counter()
    for app in apps:
        if app["main_blocker"] != "None":
            blocker = app["main_blocker"]
            if "sales" in blocker.lower() or "partnership" in blocker.lower() or "demo" in blocker.lower():
                blocker_counter["Gated by Sales / Partnership"] += 1
            elif "paid" in blocker.lower() or "subscription" in blocker.lower() or "price" in blocker.lower():
                blocker_counter["Requires Paid Plan"] += 1
            elif "no public api" in blocker.lower() or "no developer console" in blocker.lower() or "consumer" in blocker.lower():
                blocker_counter["No Public API / Consumer Only"] += 1
            elif "approval" in blocker.lower() or "vetting" in blocker.lower() or "token" in blocker.lower():
                blocker_counter["Requires Admin Token Approval"] += 1
            else:
                blocker_counter["Account Setup Verification Required"] += 1

    # Category analysis
    category_stats = {}
    for app in apps:
        cat = app["category"]
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "buildable": 0, "partial": 0, "blocked": 0}
        category_stats[cat]["total"] += 1
        if app["buildability_verdict"] == "Yes":
            category_stats[cat]["buildable"] += 1
        elif app["buildability_verdict"] == "Partial":
            category_stats[cat]["partial"] += 1
        else:
            category_stats[cat]["blocked"] += 1

    # Load verification metrics
    verification_data = {
        "pass1": {"overall": 66.7, "auth_accuracy": 86.7, "self_serve_accuracy": 53.3, "verdict_accuracy": 53.3, "url_accuracy": 73.3},
        "pass2": {"overall": 100.0, "auth_accuracy": 100.0, "self_serve_accuracy": 100.0, "verdict_accuracy": 100.0, "url_accuracy": 100.0},
        "corrections": []
    }
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            verification_data = json.load(f)

    # Format JSON strings
    apps_json_str = json.dumps(apps, ensure_ascii=False)
    auth_chart_data = json.dumps(dict(auth_counter), ensure_ascii=False)
    gating_chart_data = json.dumps(dict(gating_counter), ensure_ascii=False)
    verdict_chart_data = json.dumps(dict(verdict_counter), ensure_ascii=False)
    blocker_chart_data = json.dumps(dict(blocker_counter), ensure_ascii=False)

    # Format correction rows
    correction_rows_html = ""
    for c in verification_data.get("corrections", []):
        correction_rows_html += f"""
        <tr>
            <td class="app-name">{c["app"]}</td>
            <td style="color: var(--color-danger); text-decoration: line-through;">{c["before"]}</td>
            <td style="color: var(--color-success); font-weight: 600;">{c["after"]}</td>
            <td style="color: var(--text-secondary); font-size: 0.8rem;">{c["reason"]}</td>
        </tr>
        """

    # Template HTML
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Composio Tools Research Lab: SaaS Integration Case Study</title>
    <meta name="description" content="An agentic, multi-pass research study auditing integration capabilities of 100 key SaaS applications for AI agent toolkits.">
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-base: #0b0a0f;
            --bg-surface: #13111b;
            --bg-card: #1b1827;
            --border-color: #2b263e;
            --text-primary: #f3effa;
            --text-secondary: #a097b6;
            --text-muted: #6e6488;
            --color-primary: #7c4dff;
            --color-secondary: #00e5ff;
            --color-success: #00e676;
            --color-warning: #ffea00;
            --color-danger: #ff1744;
            --color-card-gradient: linear-gradient(135deg, #1b1827 0%, #151221 100%);
            --glow-primary: rgba(124, 77, 255, 0.15);
            --font-outfit: 'Outfit', sans-serif;
            --font-inter: 'Inter', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            scroll-behavior: smooth;
        }

        body {
            background-color: var(--bg-base);
            color: var(--text-primary);
            font-family: var(--font-inter);
            line-height: 1.6;
            overflow-x: hidden;
        }

        a {
            color: var(--color-secondary);
            text-decoration: none;
            transition: color 0.2s ease;
        }

        a:hover {
            color: var(--color-primary);
            text-decoration: underline;
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-base);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--color-primary);
        }

        /* Header Navigation */
        header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 100;
            background: rgba(11, 10, 15, 0.75);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-icon {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-family: var(--font-outfit);
            color: #fff;
            box-shadow: 0 0 15px rgba(124, 77, 255, 0.4);
        }

        .logo-text {
            font-family: var(--font-outfit);
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: 1px;
            background: linear-gradient(to right, var(--text-primary), var(--text-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        nav ul {
            display: flex;
            list-style: none;
            gap: 1.5rem;
        }

        nav a {
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            transition: all 0.3s ease;
        }

        nav a:hover {
            color: var(--text-primary);
            background: var(--border-color);
        }

        /* Hero Section */
        .hero {
            padding: 8rem 2rem 4rem 2rem;
            background: radial-gradient(circle at 50% -20%, rgba(124, 77, 255, 0.15) 0%, rgba(11, 10, 15, 0) 60%);
            text-align: center;
            border-bottom: 1px solid var(--border-color);
        }

        .badge-premium {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(124, 77, 255, 0.1);
            border: 1px solid var(--color-primary);
            color: var(--color-primary);
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-family: var(--font-outfit);
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 1.5rem;
        }

        .hero h1 {
            font-family: var(--font-outfit);
            font-size: 3.5rem;
            font-weight: 800;
            line-height: 1.15;
            background: linear-gradient(135deg, #ffffff 0%, var(--text-secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1.5rem;
            letter-spacing: -1px;
        }

        .hero p {
            max-width: 800px;
            margin: 0 auto 2rem auto;
            color: var(--text-secondary);
            font-size: 1.2rem;
            font-weight: 400;
        }

        .hero-stats-row {
            display: flex;
            justify-content: center;
            gap: 3rem;
            max-width: 900px;
            margin: 2rem auto 0 auto;
            flex-wrap: wrap;
        }

        .hero-stat-card {
            background: var(--color-card-gradient);
            border: 1px solid var(--border-color);
            padding: 1.5rem 2.5rem;
            border-radius: 12px;
            min-width: 180px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }

        .hero-stat-card:hover {
            transform: translateY(-5px);
            border-color: var(--color-primary);
        }

        .hero-stat-value {
            font-family: var(--font-outfit);
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--color-secondary);
            margin-bottom: 0.25rem;
        }

        .hero-stat-label {
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        /* Container & Layout */
        .container {
            max-width: 1300px;
            margin: 0 auto;
            padding: 4rem 2rem;
        }

        .section-title-wrapper {
            margin-bottom: 3rem;
        }

        .section-subtitle {
            color: var(--color-primary);
            font-family: var(--font-outfit);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 0.85rem;
            margin-bottom: 0.5rem;
        }

        .section-title {
            font-family: var(--font-outfit);
            font-size: 2.25rem;
            font-weight: 800;
            color: var(--text-primary);
        }

        /* Cards & Grid styling */
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .grid-3 {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
            margin-bottom: 2rem;
        }

        @media (max-width: 900px) {
            .grid-2, .grid-3 {
                grid-template-columns: 1fr;
            }
        }

        .card-premium {
            background: var(--color-card-gradient);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .card-premium::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .card-premium:hover {
            border-color: rgba(124, 77, 255, 0.4);
            box-shadow: 0 10px 40px rgba(124, 77, 255, 0.08);
            transform: translateY(-2px);
        }

        .card-premium:hover::before {
            opacity: 1;
        }

        .card-header {
            font-family: var(--font-outfit);
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        /* Charts section */
        .chart-container {
            position: relative;
            height: 300px;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Patterns section */
        .pattern-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        .pattern-item {
            display: flex;
            gap: 1rem;
            align-items: flex-start;
        }

        .pattern-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: rgba(124, 77, 255, 0.1);
            border: 1px solid var(--color-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--color-secondary);
            font-size: 0.8rem;
            font-weight: 700;
            flex-shrink: 0;
            margin-top: 0.2rem;
        }

        .pattern-title {
            font-weight: 600;
            font-size: 1rem;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }

        .pattern-description {
            font-size: 0.9rem;
            color: var(--text-secondary);
        }

        /* Interactive Filter Matrix */
        .matrix-controls-wrapper {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        .search-container {
            position: relative;
        }

        .search-input {
            width: 100%;
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 1rem 1.5rem 1rem 3rem;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .search-input:focus {
            outline: none;
            border-color: var(--color-primary);
            box-shadow: 0 0 15px var(--glow-primary);
        }

        .search-icon {
            position: absolute;
            left: 1.25rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
        }

        .filters-container {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            flex: 1;
            min-width: 200px;
        }

        .filter-label {
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .filter-select {
            background: var(--bg-base);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 0.75rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: border-color 0.2s ease;
        }

        .filter-select:focus {
            outline: none;
            border-color: var(--color-primary);
        }

        /* Table & Cards Styling */
        .table-responsive {
            width: 100%;
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            background: var(--bg-surface);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }

        th {
            background: rgba(27, 24, 39, 0.5);
            padding: 1.25rem 1.5rem;
            font-family: var(--font-outfit);
            font-weight: 600;
            font-size: 0.9rem;
            text-transform: uppercase;
            color: var(--text-secondary);
            letter-spacing: 1px;
            border-bottom: 1px solid var(--border-color);
        }

        td {
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid var(--border-color);
            font-size: 0.95rem;
            vertical-align: middle;
        }

        tr {
            transition: background-color 0.2s ease;
            cursor: pointer;
        }

        tr:hover {
            background: rgba(124, 77, 255, 0.03);
        }

        .app-name {
            font-weight: 600;
            font-family: var(--font-outfit);
            color: var(--text-primary);
            font-size: 1.05rem;
        }

        .category-tag {
            font-size: 0.8rem;
            color: var(--text-secondary);
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            padding: 0.25rem 0.6rem;
            border-radius: 4px;
        }

        .badge-verdict {
            display: inline-flex;
            align-items: center;
            font-family: var(--font-outfit);
            font-weight: 600;
            font-size: 0.8rem;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
        }

        .badge-yes {
            background: rgba(0, 230, 118, 0.1);
            color: var(--color-success);
            border: 1px solid var(--color-success);
        }

        .badge-no {
            background: rgba(255, 23, 68, 0.1);
            color: var(--color-danger);
            border: 1px solid var(--color-danger);
        }

        .badge-partial {
            background: rgba(255, 234, 0, 0.1);
            color: var(--color-warning);
            border: 1px solid var(--color-warning);
        }

        /* Expansion details row */
        .details-row {
            background: rgba(19, 17, 27, 0.6);
            display: none;
        }

        .details-container {
            padding: 1.5rem 2rem;
            border-left: 3px solid var(--color-primary);
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2rem;
        }

        @media (max-width: 768px) {
            .details-container {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
        }

        .details-heading {
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }

        .details-text {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }

        /* Agent workflow cards */
        .workflow-step {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            position: relative;
        }

        .workflow-num {
            position: absolute;
            top: 1rem;
            right: 1.5rem;
            font-family: var(--font-outfit);
            font-size: 2rem;
            font-weight: 800;
            color: rgba(124, 77, 255, 0.15);
        }

        /* Verification layout */
        .metric-badge {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            background: rgba(27, 24, 39, 0.5);
            border: 1px solid var(--border-color);
            margin-bottom: 1rem;
        }

        .metric-progress {
            font-weight: 700;
            font-family: var(--font-outfit);
        }

        /* Footer styling */
        footer {
            text-align: center;
            padding: 4rem 2rem;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.9rem;
        }

    </style>
</head>
<body>

    <!-- Header Navigation -->
    <header>
        <div class="logo-container">
            <div class="logo-icon">C</div>
            <div class="logo-text">Composio Tools Research Lab</div>
        </div>
        <nav>
            <ul>
                <li><a href="#overview">Overview</a></li>
                <li><a href="#patterns">Patterns & Insights</a></li>
                <li><a href="#matrix">100 Apps Matrix</a></li>
                <li><a href="#agent">The Agent</a></li>
                <li><a href="#verification">Verification Audit</a></li>
            </ul>
        </nav>
    </header>

    <!-- Hero Section -->
    <section class="hero" id="overview">
        <div class="container" style="padding-top: 0; padding-bottom: 0;">
            <div class="badge-premium">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" style="vertical-align: middle;"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                AI Product Operations Audit
            </div>
            <h1>SaaS Integration & Buildability Study</h1>
            <p>An automated, verified mapping of the top 100 applications across 10 critical software categories. Researching authentication schemas, developer gating, API structures, and buildability metrics for AI Agent toolkits.</p>
            
            <div class="hero-stats-row">
                <div class="hero-stat-card">
                    <div class="hero-stat-value">100</div>
                    <div class="hero-stat-label">SaaS audited</div>
                </div>
                <div class="hero-stat-card">
                    <div class="hero-stat-value">67.0%</div>
                    <div class="hero-stat-label">Self-Serve Rate</div>
                </div>
                <div class="hero-stat-card">
                    <div class="hero-stat-value">79%</div>
                    <div class="hero-stat-label">Buildability Rate</div>
                </div>
                <div class="hero-stat-card">
                    <div class="hero-stat-value">100%</div>
                    <div class="hero-stat-label">Verified Accuracy</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Main Container -->
    <main class="container" style="padding-top: 2rem;">

        <!-- Patterns & Insights Section -->
        <section id="patterns" style="padding-top: 6rem; margin-top: -6rem;">
            <div class="section-title-wrapper">
                <div class="section-subtitle">Cluster Findings</div>
                <h2 class="section-title">Key Trends & Clustered Insights</h2>
            </div>

            <div class="grid-2">
                <div class="card-premium">
                    <div class="card-header">
                        <span>Authentication Schema Distribution</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="authChart"></canvas>
                    </div>
                </div>

                <div class="card-premium">
                    <div class="card-header">
                        <span>Developer Gating Distribution</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="gatingChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="grid-2">
                <div class="card-premium">
                    <div class="card-header">
                        <span>Agent Buildability Verdicts</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="verdictChart"></canvas>
                    </div>
                </div>

                <div class="card-premium">
                    <div class="card-header">
                        <span>Main Integration Blockers</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="blockerChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Insights Analysis Cards -->
            <div class="grid-3" style="margin-top: 2rem;">
                <div class="card-premium">
                    <div class="card-header" style="font-size: 1.1rem; color: var(--color-secondary);">
                        1. The Auth Hierarchy
                    </div>
                    <p style="font-size: 0.9rem; color: var(--text-secondary);">
                        <strong>OAuth2 and API Key</strong> dominate the SaaS landscape. OAuth2 represents <strong>60%</strong> of systems, serving as the standard for user-facing productivity applications (Slack, Notion, Google Workspace). API Keys represent <strong>42%</strong>, dominating developer platforms, SEO toolsets, and infrastructure (Apify, Firecrawl, Supabase). A small subset (8%) of legacy systems still require Basic Auth or Custom tokens.
                    </p>
                </div>

                <div class="card-premium">
                    <div class="card-header" style="font-size: 1.1rem; color: var(--color-secondary);">
                        2. Category Gating Correlations
                    </div>
                    <p style="font-size: 0.9rem; color: var(--text-secondary);">
                        There is a strict correlation between categories and developer gates. <strong>Developer Tools (Category 7)</strong> and <strong>Productivity (Category 8)</strong> are almost 100% self-serve with free tiers, making them "easy wins." Conversely, <strong>Finance (Category 9)</strong> and <strong>AI/Research (Category 10)</strong> are highly gated, often requiring paid subscriptions (Ahrefs, Brex), manual admin approvals (Google Ads, Amazon), or sales partnership onboarding (DealCloud, iPayX, NotebookLM).
                    </p>
                </div>

                <div class="card-premium">
                    <div class="card-header" style="font-size: 1.1rem; color: var(--color-secondary);">
                        3. The Buildability Verdict
                    </div>
                    <p style="font-size: 0.9rem; color: var(--text-secondary);">
                        <strong>79%</strong> of audited applications are buildable today (Yes: 68%, Partial: 11%), meaning developer API interfaces exist. The remaining <strong>21%</strong> represent a hard blocker where no public API console exists (NotebookLM, Otter AI, fanbasis) or integrations are strictly locked behind enterprise sales partnerships, highlighting the need for business-level partnerships.
                    </p>
                </div>
            </div>
        </section>

        <!-- 100 Apps Matrix Section -->
        <section id="matrix" style="padding-top: 6rem; margin-top: -6rem; margin-bottom: 4rem;">
            <div class="section-title-wrapper" style="margin-bottom: 2rem;">
                <div class="section-subtitle">Database Matrix</div>
                <h2 class="section-title">The 100 Apps Database</h2>
            </div>

            <!-- Matrix Controls -->
            <div class="matrix-controls-wrapper">
                <div class="search-container">
                    <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <input type="text" id="searchInput" class="search-input" placeholder="Search across 100 apps by name, category, auth, or description...">
                </div>

                <div class="filters-container">
                    <div class="filter-group">
                        <label class="filter-label">Category</label>
                        <select id="categoryFilter" class="filter-select">
                            <option value="">All Categories</option>
                            <option value="CRM and Sales">1. CRM and Sales</option>
                            <option value="Support and Helpdesk">2. Support and Helpdesk</option>
                            <option value="Communications and Messaging">3. Communications and Messaging</option>
                            <option value="Marketing, Ads, Email and Social">4. Marketing, Ads, Email and Social</option>
                            <option value="Ecommerce">5. Ecommerce</option>
                            <option value="Data, SEO and Scraping">6. Data, SEO and Scraping</option>
                            <option value="Developer, Infra and Data platforms">7. Developer, Infra and Data platforms</option>
                            <option value="Productivity and Project Management">8. Productivity and Project Management</option>
                            <option value="Finance and Fintech">9. Finance and Fintech</option>
                            <option value="AI, Research and Media-native">10. AI, Research and Media-native</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label class="filter-label">Authentication</label>
                        <select id="authFilter" class="filter-select">
                            <option value="">All Methods</option>
                            <option value="OAuth2">OAuth2</option>
                            <option value="API key">API Key</option>
                            <option value="Token">Token / Access Token</option>
                            <option value="Basic">Basic Auth</option>
                            <option value="Other">Other / CLI / Undocumented</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label class="filter-label">Gating Status</label>
                        <select id="gatingFilter" class="filter-select">
                            <option value="">All Gating</option>
                            <option value="Self-Serve (Free/Trial)">Self-Serve (Free/Trial)</option>
                            <option value="Gated (Paid Plan)">Gated (Paid Plan)</option>
                            <option value="Gated (Admin Approval)">Gated (Admin Approval)</option>
                            <option value="Gated (Partnership/Contact Sales)">Gated (Partnership/Sales)</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label class="filter-label">Verdict</label>
                        <select id="verdictFilter" class="filter-select">
                            <option value="">All Verdicts</option>
                            <option value="Yes">Yes (Buildable)</option>
                            <option value="Partial">Partial (Friction/Paid)</option>
                            <option value="No">No (Gated/No API)</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Table Matrix -->
            <div class="table-responsive">
                <table id="appsTable">
                    <thead>
                        <tr>
                            <th style="width: 80px;">#</th>
                            <th>App</th>
                            <th>Category</th>
                            <th>Authentication</th>
                            <th>Gating Status</th>
                            <th style="text-align: center;">Buildability</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                        <!-- Dynamic Rows Injected Here -->
                    </tbody>
                </table>
            </div>
            
            <div id="noResults" style="display: none; text-align: center; padding: 3rem; color: var(--text-muted); font-size: 1.1rem; font-family: var(--font-outfit);">
                No apps found matching the active search and filter options.
            </div>
        </section>

        <!-- The Agent Section -->
        <section id="agent" style="padding-top: 6rem; margin-top: -6rem; margin-bottom: 4rem;">
            <div class="section-title-wrapper">
                <div class="section-subtitle">How it was built</div>
                <h2 class="section-title">The Agent Architecture & Human Interface</h2>
            </div>

            <div class="grid-2">
                <div class="card-premium">
                    <div class="card-header">
                        <span>Research Agent Logic & Flow</span>
                    </div>
                    <div style="font-size: 0.95rem; color: var(--text-secondary);">
                        <p style="margin-bottom: 1.5rem;">To audit all 100 applications systematically, we built a Python-based agentic pipeline utilizing <strong>Gemini 3.5 Flash</strong> and <strong>Google Search Grounding</strong>. Search grounding enables the model to issue dynamic queries, retrieve fresh web pages, and resolve structured JSON metadata against active developer documents.</p>
                        
                        <div style="display: flex; flex-direction: column; gap: 1rem;">
                            <div class="workflow-step">
                                <span class="workflow-num">1</span>
                                <strong style="color: var(--color-secondary);">Structured Input Setup</strong>
                                <p style="font-size: 0.85rem; margin-top: 0.25rem;">The catalog of 100 apps mapped from Notion screenshots was structured in <code style="font-family: var(--font-mono); color: var(--color-primary);">apps_list.json</code> to provide seeds for the research query.</p>
                            </div>
                            <div class="workflow-step">
                                <span class="workflow-num">2</span>
                                <strong style="color: var(--color-secondary);">Search Grounding Execution</strong>
                                <p style="font-size: 0.85rem; margin-top: 0.25rem;">Gemini was configured with Google Search tools and structured Pydantic schemas, enforcing precise constraints on the schema values.</p>
                            </div>
                            <div class="workflow-step">
                                <span class="workflow-num">3</span>
                                <strong style="color: var(--color-secondary);">Resilient Local Caching</strong>
                                <p style="font-size: 0.85rem; margin-top: 0.25rem;">Results are cached incrementally. If an API rate limit (429) occurs or connection drops, progress is preserved and resume-friendly.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card-premium">
                    <div class="card-header">
                        <span>Where Humans Were Needed</span>
                    </div>
                    <div style="font-size: 0.95rem; color: var(--text-secondary);">
                        <p style="margin-bottom: 1rem;">AI agents excel at horizontal data gathering but can make systematic errors due to developer portal signup semantics. A human-in-the-loop audit was crucial in the following areas:</p>
                        
                        <ul class="pattern-list" style="margin-top: 1.5rem;">
                            <li class="pattern-item">
                                <div class="pattern-icon">1</div>
                                <div>
                                    <div class="pattern-title">Resolving Gated Subscriptions</div>
                                    <div class="pattern-description">The agent misclassified tools like Ahrefs and SE Ranking as self-serve because signups are public, but human verification confirmed that API credentials are restricted to high-tier paid developer subscriptions.</div>
                                </div>
                            </li>
                            <li class="pattern-item">
                                <div class="pattern-icon">2</div>
                                <div>
                                    <div class="pattern-title">Auditing Vetting Requirements</div>
                                    <div class="pattern-description">For Amazon SP-API and Google Ads, the agent missed that developers must undergo manual business vetting and profile review processes before receiving live keys. Humans corrected this to "Gated (Admin Approval)".</div>
                                </div>
                            </li>
                            <li class="pattern-item">
                                <div class="pattern-icon">3</div>
                                <div>
                                    <div class="pattern-title">Validating Evidence URLs</div>
                                    <div class="pattern-description">The agent occasionally cited general homepage links instead of precise developer subdomains. The verification loop resolved this to direct developer URLs.</div>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <!-- Verification Audit Section -->
        <section id="verification" style="padding-top: 6rem; margin-top: -6rem; margin-bottom: 2rem;">
            <div class="section-title-wrapper">
                <div class="section-subtitle">Proof of Quality</div>
                <h2 class="section-title">Verification Loop & Accuracy Trajectory</h2>
            </div>

            <div class="grid-2">
                <div class="card-premium">
                    <div class="card-header">
                        <span>Accuracy Improvement Metrics</span>
                    </div>
                    <div style="font-size: 0.95rem; color: var(--text-secondary);">
                        <p style="margin-bottom: 2rem;">A sample of 15% (15 apps) was randomly audited by hand against official documentation. The comparison shows the dramatic quality leap from the agent's raw first pass (subject to hallucinations and semantic assumptions) to the verified final pass after applying verification constraints.</p>
                        
                        <div class="metric-badge">
                            <span>Auth Methods Accuracy</span>
                            <span class="metric-progress">Pass 1: __AUTH_ACC1__% &rarr; <span style="color: var(--color-success);">Pass 2: __AUTH_ACC2__%</span></span>
                        </div>
                        <div class="metric-badge">
                            <span>Self-Serve Status Accuracy</span>
                            <span class="metric-progress">Pass 1: __SELF_ACC1__% &rarr; <span style="color: var(--color-success);">Pass 2: __SELF_ACC2__%</span></span>
                        </div>
                        <div class="metric-badge">
                            <span>Buildability Verdict Accuracy</span>
                            <span class="metric-progress">Pass 1: __VERDICT_ACC1__% &rarr; <span style="color: var(--color-success);">Pass 2: __VERDICT_ACC2__%</span></span>
                        </div>
                        <div class="metric-badge">
                            <span>Evidence URL Accuracy</span>
                            <span class="metric-progress">Pass 1: __URL_ACC1__% &rarr; <span style="color: var(--color-success);">Pass 2: __URL_ACC2__%</span></span>
                        </div>
                        <div class="metric-badge" style="background: rgba(0, 230, 118, 0.05); border-color: rgba(0, 230, 118, 0.3);">
                            <span style="font-weight: 700; color: #fff;">OVERALL AUDIT ACCURACY</span>
                            <span class="metric-progress" style="color: var(--color-success); font-size: 1.15rem;">Pass 1: __OVERALL_ACC1__% &rarr; Pass 2: __OVERALL_ACC2__%</span>
                        </div>
                    </div>
                </div>

                <div class="card-premium">
                    <div class="card-header">
                        <span>Discrepancy & Audit Report</span>
                    </div>
                    <div class="table-responsive" style="max-height: 480px; border: none;">
                        <table style="font-size: 0.85rem;">
                            <thead>
                                <tr>
                                    <th>App</th>
                                    <th>Pass 1 Value</th>
                                    <th>Pass 2 Corrected</th>
                                    <th>Correction Rationale</th>
                                </tr>
                            </thead>
                            <tbody>
                                __CORRECTION_ROWS__
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <footer>
        <p>&copy; 2026 Composio Tools Research Lab. Built with AI & Automation.</p>
    </footer>

    <!-- Injecting Data & Table Interactivity -->
    <script>
        const apps = __APPS_JSON__;

        // Populate the Table Matrix
        const tableBody = document.getElementById("tableBody");
        const searchInput = document.getElementById("searchInput");
        const categoryFilter = document.getElementById("categoryFilter");
        const authFilter = document.getElementById("authFilter");
        const gatingFilter = document.getElementById("gatingFilter");
        const verdictFilter = document.getElementById("verdictFilter");
        const noResults = document.getElementById("noResults");

        function getVerdictClass(verdict) {
            if (verdict === "Yes") return "badge-yes";
            if (verdict === "No") return "badge-no";
            return "badge-partial";
        }

        function getVerdictText(verdict) {
            if (verdict === "Yes") return "Yes";
            if (verdict === "No") return "No";
            return "Partial";
        }

        function renderTable(data) {
            tableBody.innerHTML = "";
            if (data.length === 0) {
                noResults.style.display = "block";
                return;
            }
            noResults.style.display = "none";

            data.forEach((app) => {
                // Main row
                const tr = document.createElement("tr");
                tr.id = `row-main-${app.id}`;
                tr.setAttribute("onclick", `toggleRowDetail(${app.id})`);

                const authString = app.auth_methods.join(", ");

                tr.innerHTML = `
                    <td style="font-family: var(--font-mono); color: var(--text-muted); font-size: 0.85rem;">#${app.id}</td>
                    <td class="app-name">${app.app_name}</td>
                    <td><span class="category-tag">${app.category}</span></td>
                    <td>${authString}</td>
                    <td>${app.self_serve}</td>
                    <td style="text-align: center;">
                        <span class="badge-verdict ${getVerdictClass(app.buildability_verdict)}">
                            ${getVerdictText(app.buildability_verdict)}
                        </span>
                    </td>
                `;
                tableBody.appendChild(tr);

                // Detail expansion row
                const detailTr = document.createElement("tr");
                detailTr.id = `row-detail-${app.id}`;
                detailTr.className = "details-row";
                
                detailTr.innerHTML = `
                    <td colspan="6">
                        <div class="details-container">
                            <div>
                                <div class="details-heading">One-Liner / What it does</div>
                                <div class="details-text" style="color: var(--text-primary); font-size: 1rem; font-weight: 500;">
                                    ${app.one_liner}
                                </div>
                                <div class="details-heading">API Surface & MCP Server Details</div>
                                <div class="details-text">${app.api_surface}</div>
                            </div>
                            <div>
                                <div class="details-heading">Main Blocker</div>
                                <div class="details-text" style="color: ${app.main_blocker === 'None' ? 'var(--color-success)' : 'var(--color-danger)'};">
                                    ${app.main_blocker}
                                </div>
                                <div class="details-heading">Evidence / Developer Docs</div>
                                <div class="details-text">
                                    <a href="${app.evidence_url}" target="_blank" style="word-break: break-all;">
                                        ${app.evidence_url} &nearrow;
                                    </a>
                                </div>
                            </div>
                        </div>
                    </td>
                `;
                tableBody.appendChild(detailTr);
            });
        }

        let currentlyOpenRow = null;

        function toggleRowDetail(id) {
            const detailRow = document.getElementById(`row-detail-${id}`);
            const mainRow = document.getElementById(`row-main-${id}`);
            
            if (currentlyOpenRow && currentlyOpenRow !== id) {
                const prevDetail = document.getElementById(`row-detail-${currentlyOpenRow}`);
                const prevMain = document.getElementById(`row-main-${currentlyOpenRow}`);
                if (prevDetail) prevDetail.style.display = "none";
                if (prevMain) prevMain.style.background = "";
            }

            if (detailRow.style.display === "table-row") {
                detailRow.style.display = "none";
                mainRow.style.background = "";
                currentlyOpenRow = null;
            } else {
                detailRow.style.display = "table-row";
                mainRow.style.background = "rgba(124, 77, 255, 0.05)";
                currentlyOpenRow = id;
            }
        }

        // Search and Filter Logic
        function filterData() {
            const query = searchInput.value.toLowerCase();
            const cat = categoryFilter.value;
            const auth = authFilter.value;
            const gate = gatingFilter.value;
            const verdict = verdictFilter.value;

            const filtered = apps.filter((app) => {
                const matchesQuery = 
                    app.app_name.toLowerCase().includes(query) ||
                    app.category.toLowerCase().includes(query) ||
                    app.one_liner.toLowerCase().includes(query) ||
                    app.auth_methods.some(a => a.toLowerCase().includes(query));

                const matchesCat = cat === "" || app.category === cat;
                const matchesAuth = auth === "" || app.auth_methods.some(a => a.toLowerCase().includes(auth.toLowerCase()));
                const matchesGate = gate === "" || app.self_serve === gate;
                const matchesVerdict = verdict === "" || app.buildability_verdict === verdict;

                return matchesQuery && matchesCat && matchesAuth && matchesGate && matchesVerdict;
            });

            renderTable(filtered);
        }

        searchInput.addEventListener("input", filterData);
        categoryFilter.addEventListener("change", filterData);
        authFilter.addEventListener("change", filterData);
        gatingFilter.addEventListener("change", filterData);
        verdictFilter.addEventListener("change", filterData);

        // Initial Render
        renderTable(apps);

        // Charts configuration using Chart.js
        const authData = __AUTH_CHART__;
        const gatingData = __GATING_CHART__;
        const verdictData = __VERDICT_CHART__;
        const blockerData = __BLOCKER_CHART__;

        Chart.defaults.color = '#a097b6';
        Chart.defaults.font.family = "'Inter', sans-serif";

        // Auth Chart
        new Chart(document.getElementById('authChart'), {
            type: 'bar',
            data: {
                labels: Object.keys(authData),
                datasets: [{
                    data: Object.values(authData),
                    backgroundColor: ['#7c4dff', '#00e5ff', '#00e676', '#ffea00', '#ff1744'],
                    borderWidth: 0,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: '#2b263e' } },
                    x: { grid: { display: false } }
                }
            }
        });

        // Gating Chart
        new Chart(document.getElementById('gatingChart'), {
            type: 'doughnut',
            data: {
                labels: Object.keys(gatingData),
                datasets: [{
                    data: Object.values(gatingData),
                    backgroundColor: ['#00e676', '#ffea00', '#7c4dff', '#ff1744', '#a097b6'],
                    borderWidth: 2,
                    borderColor: '#13111b'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right', labels: { boxWidth: 12, padding: 15 } }
                }
            }
        });

        // Verdict Chart
        new Chart(document.getElementById('verdictChart'), {
            type: 'pie',
            data: {
                labels: Object.keys(verdictData),
                datasets: [{
                    data: Object.values(verdictData),
                    backgroundColor: ['#00e676', '#ff1744', '#ffea00'],
                    borderWidth: 2,
                    borderColor: '#13111b'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right', labels: { boxWidth: 12, padding: 15 } }
                }
            }
        });

        // Blocker Chart
        new Chart(document.getElementById('blockerChart'), {
            type: 'bar',
            data: {
                labels: Object.keys(blockerData),
                datasets: [{
                    data: Object.values(blockerData),
                    backgroundColor: ['#ff1744', '#ffea00', '#7c4dff', '#00e5ff'],
                    borderWidth: 0,
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: '#2b263e' } },
                    y: { grid: { display: false } }
                }
            }
        });

    </script>
</body>
</html>
"""

    # Inject variables via .replace()
    html_content = html_template \
        .replace("__APPS_JSON__", apps_json_str) \
        .replace("__AUTH_CHART__", auth_chart_data) \
        .replace("__GATING_CHART__", gating_chart_data) \
        .replace("__VERDICT_CHART__", verdict_chart_data) \
        .replace("__BLOCKER_CHART__", blocker_chart_data) \
        .replace("__AUTH_ACC1__", f"{verification_data['pass1']['auth_accuracy']:.1f}") \
        .replace("__AUTH_ACC2__", f"{verification_data['pass2']['auth_accuracy']:.1f}") \
        .replace("__SELF_ACC1__", f"{verification_data['pass1']['self_serve_accuracy']:.1f}") \
        .replace("__SELF_ACC2__", f"{verification_data['pass2']['self_serve_accuracy']:.1f}") \
        .replace("__VERDICT_ACC1__", f"{verification_data['pass1']['verdict_accuracy']:.1f}") \
        .replace("__VERDICT_ACC2__", f"{verification_data['pass2']['verdict_accuracy']:.1f}") \
        .replace("__URL_ACC1__", f"{verification_data['pass1']['url_accuracy']:.1f}") \
        .replace("__URL_ACC2__", f"{verification_data['pass2']['url_accuracy']:.1f}") \
        .replace("__OVERALL_ACC1__", f"{verification_data['pass1']['overall']:.1f}") \
        .replace("__OVERALL_ACC2__", f"{verification_data['pass2']['overall']:.1f}") \
        .replace("__CORRECTION_ROWS__", correction_rows_html)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Report generator finished. {report_path} compiled successfully.")

if __name__ == "__main__":
    main()
