import sys
from os import environ
from typing import Any

from dotenv import load_dotenv
from internetarchive import Item, configure, get_session
from models import IAMetadata
from pydantic import ValidationError


def main(identifiers: list[str]) -> None:
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
    if session:
        # type hint for this method is wrong, it returns a dict not a string
        whoami: dict[str, Any] = session.whoami()  # type: ignore
        user_info = whoami.get("value", {})
        print(
            f"Logged in as {user_info.get('itemname')} {user_info.get('username')} {user_info.get('screenname')}"
        )

    for identifier in identifiers:
        item: Item = session.get_item(identifier)
        print(item.metadata)
        try:
            IAMetadata(**item.metadata)
        except ValidationError as e:
            print(f"Validation error for {identifier}: {e}")
    # response = item.upload(["fil"], metadata={"title": "My Item Title"})


if __name__ == "__main__":
    main(sys.argv[1:])
