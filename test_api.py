
---

# ✅ `test_api_key.py` — short file to add

**Place this file at repo root.**  
Ye pehle env var check karega, agar key set hai to masked output karega. Optional: agar tum chaho to `requests` wali line uncomment karke real API call test kar sakte ho (api endpoint aur headers tumhe adjust karne honge).

```python
# test_api_key.py
import os
import sys

def mask_key(key):
    if not key:
        return None
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key)-8) + key[-4:]

def check_env_keys():
    keys = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
        "OTHER_API_KEY": os.getenv("OTHER_API_KEY")
    }
    print("Checking environment for API keys...\n")
    any_found = False
    for name, val in keys.items():
        if val:
            print(f"{name}: FOUND -> {mask_key(val)} (length {len(val)})")
            any_found = True
        else:
            print(f"{name}: NOT SET")
    if not any_found:
        print("\nNo API keys found in environment. Set them and reopen the terminal (or log off/on).")
    else:
        print("\nIf a key is set but not working in your program, make sure you restarted your IDE/Terminal after setx or exported properly.")
    return keys

def optional_http_test(eleventy_key):
    # OPTIONAL: small example to test ElevenLabs (or any) with requests.
    # Uncomment and edit the endpoint/header to your provider's quick test endpoint.
    """
    import requests
    if not eleventy_key:
        print("No ElevenLabs key for HTTP test.")
        return
    url = "https://api.elevenlabs.io/v1/voices"  # example endpoint, change if needed
    headers = {"xi-api-key": eleventy_key}
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        print("HTTP test status:", resp.status_code)
        print("Response preview:", resp.text[:400])
    except Exception as e:
        print("HTTP test error:", e)
    """

if __name__ == "__main__":
    found = check_env_keys()
    # optional_http_test(found.get("ELEVENLABS_API_KEY"))

