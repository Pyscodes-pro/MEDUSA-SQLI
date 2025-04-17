![2025-04-17_08-22](https://github.com/user-attachments/assets/c111a263-2899-43cc-bb46-3025da298603)



---
# Medusa-SQLi Scanner

**Medusa-SQLi Scanner** is a Python tool designed to assist in discovering potential SQL injection vulnerabilities by automating Google Dorking (via the Google Custom Search API) and performing basic payload checks. It also integrates with [SQLMap](https://sqlmap.org) for more advanced SQL injection testing.

---
![2025-04-17_08-23](https://github.com/user-attachments/assets/7451de7c-a31f-46c0-bceb-abf21fd49e11)

## Features

- **Single URL Scan**  
  Scan a specific URL directly for SQLi vulnerabilities.

- **Google Dorking**  
  - Search using a single manual Google dork.  
  - Scan multiple dorks from a file.  
  - Uses Google Custom Search API to fetch results.

- **Basic SQLi Checks**  
  Performs simple checks using common error-based payloads like `'`, `"`, `--`, `OR 1=1`, etc.

- **SQLMap Integration**  
  - Automatically run SQLMap on potentially vulnerable URLs.  
  - Customize parameters like risk level, threads, DB enumeration, etc.

- **Export Results**  
  Save found URLs in CSV, JSON, or TXT format.

- **TOR Proxy Support**  
  Route requests through a local TOR SOCKS5 proxy (`127.0.0.1:9050`).

- **Logging**  
  All scan activities, URLs, and errors are logged to `medusa-log.txt`.

- **Log Management**  
  View or clear logs directly from within the tool.

- **Help / About Menu**  
  Easily access tool information and usage guide.

---

## Prerequisites

- **Python 3.7+**
- **pip** – Python package installer
- **SQLMap** (optional but recommended) – Make sure it’s installed and accessible from your system’s PATH.
- **Google Custom Search API Key & CX ID** – Required for Google Dorking.

---

## Installation

1. **Clone the Repository** (if applicable):

---
git clone <repository_url>
cd <repository_directory>
---

2. **Install Dependencies**:

---
pip install -r requirements.txt
---


## Usage

Run the tool using:

---
python medusa_sqli_scanner.py
---

You'll be presented with the main menu:

- Scan Single URL
- Manual Dork Search + SQLi Scan
- Scan Dorks from File + SQLi Scan
- Toggle TOR Proxy
- Log Management
- Help / About
- Exit

Just follow the prompts for each function.

---

## SQLMap Integration

When vulnerable URLs are found, you will be asked whether to run SQLMap.

- You can configure:
  - Risk level
  - Detection level
  - Thread count
  - Database enumeration options

- Output from SQLMap is saved in the `sqlmap_output/` directory.

> Make sure `sqlmap.py` is installed and available in your system’s PATH.

---

## Disclaimer ⚠️

This tool is intended for **educational purposes and authorized testing only**.

- Do **not** use this tool on systems or networks without **explicit written permission**.
- Unauthorized usage is **illegal** and **unethical**.
- The author assumes **no responsibility** for misuse or damage caused by this tool.

---

## Contact & Support

- **Instagram:** [@pyscodes](https://instagram.com/pyscodes)  
- **Support:** [linktr.ee/pyscodes](https://linktr.ee/pyscodes)

---
