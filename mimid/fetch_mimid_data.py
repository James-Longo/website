
import xenocanto
import os
import shutil

# Ensure clean dataset start if needed, but for now we'll just add to it.
# Xeno-canto-py downloads to 'dataset' folder in CWD by default.

# Queries for Mimidae family in the US (to keep it relevant/English)
# We can expand this later.
queries = [
    'gen:Dumetella cnt:"United States" q:A length:10-60', # Gray Catbird, quality A, 10-60s
    'gen:Mimus cnt:"United States" q:A length:10-60',     # Mockingbirds
    'gen:Toxostoma cnt:"United States" q:A length:10-60'  # Thrashers
]

import asyncio

async def main():
    print("Starting download from Xeno-Canto...")
    await xenocanto.download(queries)
    print("Download complete.")

if __name__ == "__main__":
    asyncio.run(main())
