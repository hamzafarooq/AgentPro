#!/usr/bin/env python3
"""
Script to seed the database with sample call data.
Run this script to populate the database with test data.
"""

import asyncio
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add the root directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.prisma_client import prisma_client, connect_prisma, disconnect_prisma
from app.utils.logging.logger import LOG


async def seed_database():
    """Create sample call data in the database."""
    try:
        await connect_prisma()
        LOG.info("Connected to Prisma. Seeding database...")
        
        # Delete existing records for testing
        try:
            delete_count = await prisma_client.callhistory.delete_many({})
            LOG.info(f"Cleared {delete_count} existing call records")
        except Exception as e:
            LOG.warning(f"Error clearing existing records: {e}")
        
        # Create sample call types
        call_types = ["Medical", "Environmental", "Fall Detection", "Other"]
        caller_ids = ["user1", "user2", "user3", "user4", "user5"]
        caller_numbers = [
            "+1234567890", "+1987654321", "+1456789012", "+1567890123",
            "+1678901234", "+1789012345", "+1890123456", "+1901234567"
        ]
        twilio_numbers = ["+19876543210", "+18765432109", "+17654321098"]
        
        # Sample reasons/summaries for different call types
        reasons = {
            "Medical": [
                "Chest pain, difficulty breathing",
                "Diabetic emergency, low blood sugar",
                "Severe allergic reaction, administered EpiPen",
                "Fall with possible fracture",
                "Severe headache, nausea"
            ],
            "Environmental": [
                "Smoke detector activated, no visible fire",
                "Carbon monoxide detector alert, evacuated premises",
                "Water leak in basement",
                "Gas smell reported",
                "Temperature control issue"
            ],
            "Fall Detection": [
                "Fall detected in bathroom, responsive",
                "Fall detected in kitchen, unresponsive initially",
                "Fall from bed, minor injuries",
                "Fall while walking, possible hip injury",
                "Fall on stairs, conscious but in pain"
            ],
            "Other": [
                "Security alarm triggered, false alarm",
                "Power outage reported",
                "Request for medication reminder",
                "Request for assistance with equipment",
                "General wellness check"
            ]
        }

        # Sample transcripts
        transcripts = [
            "Hello, I'm calling because I need help. I'm experiencing chest pain and having trouble breathing.",
            "My smoke detector is going off but I don't see any fire.",
            "I fell in the bathroom and I think I might have broken my arm.",
            "The carbon monoxide alarm is beeping and I'm not sure what to do.",
            "I'm feeling dizzy and my blood sugar might be low.",
            "There's water leaking from my ceiling.",
            "I fell down the stairs and I'm in a lot of pain.",
            "I need a medication reminder, I'm not sure if I took my evening pills.",
            "I'm experiencing a severe headache and feeling nauseous.",
            "My security alarm was triggered but I don't see anyone around."
        ]
        
        # Create calls for the past 30 days
        now = datetime.now()
        calls_to_create = []
        
        # Create 50 sample calls - fewer to avoid timeout
        for i in range(50):
            call_type = random.choice(call_types)
            random_days = random.randint(0, 30)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            
            call_datetime = now - timedelta(
                days=random_days,
                hours=random_hours,
                minutes=random_minutes
            )
            
            is_spam_values = ["SPAM", "NOT_SPAM", "NOT_SURE"]
            
            calls_to_create.append({
                "datetime": call_datetime,
                "callerId": random.choice(caller_ids),
                "callerNumber": random.choice(caller_numbers),
                "twilioNumber": random.choice(twilio_numbers),
                "callDuration": random.randint(60, 600),  # 1-10 minutes
                "callTranscript": random.choice(transcripts),
                "isSpam": random.choice(is_spam_values),
                "reason": random.choice(reasons[call_type]),
                "type": call_type,
            })
        
        # Create calls one by one to avoid timeout issues
        LOG.info(f"Creating {len(calls_to_create)} sample call records...")
        created_count = 0
        
        for call_data in calls_to_create:
            try:
                await prisma_client.callhistory.create(data=call_data)
                created_count += 1
                if created_count % 10 == 0:
                    LOG.info(f"Created {created_count} records so far...")
            except Exception as e:
                LOG.error(f"Error creating call record: {e}")
        
        LOG.info(f"Created {created_count} sample call records")
        LOG.info("Database seeding completed successfully")
    except Exception as e:
        LOG.error(f"Error seeding database: {e}")
        # Print more detailed error information
        import traceback
        LOG.error(traceback.format_exc())
    finally:
        await disconnect_prisma()


if __name__ == "__main__":
    asyncio.run(seed_database()) 