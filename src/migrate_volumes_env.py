#!/usr/bin/env python3
"""
Azure Databricks Volume Migration Script - Environment Variable Version
Migrates files from source volume to destination volume using environment variables for secrets
"""

import os
import requests
import sys
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

class DatabricksVolumeMigrator:
    def __init__(self, host: str, token: str):
        self.host = host.rstrip('/')
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
    def list_files(self, volume_path: str) -> List[Dict[str, Any]]:
        """List all files in a volume"""
        endpoint = f"{self.host}/api/2.0/fs/list"
        params = {
            'path': volume_path
        }
        
        print(f"Listing files in: {volume_path}")
        response = requests.get(endpoint, headers=self.headers, params=params)
        
        if response.status_code != 200:
            print(f"Error listing files: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
        data = response.json()
        files = data.get('files', [])
        print(f"Found {len(files)} items in source volume")
        return files
    
    def read_file(self, file_path: str) -> bytes:
        """Read file content from Databricks volume"""
        endpoint = f"{self.host}/api/2.0/fs/files{file_path}"
        
        response = requests.get(endpoint, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Error reading file {file_path}: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
        return response.content
    
    def write_file(self, file_path: str, content: bytes) -> bool:
        """Write file to Databricks volume"""
        endpoint = f"{self.host}/api/2.0/fs/files{file_path}"
        
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/octet-stream'
        
        response = requests.put(endpoint, headers=headers, data=content)
        
        if response.status_code not in [200, 201, 204]:
            print(f"Error writing file {file_path}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        return True
    
    def create_directory(self, dir_path: str) -> bool:
        """Create a directory in Databricks volume"""
        endpoint = f"{self.host}/api/2.0/fs/directories{dir_path}"
        
        response = requests.put(endpoint, headers=self.headers)
        
        if response.status_code not in [200, 201]:
            print(f"Error creating directory {dir_path}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        return True
    
    def migrate_files(self, source_volume: str, dest_volume: str, recursive: bool = True):
        """Migrate all files from source to destination volume"""
        print(f"\n=== Starting Volume Migration ===")
        print(f"Source: {source_volume}")
        print(f"Destination: {dest_volume}")
        print(f"Recursive: {recursive}")
        print("=" * 40)
        
        # Get list of files from source
        items = self.list_files(source_volume)
        
        if not items:
            print("No files found in source volume")
            return
        
        successful = 0
        failed = 0
        
        for item in items:
            item_path = item.get('path', '')
            is_dir = item.get('is_dir', False)
            
            # Calculate relative path
            relative_path = item_path.replace(source_volume, '').lstrip('/')
            dest_path = f"{dest_volume}/{relative_path}" if relative_path else dest_volume
            
            if is_dir:
                if recursive:
                    print(f"\nProcessing directory: {item_path}")
                    # Create directory in destination
                    if self.create_directory(dest_path):
                        print(f"Created directory: {dest_path}")
                    # Recursively migrate subdirectory
                    self.migrate_files(item_path, dest_path, recursive=True)
            else:
                print(f"\nMigrating file: {item_path}")
                print(f"  -> {dest_path}")
                
                # Read file from source
                content = self.read_file(item_path)
                if content is not None:
                    # Write file to destination
                    if self.write_file(dest_path, content):
                        print(f"  ✓ Successfully migrated")
                        successful += 1
                    else:
                        print(f"  ✗ Failed to write to destination")
                        failed += 1
                else:
                    print(f"  ✗ Failed to read from source")
                    failed += 1
        
        print(f"\n=== Migration Summary ===")
        print(f"Successful: {successful} files")
        print(f"Failed: {failed} files")
        print("=" * 40)


def main():
    # Load environment variables from .env file if it exists
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("Loaded configuration from .env file")
    
    # Read configuration from environment variables
    token = os.environ.get('DATABRICKS_TOKEN')
    host = os.environ.get('DATABRICKS_HOST')
    source_volume = os.environ.get('SOURCE_VOLUME')
    dest_volume = os.environ.get('DEST_VOLUME')
    
    # Check if all required environment variables are set
    missing_vars = []
    if not token:
        missing_vars.append('DATABRICKS_TOKEN')
    if not host:
        missing_vars.append('DATABRICKS_HOST')
    if not source_volume:
        missing_vars.append('SOURCE_VOLUME')
    if not dest_volume:
        missing_vars.append('DEST_VOLUME')
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  • {var}")
        print("\nPlease set the following environment variables:")
        print("  export DATABRICKS_TOKEN='your-databricks-token'")
        print("  export DATABRICKS_HOST='https://your-databricks-instance.azuredatabricks.net/'")
        print("  export SOURCE_VOLUME='/Volumes/catalog/schema/source_volume'")
        print("  export DEST_VOLUME='/Volumes/catalog/schema/dest_volume'")
        sys.exit(1)
    
    print("Configuration loaded from environment variables")
    print(f"Host: {host}")
    print(f"Source: {source_volume}")
    print(f"Destination: {dest_volume}")
    
    # Create migrator and run migration
    migrator = DatabricksVolumeMigrator(host, token)
    
    try:
        migrator.migrate_files(source_volume, dest_volume, recursive=True)
        print("\nMigration completed!")
    except Exception as e:
        print(f"\nError during migration: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()