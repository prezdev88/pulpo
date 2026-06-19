from __future__ import annotations

import html
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import HTMLResponse, Response
    import uvicorn
except ModuleNotFoundError as exc:
    print(
        "Falta una dependencia para iniciar la GUI.\n"
        "Instala los requisitos con:\n"
        "  pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


STYLESHEET = """
:root {
  color-scheme: light;
  --bg: #e9eef5;
  --panel: rgba(255, 255, 255, 0.94);
  --text: #111827;
  --muted: #5f6b7a;
  --accent: #2563eb;
  --accent-strong: #1d4ed8;
  --border: rgba(22, 33, 38, 0.1);
  --surface-soft: rgba(255, 255, 255, 0.9);
  --surface-muted: rgba(248, 250, 251, 0.96);
  --surface-solid: rgba(255, 255, 255, 0.98);
  --surface-subtle: rgba(22, 33, 38, 0.045);
  --surface-subtle-strong: rgba(22, 33, 38, 0.075);
  --track: rgba(22, 33, 38, 0.1);
  --table-head: rgba(37, 99, 235, 0.1);
  --table-row: rgba(37, 99, 235, 0.035);
  --code-bg: #0f172a;
  --code-text: #e5eefc;
  --shadow: none;
  --sidebar-bg: #0f172a;
  --sidebar-surface: rgba(255, 255, 255, 0.04);
  --sidebar-text: #eef4ff;
  --sidebar-muted: rgba(238, 244, 255, 0.62);
  --hero-bg: #f8fbff;
  --hero-border: rgba(22, 33, 38, 0.08);
  --sidebar-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.05);
  --menu-active-bg: rgba(37, 99, 235, 0.16);
  --menu-active-border: rgba(37, 99, 235, 0.34);
  --menu-hover-shadow: none;
}

:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #0b1020;
  --panel: rgba(15, 23, 42, 0.96);
  --text: #e5ecf7;
  --muted: #90a0b7;
  --accent: #60a5fa;
  --accent-strong: #93c5fd;
  --border: rgba(170, 190, 198, 0.14);
  --surface-soft: rgba(15, 23, 42, 0.92);
  --surface-muted: rgba(12, 20, 36, 0.98);
  --surface-solid: rgba(18, 28, 48, 0.98);
  --surface-subtle: rgba(255, 255, 255, 0.04);
  --surface-subtle-strong: rgba(255, 255, 255, 0.07);
  --track: rgba(255, 255, 255, 0.1);
  --table-head: rgba(96, 165, 250, 0.16);
  --table-row: rgba(96, 165, 250, 0.05);
  --code-bg: #050816;
  --code-text: #dde8ff;
  --shadow: none;
  --sidebar-bg: #050816;
  --sidebar-surface: rgba(255, 255, 255, 0.045);
  --sidebar-text: #eef4ff;
  --sidebar-muted: rgba(238, 244, 255, 0.64);
  --hero-bg: #121c30;
  --hero-border: rgba(170, 190, 198, 0.12);
  --sidebar-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.05);
  --menu-active-bg: rgba(96, 165, 250, 0.14);
  --menu-active-border: rgba(96, 165, 250, 0.28);
  --menu-hover-shadow: none;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  font-family: "Avenir Next", "Segoe UI", "Noto Sans", "Helvetica Neue", sans-serif;
  color: var(--text);
  background: var(--bg);
}

a {
  color: inherit;
}

code {
  padding: 0.12rem 0.38rem;
  border-radius: 999px;
  background: var(--surface-subtle);
}

.shell {
  width: min(1280px, calc(100% - 32px));
  margin: 0 auto;
  padding: 48px 0 80px;
}

.home-app-shell {
  display: grid;
  grid-template-columns: 308px minmax(0, 1fr);
  min-height: 100vh;
}

.home-nav-toggle {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.home-nav-overlay,
.home-mobile-bar,
.home-nav-close {
  display: none;
}

.home-sidebar {
  display: grid;
  align-content: start;
  gap: 18px;
  padding: 20px 16px;
  border-right: 1px solid var(--border);
  position: sticky;
  top: 0;
  min-height: 100vh;
  max-height: 100vh;
  overflow-y: auto;
  background: var(--sidebar-bg);
  box-shadow: var(--sidebar-shadow);
  color: var(--sidebar-text);
}

.home-sidebar-header {
  display: grid;
  gap: 12px;
  padding: 0 4px 4px;
}

.home-sidebar-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.home-title {
  margin: 0;
  font-size: 1.2rem;
  line-height: 1.05;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--sidebar-text);
}

.home-sidebar-copy {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
}

.home-menu {
  display: grid;
  gap: 0;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.home-workspace-picker {
  display: grid;
  gap: 8px;
  padding: 0 0 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.home-workspace-picker label {
  color: var(--sidebar-muted);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.home-workspace-select {
  width: 100%;
  padding: 14px 44px 14px 14px;
  border: 1px solid var(--border);
  border-radius: 0;
  background: rgba(255, 255, 255, 0.06);
  color: var(--sidebar-text);
  font: inherit;
  cursor: pointer;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
  appearance: auto;
  -webkit-appearance: auto;
  -moz-appearance: auto;
}

.home-workspace-select option {
  color: #0f172a;
}

.home-workspace-select:focus-visible {
  outline: 2px solid rgba(37, 99, 235, 0.45);
  outline-offset: 2px;
}

.home-menu-group {
  display: grid;
  gap: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.home-menu-group.collapsible {
  gap: 0;
}

.home-menu-label {
  color: var(--sidebar-muted);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.home-menu-link {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr);
  gap: 12px;
  padding: 14px 16px;
  border: 0;
  border-radius: 0;
  background: transparent;
  color: var(--sidebar-text);
  text-decoration: none;
  transition: background 120ms ease, color 120ms ease;
}

.home-menu-link:hover,
.home-menu-link.active,
.home-menu-link:focus-visible {
  background: rgba(255, 255, 255, 0.04);
}

.home-menu-link strong {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--sidebar-text);
}

.home-menu-copy {
  display: block;
}

.home-menu-icon,
.home-menu-summary-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  color: var(--accent);
  font-size: 1.18rem;
  line-height: 1;
}

.home-menu-summary {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr);
  gap: 12px;
  padding: 14px 16px;
  border: 0;
  border-radius: 0;
  background: transparent;
  cursor: pointer;
  list-style: none;
  transition: background 120ms ease, color 120ms ease;
}

.home-menu-summary::-webkit-details-marker {
  display: none;
}

.home-menu-summary::after {
  content: "+";
  position: absolute;
  right: 16px;
  top: 16px;
  color: var(--accent-strong);
  font-size: 1.1rem;
  font-weight: 700;
}

.home-menu-group[open] .home-menu-summary::after {
  content: "-";
}

.home-menu-summary strong {
  display: block;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--sidebar-text);
}

.home-menu-group.collapsible {
  position: relative;
}

.home-menu-group.collapsible:hover .home-menu-summary,
.home-menu-group.collapsible[open] .home-menu-summary {
  background: rgba(255, 255, 255, 0.04);
}

.home-submenu {
  display: grid;
  gap: 0;
  margin: 0 0 8px;
  padding: 0 0 0 18px;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
}

.home-submenu-link {
  display: block;
  padding: 12px 12px;
  color: var(--sidebar-muted);
  text-decoration: none;
  line-height: 1.45;
  border: 0;
  border-radius: 0;
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.home-submenu-link:hover,
.home-submenu-link.active,
.home-submenu-link:focus-visible {
  color: var(--sidebar-text);
  background: rgba(255, 255, 255, 0.04);
}

.home-content {
  display: grid;
  align-content: start;
  gap: 14px;
  padding: 16px 18px 22px;
  min-width: 0;
}

.home-nav-button,
.home-nav-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  border: 1px solid var(--border);
  background: var(--sidebar-surface);
  color: var(--sidebar-text);
  font: inherit;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  transition: background 120ms ease, border-color 120ms ease, color 120ms ease;
}

.home-nav-button:hover,
.home-nav-button:focus-visible,
.home-nav-close:hover,
.home-nav-close:focus-visible {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--menu-active-border);
  color: var(--sidebar-text);
}

.home-hero {
  display: grid;
  gap: 0;
  padding: 22px 24px;
  border: 1px solid var(--hero-border);
  border-radius: 0;
  background: var(--hero-bg);
  box-shadow: var(--shadow);
}

.home-hero h1,
.document-header h1 {
  margin: 0;
  font-size: clamp(1.9rem, 3vw, 2.8rem);
  line-height: 1.05;
  letter-spacing: -0.03em;
  font-weight: 800;
}

.home-section {
  display: grid;
  gap: 18px;
  scroll-margin-top: 24px;
}

.home-section-header {
  display: grid;
  gap: 8px;
}

.home-section-header h2 {
  margin: 0;
  font-size: clamp(1.8rem, 2.4vw, 2.6rem);
}

.home-section-header p {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
}

.stack-grid {
  display: grid;
  gap: 18px;
}

.stack-grid.two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.stack-grid.three {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.home-panel {
  padding: 22px;
  border: 1px solid var(--border);
  border-radius: 0;
  background: var(--surface-soft);
  box-shadow: var(--shadow);
}

.home-panel h3 {
  margin: 0 0 12px;
  font-size: 1.28rem;
}

.home-panel p {
  color: var(--muted);
}

.home-panel p:last-child {
  margin-bottom: 0;
}

.documents-panel-list {
  display: grid;
  gap: 14px;
}

.shell-toolbar,
.document-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.shell-toolbar {
  margin-bottom: 18px;
}

.hero {
  padding: 48px;
  border: 1px solid var(--border);
  border-radius: 0;
  background: var(--panel);
  backdrop-filter: blur(16px);
  box-shadow: var(--shadow);
}

.eyebrow {
  margin: 0 0 14px;
  color: var(--accent-strong);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: clamp(2.6rem, 6vw, 5rem);
  line-height: 0.96;
}

.lede {
  max-width: 38rem;
  margin: 20px 0 0;
  color: var(--muted);
  font-size: 1.15rem;
  line-height: 1.7;
}

.dashboard-grid,
.overview-grid {
  display: grid;
  gap: 18px;
  margin-top: 24px;
}

.dashboard-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.overview-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.metric-card,
.overview-card,
.dashboard-focus-card {
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 0;
  background: var(--surface-soft);
  box-shadow: var(--shadow);
}

.metric-label {
  display: inline-block;
  color: var(--accent-strong);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.metric-card strong {
  display: block;
  margin-top: 14px;
  font-size: clamp(2rem, 5vw, 3rem);
  line-height: 0.95;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.metric-card p,
.overview-card p,
.dashboard-focus-card p {
  color: var(--muted);
}

.overview-card h2,
.dashboard-focus-card h3 {
  margin: 8px 0 12px;
  letter-spacing: -0.02em;
}

.quick-links,
.mini-status-grid {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}

.quick-link,
.primary-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  padding: 0.72rem 1rem;
  border-radius: 0;
  text-decoration: none;
  border: 1px solid transparent;
  transition: transform 120ms ease, border-color 120ms ease, background 120ms ease;
}

.quick-link {
  background: var(--surface-subtle-strong);
  color: var(--text);
}

.primary-link {
  margin-top: 16px;
  background: var(--accent);
  color: #f5fbfa;
}

.quick-link:hover,
.primary-link:hover {
  transform: translateY(-1px);
}

.quick-link:hover {
  border-color: var(--menu-active-border);
}

.mini-status-row {
  display: grid;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 0;
  background: var(--surface-subtle);
}

.mini-status-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.mini-status-topline strong {
  font-size: 1rem;
}

.mini-status-bar-track {
  width: 100%;
  height: 10px;
  border-radius: 999px;
  background: var(--track);
  overflow: hidden;
}

.mini-status-bar-fill {
  display: block;
  height: 100%;
  border-radius: 999px;
  min-width: 0;
}

.mini-status-bar-fill.todo {
  background: #dc2626;
}

.mini-status-bar-fill.inprogress {
  background: #ca8a04;
}

.mini-status-bar-fill.done {
  background: #16a34a;
}

.mini-status-bar-fill.blocked {
  background: #475569;
}

.inventory {
  margin-top: 26px;
  padding: 26px 0 0;
}

.inventory-heading h2 {
  margin: 6px 0 0;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
}

.section-kicker {
  margin: 0;
  color: var(--accent-strong);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.workspace-grid {
  display: grid;
  gap: 18px;
  margin-top: 20px;
}

.workspace-card,
.empty-state {
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 0;
  background: var(--surface-muted);
  box-shadow: var(--shadow);
}

.workspace-card header h2 {
  margin: 0;
  font-size: 1.05rem;
  letter-spacing: -0.01em;
  text-transform: uppercase;
}

.workspace-card header p {
  margin: 8px 0 0;
  color: var(--muted);
}

.workspace-card ul {
  list-style: none;
  padding: 0;
  margin: 18px 0 0;
}

.doc-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-top: 1px solid var(--track);
}

.doc-item:first-child {
  border-top: 0;
  padding-top: 0;
}

.doc-kind {
  min-width: 86px;
  padding: 0.22rem 0.55rem;
  border-radius: 999px;
  background: rgba(15, 118, 110, 0.12);
  color: var(--accent-strong);
  font-size: 0.78rem;
  font-weight: 700;
  text-align: center;
  text-transform: uppercase;
}

.doc-name,
.doc-link,
.empty-state p,
.muted {
  color: var(--muted);
}

.doc-link {
  text-decoration: none;
  transition: color 120ms ease;
}

.doc-link:hover {
  color: var(--text);
}

.empty-state strong {
  display: block;
  margin-bottom: 10px;
}

.reader-shell {
  display: grid;
  grid-template-columns: minmax(240px, 300px) minmax(0, 1fr);
  width: min(1280px, calc(100% - 32px));
  margin: 0 auto;
  padding: 28px 0 48px;
  gap: 22px;
  align-items: start;
}

.sidebar-toggle-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.sidebar-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  padding: 0.72rem 1rem;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface-solid);
  color: var(--text);
  cursor: pointer;
  font-weight: 700;
  box-shadow: var(--shadow);
}

.toolbar-actions {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.theme-switcher {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px;
  border: 1px solid var(--border);
  border-radius: 0;
  background: rgba(255, 255, 255, 0.05);
  box-shadow: none;
}

.theme-option {
  border: 0;
  border-radius: 0;
  padding: 0.58rem 0.92rem;
  background: transparent;
  color: var(--sidebar-muted);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.theme-option:hover {
  color: var(--sidebar-text);
}

.theme-option.active {
  background: var(--accent);
  color: #f5fbfa;
}

.sidebar-toggle::before {
  content: "Ocultar menu";
}

.reader-shell:has(.sidebar-toggle-input:checked) {
  grid-template-columns: minmax(0, 1fr);
}

.reader-shell:has(.sidebar-toggle-input:checked) .sidebar {
  display: none;
}

.reader-shell:has(.sidebar-toggle-input:checked) .sidebar-toggle::before {
  content: "Mostrar menu";
}

.sidebar,
.document-panel {
  border: 1px solid var(--border);
  border-radius: 0;
  background: var(--panel);
  backdrop-filter: blur(16px);
  box-shadow: var(--shadow);
}

.sidebar {
  padding: 24px 20px;
  align-self: start;
  position: sticky;
  top: 20px;
}

.home-link {
  color: var(--text);
  text-decoration: none;
  font-weight: 700;
}

.sidebar-kicker {
  margin: 18px 0 10px;
  color: var(--accent-strong);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.sidebar-workspace + .sidebar-workspace {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid var(--track);
}

.sidebar-workspace {
  display: grid;
  gap: 10px;
}

.sidebar-workspace summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 0;
  cursor: pointer;
  list-style: none;
}

.sidebar-workspace summary::-webkit-details-marker {
  display: none;
}

.sidebar-workspace summary:hover,
.sidebar-workspace[open] summary {
  background: rgba(15, 118, 110, 0.08);
}

.sidebar-workspace h2 {
  margin: 0;
  font-size: 1rem;
}

.sidebar-workspace-count {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--muted);
  font-size: 0.84rem;
}

.sidebar-workspace-count::before {
  content: "▸";
  color: var(--accent-strong);
  transition: transform 160ms ease;
}

.sidebar-workspace[open] .sidebar-workspace-count::before {
  transform: rotate(90deg);
}

.sidebar-workspace ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-doc {
  display: block;
  padding: 10px 12px;
  border-radius: 0;
  color: var(--muted);
  text-decoration: none;
}

.sidebar-doc:hover,
.sidebar-doc.active {
  background: rgba(15, 118, 110, 0.1);
  color: var(--text);
}

.document-panel {
  padding: 36px 38px;
}

.document-header {
  padding-bottom: 20px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--track);
}

.markdown-body {
  font-size: 1.05rem;
  line-height: 1.75;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  line-height: 1.15;
  margin: 1.6em 0 0.6em;
}

.markdown-body h1 {
  font-size: clamp(1.9rem, 3vw, 2.8rem);
  letter-spacing: -0.03em;
}

.markdown-body h1:first-child,
.markdown-body h2:first-child,
.markdown-body h3:first-child {
  margin-top: 0;
}

.markdown-body p,
.markdown-body ul,
.markdown-body pre,
.markdown-body .table-scroll {
  margin: 0 0 1rem;
}

.markdown-body ul {
  padding-left: 1.25rem;
}

.markdown-body li + li {
  margin-top: 0.35rem;
}

.markdown-body pre {
  overflow-x: auto;
  padding: 18px;
  border-radius: 18px;
  background: var(--code-bg);
  color: var(--code-text);
}

.markdown-body .table-scroll {
  overflow-x: auto;
}

.markdown-table {
  width: 100%;
  min-width: 520px;
  border-collapse: collapse;
  border-spacing: 0;
  background: var(--surface-soft);
  border: 1px solid var(--border);
  border-radius: 18px;
  overflow: hidden;
}

.markdown-table th,
.markdown-table td {
  padding: 14px 16px;
  vertical-align: top;
  border-bottom: 1px solid var(--track);
}

.markdown-table th {
  background: var(--table-head);
  font-weight: 700;
  text-align: left;
  white-space: nowrap;
}

.markdown-table tbody tr:nth-child(even) {
  background: var(--table-row);
}

.markdown-table tbody tr:last-child td {
  border-bottom: 0;
}

.specialized-view {
  display: grid;
  gap: 20px;
}

.status-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.status-summary-card,
.focus-card,
.task-panel,
.empty-task-card {
  padding: 18px;
  border-radius: 0;
  border: 1px solid var(--border);
  background: var(--surface-soft);
}

.status-summary-card {
  padding: 16px 18px;
}

.status-summary-card span {
  display: block;
  font-size: 0.9rem;
  line-height: 1.45;
  color: var(--muted);
}

.task-card {
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.status-summary-card strong {
  display: block;
  margin-top: 10px;
  font-size: 0.95rem;
  line-height: 1.35;
  font-weight: 520;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.status-value {
  margin: 10px 0 0;
  font-size: 1.05rem;
  line-height: 1.3;
  font-weight: 520;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.specialized-view.status-view {
  gap: 16px;
}

.status-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(220px, 0.8fr);
  gap: 18px;
  padding: 20px 22px;
  border-radius: 0;
  border: 1px solid var(--border);
  background: var(--surface-solid);
  box-shadow: 0 18px 40px rgba(87, 64, 30, 0.08);
}

.status-hero-copy {
  display: grid;
  gap: 10px;
}

.status-eyebrow {
  margin: 0;
  font-size: 1.45rem;
  line-height: 1.15;
  font-weight: 650;
  letter-spacing: -0.02em;
}

.status-hero-copy p {
  margin: 0;
  color: var(--muted);
}

.status-phase-card {
  display: grid;
  align-content: start;
  gap: 12px;
  padding: 16px 18px;
  border-radius: 0;
  background: var(--surface-solid);
  border: 1px solid rgba(15, 118, 110, 0.12);
}

.status-phase-card span {
  color: var(--muted);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.status-phase-card strong {
  font-size: 1.8rem;
  line-height: 1;
  font-weight: 600;
}

.status-phase-value {
  margin: 0;
  font-size: 1.8rem;
  line-height: 1;
  font-weight: 600;
}

.status-phase-card .status-chip {
  margin-top: 2px;
}

.status-topline-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.status-summary-card.compact {
  min-height: 118px;
}

.status-summary-card.compact strong {
  font-size: 1.05rem;
  line-height: 1.3;
  font-weight: 520;
}

.status-action-card {
  display: grid;
  gap: 10px;
  padding: 18px 20px;
  border-radius: 0;
  border: 1px solid var(--border);
  background: var(--surface-soft);
}

.status-action-card p {
  margin: 0;
}

.status-action-card strong {
  font-size: 1.08rem;
  line-height: 1.55;
  font-weight: 500;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.status-action-value {
  margin: 0;
  font-size: 1.08rem;
  line-height: 1.55;
  font-weight: 500;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.status-meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.status-meta-card {
  padding: 16px 18px;
  border-radius: 0;
  border: 1px solid var(--border);
  background: var(--surface-muted);
}

.status-meta-card dt {
  margin: 0 0 8px;
  color: var(--muted);
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.status-meta-card dd {
  margin: 0;
  font-weight: 600;
  line-height: 1.5;
  overflow-wrap: anywhere;
  word-break: break-word;
}

@media (min-width: 960px) {
  .status-summary-grid {
    grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
  }
}

.backlog-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.backlog-column {
  display: grid;
  gap: 12px;
  align-content: start;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  gap: 8px;
  padding: 0.32rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  background: var(--surface-subtle-strong);
}

.status-chip::before {
  content: "";
  width: 0.9rem;
  height: 0.9rem;
  border-radius: 999px;
  flex: 0 0 auto;
  background: rgba(31, 28, 23, 0.24);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.22);
}

.status-chip.todo {
  background: rgba(220, 38, 38, 0.12);
  color: #991b1b;
}

.status-chip.todo::before {
  background: #dc2626;
}

.status-chip.inprogress {
  background: rgba(202, 138, 4, 0.16);
  color: #854d0e;
}

.status-chip.inprogress::before {
  background: #fbbf24;
}

.status-chip.done {
  background: rgba(22, 163, 74, 0.14);
  color: #166534;
}

.status-chip.done::before {
  background: #22c55e;
}

.status-chip.blocked {
  background: rgba(31, 41, 55, 0.12);
  color: #111827;
}

.status-chip.blocked::before {
  background: #4b5563;
}

.task-card h3,
.task-panel h3,
.focus-card h2 {
  margin: 0 0 12px;
}

.task-card-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.task-card-title-row h3 {
  margin: 0;
}

.task-state-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  flex: 0 0 auto;
  margin-top: -10px;
  background: rgba(31, 28, 23, 0.22);
}

.backlog-column:has(.status-chip.todo) .task-state-dot {
  background: #dc2626;
}

.backlog-column:has(.status-chip.inprogress) .task-state-dot {
  background: #ca8a04;
}

.backlog-column:has(.status-chip.done) .task-state-dot {
  background: #16a34a;
}

.backlog-column:has(.status-chip.blocked) .task-state-dot {
  background: #1f2937;
}

.task-card ul,
.task-panel ul {
  margin: 0;
  padding-left: 1.1rem;
}

.task-card-button {
  display: flex;
  width: 100%;
  padding: 16px 18px;
  border-radius: 0;
  border: 1px solid var(--border);
  background: var(--surface-soft);
  color: var(--text);
  text-decoration: none;
  transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease;
}

.task-card-button:hover {
  transform: translateY(-1px);
  border-color: rgba(15, 118, 110, 0.28);
  box-shadow: 0 18px 40px rgba(87, 64, 30, 0.12);
}

.task-card-button:focus-visible,
.modal-close:focus-visible {
  outline: 2px solid rgba(15, 118, 110, 0.45);
  outline-offset: 3px;
}

.task-card-copy {
  display: grid;
  gap: 4px;
}

.developer-chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.task-card-copy .developer-chip-group {
  margin-top: 6px;
}

.task-card-title {
  margin: 0;
  font-size: 0.98rem;
  font-weight: 400;
  line-height: 1.4;
}

.task-code-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  padding: 0.22rem 0.56rem;
  border-radius: 999px;
  background: var(--surface-subtle-strong);
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.developer-chip {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 0.24rem 0.65rem;
  border-radius: 999px;
  background: rgba(15, 118, 110, 0.12);
  color: var(--accent-strong);
  font-size: 0.78rem;
  font-weight: 600;
}

.task-card-copy p {
  margin: 0;
  color: var(--muted);
  font-size: 0.92rem;
}

.task-modal {
  position: fixed;
  inset: 0;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(17, 24, 39, 0.56);
  z-index: 20;
}

.task-modal:target {
  display: flex;
}

.task-modal-dialog {
  width: min(680px, 100%);
  max-height: min(80vh, 720px);
  overflow: auto;
  padding: 24px;
  border-radius: 0;
  border: 1px solid var(--border);
  background: var(--panel);
  box-shadow: 0 28px 100px rgba(17, 24, 39, 0.28);
}

.task-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.task-modal-header h3 {
  margin: 8px 0 0;
}

.task-modal-body {
  display: grid;
  gap: 16px;
}

.task-modal-panel {
  padding: 18px;
  border-radius: 0;
  border: 1px solid var(--border);
  background: var(--surface-soft);
}

.task-modal-panel h4 {
  margin: 0 0 12px;
}

.task-modal-panel p,
.task-modal-panel ul {
  margin: 0;
}

.task-modal-panel ul {
  padding-left: 1.1rem;
}

.modal-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  padding: 0.72rem 1rem;
  border-radius: 999px;
  background: var(--surface-subtle-strong);
  color: var(--text);
  text-decoration: none;
  font-weight: 700;
}

.current-task-view {
  gap: 18px;
}

.focus-card {
  padding: 24px;
  border-radius: 0;
}

.task-pill {
  display: inline-flex;
  margin: 8px 0 16px;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  background: rgba(15, 118, 110, 0.12);
  color: var(--accent-strong);
  font-weight: 700;
  text-decoration: none;
}

.task-pill-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.task-pill-group .task-pill {
  margin: 8px 0 16px;
}

.focus-objective {
  margin: 0;
  color: var(--muted);
  font-size: 1.05rem;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

code {
  padding: 0.16rem 0.42rem;
  border-radius: 999px;
  background: rgba(31, 28, 23, 0.08);
  font-size: 0.95em;
}

@media (max-width: 900px) {
  .home-app-shell {
    grid-template-columns: 1fr;
  }

  .home-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 40;
    width: min(86vw, 360px);
    min-height: 100vh;
    max-height: 100vh;
    border-right: 1px solid var(--border);
    transform: translateX(-100%);
    transition: transform 180ms ease;
  }

  .home-app-shell:has(.home-nav-toggle:checked) .home-sidebar {
    transform: translateX(0);
  }

  .home-nav-overlay {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 30;
    background: rgba(5, 8, 22, 0.46);
  }

  .home-app-shell:has(.home-nav-toggle:checked) .home-nav-overlay {
    display: block;
  }

  .home-content {
    padding: 16px;
  }

  .home-mobile-bar {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 4px;
  }

  .home-nav-close {
    display: inline-flex;
  }

  .home-nav-button {
    background: var(--surface-solid);
    color: var(--text);
  }

  .home-nav-button:hover,
  .home-nav-button:focus-visible {
    background: var(--surface-muted);
    color: var(--text);
  }

  .stack-grid.two,
  .stack-grid.three {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .home-sidebar-header {
    gap: 10px;
    padding: 0;
  }

  .home-sidebar-topline {
    align-items: flex-start;
  }

  .home-title {
    font-size: 1.05rem;
    letter-spacing: 0.06em;
  }

  .home-workspace-picker {
    gap: 6px;
    padding-bottom: 10px;
  }

  .home-workspace-select {
    padding: 13px 42px 13px 12px;
    font-size: 0.98rem;
  }

  .home-menu-link,
  .home-menu-summary {
    grid-template-columns: 20px minmax(0, 1fr);
    gap: 10px;
    padding: 13px 12px;
  }

  .home-menu-icon,
  .home-menu-summary-icon {
    width: 20px;
    height: 20px;
    font-size: 1.05rem;
  }

  .home-submenu {
    padding-left: 14px;
  }

  .home-submenu-link {
    padding: 11px 10px;
    font-size: 0.95rem;
  }

  .home-content {
    gap: 12px;
    padding: 12px;
  }

  .home-hero {
    padding: 16px 14px;
  }

  .home-hero h1 {
    font-size: clamp(1.7rem, 10vw, 2.4rem);
    line-height: 0.95;
  }

  .shell {
    width: min(100% - 20px, 960px);
    padding-top: 24px;
  }

  .status-hero {
    grid-template-columns: 1fr;
  }

  .reader-shell {
    grid-template-columns: 1fr;
    width: min(100% - 20px, 1280px);
    padding-top: 20px;
  }

  .shell-toolbar,
  .document-toolbar {
    justify-content: flex-start;
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-actions,
  .theme-switcher {
    width: 100%;
  }

  .theme-option {
    flex: 1 1 0;
  }

  .sidebar {
    position: static;
  }

  .hero {
    padding: 28px 22px;
    border-radius: 0;
  }

  .document-panel {
    padding: 20px 16px;
  }

  .lede {
    font-size: 1rem;
  }

  .document-header {
    padding-bottom: 14px;
    margin-bottom: 14px;
  }

  .markdown-body {
    font-size: 0.98rem;
    line-height: 1.65;
  }

  .overview-card,
  .dashboard-focus-card,
  .workspace-card,
  .empty-state,
  .home-panel,
  .task-panel,
  .task-modal-panel,
  .focus-card {
    padding: 16px;
  }
}
"""

THEME_BOOTSTRAP_SCRIPT = """<script>
(() => {
  const stored = localStorage.getItem("iteraspec-theme");
  const theme = stored === "dark" || stored === "light" ? stored : "light";
  document.documentElement.dataset.theme = theme;
})();
</script>"""

THEME_BEHAVIOR_SCRIPT = """<script>
(() => {
  const root = document.documentElement;
  const buttons = Array.from(document.querySelectorAll("[data-theme-option]"));
  const normalizeTheme = (value) => (value === "dark" ? "dark" : "light");
  const applyTheme = (theme) => {
    const normalized = normalizeTheme(theme);
    root.dataset.theme = normalized;
    localStorage.setItem("iteraspec-theme", normalized);
    buttons.forEach((button) => {
      const active = button.dataset.themeOption === normalized;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => applyTheme(button.dataset.themeOption));
  });

  applyTheme(root.dataset.theme || "light");
})();
</script>"""

KNOWN_DOCUMENTS = ("status.md", "specs.md", "backlog.md", "board.md", "staffing.md", "current_task.md", "delivery.md")
WORKSPACE_DOCUMENT_ORDER = ("specs.md", "backlog.md", "board.md", "staffing.md", "current_task.md", "delivery.md")
GLOBAL_WORKSPACE_NAME = "_global"
DEVELOPERS_DIRNAME = "developers"
WORKSPACES_DIRNAME = "workspaces"
BACKLOG_SECTION_PATTERNS = (
    (re.compile(r"^##\s+`?🔴\s+To Do`?\s*$"), ("todo", "To Do")),
    (re.compile(r"^##\s+`?🟢\s+To Do`?\s*$"), ("todo", "To Do")),
    (re.compile(r"^##\s+`?🟡\s+In Progress`?\s*$"), ("inprogress", "In Progress")),
    (re.compile(r"^##\s+`?🔴\s+Done`?\s*$"), ("done", "Done")),
    (re.compile(r"^##\s+`?🟢\s+Done`?\s*$"), ("done", "Done")),
    (re.compile(r"^##\s+`?⚫\s+Blocked`?\s*$"), ("blocked", "Blocked")),
)
BACKLOG_SECTION_ORDER = (
    ("todo", "To Do"),
    ("inprogress", "In Progress"),
    ("done", "Done"),
    ("blocked", "Blocked"),
)


@dataclass(slots=True)
class IteraSpecDocument:
    name: str
    relative_path: str
    kind: str


@dataclass(slots=True)
class IteraSpecWorkspace:
    name: str
    relative_path: str
    documents: list[IteraSpecDocument]


@dataclass(slots=True)
class DeveloperProfile:
    filename: str
    relative_path: str
    display_name: str
    role: str
    specialty: str
    seniority: str
    primary_stacks: list[str]
    active: str


@dataclass(slots=True)
class IteraSpecDocumentContent:
    workspace_name: str
    document: IteraSpecDocument
    content: str
    size_bytes: int


@dataclass(slots=True)
class BacklogTask:
    identifier: str
    title: str
    requirement_id: str
    assignees: list[str]
    bullets: list[str]
    detail_lines: list[str]


@dataclass(slots=True)
class BacklogSection:
    key: str
    label: str
    tasks: list[BacklogTask]


@dataclass(slots=True)
class BoardItem:
    identifier: str
    note: str


@dataclass(slots=True)
class BoardSection:
    key: str
    label: str
    items: list[BoardItem]


@dataclass(slots=True)
class CurrentTaskView:
    title: str
    identifier: str
    requirement: str
    assignees: list[str]
    objective: str
    acceptance: list[str]
    notes: list[str]
    timeline: list[str]


class DocumentNotFoundError(Exception):
    pass


class InvalidDocumentRequestError(Exception):
    pass


def create_app() -> FastAPI:
    app = FastAPI(title="IteraSpec GUI Viewer")
    iteraspec_root = resolve_iteraspec_root()
    project_title = infer_project_title(iteraspec_root)

    @app.get("/styles.css")
    async def stylesheet() -> Response:
        return Response(content=STYLESHEET, media_type="text/css")

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request) -> str:
        workspaces = discover_workspaces(iteraspec_root)
        developers = discover_developers(iteraspec_root)
        theme_switcher = render_theme_switcher()
        current_section = request.query_params.get("section", "dashboard")
        selected_workspace = request.query_params.get("workspace", "")
        return _render_home_page(
            project_title,
            workspaces,
            developers,
            iteraspec_root,
            theme_switcher,
            current_section,
            selected_workspace,
        )

    @app.get("/api/workspaces")
    async def workspaces() -> dict[str, object]:
        discovered = discover_workspaces(iteraspec_root)
        return {
            "workspace_count": len(discovered),
            "workspaces": [
                {
                    "name": workspace.name,
                    "relative_path": workspace.relative_path,
                    "documents": [
                        {
                            "name": document.name,
                            "relative_path": document.relative_path,
                            "kind": document.kind,
                        }
                        for document in workspace.documents
                    ],
                }
                for workspace in discovered
            ],
        }

    @app.get("/api/developers")
    async def developers() -> dict[str, object]:
        roster = discover_developers(iteraspec_root)
        return {
            "developer_count": len(roster),
            "developers": [
                {
                    "filename": developer.filename,
                    "relative_path": developer.relative_path,
                    "display_name": developer.display_name,
                    "role": developer.role,
                    "specialty": developer.specialty,
                    "seniority": developer.seniority,
                    "primary_stacks": developer.primary_stacks,
                    "active": developer.active,
                }
                for developer in roster
            ],
        }

    @app.get("/api/workspaces/{workspace_name}/documents/{document_name}")
    async def workspace_document(workspace_name: str, document_name: str) -> dict[str, object]:
        try:
            loaded = read_workspace_document(workspace_name, document_name, iteraspec_root)
        except InvalidDocumentRequestError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except DocumentNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return {
            "workspace_name": loaded.workspace_name,
            "document": {
                "name": loaded.document.name,
                "relative_path": loaded.document.relative_path,
                "kind": loaded.document.kind,
            },
            "content": loaded.content,
            "size_bytes": loaded.size_bytes,
        }

    @app.get("/workspaces/{workspace_name}/documents/{document_name}", response_class=HTMLResponse)
    async def workspace_document_page(workspace_name: str, document_name: str) -> str:
        workspaces = discover_workspaces(iteraspec_root)
        try:
            loaded = read_workspace_document(workspace_name, document_name, iteraspec_root)
        except InvalidDocumentRequestError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except DocumentNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        return _render_document_page(
            workspaces,
            loaded.workspace_name,
            loaded.document.name,
            loaded.content,
            iteraspec_root,
        )

    @app.get("/workspaces/{workspace_name}/tasks/{task_identifier}", response_class=HTMLResponse)
    async def workspace_task_page(workspace_name: str, task_identifier: str) -> str:
        workspaces = discover_workspaces(iteraspec_root)
        identifier = normalize_task_identifier(task_identifier) or task_identifier.strip().upper()
        tasks_by_id = read_task_catalog(workspace_name, iteraspec_root)
        task = tasks_by_id.get(identifier)
        if task is None:
            raise HTTPException(status_code=404, detail=f"No se encontró la tarea {identifier}.")

        board_item, board_label = find_board_item(identifier, workspace_name, iteraspec_root)
        return _render_task_page(
            workspaces,
            workspace_name,
            task,
            board_item,
            board_label,
            tasks_by_id,
        )

    @app.get("/workspaces/{workspace_name}/requirements/{requirement_identifier}", response_class=HTMLResponse)
    async def workspace_requirement_page(workspace_name: str, requirement_identifier: str) -> str:
        workspaces = discover_workspaces(iteraspec_root)
        normalized = normalize_requirement_identifier(requirement_identifier)
        if not normalized:
            raise HTTPException(status_code=404, detail=f"Requerimiento no válido: {requirement_identifier}.")

        try:
            loaded = read_workspace_document(workspace_name, "specs.md", iteraspec_root)
        except InvalidDocumentRequestError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except DocumentNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        section_title, section_content = extract_requirement_spec_section(loaded.content, normalized)
        if not section_content:
            raise HTTPException(status_code=404, detail=f"No se encontró contexto para {normalized} en specs.md.")

        tasks_by_id = read_task_catalog(workspace_name, iteraspec_root)
        related_tasks = [task for task in tasks_by_id.values() if task.requirement_id == normalized]
        return _render_requirement_page(
            workspaces,
            workspace_name,
            normalized,
            section_title,
            section_content,
            related_tasks,
        )

    @app.get("/developers", response_class=HTMLResponse)
    async def developers_page() -> str:
        workspaces = discover_workspaces(iteraspec_root)
        developers = discover_developers(iteraspec_root)
        return _render_developer_index_page(workspaces, developers)

    @app.get("/developers/{profile_name}", response_class=HTMLResponse)
    async def developer_profile_page(profile_name: str) -> str:
        workspaces = discover_workspaces(iteraspec_root)
        developer, content = read_developer_profile(profile_name, iteraspec_root)
        return _render_developer_page(workspaces, developer, content)

    return app


def main() -> None:
    port = int(os.environ.get("PORT", "8001"))
    uvicorn.run(create_app(), host="127.0.0.1", port=port)


def resolve_iteraspec_root() -> Path:
    configured = os.environ.get("ITERASPEC_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    script_dir = Path(__file__).resolve().parent
    embedded_root = script_dir.parent
    if embedded_root.name == ".iteraspec":
        return embedded_root
    return script_dir.parent.joinpath(".iteraspec")


def infer_project_title(iteraspec_root: Path) -> str:
    project_root = iteraspec_root.parent if iteraspec_root.name == ".iteraspec" else iteraspec_root
    name = project_root.name.strip()
    if not name:
        return "Proyecto"
    return re.sub(r"[-_]+", " ", name).strip().title()


def discover_workspaces(base_dir: Path | None = None) -> list[IteraSpecWorkspace]:
    root = (base_dir or Path(".iteraspec")).resolve()
    if not root.exists() or not root.is_dir():
        return []

    workspaces: list[IteraSpecWorkspace] = []
    global_workspace = _discover_global_workspace(root)
    if global_workspace is not None:
        workspaces.append(global_workspace)
    workspaces_root = _resolve_workspaces_dir(root)
    for candidate in sorted(workspaces_root.iterdir(), key=lambda path: path.name):
        if not candidate.is_dir():
            continue
        if workspaces_root == root and candidate.name in {
            DEVELOPERS_DIRNAME,
            WORKSPACES_DIRNAME,
            "gui",
            "legacy-backup",
        }:
            continue
        workspaces.append(
            IteraSpecWorkspace(
                name=candidate.name,
                relative_path=candidate.relative_to(root.parent).as_posix(),
                documents=_discover_workspace_documents(candidate, root),
            )
        )
    return workspaces


def discover_developers(base_dir: Path | None = None) -> list[DeveloperProfile]:
    root = (base_dir or Path(".iteraspec")).resolve()
    developers_dir = _resolve_developers_dir(root)
    if not developers_dir.exists() or not developers_dir.is_dir():
        return []

    profiles: list[DeveloperProfile] = []
    for markdown_file in sorted(developers_dir.glob("*.md"), key=lambda path: path.name):
        try:
            content = markdown_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        metadata = parse_status_key_values(content)
        metadata_map = {key: value for key, value in metadata}
        profiles.append(
            DeveloperProfile(
                filename=markdown_file.name,
                relative_path=markdown_file.relative_to(root.parent).as_posix(),
                display_name=first_heading(content) or markdown_file.stem.replace("-", " ").title(),
                role=metadata_map.get("Role", "Developer"),
                specialty=metadata_map.get("Specialty", metadata_map.get("Specialties", "No especificada")),
                seniority=metadata_map.get("Seniority", "No indicada"),
                primary_stacks=_split_profile_list_value(metadata_map.get("Primary Stacks", "")),
                active=metadata_map.get("Active", "Unknown"),
            )
        )
    return profiles


def _discover_global_workspace(root_dir: Path) -> IteraSpecWorkspace | None:
    workspaces_dir = _resolve_workspaces_dir(root_dir)
    status_path = workspaces_dir / "status.md"
    if not status_path.exists() or not status_path.is_file():
        status_path = root_dir / "status.md"
    if not status_path.exists() or not status_path.is_file():
        return None

    return IteraSpecWorkspace(
        name=GLOBAL_WORKSPACE_NAME,
        relative_path=status_path.parent.relative_to(root_dir.parent).as_posix(),
        documents=[
            IteraSpecDocument(
                name="status.md",
                relative_path=status_path.relative_to(root_dir.parent).as_posix(),
                kind="status",
            )
        ],
    )


def _discover_workspace_documents(workspace_dir: Path, root_dir: Path) -> list[IteraSpecDocument]:
    documents: list[IteraSpecDocument] = []
    order_index = {name: index for index, name in enumerate(WORKSPACE_DOCUMENT_ORDER)}
    for markdown_file in sorted(
        workspace_dir.glob("*.md"),
        key=lambda path: (order_index.get(path.name, len(WORKSPACE_DOCUMENT_ORDER)), path.name),
    ):
        documents.append(
            IteraSpecDocument(
                name=markdown_file.name,
                relative_path=markdown_file.relative_to(root_dir.parent).as_posix(),
                kind=_document_kind(markdown_file.name),
            )
        )
    return documents


def _document_kind(filename: str) -> str:
    if filename in KNOWN_DOCUMENTS:
        return filename.removesuffix(".md")
    return "markdown"


def read_workspace_document(
    workspace_name: str,
    document_name: str,
    base_dir: Path | None = None,
) -> IteraSpecDocumentContent:
    _validate_name(workspace_name, "workspace")
    _validate_name(document_name, "document")

    root = (base_dir or Path(".iteraspec")).resolve()
    workspaces = discover_workspaces(root)
    workspace = next((item for item in workspaces if item.name == workspace_name), None)
    if workspace is None:
        raise DocumentNotFoundError(f"No existe el workspace '{workspace_name}'.")

    document = next((item for item in workspace.documents if item.name == document_name), None)
    if document is None:
        raise DocumentNotFoundError(
            f"No existe el documento '{document_name}' dentro de '{workspace_name}'."
        )

    document_path = (root.parent / document.relative_path).resolve()
    _ensure_within_root(document_path, root)

    try:
        content = document_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise DocumentNotFoundError(
            f"El documento '{document_name}' no está disponible actualmente."
        ) from exc

    return IteraSpecDocumentContent(
        workspace_name=workspace_name,
        document=document,
        content=content,
        size_bytes=len(content.encode("utf-8")),
    )


def read_developer_profile(
    profile_name: str,
    base_dir: Path | None = None,
) -> tuple[DeveloperProfile, str]:
    _validate_name(profile_name, "developer profile")

    root = (base_dir or Path(".iteraspec")).resolve()
    developers_dir = _resolve_developers_dir(root)
    developers = discover_developers(root)
    developer = next((item for item in developers if item.filename == profile_name), None)
    if developer is None:
        raise HTTPException(status_code=404, detail=f"No existe el developer profile '{profile_name}'.")

    profile_path = (developers_dir / profile_name).resolve()
    _ensure_within_directory(profile_path, developers_dir, "La ruta solicitada queda fuera del directorio de developers.")
    try:
        content = profile_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"El developer profile '{profile_name}' no está disponible actualmente.") from exc

    return developer, content


def _validate_name(value: str, label: str) -> None:
    if not value or "/" in value or "\\" in value or value in {".", ".."}:
        raise InvalidDocumentRequestError(f"El nombre de {label} solicitado no es válido.")


def _ensure_within_root(candidate: Path, root: Path) -> None:
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise InvalidDocumentRequestError(
            "La ruta solicitada queda fuera de .iteraspec/."
        ) from exc


def _ensure_within_directory(candidate: Path, directory: Path, message: str) -> None:
    try:
        candidate.relative_to(directory.resolve())
    except ValueError as exc:
        raise InvalidDocumentRequestError(message) from exc


def _resolve_developers_dir(root: Path) -> Path:
    embedded_dir = root / DEVELOPERS_DIRNAME
    if embedded_dir.exists() and embedded_dir.is_dir():
        return embedded_dir
    repo_dir = root.parent / DEVELOPERS_DIRNAME
    if repo_dir.exists() and repo_dir.is_dir():
        return repo_dir
    return embedded_dir


def _resolve_workspaces_dir(root: Path) -> Path:
    embedded_dir = root / WORKSPACES_DIRNAME
    if embedded_dir.exists() and embedded_dir.is_dir():
        return embedded_dir
    return root


def _split_profile_list_value(raw_value: str) -> list[str]:
    return [item.strip() for item in raw_value.split(",") if item.strip() and item.strip().lower() != "none"]


def render_theme_switcher() -> str:
    return (
        '<div class="theme-switcher" role="group" aria-label="Selector de tema">'
        '<button class="theme-option" type="button" data-theme-option="light" aria-pressed="false">Light</button>'
        '<button class="theme-option" type="button" data-theme-option="dark" aria-pressed="false">Dark</button>'
        "</div>"
    )


def render_markdown(markdown_text: str, workspace_name: str = "") -> str:
    lines = markdown_text.splitlines()
    parts: list[str] = []
    paragraph: list[str] = []
    list_items: list[tuple[int, str]] = []
    code_block: list[str] = []
    in_code_block = False
    index = 0

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(segment.strip() for segment in paragraph if segment.strip())
            if text:
                parts.append(f"<p>{_render_inline(text, workspace_name)}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            parts.append(_render_markdown_list(list_items, workspace_name))
            list_items.clear()

    def flush_code_block() -> None:
        if code_block:
            code = "\n".join(code_block)
            parts.append(f"<pre><code>{html.escape(code)}</code></pre>")
            code_block.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.rstrip()

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code_block:
                flush_code_block()
                in_code_block = False
            else:
                in_code_block = True
            index += 1
            continue

        if in_code_block:
            code_block.append(line)
            index += 1
            continue

        if not stripped.strip():
            flush_paragraph()
            flush_list()
            index += 1
            continue

        if stripped.startswith("#"):
            flush_paragraph()
            flush_list()
            level = min(len(stripped) - len(stripped.lstrip("#")), 6)
            content = stripped[level:].strip()
            parts.append(f"<h{level}>{_render_inline(content, workspace_name)}</h{level}>")
            index += 1
            continue

        list_match = re.match(r"^([ \t]*)[-*]\s+(.+)$", line)
        if list_match is not None:
            flush_paragraph()
            indent = _list_indent_width(list_match.group(1))
            item = list_match.group(2).strip()
            list_items.append((indent, item))
            index += 1
            continue

        if _looks_like_markdown_table_header(lines, index):
            flush_paragraph()
            flush_list()
            table_html, next_index = _render_markdown_table(lines, index, workspace_name)
            parts.append(table_html)
            index = next_index
            continue

        paragraph.append(stripped)
        index += 1

    if in_code_block:
        flush_code_block()
    flush_paragraph()
    flush_list()

    return "\n".join(parts) if parts else "<p class=\"muted\">Documento vacío.</p>"


def _render_markdown_list(items: list[tuple[int, str]], workspace_name: str = "") -> str:
    tree = _build_markdown_list_tree(items)
    return _render_markdown_list_nodes(tree, workspace_name)


def _build_markdown_list_tree(items: list[tuple[int, str]]) -> list[dict[str, object]]:
    root: list[dict[str, object]] = []
    stack: list[tuple[int, list[dict[str, object]]]] = [(-1, root)]

    for indent, text in items:
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        node: dict[str, object] = {"text": text, "children": []}
        stack[-1][1].append(node)
        stack.append((indent, node["children"]))  # type: ignore[arg-type]

    return root


def _render_markdown_list_nodes(nodes: list[dict[str, object]], workspace_name: str = "") -> str:
    items_markup: list[str] = []
    for node in nodes:
        text = _render_inline(str(node["text"]), workspace_name)
        children = node["children"]
        child_markup = ""
        if isinstance(children, list) and children:
            child_markup = _render_markdown_list_nodes(children, workspace_name)
        items_markup.append(f"<li>{text}{child_markup}</li>")
    return f"<ul>{''.join(items_markup)}</ul>"


def _list_indent_width(raw_indent: str) -> int:
    expanded = raw_indent.expandtabs(4)
    return len(expanded)


def _render_inline(text: str, workspace_name: str = "") -> str:
    tokens: list[tuple[str, str]] = []
    protected = _extract_inline_tokens(text, tokens)
    escaped = html.escape(protected)
    escaped = _replace_markdown_links(escaped)
    escaped = _replace_emphasis(escaped)
    escaped = _replace_requirement_mentions(escaped, workspace_name)
    return _restore_inline_tokens(escaped, tokens)


def _looks_like_markdown_table_header(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    header = lines[index].strip()
    divider = lines[index + 1].strip()
    if "|" not in header or "|" not in divider:
        return False
    header_cells = _split_markdown_table_row(header)
    divider_cells = _split_markdown_table_row(divider)
    if len(header_cells) < 2 or len(header_cells) != len(divider_cells):
        return False
    return all(_is_markdown_table_divider(cell) for cell in divider_cells)


def _render_markdown_table(lines: list[str], start_index: int, workspace_name: str = "") -> tuple[str, int]:
    header_cells = _split_markdown_table_row(lines[start_index].strip())
    alignments = [
        _table_alignment_for_divider(cell)
        for cell in _split_markdown_table_row(lines[start_index + 1].strip())
    ]
    body_rows: list[list[str]] = []
    index = start_index + 2

    while index < len(lines):
        candidate = lines[index].strip()
        if not candidate or "|" not in candidate:
            break
        row_cells = _split_markdown_table_row(candidate)
        if len(row_cells) != len(header_cells):
            break
        body_rows.append(row_cells)
        index += 1

    thead = "".join(
        _render_table_cell("th", cell, alignments[position], workspace_name)
        for position, cell in enumerate(header_cells)
    )
    tbody = "".join(
        "<tr>"
        + "".join(
            _render_table_cell("td", cell, alignments[position], workspace_name)
            for position, cell in enumerate(row)
        )
        + "</tr>"
        for row in body_rows
    )
    table_parts = [
        "<div class=\"table-scroll\">",
        "<table class=\"markdown-table\">",
        f"<thead><tr>{thead}</tr></thead>",
    ]
    if tbody:
        table_parts.append(f"<tbody>{tbody}</tbody>")
    table_parts.extend(["</table>", "</div>"])
    return "".join(table_parts), index


def _render_table_cell(tag: str, text: str, alignment: str | None, workspace_name: str = "") -> str:
    style_attr = f' style="text-align: {alignment};"' if alignment else ""
    return f"<{tag}{style_attr}>{_render_inline(text.strip(), workspace_name)}</{tag}>"


def _split_markdown_table_row(row: str) -> list[str]:
    trimmed = row.strip()
    if trimmed.startswith("|"):
        trimmed = trimmed[1:]
    if trimmed.endswith("|"):
        trimmed = trimmed[:-1]
    return [cell.strip() for cell in trimmed.split("|")]


def _is_markdown_table_divider(cell: str) -> bool:
    normalized = cell.strip()
    if not normalized:
        return False
    core = normalized.replace(":", "").replace("-", "")
    return not core and normalized.count("-") >= 3


def _table_alignment_for_divider(cell: str) -> str | None:
    normalized = cell.strip()
    if normalized.startswith(":") and normalized.endswith(":"):
        return "center"
    if normalized.endswith(":"):
        return "right"
    if normalized.startswith(":"):
        return "left"
    return None


def _extract_inline_tokens(text: str, tokens: list[tuple[str, str]]) -> str:
    parts: list[str] = []
    cursor = 0

    for match in re.finditer(r"`([^`]+)`", text):
        parts.append(text[cursor:match.start()])
        placeholder = f"@@CODETOKEN{len(tokens)}@@"
        tokens.append((placeholder, f"<code>{html.escape(match.group(1))}</code>"))
        parts.append(placeholder)
        cursor = match.end()

    parts.append(text[cursor:])
    return "".join(parts)


def _restore_inline_tokens(text: str, tokens: list[tuple[str, str]]) -> str:
    restored = text
    for placeholder, replacement in tokens:
        restored = restored.replace(html.escape(placeholder), replacement)
    return restored


def _replace_markdown_links(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        label = match.group(1)
        url = html.escape(html.unescape(match.group(2)), quote=True)
        return f'<a href="{url}">{label}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", replace, text)


def _replace_emphasis(text: str) -> str:
    rendered = re.sub(r"(?<!\*)\*\*([^*\n]+)\*\*(?!\*)", r"<strong>\1</strong>", text)
    rendered = re.sub(r"(?<!_)__([^_\n]+)__(?!_)", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", rendered)
    rendered = re.sub(r"(?<!_)_([^_\n]+)_(?!_)", r"<em>\1</em>", rendered)
    return rendered


def _replace_requirement_mentions(text: str, workspace_name: str) -> str:
    if not workspace_name or workspace_name == GLOBAL_WORKSPACE_NAME:
        return text

    def replace_segment(segment: str) -> str:
        return re.sub(
            r"\b((?:RF|RNF)\d{2})\b",
            lambda match: f'<a href="{requirement_detail_href(workspace_name, match.group(1))}">{match.group(1)}</a>',
            segment,
        )

    parts = re.split(r"(<[^>]+>)", text)
    return "".join(part if part.startswith("<") and part.endswith(">") else replace_segment(part) for part in parts)


def render_specialized_document(
    document_name: str,
    content: str,
    workspace_name: str,
    iteraspec_root: Path,
) -> str | None:
    if document_name == "status.md":
        return render_status_view(content)
    if document_name == "board.md":
        return render_board_view(content, workspace_name, iteraspec_root)
    if document_name == "backlog.md":
        return render_backlog_view(content, workspace_name)
    if document_name == "current_task.md":
        return render_current_task_view(content, workspace_name)
    return None


def render_status_view(content: str) -> str:
    key_values = parse_status_key_values(content)
    if not key_values:
        return (
            "<div class=\"specialized-view status-view\">"
            "<section class=\"focus-card\">"
            "<p class=\"section-kicker\">Estado Global</p>"
            "<h2>status.md</h2>"
            "<p>No se detectó una estructura resumible. Se muestra como Markdown estándar.</p>"
            "</section>"
            f"{render_markdown(content)}"
            "</div>"
        )

    status_map = {label: value for label, value in key_values}
    active_feature = status_map.get("Active Feature", "(none)")
    current_phase = status_map.get("Current Phase", "(none)")
    phase_state = status_map.get("Phase State", "Unknown")
    last_approved_phase = status_map.get("Last Approved Phase", "(none)")
    active_task = status_map.get("Active Task", "(none)")
    active_requirement = status_map.get("Active Requirement", "(none)")
    next_expected_action = status_map.get("Next Expected Action", "Sin proximo paso detectado.")

    topline_cards = "".join(
        (
            "<article class=\"status-summary-card compact\">"
            f"<span>{html.escape(label)}</span>"
            f"<p class=\"status-value\">{render_status_value(label, value, active_feature)}</p>"
            "</article>"
        )
        for label, value in [
            ("Active Feature", active_feature),
            ("Last Approved Phase", last_approved_phase),
            ("Active Task", active_task),
            ("Active Requirement", active_requirement),
        ]
    )
    extra_pairs = [
        (label, value)
        for label, value in key_values
        if label
        not in {
            "Active Feature",
            "Current Phase",
            "Phase State",
            "Last Approved Phase",
            "Active Task",
            "Active Requirement",
            "Next Expected Action",
        }
    ]
    extra_cards = "".join(
        (
            "<div class=\"status-meta-card\">"
            f"<dt>{html.escape(label)}</dt>"
            f"<dd>{html.escape(value)}</dd>"
            "</div>"
        )
        for label, value in extra_pairs
    )
    return (
        "<div class=\"specialized-view status-view\">"
        "<section class=\"status-hero\">"
        "<div class=\"status-hero-copy\">"
        "<p class=\"section-kicker\">Estado Global</p>"
        "<p class=\"status-eyebrow\">Resumen de reanudacion</p>"
        "<p>Checkpoint persistido en <code>.iteraspec/workspaces/status.md</code>.</p>"
        "</div>"
        "<aside class=\"status-phase-card\">"
        "<span>Fase actual</span>"
        f"<p class=\"status-phase-value\">{html.escape(current_phase)}</p>"
        f"{render_status_chip(phase_state)}"
        "</aside>"
        "</section>"
        f"<section class=\"status-topline-grid\">{topline_cards}</section>"
        "<section class=\"status-action-card\">"
        "<p class=\"section-kicker\">Next Expected Action</p>"
        f"<p class=\"status-action-value\">{html.escape(next_expected_action)}</p>"
        "</section>"
        f"{f'<section class=\"status-meta-grid\">{extra_cards}</section>' if extra_cards else ''}"
        "</div>"
    )


def render_backlog_view(content: str, workspace_name: str) -> str:
    tasks = parse_task_catalog(content)
    summary = (
        "<article class=\"status-summary-card\">"
        "<span>Catalogo</span>"
        f"<strong>{len(tasks)}</strong>"
        "<span>tareas definidas</span>"
        "</article>"
    )
    board = (
        "<section class=\"backlog-column\">"
        "<header><span class=\"status-chip done\">Task Catalog</span></header>"
        f"{render_backlog_tasks(tasks, 'catalog', workspace_name)}"
        "</section>"
    )
    return (
        "<div class=\"specialized-view\">"
        "<section class=\"status-summary-grid\">"
        f"{summary}"
        "</section>"
        "<section class=\"backlog-board\">"
        f"{board}"
        "</section>"
        "</div>"
    )


def render_board_view(content: str, workspace_name: str, iteraspec_root: Path) -> str:
    sections = parse_board(content)
    tasks_by_id = read_task_catalog(workspace_name, iteraspec_root)
    if not sections:
        legacy = parse_legacy_backlog_board(content)
        if legacy:
            sections = legacy
    sections = order_board_sections(sections)
    summary = "".join(
        (
            "<article class=\"status-summary-card\">"
            f"<span class=\"status-chip {section.key}\">{section.label}</span>"
            f"<strong>{len(section.items)}</strong>"
            "<span>tareas</span>"
            "</article>"
        )
        for section in sections
    )
    board = "".join(
        (
            "<section class=\"backlog-column\">"
            f"<header><span class=\"status-chip {section.key}\">{section.label}</span></header>"
            f"{render_board_items(section.items, section.key, workspace_name, tasks_by_id)}"
            "</section>"
        )
        for section in sections
    )
    return (
        "<div class=\"specialized-view\">"
        "<section class=\"status-summary-grid\">"
        f"{summary}"
        "</section>"
        "<section class=\"backlog-board\">"
        f"{board}"
        "</section>"
        "</div>"
    )


def render_current_task_view(content: str, workspace_name: str) -> str:
    task = parse_current_task(content)
    acceptance = "".join(f"<li>{_render_inline(item, workspace_name)}</li>" for item in task.acceptance) or "<li>Sin criterios detectados.</li>"
    notes = "".join(f"<li>{_render_inline(item, workspace_name)}</li>" for item in task.notes) or "<li>Sin notas detectadas.</li>"
    timeline = "".join(f"<li>{_render_inline(item, workspace_name)}</li>" for item in task.timeline) or "<li>Sin marcas temporales detectadas.</li>"
    assignees = render_assignee_chips(task.assignees)
    objective = _render_inline(task.objective or "Objetivo no detectado.", workspace_name)
    identifier = html.escape(task.identifier or "Sin identificador")
    requirement = html.escape(task.requirement or "Sin requerimiento")
    title = html.escape(task.title or "Tarea activa")
    identifier_markup = (
        f'<a class="task-pill" href="{task_detail_href(workspace_name, task.identifier)}">{identifier}</a>'
        if task.identifier and workspace_name and workspace_name != GLOBAL_WORKSPACE_NAME
        else f'<div class="task-pill">{identifier}</div>'
    )
    requirement_markup = (
        f'<a class="task-pill" href="{requirement_detail_href(workspace_name, task.requirement)}">{requirement}</a>'
        if task.requirement and workspace_name and workspace_name != GLOBAL_WORKSPACE_NAME
        else f'<div class="task-pill">{requirement}</div>'
    )
    return (
        "<div class=\"specialized-view current-task-view\">"
        "<section class=\"focus-card\">"
        "<p class=\"section-kicker\">Tarea Activa</p>"
        f"<h2>{title}</h2>"
        "<div class=\"task-pill-group\">"
        f"{identifier_markup}"
        f"{requirement_markup}"
        "</div>"
        f"<p class=\"focus-objective\">{objective}</p>"
        "</section>"
        "<section class=\"task-grid\">"
        "<article class=\"task-panel\">"
        "<h3>Trazabilidad temporal</h3>"
        f"<ul>{timeline}</ul>"
        "</article>"
        "<article class=\"task-panel\">"
        "<h3>Desarrolladores asignados</h3>"
        f"{assignees}"
        "</article>"
        "<article class=\"task-panel\">"
        "<h3>Criterios de aceptación</h3>"
        f"<ul>{acceptance}</ul>"
        "</article>"
        "<article class=\"task-panel\">"
        "<h3>Notas de implementación</h3>"
        f"<ul>{notes}</ul>"
        "</article>"
        "</section>"
        "</div>"
    )


def parse_task_catalog(content: str) -> list[BacklogTask]:
    tasks: list[BacklogTask] = []
    current_task: BacklogTask | None = None

    for raw_line in content.splitlines():
        line = raw_line.rstrip()

        if line.startswith("### "):
            identifier, _ = split_task_title(line[4:].strip())
            current_task = BacklogTask(
                identifier=identifier,
                title=line[4:].strip(),
                requirement_id="",
                assignees=[],
                bullets=[],
                detail_lines=[],
            )
            tasks.append(current_task)
            continue

        if current_task is None:
            continue

        if line.startswith("## "):
            current_task = None
            continue

        stripped = line.strip()
        if not stripped:
            continue

        current_task.detail_lines.append(stripped)
        if stripped.startswith("- "):
            current_task.bullets.append(stripped[2:].strip())

    for task in tasks:
        task.requirement_id = extract_requirement_id(task.detail_lines)
        task.assignees = extract_assignees(task.detail_lines)

    if tasks:
        return tasks

    return parse_task_catalog_table(content)


def parse_task_catalog_table(content: str) -> list[BacklogTask]:
    tasks: list[BacklogTask] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or line.count("|") < 6:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        if cells[0].lower() == "id" or set("".join(cells)) <= {":", "-", " "}:
            continue
        identifier = normalize_task_identifier(cells[0])
        if not identifier:
            continue
        title = cells[1] or identifier
        requirement_id = extract_requirement_id([cells[2]]) if len(cells) > 2 else ""
        detail_lines = []
        if requirement_id:
            detail_lines.append(f"- Requirement: {requirement_id}")
        if len(cells) > 3 and cells[3]:
            detail_lines.append(f"- Description: {cells[3]}")
        if len(cells) > 4 and cells[4]:
            detail_lines.append(f"- Acceptance Criteria: {cells[4]}")
        if len(cells) > 5 and cells[5]:
            detail_lines.append(f"- Dependencies: {cells[5]}")
        tasks.append(
            BacklogTask(
                identifier=identifier,
                title=f"{identifier} - {title}",
                requirement_id=requirement_id,
                assignees=[],
                bullets=[line[2:].strip() for line in detail_lines if line.startswith("- ")],
                detail_lines=detail_lines,
            )
        )
    return tasks


def parse_board(content: str) -> list[BoardSection]:
    sections: list[BoardSection] = []
    current_key = None
    current_label = None
    current_items: list[BoardItem] = []

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        section = _match_backlog_section(line)
        if section is not None:
            if current_key is not None:
                sections.append(BoardSection(current_key, current_label or current_key, current_items))
            current_key, current_label = section
            current_items = []
            continue

        if current_key is None:
            continue

        item = _parse_board_item(line)
        if item is not None:
            current_items.append(item)

    if current_key is not None:
        sections.append(BoardSection(current_key, current_label or current_key, current_items))

    return sections


def parse_legacy_backlog_board(content: str) -> list[BoardSection]:
    sections: list[BoardSection] = []
    current_key = None
    current_label = None
    current_items: list[BoardItem] = []

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        section = _match_backlog_section(line)
        if section is not None:
            if current_key is not None:
                sections.append(BoardSection(current_key, current_label or current_key, current_items))
            current_key, current_label = section
            current_items = []
            continue

        if current_key is None:
            continue

        if line.startswith("### "):
            identifier, _ = split_task_title(line[4:].strip())
            if identifier:
                current_items.append(BoardItem(identifier=identifier, note=""))

    if current_key is not None:
        sections.append(BoardSection(current_key, current_label or current_key, current_items))

    return sections


def _match_backlog_section(line: str) -> tuple[str, str] | None:
    for pattern, section in BACKLOG_SECTION_PATTERNS:
        if pattern.match(line):
            return section
    return None


def _parse_board_item(line: str) -> BoardItem | None:
    stripped = line.strip()
    if not stripped.startswith("- "):
        return None
    body = stripped[2:].strip()
    match = re.match(r"^`?(T\d{2})`?(?:\s*[:\-]\s*(.*))?$", body)
    if not match:
        return None
    return BoardItem(identifier=match.group(1), note=(match.group(2) or "").strip())


def order_board_sections(sections: list[BoardSection]) -> list[BoardSection]:
    by_key = {section.key: section for section in sections}
    ordered: list[BoardSection] = []
    for key, label in BACKLOG_SECTION_ORDER:
        ordered.append(by_key.get(key, BoardSection(key=key, label=label, items=[])))
    return ordered


def parse_current_task(content: str) -> CurrentTaskView:
    title = first_heading(content) or "Tarea activa"
    identifier = first_value_after_heading(content, "Identificador")
    requirement = first_value_after_heading(content, "Requerimiento") or first_value_after_heading(content, "Requirement")
    assignees = collect_section_bullets(content, "Asignados") or collect_section_bullets(content, "Assignees")
    objective = (
        collect_section_paragraph(content, "Objetivo")
        or collect_section_paragraph(content, "Descripcion")
        or collect_section_paragraph(content, "Descripción")
        or collect_section_paragraph(content, "Nombre")
    )
    acceptance = collect_section_bullets(content, "Criterios de aceptacion") or collect_section_bullets(
        content, "Criterios de aceptación"
    )
    notes = collect_section_bullets(content, "Notas de implementacion") or collect_section_bullets(
        content, "Notas de implementación"
    )
    timeline = collect_section_bullets(content, "Trazabilidad temporal")
    return CurrentTaskView(
        title=title,
        identifier=identifier,
        requirement=requirement,
        assignees=assignees,
        objective=objective,
        acceptance=acceptance,
        notes=notes,
        timeline=timeline,
    )


def parse_status_key_values(content: str) -> list[tuple[str, str]]:
    parsed: list[tuple[str, str]] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            line = line[2:].strip()
        match = re.match(r"^([^:]+):\s*(.+)$", line)
        if not match:
            continue
        key = match.group(1).strip().strip("`")
        value = match.group(2).strip().strip("`")
        if key and value:
            parsed.append((key, value))
    return parsed


def render_status_chip(label: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", label.lower()).strip()
    if any(token in normalized for token in {"done", "approved", "complete", "completed"}):
        tone = "done"
    elif any(token in normalized for token in {"progress", "running", "active"}):
        tone = "inprogress"
    elif any(token in normalized for token in {"blocked", "waiting", "awaiting", "hold"}):
        tone = "blocked"
    else:
        tone = "todo"
    return f"<span class=\"status-chip {tone}\">{html.escape(label)}</span>"


def render_status_value(label: str, value: str, active_feature: str) -> str:
    if label == "Active Requirement":
        workspace_name = active_feature.strip()
        requirement_id = normalize_requirement_identifier(value)
        if workspace_name and workspace_name != "(none)" and requirement_id:
            return (
                f'<a class="doc-link" href="{requirement_detail_href(workspace_name, requirement_id)}">'
                f"{html.escape(requirement_id)}</a>"
            )
    return html.escape(value)


def split_task_title(title: str) -> tuple[str, str]:
    cleaned = title.strip()
    match = re.match(r"^`?(T\d{2})`?\s*[:\-]?\s*(.*)$", cleaned)
    if match:
        identifier = match.group(1).strip()
        summary = match.group(2).strip() or identifier
        return identifier, summary
    return "", cleaned


def normalize_task_identifier(value: str) -> str:
    match = re.search(r"\b(T\d{2})\b", value.strip(), re.IGNORECASE)
    return match.group(1).upper() if match else ""


def normalize_requirement_identifier(value: str) -> str:
    match = re.search(r"\b((?:RF|RNF)\d{2})\b", value.strip(), re.IGNORECASE)
    return match.group(1).upper() if match else ""


def extract_requirement_id(lines: list[str]) -> str:
    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("- "):
            line = line[2:].strip()
        match = re.match(r"^(Requirement|Requerimiento)\s*:\s*`?((?:RF|RNF)\d{2})`?\s*$", line, re.IGNORECASE)
        if match:
            return match.group(2).upper()
        fallback = re.search(r"\b((?:RF|RNF)\d{2})\b", line, re.IGNORECASE)
        if fallback:
            return fallback.group(1).upper()
    return ""


def extract_assignees(lines: list[str]) -> list[str]:
    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("- "):
            line = line[2:].strip()
        match = re.match(r"^(Assignees|Asignados)\s*:\s*(.+)$", line, re.IGNORECASE)
        if not match:
            continue
        return [name.strip() for name in match.group(2).split(",") if name.strip() and name.strip().lower() != "none"]
    return []


def read_task_catalog(workspace_name: str, iteraspec_root: Path) -> dict[str, BacklogTask]:
    if not workspace_name or workspace_name == GLOBAL_WORKSPACE_NAME:
        return {}
    try:
        loaded = read_workspace_document(workspace_name, "backlog.md", iteraspec_root)
    except (InvalidDocumentRequestError, DocumentNotFoundError):
        return {}
    catalog = parse_task_catalog(loaded.content)
    mapped: dict[str, BacklogTask] = {}
    for task in catalog:
        identifier, _ = split_task_title(task.title)
        if identifier:
            mapped[identifier] = task
    return mapped


def render_backlog_tasks(
    tasks: list[BacklogTask],
    section_key: str,
    workspace_name: str,
) -> str:
    if not tasks:
        return "<div class=\"empty-task-card\">Sin tareas en esta columna.</div>"
    rendered: list[str] = []
    for index, task in enumerate(tasks, start=1):
        identifier, summary = split_task_title(task.title)
        task_href = task_detail_href(workspace_name, identifier or task.identifier or f"{section_key}-{index}")
        assignee_markup = render_assignee_chips(task.assignees)
        code_markup = (
            f"<span class=\"task-code-chip\">{html.escape(identifier)}</span>"
            if identifier
            else ""
        )
        rendered.append(
            "<article class=\"task-card\">"
            f"<a class=\"task-card-button\" href=\"{task_href}\">"
            "<div class=\"task-card-title-row\">"
            "<span class=\"task-state-dot\"></span>"
            "<div class=\"task-card-copy\">"
            f"{code_markup}"
            f"<div class=\"task-card-title\">{html.escape(summary)}</div>"
            f"{assignee_markup}"
            "<p>Abrir tarea completa</p>"
            "</div>"
            "</div>"
            "</a>"
            "</article>"
        )
    return "".join(rendered)


def render_board_items(
    items: list[BoardItem],
    section_key: str,
    workspace_name: str,
    tasks_by_id: dict[str, BacklogTask],
) -> str:
    if not items:
        return "<div class=\"empty-task-card\">Sin tareas en esta columna.</div>"
    rendered: list[str] = []
    for index, item in enumerate(items, start=1):
        task = tasks_by_id.get(item.identifier)
        summary = split_task_title(task.title)[1] if task else item.identifier
        task_href = task_detail_href(workspace_name, item.identifier or f"{section_key}-{index}")
        assignee_markup = render_assignee_chips(task.assignees if task else [])
        note_markup = f"<p>{html.escape(item.note)}</p>" if item.note else "<p>Ver detalle</p>"
        rendered.append(
            "<article class=\"task-card\">"
            f"<a class=\"task-card-button\" href=\"{task_href}\">"
            "<div class=\"task-card-title-row\">"
            "<span class=\"task-state-dot\"></span>"
            "<div class=\"task-card-copy\">"
            f"<span class=\"task-code-chip\">{html.escape(item.identifier)}</span>"
            f"<div class=\"task-card-title\">{html.escape(summary)}</div>"
            f"{assignee_markup}"
            f"{note_markup}"
            "</div>"
            "</div>"
            "</a>"
            "</article>"
        )
    return "".join(rendered)


def render_task_detail(task: BacklogTask, workspace_name: str = "") -> str:
    if task.detail_lines:
        return render_markdown("\n".join(task.detail_lines), workspace_name)
    return "<p>Esta tarea no tiene detalle adicional en el backlog.</p>"


def render_assignee_chips(assignees: list[str]) -> str:
    if not assignees:
        return '<p class="muted">Sin desarrolladores asignados.</p>'
    chips = "".join(f'<span class="developer-chip">{html.escape(name)}</span>' for name in assignees)
    return f'<div class="developer-chip-group">{chips}</div>'


def task_detail_href(workspace_name: str, identifier: str) -> str:
    normalized = normalize_task_identifier(identifier) or identifier.strip().upper() or "task"
    return f"/workspaces/{workspace_name}/tasks/{normalized}"


def requirement_detail_href(workspace_name: str, requirement_id: str) -> str:
    normalized = normalize_requirement_identifier(requirement_id) or requirement_id.strip().upper() or "RF00"
    return f"/workspaces/{workspace_name}/requirements/{normalized}"


def developer_detail_href(profile_name: str) -> str:
    return f"/developers/{profile_name}"


def find_board_item(identifier: str, workspace_name: str, iteraspec_root: Path) -> tuple[BoardItem | None, str]:
    try:
        loaded = read_workspace_document(workspace_name, "board.md", iteraspec_root)
    except (InvalidDocumentRequestError, DocumentNotFoundError):
        return None, ""

    for section in order_board_sections(parse_board(loaded.content)):
        for item in section.items:
            if item.identifier == identifier:
                return item, section.label
    return None, ""


def render_task_bullets(bullets: list[str]) -> str:
    if not bullets:
        return "<p class=\"muted\">Sin detalle adicional.</p>"
    items = "".join(f"<li>{html.escape(item)}</li>" for item in bullets[:4])
    return f"<ul>{items}</ul>"


def extract_requirement_spec_section(content: str, requirement_id: str) -> tuple[str, str]:
    heading_match = re.search(rf"^(#+)\s+.*\b{re.escape(requirement_id)}\b.*$", content, re.MULTILINE)
    if heading_match:
        level = len(heading_match.group(1))
        lines = content[heading_match.start():].splitlines()
        collected: list[str] = []
        for idx, line in enumerate(lines):
            if idx > 0 and re.match(r"^#{1,%d}\s+" % level, line):
                break
            collected.append(line)
        return heading_match.group(0).lstrip("# ").strip(), "\n".join(collected).strip()

    lines = content.splitlines()
    matching_indexes = [index for index, line in enumerate(lines) if requirement_id in line]
    if not matching_indexes:
        return "", ""

    start = max(0, matching_indexes[0] - 2)
    while start > 0 and lines[start - 1].strip():
        start -= 1

    end = min(len(lines), matching_indexes[-1] + 3)
    while end < len(lines) and lines[end].strip():
        end += 1

    excerpt = "\n".join(lines[start:end]).strip()
    return f"Requerimiento {requirement_id}", excerpt


def split_requirement_title(section_title: str, requirement_id: str) -> str:
    cleaned = section_title.strip()
    match = re.match(rf"^(?:Requerimiento\s+)?{re.escape(requirement_id)}\s*[-:]\s*(.+)$", cleaned, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return cleaned or requirement_id


def first_heading(content: str) -> str | None:
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def first_value_after_heading(content: str, heading: str) -> str:
    section = section_body(content, heading)
    match = re.search(r"^- `?(.+?)`?$", section, re.MULTILINE)
    if match:
        return match.group(1).strip()
    match = re.search(r"^`?(.+?)`?$", section, re.MULTILINE)
    return match.group(1).strip() if match else ""


def collect_section_paragraph(content: str, heading: str) -> str:
    section = section_body(content, heading)
    for line in section.splitlines():
        if line.strip() and not line.startswith("- ") and not line.startswith("`"):
            return line.strip()
        if line.strip().startswith("`") and line.strip().endswith("`"):
            return line.strip().strip("`").strip()
    return ""


def collect_section_bullets(content: str, heading: str) -> list[str]:
    section = section_body(content, heading)
    return [line[2:].strip() for line in section.splitlines() if line.startswith("- ")]


def section_body(content: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?:\n##\s+|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        normalized_heading = _normalize_heading(heading)
        current_heading = None
        lines: list[str] = []
        collecting = False
        for raw_line in content.splitlines():
            line = raw_line.rstrip()
            if line.startswith("## "):
                heading_text = _normalize_heading(line[3:])
                if collecting:
                    break
                if heading_text == normalized_heading:
                    collecting = True
                current_heading = heading_text
                continue
            if collecting and current_heading == normalized_heading:
                lines.append(raw_line)
        if lines:
            return "\n".join(lines).strip()
    return match.group(1).strip() if match else ""


def _normalize_heading(value: str) -> str:
    normalized = value.strip().strip("`").lower()
    replacements = str.maketrans(
        {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ü": "u",
            "ñ": "n",
        }
    )
    return normalized.translate(replacements)


def _render_workspaces(workspaces: list[IteraSpecWorkspace]) -> str:
    if not workspaces:
        return (
            "<div class=\"empty-state\">"
            "<strong>No se detectaron workspaces IteraSpec.</strong>"
            "<p>La aplicación seguirá funcionando aunque <code>.iteraspec/workspaces/</code> esté vacío o incompleto.</p>"
            "</div>"
        )

    return "".join(
        (
            "<article class=\"workspace-card\">"
            f"<header><h2>{html.escape(_workspace_label(workspace.name))}</h2><p>{html.escape(workspace.relative_path)}</p></header>"
            f"<ul>{_render_documents(workspace.name, workspace.documents)}</ul>"
            "</article>"
        )
        for workspace in workspaces
    )


def _render_home_page(
    project_title: str,
    workspaces: list[IteraSpecWorkspace],
    developers: list[DeveloperProfile],
    iteraspec_root: Path,
    theme_switcher: str,
    current_section: str,
    selected_workspace_name: str,
) -> str:
    active_workspace = _resolve_active_workspace(workspaces, iteraspec_root)
    normalized_section = current_section if current_section in {
        "dashboard",
        "board",
        "current-task",
        "documents",
        "developers",
        "status",
    } else ("documents" if current_section == "workspaces" else "dashboard")
    focus_workspace = _resolve_workspace_for_section(workspaces, active_workspace, selected_workspace_name)
    section_title, section_description, section_markup = _render_home_section_content(
        normalized_section,
        workspaces,
        developers,
        iteraspec_root,
        focus_workspace,
    )
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(project_title)}</title>
    {THEME_BOOTSTRAP_SCRIPT}
    <link rel="stylesheet" href="/styles.css">
  </head>
  <body>
    {_render_app_shell(
        _render_primary_sidebar(project_title, theme_switcher, normalized_section, workspaces, developers, focus_workspace.name if focus_workspace else "", "", ""),
        f'<header class="home-hero"><h1>{html.escape(section_title)}</h1></header><section class="home-section">{section_markup}</section>'
    )}
    {THEME_BEHAVIOR_SCRIPT}
  </body>
</html>"""


def _render_primary_sidebar(
    project_title: str,
    theme_switcher: str,
    current_section: str,
    workspaces: list[IteraSpecWorkspace],
    developers: list[DeveloperProfile],
    current_workspace_name: str,
    current_document_name: str,
    current_developer_name: str,
) -> str:
    workspace_picker = _render_workspace_picker(current_section, workspaces, current_workspace_name, current_document_name)
    return (
        "<aside class=\"home-sidebar\">"
        "<div class=\"home-sidebar-header\">"
        "<div class=\"home-sidebar-topline\">"
        f"<h1 class=\"home-title\">{html.escape(project_title)}</h1>"
        '<label for="home-nav-toggle" class="home-nav-close" aria-label="Cerrar menu">×</label>'
        "</div>"
        f"<div class=\"toolbar-actions\">{theme_switcher}</div>"
        "</div>"
        f"{workspace_picker}"
        "<nav class=\"home-menu\" aria-label=\"Secciones principales\">"
        f"{_render_primary_menu(current_section, workspaces, developers, current_workspace_name, current_document_name, current_developer_name)}"
        "</nav>"
        "</aside>"
    )


def _render_app_shell(sidebar: str, content: str) -> str:
    return (
        '<main class="home-app-shell">'
        '<input id="home-nav-toggle" class="home-nav-toggle" type="checkbox">'
        '<label for="home-nav-toggle" class="home-nav-overlay" aria-label="Cerrar menu"></label>'
        f"{sidebar}"
        '<section class="home-content">'
        '<div class="home-mobile-bar">'
        '<label for="home-nav-toggle" class="home-nav-button" aria-label="Abrir menu">☰</label>'
        "</div>"
        f"{content}"
        "</section>"
        "</main>"
    )


def _render_workspace_picker(
    current_section: str,
    workspaces: list[IteraSpecWorkspace],
    current_workspace_name: str,
    current_document_name: str,
) -> str:
    available = [workspace for workspace in workspaces if workspace.name != GLOBAL_WORKSPACE_NAME]
    if not available:
        return ""
    selected_workspace = current_workspace_name or available[0].name
    def option_href(workspace: IteraSpecWorkspace) -> str:
        if current_document_name == "status.md":
            return f"/?section=status&workspace={quote(workspace.name)}"
        if current_document_name in {"board.md", "backlog.md"}:
            board_doc_name = _preferred_board_document(workspace)
            return f"/workspaces/{quote(workspace.name)}/documents/{quote(board_doc_name)}"
        if current_document_name and any(document.name == current_document_name for document in workspace.documents):
            return f"/workspaces/{quote(workspace.name)}/documents/{quote(current_document_name)}"
        return f"/?section={quote(current_section)}&workspace={quote(workspace.name)}"
    options = "".join(
        f'<option value="{option_href(workspace)}"{" selected" if workspace.name == selected_workspace else ""}>{html.escape(_workspace_label(workspace.name))}</option>'
        for workspace in available
    )
    return (
        '<div class="home-workspace-picker">'
        '<label for="workspace-picker">Workspace</label>'
        f'<select id="workspace-picker" class="home-workspace-select" onchange="window.location.href=this.value">{options}</select>'
        "</div>"
    )


def _render_primary_menu(
    current_section: str,
    workspaces: list[IteraSpecWorkspace],
    developers: list[DeveloperProfile],
    current_workspace_name: str,
    current_document_name: str,
    current_developer_name: str,
) -> str:
    icons = {
        "dashboard": "◫",
        "status": "◎",
        "board": "▤",
        "current-task": "↳",
        "documents": "▣",
        "developers": "◍",
    }
    current_workspace = next((workspace for workspace in workspaces if workspace.name == current_workspace_name), None)
    workspace_query = f"&workspace={quote(current_workspace.name)}" if current_workspace is not None else ""
    board_href = (
        f"/workspaces/{current_workspace.name}/documents/{_preferred_board_document(current_workspace)}"
        if current_workspace is not None
        else f"/?section=board{workspace_query}"
    )
    document_submenu = (
        '<a class="home-submenu-link{}" href="/?section=documents{}">Overview</a>'.format(
            " active" if current_section == "documents" and not current_document_name else "",
            workspace_query,
        )
        + "".join(
        f'<a class="home-submenu-link{" active" if current_document_name == document.name else ""}" href="/workspaces/{current_workspace.name}/documents/{document.name}">{html.escape(document.name)}</a>'
        for document in current_workspace.documents
    ) if current_workspace is not None else '<span class="muted">Sin workspace activo.</span>'
    )
    developer_submenu = (
        '<a class="home-submenu-link{}" href="/?section=developers{}">Overview</a>'.format(
            " active" if current_section == "developers" and not current_developer_name else "",
            workspace_query,
        )
        + "".join(
        f'<a class="home-submenu-link{" active" if current_developer_name == developer.filename else ""}" href="{developer_detail_href(developer.filename)}">{html.escape(developer.display_name)}</a>'
        for developer in developers
    ) if developers else '<span class="muted">Sin developers.</span>'
    )
    items = [
        ("dashboard", "Dashboard", "Resumen general del sistema", f"/?section=dashboard{workspace_query}", "", False),
        ("status", "Status", "Lectura del estado global", f"/?section=status{workspace_query}", "", False),
        ("board", "Board", "Estado del backlog activo", board_href, "", False),
        ("current-task", "Current Task", "Tarea operativa en curso", f"/?section=current-task{workspace_query}", "", False),
        ("documents", "Documents", "Listado de artefactos del workspace activo", f"/?section=documents{workspace_query}", document_submenu, True),
        ("developers", "Developers", "Perfiles reutilizables detectados", f"/?section=developers{workspace_query}", developer_submenu, True),
    ]
    return "".join(
        _render_primary_menu_item(identifier, label, description, href, submenu, collapsible, current_section, current_document_name, icons.get(identifier, "•"))
        for identifier, label, description, href, submenu, collapsible in items
    )


def _render_primary_menu_item(
    identifier: str,
    label: str,
    description: str,
    href: str,
    submenu: str,
    collapsible: bool,
    current_section: str,
    current_document_name: str,
    icon: str,
) -> str:
    is_active = current_section == identifier or (
        identifier == "board" and current_document_name in {"board.md", "backlog.md"}
    )
    if not collapsible:
        return (
            '<div class="home-menu-group">'
            f'<a class="home-menu-link{" active" if is_active else ""}" href="{href}"><span class="home-menu-icon" aria-hidden="true">{html.escape(icon)}</span><span class="home-menu-copy"><strong>{html.escape(label)}</strong></span></a>'
            "</div>"
        )
    is_open = current_section == identifier
    return (
        f'<details class="home-menu-group collapsible"{" open" if is_open else ""}>'
        f'<summary class="home-menu-summary"><span class="home-menu-summary-icon" aria-hidden="true">{html.escape(icon)}</span><span class="home-menu-copy"><strong>{html.escape(label)}</strong></span></summary>'
        f'<div class="home-submenu">{submenu}</div>'
        "</details>"
    )


def _render_developers(developers: list[DeveloperProfile]) -> str:
    if not developers:
        return (
            "<div class=\"empty-state\">"
            "<strong>No se detectaron developers reutilizables.</strong>"
            "<p>Cuando existan perfiles en <code>.iteraspec/developers/</code>, aparecerán aquí.</p>"
            "</div>"
        )

    return "".join(
        (
            "<article class=\"workspace-card\">"
            f"<header><h2><a class=\"doc-link\" href=\"{developer_detail_href(developer.filename)}\">{html.escape(developer.display_name)}</a></h2>"
            f"<p>{html.escape(developer.relative_path)}</p></header>"
            f"<div class=\"developer-chip-group\">{''.join(f'<span class=\"developer-chip\">{html.escape(stack)}</span>' for stack in developer.primary_stacks[:4]) or '<span class=\"developer-chip\">Sin stacks declarados</span>'}</div>"
            f"<p><strong>{html.escape(developer.role)}</strong> · {html.escape(developer.specialty)}</p>"
            f"<p>Seniority: {html.escape(developer.seniority)} · Active: {html.escape(developer.active)}</p>"
            f"<a class=\"primary-link\" href=\"{developer_detail_href(developer.filename)}\">Abrir perfil</a>"
            "</article>"
        )
        for developer in developers
    )


def _render_documents(workspace_name: str, documents: list[IteraSpecDocument]) -> str:
    if not documents:
        return "<li class=\"doc-item muted\">Sin archivos Markdown detectados.</li>"

    return "".join(
        (
            "<li class=\"doc-item\">"
            f"<span class=\"doc-kind\">{html.escape(document.kind)}</span>"
            f"<a class=\"doc-link\" href=\"/workspaces/{workspace_name}/documents/{document.name}\">{html.escape(document.name)}</a>"
            "</li>"
        )
        for document in documents
    )


def _render_home_board_section(workspace: IteraSpecWorkspace | None, iteraspec_root: Path) -> str:
    if workspace is None:
        return "<article class=\"home-panel\"><h3>Sin workspace activo</h3><p>No hay un workspace disponible para leer el board.</p></article>"
    board_doc_name = _preferred_board_document(workspace)
    try:
        loaded = read_workspace_document(workspace.name, board_doc_name, iteraspec_root)
    except (InvalidDocumentRequestError, DocumentNotFoundError):
        return (
            "<article class=\"home-panel\">"
            f"<h3>{html.escape(_workspace_label(workspace.name))}</h3>"
            f"<p>No existe <code>{html.escape(board_doc_name)}</code> en este workspace.</p>"
            "</article>"
        )
    return render_board_view(loaded.content, workspace.name, iteraspec_root)


def _render_home_current_task_section(workspace: IteraSpecWorkspace | None, iteraspec_root: Path) -> str:
    if workspace is None:
        return "<article class=\"home-panel\"><h3>Sin tarea activa</h3><p>No hay workspace activo para consultar <code>current_task.md</code>.</p></article>"
    current_task = _read_current_task_snapshot(workspace.name, iteraspec_root)
    if current_task is None:
        return (
            "<article class=\"home-panel\">"
            f"<h3>{html.escape(_workspace_label(workspace.name))}</h3>"
            "<p>No existe una tarea activa detectable en este workspace.</p>"
            "</article>"
        )
    assignees = [name.strip() for name in current_task["assignees"].split(",") if name.strip()]
    return (
        "<article class=\"dashboard-focus-card\">"
        f"<p class=\"section-kicker\">{html.escape(_workspace_label(workspace.name))}</p>"
        f"<h3>{html.escape(current_task['title'])}</h3>"
        "<div class=\"task-pill-group\">"
        f'<a class="task-pill" href="{task_detail_href(workspace.name, current_task["identifier"])}">{html.escape(current_task["identifier"])}</a>'
        f'<a class="task-pill" href="{requirement_detail_href(workspace.name, current_task["requirement"])}">{html.escape(current_task["requirement"])}</a>'
        "</div>"
        f"{render_assignee_chips(assignees)}"
        f"<p>{html.escape(current_task['objective'])}</p>"
        f"<a class=\"primary-link\" href=\"/workspaces/{workspace.name}/documents/current_task.md\">Abrir tarea activa</a>"
        "</article>"
    )


def _render_home_documents_section(workspace: IteraSpecWorkspace | None) -> str:
    if workspace is None:
        return "<article class=\"home-panel\"><h3>Sin documentos</h3><p>No hay un workspace activo para mostrar accesos rápidos.</p></article>"
    return (
        "<div class=\"workspace-grid\">"
        "<article class=\"workspace-card\">"
        f"<header><h2>{html.escape(_workspace_label(workspace.name))}</h2>"
        f"<p>{html.escape(workspace.relative_path)}</p></header>"
        f"<ul class=\"documents-panel-list\">{_render_documents(workspace.name, workspace.documents)}</ul>"
        "</article>"
        "</div>"
    )


def _render_home_status_section(iteraspec_root: Path) -> str:
    status_content = _read_global_status_content(iteraspec_root)
    if status_content is None:
        return "<article class=\"home-panel\"><h3>Sin status global</h3><p>No se detectó <code>status.md</code> en la instalación actual.</p></article>"
    return render_status_view(status_content)


def _resolve_workspace_for_section(
    workspaces: list[IteraSpecWorkspace],
    active_workspace: IteraSpecWorkspace | None,
    selected_workspace_name: str,
) -> IteraSpecWorkspace | None:
    if selected_workspace_name:
        selected = next((workspace for workspace in workspaces if workspace.name == selected_workspace_name), None)
        if selected is not None:
            return selected
    return active_workspace


def _render_home_section_content(
    current_section: str,
    workspaces: list[IteraSpecWorkspace],
    developers: list[DeveloperProfile],
    iteraspec_root: Path,
    focus_workspace: IteraSpecWorkspace | None,
) -> tuple[str, str, str]:
    if current_section == "board":
        return (
            _preferred_board_document(focus_workspace) if focus_workspace else "board.md",
            "Estado del backlog del workspace actualmente enfocado.",
            _render_home_board_section(focus_workspace, iteraspec_root),
        )
    if current_section == "current-task":
        return (
            "Current Task",
            "Foco operativo en la tarea activa del workspace actual.",
            _render_home_current_task_section(focus_workspace, iteraspec_root),
        )
    if current_section == "documents":
        return (
            "Documents",
            "Listado de artefactos del workspace activo o seleccionado.",
            _render_home_documents_section(focus_workspace),
        )
    if current_section == "developers":
        return (
            "Developers",
            "Perfiles reutilizables disponibles en el proyecto.",
            f'<div class="workspace-grid">{_render_developers(developers)}</div>',
        )
    if current_section == "status":
        return (
            "Status",
            "Lectura del estado global persistido en status.md.",
            _render_home_status_section(iteraspec_root),
        )
    focused_label = _workspace_label(focus_workspace.name) if focus_workspace is not None else "Sin workspace activo"
    return (
        f"Dashboard de {focused_label}",
        f"Resumen operativo del workspace {focused_label}.",
        _render_dashboard(workspaces, iteraspec_root, focus_workspace),
    )


def _render_dashboard(
    workspaces: list[IteraSpecWorkspace],
    iteraspec_root: Path,
    focus_workspace: IteraSpecWorkspace | None = None,
) -> str:
    global_workspace = next((workspace for workspace in workspaces if workspace.name == GLOBAL_WORKSPACE_NAME), None)
    active_workspace = focus_workspace or _resolve_active_workspace(workspaces, iteraspec_root)
    active_name = active_workspace.name if active_workspace else "Sin workspace"
    active_label = _workspace_label(active_name)

    backlog_stats = _read_board_stats(active_name, iteraspec_root) if active_workspace else {}
    current_task = _read_current_task_snapshot(active_name, iteraspec_root) if active_workspace else None

    max_backlog_value = max(backlog_stats.values(), default=0)
    backlog_summary = "".join(
        _render_backlog_bar(key, label, backlog_stats.get(label, 0), max_backlog_value)
        for key, label in BACKLOG_SECTION_ORDER
    )

    quick_links = _render_quick_links(active_workspace)
    if global_workspace is not None:
        quick_links = (
            f"<a class=\"quick-link\" href=\"/workspaces/{GLOBAL_WORKSPACE_NAME}/documents/status.md\">status.md</a>"
            + quick_links
        )
    board_doc_name = _preferred_board_document(active_workspace)
    board_doc_label = "board" if board_doc_name == "board.md" else "backlog"
    escaped_active_name = html.escape(active_label)
    current_task_assignees = (
        [name.strip() for name in current_task["assignees"].split(",") if name.strip()]
        if current_task and current_task.get("assignees")
        else []
    )
    current_task_markup = (
        "<article class=\"dashboard-focus-card\">"
        "<p class=\"section-kicker\">Tarea Activa</p>"
        f"<h3>{html.escape(current_task['title'])}</h3>"
        "<div class=\"task-pill-group\">"
        f'<a class="task-pill" href="{task_detail_href(active_name, current_task["identifier"])}">{html.escape(current_task["identifier"])}</a>'
        f'<a class="task-pill" href="{requirement_detail_href(active_name, current_task["requirement"])}">{html.escape(current_task["requirement"])}</a>'
        "</div>"
        f"{render_assignee_chips(current_task_assignees)}"
        f"<p>{html.escape(current_task['objective'])}</p>"
        f"<a class=\"primary-link\" href=\"/workspaces/{active_name}/documents/current_task.md\">Abrir tarea activa</a>"
        "</article>"
        if current_task
        else (
            "<article class=\"dashboard-focus-card\">"
            "<p class=\"section-kicker\">Tarea Activa</p>"
            "<h3>No hay una tarea activa detectable</h3>"
            "<p>Cuando exista <code>current_task.md</code>, aparecerá aquí con foco prioritario.</p>"
            "</article>"
        )
    )

    return f"""
      <section class="overview-grid">
        <article class="overview-card">
          <p class="section-kicker">Workspace Prioritario</p>
          <h2>{escaped_active_name}</h2>
          <p>Accesos rápidos a los artefactos más importantes del ciclo actual.</p>
          <div class="quick-links">{quick_links}</div>
        </article>
        <article class="overview-card">
          <p class="section-kicker">Estado del Backlog</p>
          <h2>Lectura ejecutiva</h2>
          <div class="mini-status-grid">{backlog_summary}</div>
          <a class="primary-link" href="/workspaces/{active_name}/documents/{board_doc_name}">Abrir {board_doc_label}</a>
        </article>
        {current_task_markup}
      </section>
    """


def _render_backlog_bar(key: str, label: str, value: int, max_value: int) -> str:
    width = 0 if max_value == 0 else max(8, round((value / max_value) * 100))
    return (
        "<div class=\"mini-status-row\">"
        "<div class=\"mini-status-topline\">"
        f"<span class=\"status-chip {key}\">{html.escape(label)}</span>"
        f"<strong>{value}</strong>"
        "</div>"
        "<div class=\"mini-status-bar-track\">"
        f"<span class=\"mini-status-bar-fill {key}\" style=\"width: {width}%\"></span>"
        "</div>"
        "</div>"
    )


def _render_quick_links(workspace: IteraSpecWorkspace | None) -> str:
    if workspace is None:
        return "<p class=\"muted\">No hay documentos detectados.</p>"
    priority = ["specs.md", "board.md", "backlog.md", "staffing.md", "current_task.md", "delivery.md"]
    available = {document.name: document for document in workspace.documents}
    links = []
    for name in priority:
        if name in available:
            links.append(
                f"<a class=\"quick-link\" href=\"/workspaces/{workspace.name}/documents/{name}\">{html.escape(name)}</a>"
            )
    return "".join(links) if links else "<p class=\"muted\">Sin accesos prioritarios detectados.</p>"


def _preferred_board_document(workspace: IteraSpecWorkspace | None) -> str:
    if workspace is None:
        return "board.md"
    available = {document.name for document in workspace.documents}
    return "board.md" if "board.md" in available else "backlog.md"


def _resolve_active_workspace(
    workspaces: list[IteraSpecWorkspace],
    iteraspec_root: Path,
) -> IteraSpecWorkspace | None:
    workspace_map = {workspace.name: workspace for workspace in workspaces if workspace.name != GLOBAL_WORKSPACE_NAME}
    if not workspace_map:
        return None
    try:
        loaded = read_workspace_document(GLOBAL_WORKSPACE_NAME, "status.md", iteraspec_root)
    except (DocumentNotFoundError, InvalidDocumentRequestError):
        loaded = None
    if loaded is not None:
        status_map = dict(parse_status_key_values(loaded.content))
        active_feature = status_map.get("Active Feature", "").strip().strip("`")
        if active_feature in workspace_map:
            return workspace_map[active_feature]
    return next(iter(workspace_map.values()))


def _read_global_status_content(iteraspec_root: Path) -> str | None:
    try:
        loaded = read_workspace_document(GLOBAL_WORKSPACE_NAME, "status.md", iteraspec_root)
    except (DocumentNotFoundError, InvalidDocumentRequestError):
        return None
    return loaded.content


def _read_board_stats(workspace_name: str, iteraspec_root: Path) -> dict[str, int]:
    try:
        loaded = read_workspace_document(workspace_name, "board.md", iteraspec_root)
    except (InvalidDocumentRequestError, DocumentNotFoundError):
        return _read_legacy_backlog_stats(workspace_name, iteraspec_root)
    parsed = parse_board(loaded.content)
    return {section.label: len(section.items) for section in parsed}


def _read_legacy_backlog_stats(workspace_name: str, iteraspec_root: Path) -> dict[str, int]:
    try:
        loaded = read_workspace_document(workspace_name, "backlog.md", iteraspec_root)
    except (InvalidDocumentRequestError, DocumentNotFoundError):
        return {}
    parsed = parse_legacy_backlog_board(loaded.content)
    return {section.label: len(section.items) for section in parsed}


def _read_current_task_snapshot(workspace_name: str, iteraspec_root: Path) -> dict[str, str] | None:
    try:
        loaded = read_workspace_document(workspace_name, "current_task.md", iteraspec_root)
    except (InvalidDocumentRequestError, DocumentNotFoundError):
        return None
    parsed = parse_current_task(loaded.content)
    return {
        "title": parsed.title or "Tarea activa",
        "identifier": parsed.identifier or "Sin identificador",
        "requirement": parsed.requirement or "Sin requerimiento",
        "assignees": ", ".join(parsed.assignees),
        "objective": parsed.objective or "Sin objetivo detectado.",
    }


def _render_task_page(
    workspaces: list[IteraSpecWorkspace],
    workspace_name: str,
    task: BacklogTask,
    board_item: BoardItem | None,
    board_label: str,
    tasks_by_id: dict[str, BacklogTask],
) -> str:
    project_title = infer_project_title(resolve_iteraspec_root())
    developers = discover_developers(resolve_iteraspec_root())
    identifier, summary = split_task_title(task.title)
    theme_switcher = render_theme_switcher()
    detail_markup = render_task_detail(task, workspace_name)
    note_panel = (
        "<article class=\"task-modal-panel\">"
        "<h4>Nota de estado</h4>"
        f"<p>{html.escape(board_item.note)}</p>"
        "</article>"
        if board_item is not None and board_item.note
        else ""
    )
    assignee_panel = (
        "<article class=\"task-modal-panel\">"
        "<h4>Desarrolladores asignados</h4>"
        f"{render_assignee_chips(task.assignees)}"
        "</article>"
    )
    state_panel = (
        "<article class=\"task-modal-panel\">"
        "<h4>Estado en board</h4>"
        f"<p>{render_status_chip(board_label)}</p>"
        "</article>"
        if board_label
        else ""
    )
    requirement_panel = (
        "<article class=\"task-modal-panel\">"
        "<h4>Requerimiento asociado</h4>"
        f'<p><a class="task-code-chip" href="{requirement_detail_href(workspace_name, task.requirement_id)}">{html.escape(task.requirement_id)}</a></p>'
        "</article>"
        if task.requirement_id
        else ""
    )
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(identifier or summary)} · {html.escape(project_title)}</title>
    {THEME_BOOTSTRAP_SCRIPT}
    <link rel="stylesheet" href="/styles.css">
  </head>
  <body>
    {_render_app_shell(
      _render_primary_sidebar(project_title, theme_switcher, "documents", workspaces, developers, workspace_name, "backlog.md", ""),
      f"""<article class="document-panel">
        <header class="document-header">
          <h1>{html.escape(summary)}</h1>
          <div class="task-pill-group">
            {f'<a class="task-pill" href="{task_detail_href(workspace_name, identifier)}">{html.escape(identifier)}</a>' if identifier else ''}
            {f'<a class="task-pill" href="{requirement_detail_href(workspace_name, task.requirement_id)}">{html.escape(task.requirement_id)}</a>' if task.requirement_id else ''}
          </div>
        </header>
        <section class="markdown-body">
          <div class="specialized-view current-task-view">
            <section class="task-grid">
              {state_panel}
              {requirement_panel}
              {assignee_panel}
              {note_panel}
            </section>
            <section class="task-panel">
              <h3>Detalle</h3>
              {detail_markup}
            </section>
          </div>
        </section>
        </article>"""
    )}
    {THEME_BEHAVIOR_SCRIPT}
  </body>
</html>"""


def _render_requirement_page(
    workspaces: list[IteraSpecWorkspace],
    workspace_name: str,
    requirement_id: str,
    section_title: str,
    section_content: str,
    related_tasks: list[BacklogTask],
) -> str:
    project_title = infer_project_title(resolve_iteraspec_root())
    developers = discover_developers(resolve_iteraspec_root())
    theme_switcher = render_theme_switcher()
    requirement_title = split_requirement_title(section_title, requirement_id)
    related_markup = "".join(
        (
            "<li>"
            f'<a class="doc-link" href="{task_detail_href(workspace_name, task.identifier)}">'
            f"{html.escape(task.identifier)} - {html.escape(split_task_title(task.title)[1])}"
            "</a>"
            "</li>"
        )
        for task in related_tasks
        if task.identifier
    ) or "<li>Sin tareas asociadas detectadas.</li>"
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(requirement_title)} · {html.escape(project_title)}</title>
    {THEME_BOOTSTRAP_SCRIPT}
    <link rel="stylesheet" href="/styles.css">
  </head>
  <body>
    {_render_app_shell(
      _render_primary_sidebar(project_title, theme_switcher, "documents", workspaces, developers, workspace_name, "specs.md", ""),
      f"""<article class="document-panel">
        <header class="document-header">
          <h1>{html.escape(requirement_title)}</h1>
          <div class="task-pill-group">
            <a class="task-pill" href="{requirement_detail_href(workspace_name, requirement_id)}">{html.escape(requirement_id)}</a>
          </div>
        </header>
        <section class="markdown-body">
          <div class="specialized-view current-task-view">
            <section class="task-grid">
              <article class="task-modal-panel">
                <h4>Tareas relacionadas</h4>
                <ul>{related_markup}</ul>
              </article>
            </section>
            <section class="task-panel">
              <h3>Contexto en specs.md</h3>
              {render_markdown(section_content, workspace_name)}
            </section>
          </div>
        </section>
        </article>"""
    )}
    {THEME_BEHAVIOR_SCRIPT}
  </body>
</html>"""


def _render_document_page(
    workspaces: list[IteraSpecWorkspace],
    current_workspace_name: str,
    current_document_name: str,
    content: str,
    iteraspec_root: Path,
) -> str:
    project_title = infer_project_title(resolve_iteraspec_root())
    developers = discover_developers(resolve_iteraspec_root())
    theme_switcher = render_theme_switcher()
    article = (
        render_specialized_document(
            current_document_name,
            content,
            current_workspace_name,
            iteraspec_root,
        )
        or render_markdown(content, current_workspace_name)
    )
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(current_document_name)} · {html.escape(project_title)}</title>
    {THEME_BOOTSTRAP_SCRIPT}
    <link rel="stylesheet" href="/styles.css">
  </head>
  <body>
    {_render_app_shell(
      _render_primary_sidebar(project_title, theme_switcher, "status" if current_document_name == "status.md" else "documents", workspaces, developers, current_workspace_name, current_document_name, ""),
      f"""<article class="document-panel">
        <header class="document-header">
          <h1>{html.escape(current_document_name)}</h1>
        </header>
        <section class="markdown-body">
          {article}
        </section>
        </article>"""
    )}
    {THEME_BEHAVIOR_SCRIPT}
  </body>
</html>"""


def _render_developer_index_page(
    workspaces: list[IteraSpecWorkspace],
    developers: list[DeveloperProfile],
) -> str:
    project_title = infer_project_title(resolve_iteraspec_root())
    theme_switcher = render_theme_switcher()
    developer_markup = _render_developers(developers)
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Developer Staff · {html.escape(project_title)}</title>
    {THEME_BOOTSTRAP_SCRIPT}
    <link rel="stylesheet" href="/styles.css">
  </head>
  <body>
    {_render_app_shell(
      _render_primary_sidebar(project_title, theme_switcher, "developers", workspaces, developers, "", "", ""),
      f"""<article class="document-panel">
        <header class="document-header">
          <h1>Perfiles reutilizables</h1>
        </header>
        <section class="workspace-grid">
          {developer_markup}
        </section>
        </article>"""
    )}
    {THEME_BEHAVIOR_SCRIPT}
  </body>
</html>"""


def _render_developer_page(
    workspaces: list[IteraSpecWorkspace],
    developer: DeveloperProfile,
    content: str,
) -> str:
    project_title = infer_project_title(resolve_iteraspec_root())
    theme_switcher = render_theme_switcher()
    developers = discover_developers(resolve_iteraspec_root())
    stacks = render_assignee_chips(developer.primary_stacks) if developer.primary_stacks else '<p class="muted">Sin stacks declarados.</p>'
    article = render_markdown(content)
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(developer.display_name)} · {html.escape(project_title)}</title>
    {THEME_BOOTSTRAP_SCRIPT}
    <link rel="stylesheet" href="/styles.css">
  </head>
  <body>
    {_render_app_shell(
      _render_primary_sidebar(project_title, theme_switcher, "developers", workspaces, developers, "", "", developer.filename),
      f"""<article class="document-panel">
        <header class="document-header">
          <h1>{html.escape(developer.display_name)}</h1>
          <div class="task-pill-group">
            <div class="task-pill">{html.escape(developer.seniority)}</div>
            <div class="task-pill">{html.escape(developer.active)}</div>
          </div>
        </header>
        <section class="markdown-body">
          <div class="specialized-view current-task-view">
            <section class="task-grid">
              <article class="task-panel">
                <h3>Stacks principales</h3>
                {stacks}
              </article>
              <article class="task-panel">
                <h3>Archivo fuente</h3>
                <p><code>{html.escape(developer.relative_path)}</code></p>
              </article>
            </section>
            <section class="task-panel">
              <h3>Perfil completo</h3>
              {article}
            </section>
          </div>
        </section>
        </article>"""
    )}
    {THEME_BEHAVIOR_SCRIPT}
  </body>
</html>"""


def _render_sidebar(
    workspaces: list[IteraSpecWorkspace],
    current_workspace_name: str,
    current_document_name: str,
    current_developer_name: str = "",
) -> str:
    sections: list[str] = []
    for workspace in workspaces:
        items = []
        for document in workspace.documents:
            classes = ["sidebar-doc"]
            if workspace.name == current_workspace_name and document.name == current_document_name:
                classes.append("active")
            items.append(
                f"<li><a class=\"{' '.join(classes)}\" href=\"/workspaces/{workspace.name}/documents/{document.name}\">{html.escape(document.name)}</a></li>"
            )
        is_open = workspace.name == current_workspace_name and bool(current_document_name)
        document_count = len(workspace.documents)
        count_label = "1 documento" if document_count == 1 else f"{document_count} documentos"
        sections.append(
            f"<details class=\"sidebar-workspace\"{' open' if is_open else ''}>"
            "<summary>"
            f"<h2>{html.escape(_workspace_label(workspace.name))}</h2>"
            f"<span class=\"sidebar-workspace-count\">{html.escape(count_label)}</span>"
            "</summary>"
            f"<ul>{''.join(items) if items else '<li class=\"muted\">Sin documentos.</li>'}</ul>"
            "</details>"
        )
    developers = discover_developers(resolve_iteraspec_root())
    developer_items = []
    for developer in developers:
        classes = ["sidebar-doc"]
        if developer.filename == current_developer_name:
            classes.append("active")
        developer_items.append(
            f"<li><a class=\"{' '.join(classes)}\" href=\"{developer_detail_href(developer.filename)}\">{html.escape(developer.display_name)}</a></li>"
        )
    sections.append(
        "<section class=\"sidebar-workspace\">"
        "<h2>Developers</h2>"
        f"<ul><li><a class=\"sidebar-doc{' active' if not current_workspace_name and not current_document_name and not current_developer_name else ''}\" href=\"/developers\">staff</a></li>{''.join(developer_items) if developer_items else '<li class=\"muted\">Sin developers.</li>'}</ul>"
        "</section>"
    )
    return "".join(sections)


def _workspace_label(name: str) -> str:
    return "Global" if name == GLOBAL_WORKSPACE_NAME else name


if __name__ == "__main__":
    main()
