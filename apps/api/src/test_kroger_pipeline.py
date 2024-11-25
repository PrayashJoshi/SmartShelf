# src/test_ingredients_pipeline.py
import logging
from pipelines.kroger_pipeline import KrogerPipeline, DatabaseError
from pipelines.kroger_api_utils import KrogerAPI, KrogerAPIError
from rich.console import Console
from rich.table import Table
from rich.status import Status
from rich.panel import Panel
import json
import os
from typing import Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up pretty printing
console = Console()


class TestRunner:
    """Class to handle testing of Kroger API and Ingredient Pipeline"""

    def __init__(self):
        self.success = load_dotenv()
        self.client_id = os.getenv("KROGER_CLIENT_ID")
        self.client_secret = os.getenv("KROGER_CLIENT_SECRET")
        self.location_id = os.getenv("KROGER_LOCATION_ID", "70100465")
        self.api: Optional[KrogerAPI] = None
        self.pipeline: Optional[KrogerPipeline] = None

    def check_credentials(self) -> bool:
        """Verify API credentials are available"""
        if not self.client_id or not self.client_secret:
            console.print(Panel(
                "[red]Missing Kroger API credentials[/red]\n"
                "Please set environment variables:\n"
                "- KROGER_CLIENT_ID\n"
                "- KROGER_CLIENT_SECRET",
                title="Configuration Error"
            ))
            console.print(self.success)
            console.print(os.getenv("NUTRITION_KEY"))
            return False
        return True

    async def test_kroger_api(self) -> bool:
        """Test Kroger API authentication and product search"""
        console.print("\n[bold]Testing Kroger API Connection...[/bold]")
        try:
            # Initialize API
            self.api = KrogerAPI(self.client_id, self.client_secret)
            # Test authentication
            with Status("[bold green]Getting access token..."):
                token = self.api.get_access_token()
                console.print("[green]✓ Successfully authenticated[/green]")
            # Test product search
            test_ingredients = ["milk"]
            for ingredient in test_ingredients:
                console.print(f"\nTesting search for: {ingredient}")
                with Status("[bold green]Searching products..."):
                    products = self.api.search_products(
                        ingredient=ingredient,
                        location_id=self.location_id,
                        limit=3
                    )
                if products:
                    table = Table(
                        title=f"Products matching '{ingredient}'",
                        show_header=True,
                        header_style="bold magenta"
                    )
                    table.add_column("ID", style="cyan")
                    table.add_column("Name", style="magenta")
                    table.add_column("Brand", style="green")
                    table.add_column("Price", justify="right", style="yellow")
                    table.add_column("Category", style="blue")
                    for product in products:
                        table.add_row(
                            str(product.product_id),
                            product.name,
                            product.brand,
                            f"${product.price:.2f}",
                            product.category
                        )
                    console.print(table)
                else:
                    console.print(f"[yellow]No products found for {ingredient}[/yellow]")
            return True
        except KrogerAPIError as e:
            console.print(f"[red]Kroger API Error: {e.message}[/red]")
            if hasattr(e, 'status_code'):
                console.print(f"[red]Status Code: {e.status_code}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Unexpected error testing Kroger API: {str(e)}[/red]")
            return False

    def init_pipeline(self):
        """Initialize the ingredient pipeline"""
        self.pipeline = KrogerPipeline(
            client_id=self.client_id,
            client_secret=self.client_secret,
            location_id=self.location_id
        )

    def display_recipes(self):
        """Display available recipes in a table"""
        try:
            recipes = self.pipeline.get_recipe_details_all()
            if not recipes:
                console.print("[yellow]No recipes found in database[/yellow]")
                return False
            table = Table(
                title="Available Recipes",
                show_header=True,
                header_style="bold magenta"
            )
            table.add_column("ID", justify="right", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Category", style="blue")
            table.add_column("Cuisine", style="green")
            table.add_column("Cook Time", style="yellow")
            table.add_column("Difficulty", style="red")
            for recipe in recipes:
                table.add_row(
                    str(recipe['recipe_id']),
                    recipe['name'],
                    recipe['category'],
                    recipe['cuisine_type'],
                    f"{recipe['cooking_time']} min" if recipe['cooking_time'] else "-",
                    recipe['difficulty_level']
                )
            console.print(table)
            return True
        except DatabaseError as e:
            console.print(f"[red]Database Error: {str(e)}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Error displaying recipes: {str(e)}[/red]")
            return False

    def process_recipe(self, recipe_id: int):
        """Process a recipe and display results"""
        try:
            with Status(f"[bold green]Processing recipe {recipe_id}..."):
                results = self.pipeline.process_recipe(recipe_id, verbose=True)
            # Display shopping list
            if results['shopping_list']:
                table = Table(
                    title=f"Shopping List for {results['recipe']['name']}",
                    show_header=True,
                    header_style="bold magenta"
                )
                table.add_column("Ingredient", style="cyan")
                table.add_column("Amount", style="magenta")
                table.add_column("Product", style="green")
                table.add_column("Brand", style="blue")
                table.add_column("Price", justify="right", style="yellow")
                for item in results['shopping_list']:
                    table.add_row(
                        item['ingredient_name'],
                        f"{item['quantity']} {item['measurement_unit']}",
                        item['product_name'],
                        item['brand'],
                        f"${item['price']:.2f}"
                    )
                console.print(table)
                console.print(f"\n[green]Total Cost: ${results['total_cost']:.2f}[/green]")
            # Save results
            filename = f"recipe_{recipe_id}_results.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            console.print(f"\n[green]Results saved to {filename}[/green]")
        except DatabaseError as e:
            console.print(f"[red]Database Error: {str(e)}[/red]")
        except KrogerAPIError as e:
            console.print(f"[red]Kroger API Error: {e.message}[/red]")
        except Exception as e:
            console.print(f"[red]Error processing recipe: {str(e)}[/red]")

    async def run(self):
        """Main test runner"""
        console.print(Panel.fit(
            "[bold blue]SmartShelf Recipe Testing Tool[/bold blue]",
            subtitle="v1.0"
        ))
        # Check credentials
        if not self.check_credentials():
            return
        # Test Kroger API
        if not await self.test_kroger_api():
            console.print("[red]Kroger API test failed. Please fix API issues before proceeding.[/red]")
            return
        # Initialize pipeline
        self.init_pipeline()
        # Display recipes
        if not self.display_recipes():
            return
        # Interactive recipe processing
        while True:
            try:
                recipe_id = console.input("\nEnter recipe ID to test (or 'q' to quit): ")
                if recipe_id.lower() == 'q':
                    break
                self.process_recipe(int(recipe_id))
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")


async def main():
    """Main entry point"""
    runner = TestRunner()
    await runner.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
