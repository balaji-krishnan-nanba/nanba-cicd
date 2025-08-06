#!/usr/bin/env python3
"""
Verification script to check if files were successfully migrated
"""

import os
import requests
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

class MigrationVerifier:
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
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        
        if response.status_code != 200:
            print(f"Error listing files in {volume_path}: {response.status_code}")
            return []
            
        data = response.json()
        return data.get('files', [])
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata"""
        endpoint = f"{self.host}/api/2.0/fs/get-status"
        params = {
            'path': file_path
        }
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        
        if response.status_code != 200:
            return None
            
        return response.json()
    
    def verify_migration(self, source_volume: str, dest_volume: str):
        """Verify that all files from source exist in destination"""
        print("\n=== Migration Verification ===")
        print(f"Source: {source_volume}")
        print(f"Destination: {dest_volume}")
        print("=" * 50)
        
        # List files in source
        print("\n📁 Source Volume Contents:")
        source_files = self.list_files(source_volume)
        
        if not source_files:
            print("  No files found in source volume")
        else:
            for file in source_files:
                path = file.get('path', '')
                is_dir = file.get('is_dir', False)
                size = file.get('file_size', 0)
                
                if not is_dir:
                    print(f"  • {path.split('/')[-1]} ({size:,} bytes)")
                else:
                    print(f"  📂 {path.split('/')[-1]}/")
        
        # List files in destination
        print("\n📁 Destination Volume Contents:")
        dest_files = self.list_files(dest_volume)
        
        if not dest_files:
            print("  No files found in destination volume")
        else:
            for file in dest_files:
                path = file.get('path', '')
                is_dir = file.get('is_dir', False)
                size = file.get('file_size', 0)
                
                if not is_dir:
                    print(f"  • {path.split('/')[-1]} ({size:,} bytes)")
                else:
                    print(f"  📂 {path.split('/')[-1]}/")
        
        # Compare files
        print("\n🔍 Verification Results:")
        
        source_file_names = {f['path'].split('/')[-1]: f for f in source_files if not f.get('is_dir')}
        dest_file_names = {f['path'].split('/')[-1]: f for f in dest_files if not f.get('is_dir')}
        
        all_verified = True
        
        for filename, source_file in source_file_names.items():
            if filename in dest_file_names:
                source_size = source_file.get('file_size', 0)
                dest_size = dest_file_names[filename].get('file_size', 0)
                
                if source_size == dest_size:
                    print(f"  ✅ {filename} - Successfully migrated ({source_size:,} bytes)")
                else:
                    print(f"  ⚠️  {filename} - Size mismatch (source: {source_size:,}, dest: {dest_size:,})")
                    all_verified = False
            else:
                print(f"  ❌ {filename} - Not found in destination")
                all_verified = False
        
        # Check for extra files in destination
        for filename in dest_file_names:
            if filename not in source_file_names:
                print(f"  ℹ️  {filename} - Extra file in destination (not in source)")
        
        print("\n" + "=" * 50)
        if all_verified and len(source_file_names) > 0:
            print("✅ All files successfully migrated!")
        elif len(source_file_names) == 0:
            print("⚠️  No files to migrate in source volume")
        else:
            print("⚠️  Some files were not migrated successfully")
        print("=" * 50)


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
        print("\nPlease set the following environment variables or create a .env file:")
        print("  export DATABRICKS_TOKEN='your-databricks-token'")
        print("  export DATABRICKS_HOST='https://your-databricks-instance.azuredatabricks.net/'")
        print("  export SOURCE_VOLUME='/Volumes/catalog/schema/source_volume'")
        print("  export DEST_VOLUME='/Volumes/catalog/schema/dest_volume'")
        sys.exit(1)
    
    # Create verifier and run verification
    verifier = MigrationVerifier(host, token)
    verifier.verify_migration(source_volume, dest_volume)


if __name__ == "__main__":
    main()