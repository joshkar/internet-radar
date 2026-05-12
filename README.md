# Internet Radar

A lightweight desktop tool that checks the reachability of popular internet
services in real time. It runs DNS, ICMP ping, and HTTPS probes against a
curated list of well-known endpoints and shows the results on a dark,
glanceable dashboard.

## Why

When a connection feels broken, the hard part is usually figuring out *what*
is broken — your DNS resolver, your route, a specific provider, or a regional
block. Internet Radar runs three layers of checks concurrently against
twenty-four well-known services so you can tell at a glance whether the
problem is local, regional, or limited to a specific platform.

## Features

- **Three-layer probe per service** — DNS resolution, ICMP ping, and HTTPS
  status code, so a single red dot tells you exactly which layer is failing.
- **Fully concurrent scan** — all checks run in parallel via `asyncio.gather`
  with blocking calls dispatched to a thread pool, so a full sweep of every
  service finishes in roughly three seconds even when some targets time out.
- **Grouped view** — DNS providers, CDNs, dev tools, Google, Microsoft, AI
  services, and gaming, each with its own accent colour.
- **One-click filter** to focus on a single category.
- **Failures first** — services with any failing check sort to the top of the
  grid so problems are immediately visible.
- **Responsive dark UI** built with [Flet](https://flet.dev), scaling cleanly
  from 640 px upward.

## Screenshots

| | |
|---|---|
| ![Main dashboard](images/screen-1.png) | ![Category filter](images/screen-2.png) |
| ![Loading skeleton](images/screen-3.png) | ![Failure state](images/screen-4.png) |

## Install

Requires Python 3.9 or newer (for `asyncio.to_thread`).

```bash
pip install -r requirements.txt
```

## Run

```bash
python gui-radar.py
```

The window opens at 980×720 and rescans on demand via the **Rescan** button in
the header.

## How it works

For each target, three checks run concurrently:

1. **DNS** — TCP connect to port 53 with a 1 s timeout.
2. **Ping** — one ICMP echo request via the system `ping` command, 1 s
   timeout.
3. **HTTPS** — `GET https://<host>` with a 3 s timeout. SSL verification is
   disabled so probes still report a status even when a certificate is
   mismatched or self-signed.

Blocking calls (`ping` and the DNS socket) are handed off to a thread pool via
`asyncio.to_thread`, so one slow target never stalls the others.

## Customising the target list

Open `gui-radar.py` and edit the `TARGETS` list at the top of the file. Each
entry is a tuple of `(display_name, host, group)`. To introduce a new
category, add a matching key to `GROUP_COLORS` and `GROUP_LABELS`.
