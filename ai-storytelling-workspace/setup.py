"""Setup configuration for AI Storytelling Workspace."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="storytelling-workspace",
    version="0.1.0",
    author="AI Storytelling Team",
    description="Multi-agent orchestration system for AI-assisted book writing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SyedMuhammadHunain/ai-storytelling-workspace",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
    ],
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "storytelling-workspace=storytelling_workspace.cli:main",
        ],
    },
)
