# Security Policy

## Project posture

A-Proxy is a **local research and experimentation tool.** It is designed to run on a
single user's machine: it binds to `127.0.0.1` (localhost) by default, and the Docker
Compose setup publishes its ports to `127.0.0.1` only.

It is **not hardened for network, multi-user, or internet-facing deployment.** For local
convenience it intentionally ships defaults that are unsafe on a shared or public host:

- a default login (`admin@example.com` / `password`),
- a publicly-known development `SECRET_KEY` default,
- the Flask development server (the interactive debugger is off by default and is refused
  outright when binding to a public interface), and
- browsing endpoints that fetch arbitrary user-supplied URLs from the server — this is by
  design, since persona-driven browsing is the tool's purpose.

These are acceptable **only** because the app is reachable from localhost alone. Exposing
it to a network — publishing the container port on `0.0.0.0`, running `--host 0.0.0.0`
outside Docker, or port-forwarding to it — removes that protection and is **not
supported.** Doing so safely requires a dedicated security pass: authentication on all
routes, a real `SECRET_KEY`, a changed admin password, SSRF/URL validation, and transport
security.

## Supported versions

Only the latest release on the default branch receives fixes.

| Version | Supported |
|---------|-----------|
| 1.1.x   | ✅ |
| < 1.1   | ❌ |

## Reporting a vulnerability

Please report security issues **privately** — do not open a public issue for an
undisclosed vulnerability.

- **Preferred:** GitHub private vulnerability reporting — the **"Report a vulnerability"**
  button under the repository's **Security** tab.
  *(Maintainers: enable this under Settings → Security → Reporting if it isn't already.)*
- Include the affected version or commit, clear reproduction steps, and the impact.

Because A-Proxy is a localhost research tool, reports whose only impact requires deploying
it outside the documented local setup (for example, binding to a public interface) are
considered **out of scope** unless they also affect the default localhost configuration.
