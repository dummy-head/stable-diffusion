import logging
import os
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

os.environ["TORCH_CUDNN_V8_API_ENABLED"] = "1"
os.environ["CUDA_MODULE_LOADING"] = "LAZY"

from core.install_requirements import (  # pylint: disable=wrong-import-position
    commit_hash,
    create_environment,
    in_virtualenv,
    install_pytorch,
    is_installed,
    version_check,
)

parser = ArgumentParser()
parser.add_argument(
    "--log-level",
    default="INFO",
    help="Log level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
)
parser.add_argument("--ngrok", action="store_true", help="Use ngrok to expose the API")
args = parser.parse_args()

logging.basicConfig(level=args.log_level)
logger = logging.getLogger(__name__)

# Suppress some annoying logs
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.INFO)
logging.getLogger("xformers").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

# Create necessary folders
Path("traced_unet").mkdir(exist_ok=True)
Path("onnx").mkdir(exist_ok=True)
Path("engine").mkdir(exist_ok=True)


def main():
    "Run the API"
    import torch.backends.cudnn

    # Benchmark a few fucntions to find the best configuration
    torch.backends.cudnn.benchmark = True

    if args.ngrok:
        import nest_asyncio
        from pyngrok import ngrok

        ngrok_tunnel = ngrok.connect(5003)
        logger.info(f"Public URL: {ngrok_tunnel.public_url}")
        nest_asyncio.apply()

    from uvicorn import run as uvicorn_run

    from api.app import app as api_app

    uvicorn_run(api_app, host="0.0.0.0", port=5003)


def checks():
    "Check if the script is run from a virtual environment, if yes, check requirements"

    if not in_virtualenv():
        create_environment()

        logger.error("Please run the script from a virtual environment")
        sys.exit(1)

    # Install more user friendly logging
    if not is_installed("coloredlogs"):
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "coloredlogs",
            ]
        )

    # Inject coloredlogs
    from coloredlogs import install as coloredlogs_install

    coloredlogs_install(level=args.log_level)

    # Check if we are up to date with the latest release
    version_check(commit_hash())

    # Install pytorch and api requirements
    install_pytorch()


if __name__ == "__main__":
    checks()
    main()
