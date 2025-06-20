# Docker Hub Usage Guide

## Quick Start with Docker Hub

Pull and run the pre-built image from Docker Hub:

```bash
docker pull mbradley672/caddy-cloudflare-updater:latest
```

### Method 1: Docker Run (Simple)

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
CF_DOMAIN=example.com
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
      - RUN_MODE=watcher
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

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CF_API_TOKEN` | ✅ Yes | - | Cloudflare API token with DNS edit permissions |
| `CF_ZONE_ID` | ✅ Yes | - | Cloudflare Zone ID for your domain |
| `CF_DOMAIN` | ✅ Yes | - | Your root domain (e.g., example.com) |
| `CADDYFILE_PATH` | ❌ No | `/etc/caddy/Caddyfile` | Path to your Caddyfile inside the container |
| `LOG_LEVEL` | ❌ No | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR |
| `RUN_MODE` | ❌ No | `watcher` | Run mode: `once`, `watcher`, `cron`, `hybrid` |

### Run Modes

- **`once`**: Run DNS sync once and exit
- **`watcher`**: Watch Caddyfile for changes and sync automatically 
- **`cron`**: Run on schedule (every 10 minutes by default)
- **`hybrid`**: Both cron and watcher (recommended for production)

### Volume Mounts

- **Caddyfile**: Mount your Caddyfile to `/etc/caddy/Caddyfile:ro` (read-only)
- **Logs**: Optionally mount `/var/log` to persist logs on the host

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

## Monitoring and Logs

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

# Check last sync status
docker exec caddy-dns-updater tail -n 20 /var/log/caddy-updater.log
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

## Security Best Practices

1. **Use Environment Files**: Store secrets in `.env` files, not in compose files
2. **Read-only Mounts**: Mount Caddyfile as read-only (`:ro`)
3. **Least Privilege**: Use Cloudflare API tokens with minimal required permissions
4. **Regular Updates**: Keep the Docker image updated
5. **Log Monitoring**: Monitor logs for failed API calls or errors

## Support

For issues, feature requests, or contributions, visit:
https://github.com/mbradley672/caddy-cloudflare-updater
