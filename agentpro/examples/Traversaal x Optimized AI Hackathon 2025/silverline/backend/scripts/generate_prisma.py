#!/usr/bin/env python
"""
Script to generate Prisma client for Python.
Run this script after making changes to the Prisma schema.
"""
import os
import subprocess
import sys

def generate_prisma_client():
    """Generate Prisma client for Python."""
    try:
        # Ensure we're in the backend directory
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Generate Prisma client
        print("Generating Prisma client...")
        subprocess.run(["prisma", "generate"], check=True)
        
        print("Prisma client generated successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating Prisma client: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = generate_prisma_client()
    sys.exit(0 if success else 1) 