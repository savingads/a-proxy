# Proxy & Geo-IP Setup

A-Proxy supports optional SOCKS5/HTTP proxies to simulate geographic location for personas. This allows capturing web content as it appears to users in different regions -- no VPN software required.

## Purpose

Geographic location affects web content through:

- GeoIP-based content localization
- Regional pricing and availability
- Language and locale defaults
- Legal/regulatory content restrictions
- Targeted advertising based on location

Proxy-based geo-IP shifting enables researchers to capture these variations systematically.

## How It Works

A-Proxy uses Playwright's built-in per-context proxy support. Each browser context (i.e., each persona browsing session) can route traffic through a different proxy, providing isolated geo-IP shifting without any system-wide VPN configuration.

```
Persona A (US proxy) ──> Playwright Context ──> SOCKS5 proxy ──> US exit IP
Persona B (DE proxy) ──> Playwright Context ──> SOCKS5 proxy ──> DE exit IP
Persona C (no proxy) ──> Playwright Context ──> Direct connection
```

## Configuration

### Default Proxy (Environment Variable)

Set a default proxy for all sessions in `.env`:

```bash
PROXY_URL=socks5://user:pass@host:port
```

This proxy is used when no per-session override is set.

### Per-Session Proxy (Web UI)

Override the default proxy for your current session:

1. Open the A-Proxy dashboard
2. Find the **Proxy Settings** section
3. Enter a proxy URL (e.g., `socks5://host:port`)
4. Click **Set Proxy**

To clear the session proxy and revert to the default:

1. Click **Clear Proxy**

### No Proxy

A-Proxy works without any proxy configured. Browsing will use your direct internet connection.

## Proxy Types

| Protocol | Example | Notes |
|----------|---------|-------|
| SOCKS5 | `socks5://host:1080` | Recommended, supports UDP |
| SOCKS5 with auth | `socks5://user:pass@host:1080` | Authenticated SOCKS5 |
| HTTP | `http://host:8080` | HTTP proxy |
| HTTPS | `https://host:8080` | HTTPS proxy |

## Checking Connection Status

### Network Status Page

The dashboard shows:

| Info | Description |
|------|-------------|
| Proxy Configured | Whether a proxy URL is active |
| Current IP | Your apparent IP address |
| Location | GeoIP-detected city/region/country |
| ISP/Org | Network organization |

### Verification

To verify your proxy is working:

1. Check the IP info displayed on the dashboard
2. Confirm the location matches your intended region
3. Visit a GeoIP detection site through the browse-as-persona feature

## Regional Coverage

A-Proxy includes a built-in region selector with pre-configured geolocation, language, and timezone for 16 regions:

| Region | Language | Timezone |
|--------|----------|----------|
| United States | en-US | America/New_York |
| United Kingdom | en-GB | Europe/London |
| Germany | de-DE | Europe/Berlin |
| France | fr-FR | Europe/Paris |
| Japan | ja-JP | Asia/Tokyo |
| Brazil | pt-BR | America/Sao_Paulo |
| ... | ... | ... |

Selecting a region auto-populates the browser context with the correct locale, geolocation coordinates, and timezone -- independent of proxy configuration.

## Proxy Providers

You can use any SOCKS5/HTTP proxy service. Some options:

- **Residential proxy services** (Bright Data, Oxylabs, SmartProxy) for realistic geo-IP
- **Datacenter proxies** for speed and cost
- **SSH tunnels** (`ssh -D 1080 user@remote-host` creates a local SOCKS5 proxy)
- **Self-hosted** proxies on cloud instances in target regions

## Limitations

### Geographic Precision

- Proxy exits at datacenter/city level, not precise location
- Some services detect proxy/datacenter traffic
- Playwright's geolocation emulation provides precise coordinates to the browser regardless of actual IP

### Detection

Some websites detect and block proxy traffic:

- Check if target sites work through your proxy
- Document any access restrictions
- Consider this limitation in research design

## Troubleshooting

### Pages Not Loading Through Proxy

1. Verify the proxy URL is correct and the proxy server is running
2. Test the proxy independently: `curl -x socks5://host:port https://ipinfo.io`
3. Try without proxy to isolate the issue
4. Check firewall rules

### Wrong Region Detected

1. Verify the proxy is active (check dashboard IP info)
2. Some sites use additional detection beyond GeoIP
3. Browser geolocation emulation is separate from IP-based geolocation

### Slow Performance

1. Try a proxy server closer to the target region
2. Use SOCKS5 instead of HTTP proxy
3. Check proxy server load

## Related Guides

- [Browse as Persona](browse-as-persona.md) - Using proxy during browsing
- [Installation](../getting-started/installation.md) - Proxy setup during install
- [Persona Model](../concepts/persona-model.md) - Geographic attributes
