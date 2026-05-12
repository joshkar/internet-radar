import asyncio
import aiohttp
import subprocess
import socket
import platform
import flet as ft
from datetime import datetime

# ================= TARGETS =================

TARGETS = [
    ("Google DNS", "1.1.1.1", "dns"),
    ("Cloudflare DNS", "1.0.0.1", "dns"),
    ("Google DNS 2", "8.8.8.8", "dns"),
    ("Quad9", "9.9.9.9", "dns"),
    ("Cloudflare", "cloudflare.com", "cdn"),
    ("Fastly", "fastly.com", "cdn"),
    ("Akamai", "akamai.com", "cdn"),
    ("GitHub", "github.com", "dev"),
    ("NPM Registry", "registry.npmjs.org", "dev"),
    ("Docker Hub", "registry-1.docker.io", "dev"),
    ("StackOverflow", "stackoverflow.com", "dev"),
    ("Google", "google.com", "google"),
    ("YouTube", "youtube.com", "google"),
    ("Google APIs", "www.googleapis.com", "google"),
    ("Microsoft", "microsoft.com", "ms"),
    ("Azure", "azure.microsoft.com", "ms"),
    ("OneDrive", "onedrive.live.com", "ms"),
    ("Outlook", "outlook.live.com", "ms"),
    ("ChatGPT", "chat.openai.com", "ai"),
    ("Claude AI", "claude.ai", "ai"),
    ("Gemini", "gemini.google.com", "ai"),
    ("HuggingFace", "huggingface.co", "ai"),
    ("Steam", "store.steampowered.com", "gaming"),
    ("PlayStation", "www.playstation.com", "gaming"),
]

GROUP_COLORS = {
    "dns":    "#3DAFD4",
    "cdn":    "#5B9E65",
    "dev":    "#C98A3E",
    "google": "#B8546E",
    "ms":     "#4A82BC",
    "ai":     "#9B6FBE",
    "gaming": "#BC6B45",
}

GROUP_LABELS = {
    "dns": "DNS",
    "cdn": "CDN",
    "dev": "Dev",
    "google": "Google",
    "ms": "Microsoft",
    "ai": "AI",
    "gaming": "Gaming",
}

# ================= CHECKS =================

def is_ip(host):
    return host.replace(".", "").isdigit()

def ping(host):
    try:
        system = platform.system().lower()
        if system == "windows":
            cmd = ["ping", "-n", "1", "-w", "1000", host]
        else:
            cmd = ["ping", "-c", "1", "-W", "1", host]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except:
        return False

def dns_check(host):
    if is_ip(host):
        return True
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((host, 53))
        sock.close()
        return True
    except:
        return False

async def https_check(session, host):
    if is_ip(host):
        return None
    try:
        async with session.get(f"https://{host}", timeout=aiohttp.ClientTimeout(total=3), ssl=False) as r:
            return r.status
    except:
        return None

async def check_target(session, target):
    name, host, group = target
    dns_ok, ping_ok, https_val = await asyncio.gather(
        asyncio.to_thread(dns_check, host),
        asyncio.to_thread(ping, host),
        https_check(session, host),
    )
    return {
        "name": name,
        "host": host,
        "group": group,
        "dns": dns_ok,
        "ping": ping_ok,
        "https": https_val,
    }

async def run_checks():
    async with aiohttp.ClientSession() as session:
        tasks = [check_target(session, t) for t in TARGETS]
        return await asyncio.gather(*tasks)

# ================= UI COMPONENTS =================

def status_dot(ok, size=10):
    color = "#4CAF50" if ok else "#E05555"
    return ft.Container(
        width=size, height=size,
        border_radius=size,
        bgcolor=color,
        shadow=ft.BoxShadow(blur_radius=4, color=color + "55", spread_radius=0),
    )

def service_card(result):
    group = result["group"]
    color = GROUP_COLORS.get(group, "#888888")
    name = result["name"]
    host = result["host"]

    dns_ok = result["dns"]
    ping_ok = result["ping"]
    https_val = result["https"]
    https_ok = isinstance(https_val, int) and https_val < 400

    all_ok = dns_ok and ping_ok and (https_val is None or https_ok)
    any_fail = not dns_ok or not ping_ok or (https_val is not None and not https_ok)

    border_color = "#2A3D2A" if all_ok else ("#3D2A2A" if any_fail else "#3D3020")
    card_bg = "#0F0F0F"

    https_text = f"{https_val}" if isinstance(https_val, int) else ("—" if https_val is None else "✗")
    https_color = "#4CAF50" if https_ok else ("#4A4A4A" if https_val is None else "#E05555")

    badge = ft.Container(
        content=ft.Text(GROUP_LABELS.get(group, group), size=10, color=color, weight=ft.FontWeight.W_500),
        bgcolor="#161616",
        border_radius=4,
        padding=ft.padding.symmetric(horizontal=7, vertical=2),
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text(name, size=13, weight=ft.FontWeight.W_600, color="#DEDEDE", expand=True),
                badge,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(host, size=11, color="#454545"),
            ft.Container(height=8),
            ft.Row([
                ft.Column([
                    ft.Text("DNS", size=10, color="#585858"),
                    status_dot(dns_ok, 8),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
                ft.Column([
                    ft.Text("Ping", size=10, color="#585858"),
                    status_dot(ping_ok, 8),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
                ft.Column([
                    ft.Text("HTTPS", size=10, color="#585858"),
                    ft.Text(https_text, size=11, color=https_color, weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
        ], spacing=4),
        padding=ft.padding.all(14),
        border_radius=10,
        bgcolor=card_bg,
        border=ft.border.all(1, border_color),
        expand=True,
    )

def loading_card():
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(width=100, height=10, bgcolor="#1E1E1E", border_radius=4),
                ft.Container(width=32, height=16, bgcolor="#1E1E1E", border_radius=4),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(width=80, height=8, bgcolor="#181818", border_radius=4),
            ft.Container(height=8),
            ft.Row([
                ft.Column([
                    ft.Container(width=24, height=8, bgcolor="#1E1E1E", border_radius=4),
                    ft.Container(width=8, height=8, bgcolor="#1E1E1E", border_radius=8),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
                ft.Column([
                    ft.Container(width=24, height=8, bgcolor="#1E1E1E", border_radius=4),
                    ft.Container(width=8, height=8, bgcolor="#1E1E1E", border_radius=8),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
                ft.Column([
                    ft.Container(width=32, height=8, bgcolor="#1E1E1E", border_radius=4),
                    ft.Container(width=16, height=8, bgcolor="#1E1E1E", border_radius=4),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
        ], spacing=4),
        padding=ft.padding.all(14),
        border_radius=10,
        bgcolor="#0E0E0E",
        border=ft.border.all(1, "#1A1A1A"),
        expand=True,
    )

# ================= MAIN APP =================

async def main(page: ft.Page):
    page.title = "Internet Radar"
    page.bgcolor = "#0C0C0D"
    page.padding = 24
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 980
    page.window.height = 720
    page.window.min_width = 640
    page.window.min_height = 520

    results_grid = ft.ResponsiveRow(spacing=8, run_spacing=8)
    last_update_text = ft.Text("", size=11, color="#505050")
    status_text = ft.Text("", size=11, color="#4A9CB8")
    progress_ring = ft.ProgressRing(width=14, height=14, stroke_width=2, color="#4A9CB8")
    scanning_row = ft.Row([progress_ring, status_text], spacing=8, visible=False)

    selected_group = "all"
    all_results = []

    group_buttons_row = ft.Row(spacing=6, wrap=True)

    def build_group_buttons(active="all"):
        buttons = []
        groups = ["all"] + list(GROUP_LABELS.keys())
        for g in groups:
            label = "All" if g == "all" else GROUP_LABELS[g]
            is_active = g == active
            color = GROUP_COLORS.get(g, "#888888") if g != "all" else "#888888"
            btn = ft.Container(
                content=ft.Row([
                    ft.Container(
                        width=5, height=5,
                        border_radius=5,
                        bgcolor=color,
                        visible=is_active and g != "all",
                    ),
                    ft.Text(
                        label,
                        size=11,
                        color="#D8D8D8" if is_active else "#505050",
                        weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.NORMAL,
                    ),
                ], spacing=5, tight=True),
                bgcolor="#1C1C1C" if is_active else "transparent",
                border_radius=6,
                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                border=ft.border.all(1, "#2E2E2E" if is_active else "transparent"),
                on_click=lambda e, grp=g: filter_group(grp),
                animate=ft.Animation(120, ft.AnimationCurve.EASE_IN_OUT),
            )
            buttons.append(btn)
        return buttons

    def filter_group(group):
        nonlocal selected_group
        selected_group = group
        render_results(all_results, group)
        group_buttons_row.controls = build_group_buttons(group)
        page.update()

    def render_loading():
        results_grid.controls.clear()
        for _ in TARGETS:
            results_grid.controls.append(
                ft.Container(loading_card(), col={"xs": 12, "sm": 6, "md": 4, "lg": 3, "xl": 2})
            )

    def render_results(results, group="all"):
        results_grid.controls.clear()
        filtered = [r for r in results if group == "all" or r["group"] == group]
        filtered.sort(key=lambda r: (
            r["dns"] and r["ping"] and (r["https"] is None or (isinstance(r["https"], int) and r["https"] < 400))
        ), reverse=False)
        for r in filtered:
            card = service_card(r)
            results_grid.controls.append(
                ft.Container(card, col={"xs": 12, "sm": 6, "md": 4, "lg": 3, "xl": 2})
            )

    async def run_scan():
        nonlocal all_results
        progress_ring.visible = True
        scanning_row.visible = True
        status_text.value = "Scanning..."
        render_loading()
        page.update()
        await asyncio.sleep(0.05)

        all_results = list(await run_checks())

        render_results(all_results, selected_group)
        last_update_text.value = f"Updated {datetime.now().strftime('%H:%M')}"
        progress_ring.visible = False
        status_text.value = f"{len(all_results)} services"
        page.update()

    async def on_refresh(e):
        page.run_task(run_scan)

    refresh_btn = ft.OutlinedButton(
        "Rescan",
        icon=ft.icons.REFRESH_ROUNDED,
        on_click=on_refresh,
        tooltip="Re-check all services",
        style=ft.ButtonStyle(
            color="#4A9CB8",
            side=ft.BorderSide(1, "#1D3A47"),
            shape=ft.RoundedRectangleBorder(radius=7),
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
        ),
    )

    group_buttons_row.controls = build_group_buttons("all")

    header = ft.Row([
        ft.Column([
            ft.Row([
                ft.Icon(ft.icons.RADAR, color="#3DAFD4", size=22),
                ft.Text("Internet Radar", size=20, weight=ft.FontWeight.BOLD, color="#DEDEDE"),
            ], spacing=10),
            ft.Text("Network status & filtering monitor", size=11, color="#4A4A4A"),
        ], spacing=4, expand=True),
        ft.Column([
            ft.Row([
                scanning_row,
                last_update_text,
                refresh_btn,
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2),
    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)

    page.add(
        ft.Column([
            header,
            ft.Divider(color="#181818", height=24),
            ft.Row([
                ft.Icon(ft.icons.FILTER_LIST_ROUNDED, color="#444444", size=15),
                ft.Text("Filter", size=11, color="#484848"),
                group_buttons_row,
            ], spacing=8, wrap=True),
            ft.Container(height=8),
            results_grid,
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
    )

    page.run_task(run_scan)

ft.app(target=main)
