import os
from dotenv import load_dotenv

from echomind.ui.gradio_app import create_interface


def main() -> None:
    load_dotenv()
    iface = create_interface()
    iface.launch()


if __name__ == "__main__":
    main()


