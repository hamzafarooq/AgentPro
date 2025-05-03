# app\test\insert_dummy_values.py

import os
import json
import pathlib
import asyncio
from datetime import datetime
from app.db.prisma_client import prisma_client

def convert_snake_to_camel(record):
    """Convert snake_case keys from JSON to camelCase for the database"""
    mapping = {
        "caller_number": "callerNumber",
        "twilio_number": "twilioNumber",
        "call_duration": "callDuration",
        "is_spam": "isSpam",
        "datetime": "datetime",
        "type": "type",
        "reason": "reason"
    }
    
    return {mapping.get(k, k): v for k, v in record.items() if k != "id"}

async def insert_sequentially(records):
    """Insert records one by one sequentially"""
    inserted_count = 0
    for record in records:
        try:
            await prisma_client.callhistory.create(data=record)
            inserted_count += 1
            print(f"Inserted record {inserted_count}/{len(records)}")
        except Exception as e:
            print(f"Error inserting record: {e}")
    
    return inserted_count

async def insert_dummy_data():
    """Insert dummy data into the CallHistory collection from JSON file"""
    try:
        # Get the path to the JSON file
        base_dir = pathlib.Path(__file__).parent.parent.parent
        json_path = os.path.join(base_dir, "app", "utils", "mock_jsons", "call_history_data.json")
        
        # Load the JSON data
        with open(json_path, 'r') as file:
            dummy_records = json.load(file)
            
        # Transform records to match database schema
        transformed_records = []
        for record in dummy_records:
            # Convert snake_case to camelCase
            transformed = convert_snake_to_camel(record)
            
            # Convert string dates to datetime objects
            if isinstance(transformed["datetime"], str):
                transformed["datetime"] = datetime.fromisoformat(transformed["datetime"])
                
            transformed_records.append(transformed)
        
        # Connect to the Prisma client
        await prisma_client.connect()
        
        # Sequential insertion
        print("Inserting records sequentially...")
        inserted_count = await insert_sequentially(transformed_records)
        print(f"Successfully inserted {inserted_count} records sequentially")
        
    except Exception as e:
        print(f"Error inserting dummy data: {e}")
    finally:
        # Disconnect from Prisma
        await prisma_client.disconnect()

if __name__ == "__main__":
    asyncio.run(insert_dummy_data())
