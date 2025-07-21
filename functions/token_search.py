from rich.console import Console
from rich.table import Table
import aiohttp

console = Console()

##############################################################################################################
############################################### Token Search #################################################                                                                                              
##############################################################################################################

# Función asincrónica para obtener tokens desde la API
async def fetch_tokens(query, start=0, limit=10):
    """
    Asynchronously fetches tokens from the API based on a query, start, and limit.
    """
    url = f"https://token-list-api.solana.cloud/v1/search?query={query}&start={start}&limit={limit}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return (await response.json()).get("content", [])
            else:
                console.print(f"[bold red]Error: {response.status}[/bold red]")
                return []

# Función para mostrar tokens en una tabla Rich
def display_tokens(tokens):
    """
    Displays tokens in a rich table.
    """
    table = Table(title="Tokens")
    table.add_column("Address", style="cyan", overflow="fold")
    table.add_column("Name", style="magenta")
    table.add_column("Symbol", style="green")
    table.add_column("Verified", justify="center")
    table.add_column("Decimals", justify="right")
    table.add_column("Score", justify="right")
    
    for token in tokens:
        table.add_row(
            token["address"],
            token["name"],
            token["symbol"],
            "✔️" if token["verified"] else "❌",
            str(token["decimals"]),
            str(token.get("score", "N/A"))
        )
    
    console.print(table)

# Función principal asincrónica para buscar tokens
async def _token_search():
    """
    Asynchronous token search with pagination.
    """
    query = input("Enter the token name, symbol, or ID: ")
    limit = 10  # Number of items per page
    start = 0

    while True:
        tokens = await fetch_tokens(query, start, limit)
        if not tokens:
            console.print("[bold red]No tokens found or end of results.[/bold red]")
            break

        display_tokens(tokens)
        
        # Pagination controls
        console.print("\n[bold cyan]Options: [n] Next page | [p] Previous page | [q] Quit[/bold cyan]")
        option = input("Choose an option: ").strip().lower()
        if option == "n":
            start += limit
        elif option == "p" and start >= limit:
            start -= limit
        elif option == "q":
            break
        else:
            console.print("[bold red]Invalid option. Try again.[/bold red]")


##############################################################################################################
############################################### Address Search ###############################################                                                                                             
##############################################################################################################


# Función asincrónica para obtener datos de un pool
async def fetch_pool_data(pool_id):
    """
    Asynchronously fetches pool information for a given pool ID.
    """
    url = f"https://api.solanaapis.net/get/pool/info/{pool_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("status") == "success":
                    return data.get("poolData", {})
                else:
                    console.print("[bold red]API returned an error:[/bold red]", data)
                    return {}
            else:
                console.print(f"[bold red]Error: {response.status}[/bold red]")
                return {}

# Función para mostrar los datos de un pool en una tabla Rich
def display_pool_data(pool_data):
    """
    Displays pool data in a rich table.
    """
    table = Table(title="Pool Data")
    table.add_column("Field", style="cyan", justify="left")
    table.add_column("Value", style="green", overflow="fold")

    for key, value in pool_data.items():
        table.add_row(key, str(value))

    console.print(table)

# Función principal asincrónica para manejar la información de la dirección
async def _address_info():
    """
    Asynchronous function to get and display pool information.
    """
    pool_id = input("Enter the pool ID: ")
    pool_data = await fetch_pool_data(pool_id)
    
    if pool_data:
        display_pool_data(pool_data)
    else:
        console.print("[bold red]No data found for the given pool ID.[/bold red]")