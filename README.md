# Internet Radar

A small desktop tool that shows which popular online services your
current internet connection can actually reach. Built for users in
Iran, where heavy filtering and unreliable VPN routes mean "is the
internet up?" is rarely a yes-or-no question — one service works,
another doesn't, and the answer changes depending on which DNS
resolver, VPN, or ISP you happen to be on at the moment.

Internet Radar gives that answer for two dozen well-known services at
a glance, so you can stop guessing whether the problem is your
connection, your VPN, the service itself, or a fresh round of blocks.

## What it checks

For each target, three checks run concurrently:

- **DNS** — TCP connect to port 53, 1 s timeout.
- **Ping** — one ICMP echo via the system `ping` command, 1 s timeout.
- **HTTPS** — `GET https://<host>` with a 3 s timeout. SSL verification
  is disabled so the probe still returns a status code when a
  certificate is mismatched or self-signed.

Showing all three layers side by side matters in a filtered
environment: DNS poisoning, IP-level routing blocks, and TLS/SNI-layer
filtering each leave a different fingerprint in the grid, so the
failure mode tells you something about *how* a service is being
blocked, not just whether it is.

## Targets

Twenty-four services across seven groups:

- **DNS** — Cloudflare `1.1.1.1`, Cloudflare `1.0.0.1`, Google
  `8.8.8.8`, Quad9 `9.9.9.9`
- **CDN** — Cloudflare, Fastly, Akamai
- **Dev** — GitHub, npm registry, Docker Hub, Stack Overflow
- **Google** — Google, YouTube, Google APIs
- **Microsoft** — Microsoft, Azure, OneDrive, Outlook
- **AI** — ChatGPT, Claude, Gemini, Hugging Face
- **Gaming** — Steam, PlayStation

## Features

- **Fully concurrent scan** — a full sweep of every service finishes
  in about three seconds even when half the targets time out.
- **Grouped view** with one-click category filter.
- **Failures first** — any service with a failing check sorts to the
  top of the grid so problems are immediately visible.
- **Responsive dark UI** that scales cleanly from 640 px upward.

## Screenshots

| | |
|---|---|
| ![Main dashboard](images/screen-1.png) | ![Category filter](images/screen-2.png) |
| ![Loading skeleton](images/screen-3.png) | ![Failure state](images/screen-4.png) |

## Install

Requires Python 3.9 or newer.

```bash
pip install -r requirements.txt
```

## Run

```bash
python radar.py
```

The window opens at 980×720 and rescans on demand via the **Rescan**
button in the header.

## Customising the target list

Open `radar.py` and edit the `TARGETS` list at the top of the file.
Each entry is a tuple of `(display_name, host, group)`. To introduce
a new category, add a matching key to `GROUP_COLORS` and
`GROUP_LABELS`.
