#!/usr/bin/env python3
"""
Setup script for Private Assistant Chatbot
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Private Assistant Chatbot"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Filter out comments and empty lines
            return [line.strip() for line in lines 
                   if line.strip() and not line.startswith('#')]
    return []

setup(
    name="private-assistant",
    version="1.0.0",
    author="Private Assistant Team",
    author_email="",
    description="A private assistant chatbot with fine-tuning, profiling, and knowledge management capabilities",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/private-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "ml": [
            "torch>=1.13.0",
            "transformers>=4.20.0",
            "numpy>=1.21.0",
        ],
        "nlp": [
            "nltk>=3.8",
            "spacy>=3.4.0",
        ],
        "web": [
            "requests>=2.28.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "private-assistant=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.txt", "*.md"],
    },
)