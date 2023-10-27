from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="FastThrottle",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An efficient and easy-to-integrate rate limiter for FastAPI applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/FastThrottle",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'fastapi',
        'redis',
        'aioredis',

    ],
    python_requires='>=3.6',
)
