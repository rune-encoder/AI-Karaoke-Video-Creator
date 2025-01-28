# Local Application Imports
from modules.config import initialize_directories
from modules.logging_config import configure_logging
from interface.main_app import main_app

def run():
    # Initialize the project directories
    project_root, cache_dir, output_dir = initialize_directories()

    # Configure logging based on the verbose flag
    configure_logging(verbose=True)

    # Launch the main application
    app = main_app(cache_dir, output_dir)
    app.launch()

if __name__ == "__main__":
    run()