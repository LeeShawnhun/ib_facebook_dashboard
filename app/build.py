import subprocess
from pathlib import Path

def minify_js():
    subprocess.run(["terser", "static/js/index.js", "-o", "static/js/index.min.js"])

def minify_css():
    subprocess.run(["cleancss", "-o", "static/css/index.min.css", "static/css/index.css"])

if __name__ == "__main__":
    minify_js()
    minify_css()