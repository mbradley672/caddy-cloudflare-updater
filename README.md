# Caddy Cloudflare DNS Updater

[![Docker Hub](https://img.shields.io/docker/v/mbradley672/caddy-cloudflare-updater?label=Docker%20Hub)](https://hub.docker.com/r/mbradley672/caddy-cloudflare-updater)
[![Build Status](https://github.com/mbradley672/caddy-cloudflare-updater/workflows/Build%20and%20Push%20Docker%20Image/badge.svg)](https://github.com/mbradley672/caddy-cloudflare-updater/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python application that automatically synchronizes domains from your Caddy configuration with Cloudflare DNS records. This tool monitors your Caddyfile and updates corresponding A/AAAA records in Cloudflare to point to your server's public IP address.

## Features

- **Automatic DNS Sync**: Reads domains from your Caddyfile and creates/updates Cloudflare DNS records
- **Dynamic IP Detection**: Automatically detects your server's public IP address
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **File Watching**: Monitor Caddyfile changes and update DNS records automatically
- **IPv4/IPv6 Support**: Handles both A and AAAA records based on IP version

## Prerequisites

- Cloudflare account with API access
- Cloudflare API token with DNS edit permissions
- Python 3.7+ (if running without Docker)
- Docker and Docker Compose (for containerized deployment)

## Installation

### Option 1: Docker Hub (Easiest)

Use the pre-built Docker image from Docker Hub:

```bash
# Pull the image
docker pull mbradley672/caddy-cloudflare-updater:latest

# Run with Docker (Linux/macOS example)
docker run -d \
  --name caddy-dns-updater \
  --restart unless-stopped \
  -e CF_API_TOKEN=your_cloudflare_api_token \
  -e CF_ZONE_ID=your_cloudflare_zone_id \
  -e CF_DOMAIN=yourdomain.com \
  -v /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro \
  mbradley672/caddy-cloudflare-updater:latest

# Windows example (adjust the path as needed)
docker run -d \
  --name caddy-dns-updater \
  --restart unless-stopped \
  -e CF_API_TOKEN=your_cloudflare_api_token \
  -e CF_ZONE_ID=your_cloudflare_zone_id \
  -e CF_DOMAIN=yourdomain.com \
  -v C:\caddy\Caddyfile:/etc/caddy/Caddyfile:ro \
  mbradley672/caddy-cloudflare-updater:latest
```

📖 **See [DOCKER_HUB_README.md](DOCKER_HUB_README.md) for detailed Docker Hub usage instructions**

### Option 2: Build from Source (Docker)

1. Clone this repository:
```bash
git clone https://github.com/yourusername/caddy-cloudflare-updater.git
cd caddy-cloudflare-updater
```

2. Copy the environment file template:
```bash
cp .env.example .env
```

3. Edit `.env` with your Cloudflare credentials:
```env
CF_API_TOKEN=your_cloudflare_api_token
CF_ZONE_ID=your_cloudflare_zone_id
CF_DOMAIN=yourdomain.com
CADDYFILE_PATH=/etc/caddy/Caddyfile
```

4. Choose the appropriate docker-compose file for your system:
   - **Linux/macOS**: Use `docker-compose.linux.yml` 
   - **Windows**: Use `docker-compose.windows.yml`
   - **Generic**: Use `docker-compose.hub.yml`

5. Update the Caddyfile path in your chosen compose file:
```yaml
volumes:
  # Linux/macOS example:
  - /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro
  
  # Windows example:  
  - C:/caddy/Caddyfile:/etc/caddy/Caddyfile:ro
  
  # Same directory:
  - ./Caddyfile:/etc/caddy/Caddyfile:ro
```

6. Run with Docker Compose:
```bash
# Linux/macOS
docker-compose -f docker-compose.linux.yml up -d

# Windows  
docker-compose -f docker-compose.windows.yml up -d
```

### Option 2: Python Virtual Environment

1. Clone and navigate to the repository:
```bash
git clone https://github.com/yourusername/caddy-cloudflare-updater.git
cd caddy-cloudflare-updater
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables or create a `.env` file:
```bash
export CF_API_TOKEN=your_cloudflare_api_token
export CF_ZONE_ID=your_cloudflare_zone_id
export CF_DOMAIN=yourdomain.com
export CADDYFILE_PATH=/path/to/your/Caddyfile
```

5. Run the application:
```bash
python main.py
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `CF_API_TOKEN` | Cloudflare API token with DNS edit permissions | Yes |
| `CF_ZONE_ID` | Cloudflare Zone ID for your domain | Yes |
| `CF_DOMAIN` | Your root domain (e.g., example.com) | Yes |
| `CADDYFILE_PATH` | Path to your Caddyfile | No (default: `/etc/caddy/Caddyfile`) |

### Getting Cloudflare Credentials

1. **API Token**: Go to [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens) and create a token with:
   - Zone permissions: `Zone:Read`, `DNS:Edit`
   - Zone resources: Include your specific zone

2. **Zone ID**: Found in your domain's overview page in the Cloudflare dashboard

## Usage

### One-time Sync
Run the script once to sync current domains:
```bash
python main.py
```

### Continuous Monitoring
Use the watcher script to monitor Caddyfile changes:
```bash
python watcher.py
```

### Scheduled Updates
Use the provided crontab example to run periodic updates:
```bash
# Run every 5 minutes
*/5 * * * * /usr/local/bin/python /path/to/caddy-cloudflare-updater/main.py
```

## How It Works

1. **Domain Extraction**: Parses your Caddyfile to extract all configured domains
2. **IP Detection**: Fetches your server's current public IP address
3. **DNS Comparison**: Compares existing Cloudflare DNS records with Caddyfile domains
4. **Record Management**: Creates new records or updates existing ones to point to your server

## File Structure

```
caddy-cloudflare-updater/
├── main.py              # Main synchronization script
├── watcher.py           # File watcher for automatic updates
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker container configuration
├── docker-compose.yml  # Docker Compose setup
├── .env.example        # Environment variables template
├── crontab.txt         # Example cron configuration
└── README.md           # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Common Issues

1. **Invalid API Token**: Ensure your Cloudflare API token has the correct permissions
2. **Zone ID Mismatch**: Verify the Zone ID matches your domain in Cloudflare
3. **Caddyfile Not Found**: Check that the `CADDYFILE_PATH` points to the correct file
4. **DNS Record Conflicts**: The script will update existing records; ensure this is intended

### Debug Mode

Set environment variable for verbose logging:
```bash
export DEBUG=1
python main.py
```

## Security

- Store your API tokens securely and never commit them to version control
- Use environment variables or secure secret management systems
- Regularly rotate your Cloudflare API tokens
- Limit API token permissions to only what's necessary

## Changelog

### v1.0.0
- Initial release with Docker Hub support
- Basic Caddyfile parsing and Cloudflare DNS sync
- Docker support with multiple run modes
- File watching capabilities
- Comprehensive documentation and examples
- Multi-platform Docker images (AMD64/ARM64)
- GitHub Actions CI/CD pipeline
