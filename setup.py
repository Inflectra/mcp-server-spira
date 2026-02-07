"""
Defines the entry point of the extension
"""

import setuptools  # type: ignore[import-untyped]

with open("README.md") as readme_file:
    long_description = readme_file.read()

# Register plugin
setuptools.setup(
    name="mcp-server-spira",
    version="1.1.1",
    author="Inflectra Corporation",
    author_email="support@inflectra.com",
    url="https://github.com/Inflectra/mcp-server-spira",
    description="A Model Context Protocol (MCP) server enabling AI assistants to interact with Spira by Inflectra.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "mcp-server-spira = mcp_server_spira.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.cfg", "*.json", "*.yaml", "*.yml"],
        "mcp_server_spira": [
            "**/*.py",
            "**/*.md",
            "**/*.json",
            "**/*.yaml",
            "**/*.yml",
            "**/*.cfg",
        ],
    },
)
