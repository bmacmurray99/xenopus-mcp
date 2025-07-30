#!/usr/bin/env python3
import sys
import os
import subprocess  # CORRECT: Import the required 'subprocess' module
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from export_headers import export_tabs, bulk_exports, save_reports

# --- BEST PRACTICE: Configure structured logging to stderr ---
# This provides a dedicated debug channel, separate from the stdout JSON-RPC traffic.
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,  # Direct logs to stderr
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# -----------------------------------------------------------

# TEST VARIABLES
DEFAULT_EXPORTS_FOLDER = "exports"
DEFAULT_EXPORT_TABS = export_tabs
DEFAULT_BULK_EXPORTS = bulk_exports
DEFAULT_REPORTS = save_reports

mcp = FastMCP("xenopus")

@mcp.tool()
def domain_crawl(domain: str,
                 export_tabs: list,
                 bulk_exports: list,
                 reports: list,
                 output_folder: str = DEFAULT_EXPORTS_FOLDER,
                 business_name: str = "default_business_name",
                 config: str = "default.seospider"
                 ) -> dict:
    """Run a ScreamingFrog crawl and return a status dictionary."""
    logging.info(f"Received request to crawl domain: {domain}")
    
    command = [
        'screamingfrogseospider',
        '--crawl', domain,
        '--headless',
        '--output-folder', output_folder,
        '--export-format', 'csv',
        '--timestamped-output',
        '--save-crawl'
    ]

    # Add export tabs if provided
    if export_tabs:
        command.append('--export-tabs')
        command.extend(export_tabs)

    # Add bulk exports if provided
    if bulk_exports:
        command.append('--bulk-export')
        command.extend(bulk_exports)

    # Add reports if provided
    if reports:
        command.append('--save-report')
        command.extend(reports)
        
    logging.info(f"Executing command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logging.info(f"Screaming Frog crawl for {domain} completed successfully.")
        logging.info(f"STDOUT: {result.stdout}")
        return {"status": "success", "domain": domain, "message": "Crawl completed."}
    
    except FileNotFoundError:
        error_message = "Error: 'screamingfrogseospider' command not found. Ensure it is installed and in the system's PATH."
        logging.error(error_message)
        return {"status": "error", "domain": domain, "message": error_message}
    
    except subprocess.CalledProcessError as e:
        error_message = f"Error running Screaming Frog for domain {domain}. Return code: {e.returncode}"
        # Log the detailed output from the failed command for debugging
        logging.error(error_message)
        logging.error(f"STDOUT: {e.stdout}")
        logging.error(f"STDERR: {e.stderr}")
 
        return {"status": "error", "domain": domain, "message": error_message, "details": e.stderr}
        


@mcp.tool()
def post_crawl_export(crawl_file: str,
                      export_tabs: list = [],
                      bulk_exports: list= [],
                      reports: list=[],
                      output_folder: str = "postcrawl-exports"
                      ) -> dict:
    """Load a crawl file and export data."""
    logging.info(f"Received request to export data from crawl file: {crawl_file}")
    
    # Determine the directory of the crawl file
    crawl_file_directory = os.path.dirname(crawl_file)
    
    # Construct the new output folder path relative to the crawl file's directory
    # If output_folder is an absolute path, it will remain absolute.
    # Otherwise, it will be relative to crawl_file_directory.
    export_output_folder = os.path.join(crawl_file_directory, output_folder)

    # Ensure the output directory exists
    os.makedirs(export_output_folder, exist_ok=True)

    command = [
        'screamingfrogseospider',
        '--headless',
        '--output-folder', export_output_folder,
        '--export-format', 'csv',
        '--timestamped-output',
        '--load-crawl', crawl_file
    ]

    # Add export tabs if provided
    if export_tabs:
        command.append('--export-tabs')
        command.extend(export_tabs)

    # Add bulk exports if provided
    if bulk_exports:
        command.append('--bulk-export')
        command.extend(bulk_exports)

    # Add reports if provided
    if reports:
        command.append('--save-report')
        command.extend(reports)
        
    logging.info(f"Executing command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logging.info(f"Data export from {crawl_file} completed successfully.")
        logging.info(f"STDOUT: {result.stdout}")
        return {"status": "success", "crawl_file": crawl_file, "message": "Data export completed."}
    
    except FileNotFoundError:
        error_message = "Error: 'screamingfrogseospider' command not found. Ensure it is installed and in the system's PATH."
        logging.error(error_message)
        return {"status": "error", "crawl_file": crawl_file, "message": error_message}
    
    except subprocess.CalledProcessError as e:
        error_message = f"Error exporting data from {crawl_file}. Return code: {e.returncode}"
        # Log the detailed output from the failed command for debugging
        logging.error(error_message)
        logging.error(f"STDOUT: {e.stdout}")
        logging.error(f"STDERR: {e.stderr}")
 
        return {"status": "error", "crawl_file": crawl_file, "message": error_message, "details": e.stderr}
        
@mcp.resource("data://export-header-reference")
def export_header_reference()-> dict:
	"This resource describes the available export headers for ScreamingFrog"
	return {
	"export-tabs":export_tabs,
	"bulk-exports":bulk_exports, 
	"save-reports":save_reports
	}
@mcp.resource("data://database-id-list")
def database_id_list ()-> dict:
	"This resource returns a list of database IDs to be loaded with the post_crawl_export tool"
	return {"database-ids":os.listdir(str(Path.home())+"/.ScreamingFrogSEOSpider/ProjectInstanceData")}



def main():
    try:
        logging.info("Xenopus MCP server starting up...")
        mcp.run(transport="stdio")
        logging.info("Xenopus MCP server shutting down normally.")
    except Exception as e:
        # Log any unexpected errors during server run
        logging.critical("MCP server failed to run", exc_info=True)
        raise

if __name__ == "__main__":
    main()
