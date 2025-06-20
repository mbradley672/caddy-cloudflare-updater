# main.py
import os
import requests
from caddyparser import parse_caddyfile
from ipaddress import ip_address

def get_public_ip():
    return requests.get("https://api.ipify.org").text.strip()

def get_caddy_domains(file_path):
    with open(file_path) as f:
        config = parse_caddyfile(f.read())
    domains = set()
    for block in config:
        if "keys" in block:
            domains.update(block["keys"])
    return domains

def sync_to_cloudflare(subdomains, ip):
    token = os.getenv("CF_API_TOKEN")
    zone = os.getenv("CF_ZONE_ID")
    root_domain = os.getenv("CF_DOMAIN")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    r = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records", headers=headers)
    records = r.json()["result"]
    existing = {r["name"]: r for r in records if r["type"] in ("A", "AAAA")}

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
            rec_id = existing[fqdn]["id"]
            print(f"Updating {fqdn}")
            requests.put(f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records/{rec_id}", headers=headers, json=data)
        else:
            print(f"Creating {fqdn}")
            requests.post(f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records", headers=headers, json=data)

def run_sync():
    ip = get_public_ip()
    domains = get_caddy_domains(os.getenv("CADDYFILE_PATH", "/etc/caddy/Caddyfile"))
    sync_to_cloudflare(domains, ip)

if __name__ == "__main__":
    run_sync()
