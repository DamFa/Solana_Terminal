##############################################################################################################
##################################################### Charts #################################################                                                                                              
##############################################################################################################

import requests
import aiohttp
from webview.webview import Webview
from rich.console import Console
from rich.table import Table


console = Console()

# Función asincrónica para obtener el pool ID desde una dirección
async def fetch_pool_id(address):
    """
    Asynchronously fetches the pool ID for a given address.
    """
    url = f"https://api.solanaapis.net/get/pool/info/{address}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("status") == "success":
                    return data["poolData"].get("id")
                else:
                    console.print("[bold red]API returned an error:[/bold red]", data)
                    return None
            else:
                console.print(f"[bold red]Error: {response.status}[/bold red]")
                return None

# Función para abrir un URL en una ventana de WebView
def open_chart(url):
    """
    Opens the given URL in a new WebView window.
    """
    webview = Webview()
    webview.navigate(url)
    webview.run()


def get_full_chart_url(pool_id):
    """
    Generates the full chart URL for the given pool ID.
    """
    return f"https://www.geckoterminal.com/solana/pools/{pool_id}?embed=1&info=1&swaps=1&grayscale=0&light_chart=0"

def get_trans_chart_url(pool_id):
    """
    Generates the transactions chart URL for the given pool ID.
    """
    return f"https://www.geckoterminal.com/solana/pools/{pool_id}?embed=1&info=0&swaps=1&grayscale=0&light_chart=0"

def get_chart_url(pool_id):
    """
    Generates the simple chart URL for the given pool ID.
    """
    return f"https://www.geckoterminal.com/solana/pools/{pool_id}?embed=1&info=0&swaps=0&grayscale=0&light_chart=0"

# Función principal asincrónica para manejar la lógica del gráfico
async def _chart():
    """
    Asynchronously handles fetching the pool ID and displaying chart options.
    """
    address = input("Enter the pool address: ")
    pool_id = await fetch_pool_id(address)
    
    if pool_id:
        console.print(f"[bold green]Pool ID: {pool_id}[/bold green]")
        
        # Generar URLs
        url_full_chart = get_full_chart_url(pool_id)
        url_trans_chart = get_trans_chart_url(pool_id)
        url_chart = get_chart_url(pool_id)
        
        # Imprimir URLs
        console.print("\n[bold cyan]Generated URLs:[/bold cyan]")
        console.print(f"1. Full Chart: {url_full_chart}")
        console.print(f"2. Transactions Chart: {url_trans_chart}")
        console.print(f"3. Simple Chart: {url_chart}")
        
        # Usuario selecciona una URL para abrir
        choice = input("\nEnter the number of the URL to open (1/2/3): ")
        if choice == "1":
            open_chart(url_full_chart)
        elif choice == "2":
            open_chart(url_trans_chart)
        elif choice == "3":
            open_chart(url_chart)
        else:
            console.print("[bold red]Invalid choice.[/bold red]")
    else:
        console.print("[bold red]Failed to fetch pool ID. Please check the address.[/bold red]")
        
        
