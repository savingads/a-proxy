from setuptools import setup, find_packages

setup(
    name="personaclient",
    version="0.1.0",
    description="Python client for the Persona API Service",
    long_description=open("README.md").read() if open("README.md", "r") else "",
    long_description_content_type="text/markdown",
    author="A-Proxy Team",
    author_email="your-email@example.com",
    url="https://github.com/your-organization/persona-client",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=2.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
