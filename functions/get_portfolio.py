# Get the portfolio of a solana wallet

# Funcion para hacerlo: asyncio.get_event_loop().run_until_complete(get_portfolio())

import nest_asyncio
import aiohttp
from rich.console import Console
from rich.table import Table

#################
# Get Portfolio # 
#################

# Necesario para permitir reentrancia del bucle en entornos interactivos como Jupyter
nest_asyncio.apply()

# Settings
solana_url = "https://api.mainnet-beta.solana.com"
headers = {"Content-Type": "application/json"}

# URL de la API de Raydium (v3)
raydium_api_url = "https://api-v3.raydium.io/mint/price?mints="

# Función para obtener el balance de SOL en la wallet
async def get_sol_balance(wallet_address, session):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [wallet_address]
    }
    async with session.post(solana_url, json=payload, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            sol_balance = data.get("result", {}).get("value", 0) / (10**9)  # Convertir de lamports a SOL
            return sol_balance
        else:
            print(f"Error: {response.status}, {await response.text()}")
            return 0

# Función para obtener el precio de un token usando Raydium API (basado en su mint address)
async def get_token_price_from_raydium(mint_addresses):
    url = f"{raydium_api_url}{','.join(mint_addresses)}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success", False):
                    # Obtener los precios desde el campo 'data' y convertirlos a flotantes
                    prices = data.get("data", {})
                    return {
                        mint: float(price) if price is not None and isinstance(price, (str, float)) else 0
                        for mint, price in prices.items()
                    }
                else:
                    print(f"Error al obtener el precio de los tokens: {data.get('msg', 'Unknown error')}")
                    return {}
            else:
                print(f"Error al obtener el precio de los tokens: {response.status}")
                return {}

# Función para obtener los tokens asociados a una wallet
async def get_tokens_associated_with_wallet(wallet_address, session):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet_address,
            {
                "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
            },
            {
                "encoding": "jsonParsed"
            }
        ]
    }
    async with session.post(solana_url, json=payload, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            tokens = data.get("result", {}).get("value", [])
            # Filtrar tokens con balance 0
            tokens_with_balance = [
                token for token in tokens
                if token["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"] > 0
            ]
            return tokens_with_balance
        else:
            print(f"Error: {response.status}, {await response.text()}")
            return []

# Función para obtener información de tokens a partir de las direcciones de mint
async def get_tokens_by_mints(addresses, session):
    payload = {
        "addresses": addresses
    }
    async with session.post("https://token-list-api.solana.cloud/v1/mints", json=payload, headers=headers) as response:
        if response.status == 200:
            return (await response.json()).get("content", [])
        else:
            print(f"Error loading tokens by mints: {response.status}, {await response.text()}")
            return []





async def _get_portfolio():
    console = Console()

    # User inputs
    input_wallet_address = input("Insert a Solana wallet: ")

    async with aiohttp.ClientSession() as session:
        wallet_address = input_wallet_address
        tokens = await get_tokens_associated_with_wallet(wallet_address, session)

        # Obtener el balance en SOL
        sol_balance = await get_sol_balance(wallet_address, session)

        # Extraer las direcciones de mint de los tokens asociados
        mint_addresses = [token["account"]["data"]["parsed"]["info"]["mint"] for token in tokens]

        # Obtener la información de los tokens desde la API por las direcciones de mint
        token_info_list = await get_tokens_by_mints(mint_addresses, session)

        if not token_info_list:
            console.print(f"No se encontraron tokens con balance mayor a 0 para la wallet [bold]{wallet_address}[/bold].", style="bold red")
            return

        # Obtener los precios de los tokens desde Raydium API
        token_prices = await get_token_price_from_raydium(mint_addresses)

        # Crear una lista para almacenar los valores calculados
        tokens_with_values = []

        for token in token_info_list:
            mint = token.get("address", "N/A")
            name = token.get("name", "N/A")
            symbol = token.get("symbol", "N/A")
            amount = next(
                (
                    t["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
                    for t in tokens
                    if t["account"]["data"]["parsed"]["info"]["mint"] == mint
                ),
                0
            )
            decimals = next(
                (
                    t["account"]["data"]["parsed"]["info"]["tokenAmount"]["decimals"]
                    for t in tokens
                    if t["account"]["data"]["parsed"]["info"]["mint"] == mint
                ),
                0
            )

            # Verificar si el precio está disponible
            token_price = token_prices.get(mint, 0)

            # Calcular el valor en SOL y USD
            value_in_sol = amount * token_price if token_price else 0
            value_in_usd = value_in_sol * sol_balance  # Usar el balance de SOL como referencia si no hay precio directo en USD

            tokens_with_values.append({
                "name": name,
                "symbol": symbol,
                "mint": mint,
                "amount": amount,
                "decimals": decimals,
                "value_in_usd": value_in_sol,  # Corregir el valor
                # "value_in_sol": value_in_usd   # Corregir el valor
            })

        # Ordenar los tokens por el valor en USD de mayor a menor
        tokens_with_values.sort(key=lambda x: x['value_in_usd'], reverse=True)

        # Crear una tabla con Rich
        table = Table(title=f"Tokens asociados a la wallet [bold]{wallet_address}[/bold]")

        # Definir las columnas
        table.add_column("Token Name", style="yellow", no_wrap=True)
        table.add_column("Token Symbol", style="yellow")
        table.add_column("Mint Address", style="green")
        table.add_column("Token Balance", justify="right", style="green")
        table.add_column("Decimals", justify="right", style="cyan")
        table.add_column("Balance in USD", justify="right", style="cyan")  # Solo mostrar USD
        # table.add_column("Value in SOL", justify="right", style="cyan")   # Solo mostrar SOL

        # Añadir filas a la tabla
        for token in tokens_with_values:
            table.add_row(
                token["name"],
                token["symbol"],
                token["mint"],
                f"{token['amount']}",
                f"{token['decimals']}",
                f"${token['value_in_usd']:.2f}",
                # f"{token['value_in_sol']:.2f}"
            )

        # Mostrar la tabla en la consola
        console.print(table)