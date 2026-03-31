import random
import sqlite3
import string
from pathlib import Path


DB_PATH = Path("urls.db")
BASE_SHORT_URL = "https://short.local/"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def create_table() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL UNIQUE,
                short_code TEXT NOT NULL UNIQUE
            )
        """)
        conn.commit()


def generate_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def short_code_exists(short_code: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT 1 FROM urls WHERE short_code = ?",
            (short_code,)
        )
        return cursor.fetchone() is not None


def generate_unique_code() -> str:
    while True:
        code = generate_code()
        if not short_code_exists(code):
            return code


def is_valid_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def shorten_url(original_url: str) -> tuple[str, bool]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT short_code FROM urls WHERE original_url = ?",
            (original_url,)
        )
        row = cursor.fetchone()

        if row:
            return f"{BASE_SHORT_URL}{row[0]}", False

        code = generate_unique_code()
        conn.execute(
            "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
            (original_url, code)
        )
        conn.commit()
        return f"{BASE_SHORT_URL}{code}", True


def get_original_url(short_code: str) -> str | None:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT original_url FROM urls WHERE short_code = ?",
            (short_code,)
        )
        row = cursor.fetchone()
        return row[0] if row else None


def list_urls() -> None:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT original_url, short_code FROM urls ORDER BY id DESC"
        )
        rows = cursor.fetchall()

    if not rows:
        print("\nNo hay URLs guardadas.")
        return

    print("\n--- URLS GUARDADAS ---")
    for index, (original_url, short_code) in enumerate(rows, start=1):
        print(f"{index}. {original_url}")
        print(f"   {BASE_SHORT_URL}{short_code}")


def show_menu() -> None:
    print("\n" + "=" * 50)
    print("        URL SHORTENER WITH SQLITE")
    print("=" * 50)
    print("1. Acortar URL")
    print("2. Buscar URL original por código")
    print("3. Listar URLs guardadas")
    print("4. Salir")


def main() -> None:
    create_table()

    while True:
        show_menu()
        option = input("Elige una opción: ").strip()

        if option == "1":
            original_url = input("Ingresa la URL original: ").strip()

            if not is_valid_url(original_url):
                print("URL inválida. Debe comenzar con http:// o https://")
                continue

            short_url, created = shorten_url(original_url)

            if created:
                print("\nURL acortada correctamente:")
            else:
                print("\nLa URL ya existía. Se reutiliza el mismo código:")

            print(short_url)
            print("\nNota: esta URL corta es simulada para uso local.")

        elif option == "2":
            short_code = input("Ingresa el código corto: ").strip()
            original_url = get_original_url(short_code)

            if original_url:
                print("\nURL original encontrada:")
                print(original_url)
            else:
                print("\nNo se encontró ninguna URL con ese código.")

        elif option == "3":
            list_urls()

        elif option == "4":
            print("\nGracias por usar este proyecto.")
            print("Portfolio: https://dax-adorno.github.io/")
            break

        else:
            print("Opción inválida. Intenta nuevamente.")


if __name__ == "__main__":
    main()