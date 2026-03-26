from os import environ

from dotenv import load_dotenv
from internetarchive import Item, configure, get_session


def main():
    dotenv_loaded: bool = load_dotenv()
    if not dotenv_loaded:
        print("Warning: .env file not found, unable to authenticate")
        exit(1)

    configure(
        environ.get("IA_EMAIL", ""),
        environ.get("IA_PASSWORD", ""),
        config_file="ia.ini",
    )
    session = get_session(config_file="ia.ini")
    print(session.whoami())
    # item: Item = session.get_item("your-identifier")
    # response = item.upload(["fil"], metadata={"title": "My Item Title"})


if __name__ == "__main__":
    main()
