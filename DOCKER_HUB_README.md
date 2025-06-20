# Docker Hub Usage Guide

## Quick Start with Docker Hub

Pull and run the pre-built image from Docker Hub:

```bash
docker pull mbradley672/caddy-cloudflare-updater:latest
```

### Method 1: Docker Run (Simple)

```bash
docker run -d \
  --name caddy-dns-updater \
  --restart unless-stopped \
  -e CF_API_TOKEN=your_cloudflare_api_token \
  -e CF_ZONE_ID=your_cloudflare_zone_id \
  -e CF_DOMAIN=example.com \
  -e RUN_MODE=watcher \
  -v /path/to/your/Caddyfile:/etc/caddy/Caddyfile:ro \
  -v ./logs:/var/log \
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
      - /path/to/your/Caddyfile:/etc/caddy/Caddyfile:ro
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

## Examples

### One-time Sync
```bash
docker run --rm \
  -e CF_API_TOKEN=your_token \
  -e CF_ZONE_ID=your_zone_id \
  -e CF_DOMAIN=example.com \
  -e RUN_MODE=once \
  -v /path/to/Caddyfile:/etc/caddy/Caddyfile:ro \
  mbradley672/caddy-cloudflare-updater:latest
```

### Production Setup (Hybrid Mode)
```bash
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
```

### With Custom Caddyfile Location
```bash
docker run -d \
  --name caddy-dns-updater \
  -e CF_API_TOKEN=your_token \
  -e CF_ZONE_ID=your_zone_id \
  -e CF_DOMAIN=example.com \
  -e CADDYFILE_PATH=/custom/path/Caddyfile \
  -v /home/user/my-caddyfile:/custom/path/Caddyfile:ro \
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

1. **Permission Denied for Caddyfile**
   ```bash
   # Make sure the file is readable
   chmod 644 /path/to/Caddyfile
   ```

2. **Invalid API Token**
   ```bash
   # Test your token
   curl -X GET "https://api.cloudflare.com/client/v4/user" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **Container Exits Immediately**
   ```bash
   # Check logs for errors
   docker logs caddy-dns-updater
   ```

4. **No Domains Found**
   - Verify your Caddyfile syntax
   - Check if the Caddyfile path is correct inside the container

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
