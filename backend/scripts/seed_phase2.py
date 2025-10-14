"""
Seed data script for Phase 2: Room Management

Creates:
- 3 room types (Standard, Deluxe, VIP)
- 10 rooms (distributed across 2 floors)
- 6 room rates (2 rates per room type: overnight & temporary)
"""
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.room_type import RoomType
from app.models.room import Room, RoomStatus
from app.models.room_rate import RoomRate, StayType
from datetime import date
import uuid


async def seed_phase2():
    """Main seeding function"""
    async with AsyncSessionLocal() as db:
        try:
            print("🌱 Starting Phase 2 seed data...")
            print("=" * 60)

            # 1. Create Room Types
            print("\n📦 Creating Room Types...")
            room_types_data = [
                {
                    "name": "Standard",
                    "description": "ห้องพักมาตรฐาน สะดวกสบาย เหมาะสำหรับนักท่องเที่ยว",
                    "amenities": ["ทีวี", "แอร์", "ตู้เย็น", "ห้องน้ำในตัว", "Wi-Fi ฟรี"],
                    "max_guests": 2,
                    "bed_type": "เตียงคู่",
                    "room_size_sqm": 25.00,
                    "is_active": True
                },
                {
                    "name": "Deluxe",
                    "description": "ห้องพักระดับดีลักซ์ พื้นที่กว้างขวาง สิ่งอำนวยความสะดวกครบครัน",
                    "amenities": ["ทีวี LED 42\"", "แอร์", "ตู้เย็น", "ห้องน้ำในตัว", "Wi-Fi ฟรี", "โต๊ะทำงาน", "โซฟานั่งเล่น"],
                    "max_guests": 3,
                    "bed_type": "เตียงคิงไซส์",
                    "room_size_sqm": 35.00,
                    "is_active": True
                },
                {
                    "name": "VIP",
                    "description": "ห้องพักระดับวีไอพี หรูหรา พิเศษสุด มีจากุซซี่",
                    "amenities": ["ทีวี LED 55\"", "แอร์", "ตู้เย็น", "ห้องน้ำในตัว", "Wi-Fi ฟรี", "โต๊ะทำงาน", "โซฟานั่งเล่น", "จากุซซี่", "ระเบียงส่วนตัว"],
                    "max_guests": 4,
                    "bed_type": "เตียงคิงไซส์ + โซฟาเบด",
                    "room_size_sqm": 50.00,
                    "is_active": True
                }
            ]

            created_room_types = []
            for data in room_types_data:
                # Check if room type already exists
                result = await db.execute(
                    select(RoomType).where(RoomType.name == data["name"])
                )
                existing = result.scalar_one_or_none()

                if existing:
                    print(f"  ⚠️  Room type '{data['name']}' already exists, skipping...")
                    created_room_types.append(existing)
                else:
                    room_type = RoomType(**data)
                    db.add(room_type)
                    await db.flush()
                    created_room_types.append(room_type)
                    print(f"  ✅ Created room type: {room_type.name} ({room_type.max_guests} guests, {room_type.room_size_sqm} sqm)")

            await db.commit()

            # 2. Create Rooms (10 rooms total)
            print("\n🏨 Creating Rooms...")
            rooms_data = [
                # Floor 1 - Standard (3 rooms) + Deluxe (2 rooms)
                {"room_number": "101", "room_type": "Standard", "floor": 1},
                {"room_number": "102", "room_type": "Standard", "floor": 1},
                {"room_number": "103", "room_type": "Standard", "floor": 1},
                {"room_number": "104", "room_type": "Deluxe", "floor": 1},
                {"room_number": "105", "room_type": "Deluxe", "floor": 1},

                # Floor 2 - Mixed (2 Standard + 2 Deluxe + 1 VIP)
                {"room_number": "201", "room_type": "Standard", "floor": 2},
                {"room_number": "202", "room_type": "Standard", "floor": 2},
                {"room_number": "203", "room_type": "Deluxe", "floor": 2},
                {"room_number": "204", "room_type": "VIP", "floor": 2},
                {"room_number": "205", "room_type": "VIP", "floor": 2},
            ]

            room_type_map = {rt.name: rt for rt in created_room_types}

            for data in rooms_data:
                room_type_name = data.pop("room_type")
                room_type = room_type_map[room_type_name]

                # Check if room already exists
                result = await db.execute(
                    select(Room).where(Room.room_number == data["room_number"])
                )
                existing = result.scalar_one_or_none()

                if existing:
                    print(f"  ⚠️  Room {data['room_number']} already exists, skipping...")
                else:
                    room = Room(
                        **data,
                        room_type_id=room_type.id,
                        status=RoomStatus.AVAILABLE,
                        qr_code=f"ROOM-{str(uuid.uuid4())[:8].upper()}",
                        is_active=True
                    )
                    db.add(room)
                    print(f"  ✅ Created room: {room.room_number} ({room_type_name}, Floor {data['floor']}, QR: {room.qr_code})")

            await db.commit()

            # 3. Create Room Rates (current rates)
            print("\n💰 Creating Room Rates...")
            room_rates_data = [
                # Standard
                {"room_type": "Standard", "stay_type": StayType.OVERNIGHT, "rate": 600.00},
                {"room_type": "Standard", "stay_type": StayType.TEMPORARY, "rate": 300.00},

                # Deluxe
                {"room_type": "Deluxe", "stay_type": StayType.OVERNIGHT, "rate": 900.00},
                {"room_type": "Deluxe", "stay_type": StayType.TEMPORARY, "rate": 450.00},

                # VIP
                {"room_type": "VIP", "stay_type": StayType.OVERNIGHT, "rate": 1500.00},
                {"room_type": "VIP", "stay_type": StayType.TEMPORARY, "rate": 750.00},
            ]

            for data in room_rates_data:
                room_type_name = data.pop("room_type")
                room_type = room_type_map[room_type_name]

                # Check if rate already exists
                result = await db.execute(
                    select(RoomRate).where(
                        RoomRate.room_type_id == room_type.id,
                        RoomRate.stay_type == data["stay_type"],
                        RoomRate.effective_from == date.today()
                    )
                )
                existing = result.scalar_one_or_none()

                if existing:
                    print(f"  ⚠️  Rate for {room_type_name} - {data['stay_type'].value} already exists, skipping...")
                else:
                    room_rate = RoomRate(
                        room_type_id=room_type.id,
                        stay_type=data["stay_type"],
                        rate=data["rate"],
                        effective_from=date.today(),
                        effective_to=None,  # No end date = current rate
                        is_active=True
                    )
                    db.add(room_rate)
                    print(f"  ✅ Created rate: {room_type_name} - {data['stay_type'].value} = {data['rate']:.2f} บาท")

            await db.commit()

            # 4. Summary
            print("\n" + "=" * 60)
            print("🎉 Phase 2 seed data completed successfully!")
            print("=" * 60)

            # Count totals
            room_types_count = await db.execute(select(RoomType))
            rooms_count = await db.execute(select(Room))
            rates_count = await db.execute(select(RoomRate))

            print(f"\n📊 Summary:")
            print(f"   - Room Types: {len(room_types_count.scalars().all())}")
            print(f"   - Rooms: {len(rooms_count.scalars().all())}")
            print(f"   - Room Rates: {len(rates_count.scalars().all())}")
            print()

        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(seed_phase2())
