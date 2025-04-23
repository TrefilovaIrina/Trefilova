from setuptools import setup, find_packages

setup(
    name="prompt_enhancer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.3.23",
        "langchain-community>=0.3.21",
        "langchain-core>=0.3.51",
        "langchain-openai>=0.3.12",
        "python-dotenv>=1.0.1",
        "httpx>=0.28.1",
        "requests>=2.32.3",
        "httpcore>=1.0.7",
        "h11>=0.14.0",
        "sniffio>=1.3.1",
        "anyio>=4.9.0",
        "cachetools>=5.5.2",
        "redis>=5.2.1",
        "backoff>=2.2.1",
        "tenacity>=9.1.2",
        "PyYAML>=6.0.2",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.5",
            "pytest-cov>=6.1.1",
            "pytest-mock>=3.14.0",
            "coverage>=7.8.0",
        ],
    },
) 