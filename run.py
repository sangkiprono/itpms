# run.py
import os
import sys

# Add the project root directory to Python's path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)