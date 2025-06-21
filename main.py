#!/usr/bin/env python3
"""
Caddy Cloudflare DNS Updater
Automatically sync domains from Caddyfile to Cloudflare DNS records
"""

import os
import re
import logging
import requests
from ipaddress import ip_address

try:
    from version import __version__
except ImportError:
    __version__ = "unknown"

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_caddyfile(content):
    """Simple Caddyfile parser to extract domain names"""
    domains = set()
    
    # Remove comments and clean content
    lines = []
    for line in content.split('\n'):
        # Remove comments (everything after #)
        line = line.split('#')[0].strip()
        if line:
            lines.append(line)
    
    # Process line by line to find domain blocks
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines, directives, and block delimiters
        if (not line or 
            line.startswith('{') or 
            line.startswith('}') or
            line.startswith('import') or
            line.startswith('log') or
            line.startswith('tls') or
            line.startswith('reverse_proxy') or
            line.startswith('file_server') or
            line.startswith('root') or
            line.startswith('header') or
            line.startswith('encode') or
            line.startswith('redir') or
            line.startswith('handle') or
            line.startswith('route') or
            line.startswith('respond') or
            line.startswith('rewrite') or
            line.startswith('uri') or
            line.startswith('try_files') or
            line.startswith('@') or  # matchers
            '=' in line):  # variable assignments
            i += 1
            continue
        
        # Look for domain patterns at the start of blocks
        # Pattern: domain.com {
        domain_block_match = re.match(r'^([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s*\{', line)
        if domain_block_match:
            domain = domain_block_match.group(1)
            if is_valid_domain(domain):
                domains.add(domain)
            i += 1
            continue
        
        # Pattern: domain1.com, domain2.com {
        multi_domain_match = re.match(r'^([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\s*,\s*[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})*)\s*\{', line)
        if multi_domain_match:
            domain_list = multi_domain_match.group(1)
            for domain in domain_list.split(','):
                domain = domain.strip()
                if is_valid_domain(domain):
                    domains.add(domain)
            i += 1
            continue
        
        # Pattern: standalone domain (followed by opening brace on next line)
        if (i + 1 < len(lines) and 
            lines[i + 1].strip() == '{' and
            re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', line)):
            if is_valid_domain(line):
                domains.add(line)
            i += 1
            continue
        
        # Pattern: multiple domains on one line followed by brace
        domain_list_match = re.match(r'^([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\s*,\s*[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})*)$', line)
        if (domain_list_match and 
            i + 1 < len(lines) and 
            lines[i + 1].strip() == '{'):
            domain_list = domain_list_match.group(1)
            for domain in domain_list.split(','):
                domain = domain.strip()
                if is_valid_domain(domain):
                    domains.add(domain)
            i += 1
            continue
        
        i += 1
    
    return list(domains)

def is_valid_domain(domain):
    """Validate if a string is a valid domain name"""
    if not domain:
        return False
    
    # Reject domains that start with a dot (like .beavis.tech)
    if domain.startswith('.'):
        return False
    
    # Remove trailing dots
    domain = domain.rstrip('.')
    
    # Basic validation
    if (len(domain) < 4 or  # minimum: a.co
        len(domain) > 253 or  # maximum domain length
        domain.startswith('-') or
        domain.endswith('-') or
        '..' in domain or
        domain.startswith('localhost') or
        domain.startswith('example.') or
        domain.startswith('test.') or
        domain.endswith('.key') or
        domain.endswith('.pem') or
        domain.endswith('.crt') or
        domain.endswith('.cert') or
        domain.endswith('.p12') or
        domain.endswith('.pfx') or
        'env.' in domain.lower() or
        'cloudflare' in domain.lower() and not domain.endswith('.com')):
        return False
    
    # Check if it's an IP address
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain):
        return False
    
    # Must contain at least one dot and have valid TLD
    parts = domain.split('.')
    if len(parts) < 2:
        return False
    
    # TLD should be at least 2 characters and only letters
    tld = parts[-1]
    if len(tld) < 2 or not tld.isalpha():
        return False
    
    # Each part should be valid
    for part in parts:
        if (not part or 
            len(part) > 63 or
            part.startswith('-') or
            part.endswith('-') or
            not re.match(r'^[a-zA-Z0-9-]+$', part)):
            return False
    
    return True

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
        
        domains = parse_caddyfile(content)
        
        if domains:
            logger.info(f"Found {len(domains)} valid domains in Caddyfile: {', '.join(sorted(domains))}")
        else:
            logger.warning("No valid domains found in Caddyfile - check your configuration")
            # Log some debug info about what was found
            logger.debug(f"Caddyfile content preview: {content[:200]}...")
        
        return set(domains)
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
        error_details = ""
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_json = e.response.json()
                if 'errors' in error_json and error_json['errors']:
                    error_messages = [err.get('message', str(err)) for err in error_json['errors']]
                    error_details = f" - API Errors: {'; '.join(error_messages)}"
                elif 'message' in error_json:
                    error_details = f" - API Message: {error_json['message']}"
            except:
                error_details = f" - Response: {e.response.text[:200] if e.response.text else 'No response body'}"
        
        logger.error(f"Cloudflare API request failed: {e}{error_details}")
        raise
    except Exception as e:
        logger.error(f"Failed to sync to Cloudflare: {e}")
        raise

def run_sync():
    """Main synchronization function"""
    try:
        logger.info(f"=== Caddy Cloudflare DNS Updater v{__version__} ===")
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
        raise

if __name__ == "__main__":
    run_sync()
