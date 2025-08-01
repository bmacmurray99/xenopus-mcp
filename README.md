# Xenopus MCP

Xenopus MCP is a tool that provides an interface to the Screaming Frog SEO Spider. It allows you to automate crawling and data extraction from websites. 

## Features

*   Crawl a website and export a wide variety of data.
*   Load existing crawl files and export data from them.
*   Allows AI agents to choose the relevant exports for a given task

## Requirements
This MCP runs locally and needs the following:
*   Screaming Frog SEO Spider installed and in your system's PATH, aliased to `screamingfrogseospider`
*   A Valid Screaming Frog SEO Spider License
*   Python 3.
*   Python MCP SDK

## Installation

1.  Clone this repository.
2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Gemini-CLI configuration
Add the following to ".gemini/settings.json" in your project folder:
```json  
"mcpServers": {
"xenopus": {
      "type": "stdio",
      "command": "python3",
      "args": ["PATH_TO_XENOPUS_MCP_REPOSITORY/server.py"]
      }
}
```



### Tools

*   `domain_crawl`: Runs a Screaming Frog crawl on the specified domain.
*   `post_crawl_export`: Loads a crawl file and exports data.

### Resources

*   `data://export-header-reference`: Returns a dictionary of available export headers.
*   `data://database-id-list`: Returns a list of available crawl database IDs.



