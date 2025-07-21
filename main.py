from functions.charts import _chart
from functions.get_portfolio import _get_portfolio
from functions.token_search import _token_search, _address_info
import asyncio

import typer

app = typer.Typer()  

# Función principal para mostrar el portfolio de una wallet
@app.command()
def get_portfolio():
    """
    CLI command to fetch and display the token portfolio.
    """
    asyncio.run(_get_portfolio())
    
    

# Función principal para buscar tokens
@app.command()
def token_search():
    """
    CLI command to fetch and display tokens data by name or symbol.
    """
    asyncio.run(_token_search())
    


# Función principal para buscar tokens por direccion
@app.command()
def address_info():
    """
    CLI command to fetch and display data of a token address.
    """
    asyncio.run(_address_info())
    
    
# Función principal para mostrar graficos de una address
@app.command()
def chart():
    """
    CLI command to display a chart of a given address
    """
    asyncio.run(_chart())
    
if __name__ == "__main__":
    app()
    
# asyncio.get_event_loop().run_until_complete(get_portfolio())