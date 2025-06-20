# main.py
import os
import sys
import requests
import logging
import re
from ipaddress import ip_address
from datetime import datetime

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/caddy-updater.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_caddyfile(content):
    """Simple Caddyfile parser to extract domain names"""
    domains = set()
    
    # Remove comments
    lines = []
    for line in content.split('\n'):
        # Remove comments (everything after #)
        line = line.split('#')[0].strip()
        if line:
            lines.append(line)
    
    # Join lines and split by blocks
    content = ' '.join(lines)
    
    # Extract domains using regex patterns
    # Pattern 1: domain.com { ... }
    domain_blocks = re.findall(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s*\{', content)
    domains.update(domain_blocks)
    
    # Pattern 2: *.domain.com or subdomain.domain.com
    wildcard_domains = re.findall(r'(\*\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', content)
    for wildcard, domain in wildcard_domains:
        if not wildcard:  # Skip wildcards for now, add the domain
            domains.add(domain)
    
    # Pattern 3: Simple domain at start of line
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('{') and not line.startswith('}'):
            # Check if line starts with a domain
            domain_match = re.match(r'^([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
            if domain_match:
                domains.add(domain_match.group(1))
    
    # Filter out common false positives
    filtered_domains = set()
    for domain in domains:
        # Skip localhost, example domains, and IP addresses
        if (not domain.startswith('localhost') and 
            not domain.startswith('example.') and
            not domain.startswith('test.') and
            not re.match(r'^\d+\.\d+\.\d+\.\d+', domain)):
            filtered_domains.add(domain)
    
    return [{"keys": list(filtered_domains)}] if filtered_domains else []

def get_public_ip():
    """Get the server's public IP address"""
    try:
        response = requests.get("https://api.ipify.org", timeout=10)
        response.raise_for_status()
        ip = response.text.strip()
        logger.info(f"Detected public IP: {ip}")
        return ip
    except requests.RequestException as e:
        logger.error(f"Failed to get public IP: {e}")
        raise

def get_caddy_domains(file_path):
    """Extract domains from Caddyfile"""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Caddyfile not found at {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        config = parse_caddyfile(content)
        
        domains = set()
        for block in config:
            if "keys" in block:
                domains.update(block["keys"])
        
        logger.info(f"Found {len(domains)} domains in Caddyfile: {', '.join(sorted(domains))}")
        return domains
    except Exception as e:
        logger.error(f"Failed to parse Caddyfile: {e}")
        raise

def sync_to_cloudflare(subdomains, ip):
    """Sync domains to Cloudflare DNS"""
    token = os.getenv("CF_API_TOKEN")
    zone = os.getenv("CF_ZONE_ID")
    root_domain = os.getenv("CF_DOMAIN")

    if not all([token, zone, root_domain]):
        raise ValueError("Missing required Cloudflare environment variables")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        # Get existing DNS records
        logger.info(f"Fetching existing DNS records for zone {zone}")
        r = requests.get(
            f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records", 
            headers=headers,
            timeout=30
        )
        r.raise_for_status()
        records = r.json()["result"]
        existing = {r["name"]: r for r in records if r["type"] in ("A", "AAAA")}
        logger.info(f"Found {len(existing)} existing DNS records")

        # Process each domain
        for domain in subdomains:
            fqdn = domain if "." in domain else f"{domain}.{root_domain}"
            record_type = "A" if ip_address(ip).version == 4 else "AAAA"
            
            data = {
                "type": record_type,
                "name": fqdn,
                "content": ip,
                "ttl": 300,
                "proxied": False
            }

            if fqdn in existing:
                # Update existing record
                rec_id = existing[fqdn]["id"]
                current_ip = existing[fqdn]["content"]
                
                if current_ip == ip:
                    logger.info(f"DNS record for {fqdn} is already up to date ({ip})")
                    continue
                
                logger.info(f"Updating DNS record for {fqdn}: {current_ip} -> {ip}")
                response = requests.put(
                    f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records/{rec_id}", 
                    headers=headers, 
                    json=data,
                    timeout=30
                )
                response.raise_for_status()
                logger.info(f"Successfully updated {fqdn}")
            else:
                # Create new record
                logger.info(f"Creating new DNS record for {fqdn} -> {ip}")
                response = requests.post(
                    f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records", 
                    headers=headers, 
                    json=data,
                    timeout=30
                )
                response.raise_for_status()
                logger.info(f"Successfully created {fqdn}")
                
    except requests.RequestException as e:
        logger.error(f"Cloudflare API request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to sync to Cloudflare: {e}")
        raise

def run_sync():
    """Main synchronization function"""
    try:
        logger.info("=== Starting DNS synchronization ===")
        
        # Get current public IP
        ip = get_public_ip()
        
        # Get domains from Caddyfile
        caddyfile_path = os.getenv("CADDYFILE_PATH", "/etc/caddy/Caddyfile")
        domains = get_caddy_domains(caddyfile_path)
        
        if not domains:
            logger.warning("No domains found in Caddyfile")
            return
        
        # Sync to Cloudflare
        sync_to_cloudflare(domains, ip)
        
        logger.info("=== DNS synchronization completed successfully ===")
        
    except Exception as e:
        logger.error(f"DNS synchronization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_sync()
