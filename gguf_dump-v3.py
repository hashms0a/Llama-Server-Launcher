#!/usr/bin/env python3
from __future__ import annotations
import logging
import argparse
import os
import sys
from pathlib import Path
from typing import Any

# Necessary to load the local gguf package
if "NO_LOCAL_GGUF" not in os.environ and (Path(__file__).parent.parent.parent.parent / 'llama_server_UI').exists():
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gguf import GGUFReader, GGUFValueType  # noqa: E402

logger = logging.getLogger("gguf-extract")

def extract_block_and_context(reader: GGUFReader) -> None:
    """Extract and print only block_count and context_length values, regardless of prefix."""
    block_count = None
    context_length = None
    
    # Search through all fields for block_count and context_length
    for field in reader.fields.values():
        field_name = field.name.lower()
        
        # Check for block_count with any prefix
        if field_name.endswith('.block_count') or field_name == 'block_count':
            block_count = field.contents()
            
        # Check for context_length with any prefix
        if field_name.endswith('.context_length') or field_name == 'context_length':
            context_length = field.contents()
            
        # If we found both values, we can stop
        if block_count is not None and context_length is not None:
            break
    
    # Print the results
    if block_count is not None:
        print(f"block_count = {block_count}")
    else:
        print("block_count not found")
        
    if context_length is not None:
        print(f"context_length = {context_length}")
    else:
        print("context_length not found")

def main() -> None:
    parser = argparse.ArgumentParser(description="Extract block_count and context_length from GGUF file metadata")
    parser.add_argument("model", type=str, help="GGUF format model filename")
    args = parser.parse_args(None if len(sys.argv) > 1 else ["--help"])
    
    logging.basicConfig(level=logging.INFO)
    logger.info(f'* Loading: {args.model}')
    
    reader = GGUFReader(args.model, 'r')
    extract_block_and_context(reader)

if __name__ == '__main__':
    main()
