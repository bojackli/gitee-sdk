from setuptools import setup, find_packages
import re

def increment_version():
    with open('pyproject.toml', 'r') as f:
        content = f.read()
        version = re.search(r'version = "(\d+\.\d+\.\d+)"', content).group(1)
        a, b, c = version.split('.')
        new_version = f'{a}.{b}.{int(c)+1}'
        return new_version

setup(
    name="gitee-openapi",
    version=increment_version(),
    description="Python SDK for Gitee API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="bojackli",
    author_email="lovenpeace648@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    python_requires=">=3.8",
)