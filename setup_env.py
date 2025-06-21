#!/usr/bin/env python3
"""
Environment setup and validation for Caddy Cloudflare DNS Updater
"""

import os
import requests
import json

try:
    from version import __version__
except ImportError:
    __version__ = "unknown"

def test_cloudflare_credentials():
    """Test Cloudflare API credentials"""
    token = os.getenv("CF_API_TOKEN")
    zone_id = os.getenv("CF_ZONE_ID")
    domain = os.getenv("CF_DOMAIN")
    
    print("=== Cloudflare Credentials Check ===")
    print(f"CF_API_TOKEN: {'✓ Set' if token else '✗ Missing'}")
    print(f"CF_ZONE_ID: {'✓ Set' if zone_id else '✗ Missing'}")
    print(f"CF_DOMAIN: {'✓ Set' if domain else '✗ Missing'}")
    
    if not all([token, zone_id, domain]):
        print("\n❌ Missing required environment variables!")
        print("\nTo set them in PowerShell:")
        print('$env:CF_API_TOKEN="your_api_token_here"')
        print('$env:CF_ZONE_ID="your_zone_id_here"')
        print('$env:CF_DOMAIN="beavis.tech"')
        return False
    
    print(f"\n🔍 Testing API connection...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test API token validity
        print("1. Testing API token validity...")
        response = requests.get(
            "https://api.cloudflare.com/client/v4/user/tokens/verify",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("   ✅ API token is valid!")
            else:
                print(f"   ❌ API token invalid: {result.get('errors', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ API token validation failed: {response.status_code} - {response.text}")
            return False
        
        # Test zone access
        print("2. Testing zone access...")
        response = requests.get(
            f"https://api.cloudflare.com/client/v4/zones/{zone_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                zone_name = result["result"]["name"]
                print(f"   ✅ Zone access confirmed! Zone: {zone_name}")
                if zone_name != domain:
                    print(f"   ⚠️  Warning: Zone name ({zone_name}) doesn't match CF_DOMAIN ({domain})")
            else:
                print(f"   ❌ Zone access failed: {result.get('errors', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Zone access failed: {response.status_code} - {response.text}")
            return False
        
        # Test DNS records access
        print("3. Testing DNS records access...")
        response = requests.get(
            f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                records = result["result"]
                print(f"   ✅ DNS records access confirmed! Found {len(records)} existing records")
            else:
                print(f"   ❌ DNS records access failed: {result.get('errors', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ DNS records access failed: {response.status_code} - {response.text}")
            return False
        
        print("\n🎉 All credentials are working correctly!")
        return True
        
    except requests.RequestException as e:
        print(f"   ❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def show_setup_instructions():
    """Show detailed setup instructions"""
    print("\n" + "="*60)
    print("📋 CLOUDFLARE SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n1. 🔑 CREATE API TOKEN:")
    print("   - Go to: https://dash.cloudflare.com/profile/api-tokens")
    print("   - Click 'Create Token'")
    print("   - Choose 'Custom token'")
    print("   - Set permissions:")
    print("     * Zone Resources: Include → Specific zone → beavis.tech")
    print("     * Zone Permissions: Zone:Read")
    print("     * Zone Permissions: DNS:Edit")
    print("   - Copy the generated token")
    
    print("\n2. 📍 FIND ZONE ID:")
    print("   - Go to your Cloudflare dashboard")
    print("   - Select your domain (beavis.tech)")
    print("   - Look for 'Zone ID' in the right sidebar")
    print("   - Copy the Zone ID")
    
    print("\n3. 🔧 SET ENVIRONMENT VARIABLES (PowerShell):")
    print('   $env:CF_API_TOKEN="your_api_token_from_step_1"')
    print('   $env:CF_ZONE_ID="your_zone_id_from_step_2"')
    print('   $env:CF_DOMAIN="beavis.tech"')
    
    print("\n4. ✅ TEST SETUP:")
    print("   Run this script again to verify credentials")
    
    print("\n5. 🚀 RUN THE UPDATER:")
    print("   Once verified, you can run the main script")

if __name__ == "__main__":
    print(f"🌐 Caddy Cloudflare DNS Updater v{__version__} - Setup & Validation")
    print("="*60)
    
    if not test_cloudflare_credentials():
        show_setup_instructions()
    else:
        print("\n✅ Your setup is ready! You can now run the DNS updater.")
        print(f"\nTo run the updater:")
        print(f"   python main.py")
