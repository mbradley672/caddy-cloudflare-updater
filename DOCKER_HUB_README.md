# Caddy Cloudflare DNS Updater

Automatically synchronize domains from your Caddy web server configuration with Cloudflare DNS records. This lightweight Docker container monitors your Caddyfile and ensures your DNS A/AAAA records always point to your server's current public IP address.

[![Docker Image Version](https://img.shields.io/docker/v/mbradley672/caddy-cloudflare-updater?sort=semver)](https://hub.docker.com/r/mbradley672/caddy-cloudflare-updater)
[![Docker Image Size](https://img.shields.io/docker/image-size/mbradley672/caddy-cloudflare-updater/latest)](https://hub.docker.com/r/mbradley672/caddy-cloudflare-updater)
[![Docker Pulls](https://img.shields.io/docker/pulls/mbradley672/caddy-cloudflare-updater)](https://hub.docker.com/r/mbradley672/caddy-cloudflare-updater)
[![Build Status](https://github.com/mbradley672/caddy-cloudflare-updater/workflows/Build%20and%20Push%20Docker%20Image/badge.svg)](https://github.com/mbradley672/caddy-cloudflare-updater/actions)

## 🚀 Quick Start

Pull and run the pre-built image from Docker Hub:

```bash
docker pull mbradley672/caddy-cloudflare-updater:latest
```

## ✨ Key Features

- **🔄 Automatic DNS Sync**: Reads domains from Caddyfile and updates Cloudflare DNS records
- **📡 Dynamic IP Detection**: Automatically detects your server's current public IP address
- **👁️ Real-time Monitoring**: Watches Caddyfile for changes and updates DNS immediately
- **⏰ Scheduled Updates**: Optional cron-based periodic synchronization (every 10 minutes)
- **🌐 IPv4/IPv6 Support**: Handles both A and AAAA DNS records automatically
- **📊 Comprehensive Logging**: Detailed logs with configurable verbosity levels
- **🏗️ Multi-Architecture**: Native support for AMD64 and ARM64 platforms
- **🔒 Secure**: API tokens via environment variables, read-only file mounts

## 🎯 Perfect For

- **Home Labs**: Keep your self-hosted services accessible with dynamic IPs
- **Small Businesses**: Automate DNS management for web services  
- **Developers**: Seamless integration with Caddy reverse proxy setups
- **Remote Workers**: Maintain access to home services from anywhere

## 🐳 Installation & Usage

### Method 1: Docker Run (Simple)

**Basic Usage:**
```bash
docker run -d \
  --name caddy-dns-updater \
  --restart unless-stopped \
  -e CF_API_TOKEN=your_cloudflare_api_token \
  -e CF_ZONE_ID=your_cloudflare_zone_id \
  -e CF_DOMAIN=example.com \
  -e RUN_MODE=watcher \
  -v /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro \
  -v ./logs:/var/log \
  mbradley672/caddy-cloudflare-updater:latest
```

**Platform-Specific Examples:**

**Linux/macOS:**
```bash
docker run -d \
  --name caddy-dns-updater \
  --restart unless-stopped \
  -e CF_API_TOKEN=your_cloudflare_api_token \
  -e CF_ZONE_ID=your_cloudflare_zone_id \
  -e CF_DOMAIN=example.com \
  -e RUN_MODE=watcher \
  -v /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro \
  -v ./logs:/var/log \
  mbradley672/caddy-cloudflare-updater:latest
```

**Windows (PowerShell):**
```powershell
docker run -d `
  --name caddy-dns-updater `
  --restart unless-stopped `
  -e CF_API_TOKEN=your_cloudflare_api_token `
  -e CF_ZONE_ID=your_cloudflare_zone_id `
  -e CF_DOMAIN=example.com `
  -e RUN_MODE=watcher `
  -v C:\caddy\Caddyfile:/etc/caddy/Caddyfile:ro `
  -v ${PWD}\logs:/var/log `
  mbradley672/caddy-cloudflare-updater:latest
```

**Windows (Command Prompt):**
```cmd
docker run -d ^
  --name caddy-dns-updater ^
  --restart unless-stopped ^
  -e CF_API_TOKEN=your_cloudflare_api_token ^
  -e CF_ZONE_ID=your_cloudflare_zone_id ^
  -e CF_DOMAIN=example.com ^
  -e RUN_MODE=watcher ^
  -v C:\caddy\Caddyfile:/etc/caddy/Caddyfile:ro ^
  -v %CD%\logs:/var/log ^
  mbradley672/caddy-cloudflare-updater:latest
```

### Method 2: Docker Compose (Recommended)

1. Create a `.env` file:
```env
CF_API_TOKEN=your_cloudflare_api_token
CF_ZONE_ID=your_cloudflare_zone_id
CF_DOMAIN=yourdomain.com
```

2. Create a `docker-compose.yml`:
```yaml
version: "3.9"
services:
  caddy-dns-updater:
    image: mbradley672/caddy-cloudflare-updater:latest
    container_name: caddy-dns-updater
    restart: unless-stopped
    env_file: .env
    environment:
      - CADDYFILE_PATH=/etc/caddy/Caddyfile
      - LOG_LEVEL=INFO
      - RUN_MODE=hybrid
    volumes:
      # CHANGE THIS: Update the path to your actual Caddyfile location
      # Linux/macOS: /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro
      # Windows: C:/caddy/Caddyfile:/etc/caddy/Caddyfile:ro
      # Custom path: /home/user/mycaddy/Caddyfile:/etc/caddy/Caddyfile:ro
      - /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro
      - ./logs:/var/log
```

3. Run:
```bash
docker-compose up -d
```

## 🔧 Run Modes

Choose the mode that best fits your needs:

| Mode | Description | Use Case |
|------|-------------|----------|
| `watcher` | Monitor Caddyfile for changes (default) | Development, frequent config changes |
| `cron` | Scheduled updates every 10 minutes | Production, stable configurations |
| `hybrid` | Both file watching + scheduled updates | Best of both worlds (recommended) |
| `once` | One-time sync and exit | Testing, manual updates |

## 📋 Configuration

### Required Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `CF_API_TOKEN` | Cloudflare API token with DNS edit permissions | `abc123...` |
| `CF_ZONE_ID` | Cloudflare Zone ID for your domain | `def456...` |
| `CF_DOMAIN` | Your root domain name | `example.com` |

### Optional Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `RUN_MODE` | `watcher` | Run mode: `watcher`/`cron`/`hybrid`/`once` |
| `LOG_LEVEL` | `INFO` | Logging level: `DEBUG`/`INFO`/`WARNING`/`ERROR` |
| `CADDYFILE_PATH` | `/etc/caddy/Caddyfile` | Path to Caddyfile inside container |

## 🛠️ Setup Guide

### 1. Get Cloudflare Credentials

1. **API Token**: Go to [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens)
   - Create token with `Zone:Read` and `DNS:Edit` permissions
   - Choose your specific zone for security
2. **Zone ID**: Found in your domain's overview page in Cloudflare dashboard

### 2. Locate Your Caddyfile

### 2. Locate Your Caddyfile

#### Common Caddyfile Locations

| System | Typical Location | Docker Mount Example |
|--------|------------------|---------------------|
| **Linux (systemd)** | `/etc/caddy/Caddyfile` | `-v /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro` |
| **Linux (manual)** | `/opt/caddy/Caddyfile` | `-v /opt/caddy/Caddyfile:/etc/caddy/Caddyfile:ro` |
| **macOS (Homebrew)** | `/opt/homebrew/etc/Caddyfile` | `-v /opt/homebrew/etc/Caddyfile:/etc/caddy/Caddyfile:ro` |
| **Windows** | `C:\caddy\Caddyfile` | `-v C:\caddy\Caddyfile:/etc/caddy/Caddyfile:ro` |
| **Docker Compose** | `./Caddyfile` | `-v ./Caddyfile:/etc/caddy/Caddyfile:ro` |
| **Custom location** | `/home/user/config/Caddyfile` | `-v /home/user/config/Caddyfile:/etc/caddy/Caddyfile:ro` |

💡 **Tip**: Use `find / -name "Caddyfile" 2>/dev/null` on Linux/macOS to locate your Caddyfile

### 3. Create Environment File

```bash
# .env
CF_API_TOKEN=your_cloudflare_api_token_here
CF_ZONE_ID=your_cloudflare_zone_id_here
CF_DOMAIN=yourdomain.com
```

### 4. Run the Container

Choose your preferred method from the examples above!

## Examples

### One-time Sync
```bash
# Linux/macOS
docker run --rm \
  -e CF_API_TOKEN=your_token \
  -e CF_ZONE_ID=your_zone_id \
  -e CF_DOMAIN=example.com \
  -e RUN_MODE=once \
  -v /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro \
  mbradley672/caddy-cloudflare-updater:latest

# Windows
docker run --rm \
  -e CF_API_TOKEN=your_token \
  -e CF_ZONE_ID=your_zone_id \
  -e CF_DOMAIN=example.com \
  -e RUN_MODE=once \
  -v C:\caddy\Caddyfile:/etc/caddy/Caddyfile:ro \
  mbradley672/caddy-cloudflare-updater:latest
```

### Production Setup (Hybrid Mode)
```bash
# Linux/macOS
docker run -d \
  --name caddy-dns-updater \
  --restart unless-stopped \
  -e CF_API_TOKEN=your_token \
  -e CF_ZONE_ID=your_zone_id \
  -e CF_DOMAIN=example.com \
  -e RUN_MODE=hybrid \
  -e LOG_LEVEL=INFO \
  -v /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro \
  -v /var/log/caddy-updater:/var/log \
  mbradley672/caddy-cloudflare-updater:latest

# Windows
docker run -d \
  --name caddy-dns-updater \
  --restart unless-stopped \
  -e CF_API_TOKEN=your_token \
  -e CF_ZONE_ID=your_zone_id \
  -e CF_DOMAIN=example.com \
  -e RUN_MODE=hybrid \
  -e LOG_LEVEL=INFO \
  -v C:\caddy\Caddyfile:/etc/caddy/Caddyfile:ro \
  -v C:\logs\caddy-updater:/var/log \
  mbradley672/caddy-cloudflare-updater:latest
```

### With Custom Caddyfile Location
```bash
# Homebrew macOS installation
docker run -d \
  --name caddy-dns-updater \
  -e CF_API_TOKEN=your_token \
  -e CF_ZONE_ID=your_zone_id \
  -e CF_DOMAIN=example.com \
  -v /opt/homebrew/etc/Caddyfile:/etc/caddy/Caddyfile:ro \
  mbradley672/caddy-cloudflare-updater:latest

# Custom user directory
docker run -d \
  --name caddy-dns-updater \
  -e CF_API_TOKEN=your_token \
  -e CF_ZONE_ID=your_zone_id \
  -e CF_DOMAIN=example.com \
  -e CADDYFILE_PATH=/custom/path/Caddyfile \
  -v /home/user/caddy-config/Caddyfile:/custom/path/Caddyfile:ro \
  mbradley672/caddy-cloudflare-updater:latest

# Docker Compose with Caddy
docker run -d \
  --name caddy-dns-updater \
  --network caddy_network \
  -e CF_API_TOKEN=your_token \
  -e CF_ZONE_ID=your_zone_id \
  -e CF_DOMAIN=example.com \
  -v caddy_config:/etc/caddy/Caddyfile:ro \
  mbradley672/caddy-cloudflare-updater:latest
```

## 📊 Monitoring & Logs

### View Logs
```bash
# Follow logs in real-time
docker logs -f caddy-dns-updater

# View recent logs
docker logs --tail 50 caddy-dns-updater

# If you mounted the log directory
tail -f ./logs/caddy-updater.log
```

### Health Check
```bash
# Check if container is running
docker ps | grep caddy-dns-updater

# Test configuration (one-time run)
docker run --rm \
  -e CF_API_TOKEN=your_token \
  -e CF_ZONE_ID=your_zone_id \
  -e CF_DOMAIN=example.com \
  -e RUN_MODE=once \
  -e LOG_LEVEL=DEBUG \
  -v /path/to/Caddyfile:/etc/caddy/Caddyfile:ro \
  mbradley672/caddy-cloudflare-updater:latest
```

## Troubleshooting

### Common Issues

1. **Caddyfile Not Found**
   ```bash
   # Find your Caddyfile location (Linux/macOS)
   find / -name "Caddyfile" 2>/dev/null
   
   # Check if file exists and is readable
   ls -la /path/to/your/Caddyfile
   
   # Windows - search for Caddyfile
   Get-ChildItem -Path C:\ -Name "Caddyfile" -Recurse -ErrorAction SilentlyContinue
   ```

2. **Permission Denied for Caddyfile**
   ```bash
   # Make sure the file is readable
   chmod 644 /path/to/Caddyfile
   
   # Check file permissions
   ls -la /path/to/Caddyfile
   ```

3. **Windows Path Issues**
   ```bash
   # Use forward slashes or escape backslashes
   # Good: C:/caddy/Caddyfile:/etc/caddy/Caddyfile:ro
   # Good: C:\\caddy\\Caddyfile:/etc/caddy/Caddyfile:ro
   # Bad:  C:\caddy\Caddyfile:/etc/caddy/Caddyfile:ro
   ```

4. **Invalid API Token**
   ```bash
   # Test your token
   curl -X GET "https://api.cloudflare.com/client/v4/user" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

5. **Container Exits Immediately**
   ```bash
   # Check logs for errors
   docker logs caddy-dns-updater
   
   # Run in foreground to see errors
   docker run --rm \
     -e CF_API_TOKEN=your_token \
     -e CF_ZONE_ID=your_zone_id \
     -e CF_DOMAIN=example.com \
     -e RUN_MODE=once \
     -v /path/to/Caddyfile:/etc/caddy/Caddyfile:ro \
     mbradley672/caddy-cloudflare-updater:latest
   ```

6. **No Domains Found**
   ```bash
   # Verify Caddyfile is mounted correctly
   docker exec caddy-dns-updater cat /etc/caddy/Caddyfile
     # Check Caddyfile syntax and domains
   docker exec caddy-dns-updater python -c "
   import sys
   sys.path.append('/app')
   from main import get_caddy_domains
   try:
       domains = get_caddy_domains('/etc/caddy/Caddyfile')
       print(f'Found domains: {domains}')
   except Exception as e:
       print(f'Error: {e}')
   "
   ```

### Debug Mode
```bash
docker run --rm \
  -e CF_API_TOKEN=your_token \
  -e CF_ZONE_ID=your_zone_id \
  -e CF_DOMAIN=example.com \
  -e LOG_LEVEL=DEBUG \
  -e RUN_MODE=once \
  -v /path/to/Caddyfile:/etc/caddy/Caddyfile:ro \
  mbradley672/caddy-cloudflare-updater:latest
```

## 🏷️ Image Tags & Architecture

- **`latest`** - Latest stable release
- **`v1.x.x`** - Specific version releases  
- **`master`** - Latest development build

All images support multiple architectures:
- `linux/amd64` - Intel/AMD 64-bit
- `linux/arm64` - ARM 64-bit (Raspberry Pi 4, Apple Silicon, etc.)

## 🔒 Security Best Practices

1. **Use Environment Files**: Store secrets in `.env` files, not in compose files
2. **Read-only Mounts**: Mount Caddyfile as read-only (`:ro`)
3. **Least Privilege**: Use Cloudflare API tokens with minimal required permissions
4. **Regular Updates**: Keep the Docker image updated
5. **Log Monitoring**: Monitor logs for failed API calls or errors

## 📚 Documentation & Support

- **📖 Full Documentation**: [GitHub Repository](https://github.com/mbradley672/caddy-cloudflare-updater)
- **🐛 Issues & Feature Requests**: [GitHub Issues](https://github.com/mbradley672/caddy-cloudflare-updater/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/mbradley672/caddy-cloudflare-updater/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/mbradley672/caddy-cloudflare-updater/blob/master/LICENSE) file for details.

---

⭐ **Found this useful?** Please star the [GitHub repository](https://github.com/mbradley672/caddy-cloudflare-updater) to help others discover it!
