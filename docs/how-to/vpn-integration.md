# VPN Integration

A-Proxy supports VPN integration to simulate geographic location for personas. This allows capturing web content as it appears to users in different regions.

## Purpose

Geographic location affects web content through:

- GeoIP-based content localization
- Regional pricing and availability
- Language and locale defaults
- Legal/regulatory content restrictions
- Targeted advertising based on location

VPN integration enables researchers to capture these variations systematically.

## Supported VPN

A-Proxy currently supports NordVPN through OpenVPN configuration files.

## Setup

### Prerequisites

1. Active NordVPN subscription
2. OpenVPN configuration files
3. Docker environment (recommended)

### Configuration Steps

#### 1. Create Credentials File

```bash
mkdir -p nordvpn
echo "your_nordvpn_username" > nordvpn/auth.txt
echo "your_nordvpn_password" >> nordvpn/auth.txt
chmod 600 nordvpn/auth.txt
```

#### 2. Download OpenVPN Configurations

1. Visit [NordVPN OpenVPN Configuration](https://nordvpn.com/ovpn/)
2. Download configuration files for target regions
3. Place UDP files in `nordvpn/ovpn_udp/`
4. Place TCP files in `nordvpn/ovpn_tcp/`

#### 3. Directory Structure

```
nordvpn/
├── auth.txt
├── ovpn_udp/
│   ├── us1234.nordvpn.com.udp.ovpn
│   ├── de5678.nordvpn.com.udp.ovpn
│   └── ...
└── ovpn_tcp/
    ├── us1234.nordvpn.com.tcp.ovpn
    └── ...
```

## Using VPN with Personas

### Automatic Server Selection

When a persona has geographic attributes set:

1. System identifies target country/region
2. Selects appropriate VPN server
3. Establishes connection before browsing

### Manual Server Selection

Override automatic selection:

1. Navigate to **Settings**
2. Select **VPN Configuration**
3. Choose specific server
4. Apply to current session

## Connection Status

### Indicators

The interface displays:

| Status | Meaning |
|--------|---------|
| Connected | VPN active, traffic routed through exit node |
| Connecting | Establishing VPN tunnel |
| Disconnected | Direct connection, no VPN |
| Error | Connection failed |

### Verification

Verify VPN is working:

1. Check displayed exit IP region
2. Visit a GeoIP detection site
3. Confirm location matches persona configuration

## Protocol Selection

### UDP (Recommended)

- Lower latency
- Better for browsing
- May be blocked on some networks

### TCP

- More reliable through firewalls
- Higher latency
- Use when UDP fails

## Regional Coverage

NordVPN provides servers in 60+ countries. Common research regions:

| Region | Server Count | Use Case |
|--------|--------------|----------|
| United States | 1900+ | US-specific content |
| Germany | 240+ | EU/GDPR context |
| United Kingdom | 440+ | UK-specific content |
| Japan | 130+ | Asian market content |
| Australia | 190+ | APAC content |

## Limitations

### Geographic Precision

- VPN exits at city level, not precise location
- Some services detect VPN usage
- Latitude/longitude in persona may not match VPN exit exactly

### Detection Avoidance

Some websites detect and block VPN traffic:

- Check if target sites block VPN
- Document any access restrictions
- Consider this limitation in research design

### Connection Stability

- VPN connections may drop
- Implement reconnection handling
- Monitor connection status during extended sessions

## Security Considerations

### Credential Storage

- Credentials stored in plain text in `auth.txt`
- Secure the `nordvpn/` directory with appropriate permissions
- Do not commit credentials to version control

### Network Isolation

In Docker deployment:

- VPN runs within container
- Host network is not affected
- Container isolation provides security boundary

## Troubleshooting

### Connection Fails

1. Verify credentials in `auth.txt`
2. Check OpenVPN configuration file validity
3. Try TCP if UDP fails
4. Check network firewall rules

### Wrong Region Detected

1. Verify VPN is connected (not just started)
2. Check the specific server configuration
3. Some sites use additional detection methods

### Slow Performance

1. Try servers closer to target region
2. Switch from TCP to UDP
3. Select less loaded servers

## Alternative Approaches

For regions without VPN coverage or when VPN is detected:

- Proxy servers (requires additional configuration)
- Cloud instances in target regions
- Tor network (limited geographic targeting)

## Related Guides

- [Browse as Persona](browse-as-persona.md) - Using VPN during browsing
- [Installation](../getting-started/installation.md) - VPN setup during install
- [Persona Model](../concepts/persona-model.md) - Geographic attributes
