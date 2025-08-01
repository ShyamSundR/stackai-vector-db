#!/usr/bin/env python3
"""
StackAI Vector Database Python SDK Setup
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "StackAI Vector Database Python SDK"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['requests>=2.25.0']

setup(
    name="stackai-sdk",
    version="1.0.0",
    author="StackAI Team",
    author_email="contact@stackai.com",
    description="Python SDK for StackAI Vector Database",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/stackai/vector-database",
    packages=find_packages(exclude=['tests*', 'examples*']),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0; python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "examples": [
            "numpy>=1.20.0",
            "matplotlib>=3.3.0",
            "pandas>=1.3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "stackai-sdk-examples=stackai_sdk.examples.basic_usage:main",
        ],
    },
    keywords=[
        "vector database", 
        "similarity search", 
        "machine learning", 
        "embeddings", 
        "ai", 
        "artificial intelligence",
        "semantic search",
        "nlp",
        "fastapi"
    ],
    project_urls={
        "Bug Reports": "https://github.com/stackai/vector-database/issues",
        "Documentation": "https://stackai.readthedocs.io/",
        "Source": "https://github.com/stackai/vector-database",
    },
    include_package_data=True,
    package_data={
        "stackai_sdk": ["py.typed"],
    },
    zip_safe=False,
) 