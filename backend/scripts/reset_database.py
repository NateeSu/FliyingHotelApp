"""
Database Reset Script - Complete reset and reseed database
Completely clears all data and reseeds with fresh test data

Usage:
    docker-compose exec backend python scripts/reset_database.py

This script will:
1. Drop all data from all tables (respecting foreign key constraints)
2. Reseed with fresh test data
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.session import AsyncSessionLocal, engine
from datetime import date
from app.models.user import User, UserRole
from app.models.room_type import RoomType
from app.models.room import Room, RoomStatus
from app.models.room_rate import RoomRate, StayType
from app.models.product import Product, ProductCategoryEnum
from app.models.system_setting import SystemSetting, SettingDataTypeEnum
from app.core.security import get_password_hash


async def clear_all_tables(db):
    """Clear all data from all tables in correct order"""
    print("\n" + "=" * 60)
    print("STEP 1: Clearing all existing data...")
    print("=" * 60)

    # Disable foreign key checks for MySQL
    await db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

    # List of tables in order to truncate (order matters less with FK checks disabled)
    tables = [
        # Dependent tables first
        "breaker_control_queue",
        "breaker_activity_logs",
        "breakers",
        "home_assistant_configs",
        "activity_logs",
        "notifications",
        "payments",
        "orders",
        "housekeeping_tasks",
        "maintenance_tasks",
        "check_ins",
        "bookings",
        "customers",
        "products",
        "room_rates",
        "rooms",
        "room_types",
        "system_settings",
        "users",
    ]

    for table in tables:
        try:
            await db.execute(text(f"TRUNCATE TABLE {table}"))
            print(f"   TRUNCATE TABLE {table}")
        except Exception as e:
            # Table might not exist, try DELETE instead
            try:
                await db.execute(text(f"DELETE FROM {table}"))
                print(f"   DELETE FROM {table}")
            except Exception as e2:
                print(f"   (skipped) {table}: {str(e2)[:50]}...")

    # Re-enable foreign key checks
    await db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    await db.commit()

    print("\nAll tables cleared successfully!")


async def seed_users(db):
    """Create default users"""
    print("\n" + "-" * 40)
    print("Creating Users...")
    print("-" * 40)

    users_data = [
        {
            "username": "admin",
            "password": "admin123",
            "full_name": "ผู้ดูแลระบบ",
            "role": UserRole.ADMIN,
        },
        {
            "username": "reception1",
            "password": "reception123",
            "full_name": "พนักงานต้อนรับ 1",
            "role": UserRole.RECEPTION,
        },
        {
            "username": "reception2",
            "password": "reception123",
            "full_name": "พนักงานต้อนรับ 2",
            "role": UserRole.RECEPTION,
        },
        {
            "username": "housekeeping1",
            "password": "house123",
            "full_name": "พนักงานทำความสะอาด 1",
            "role": UserRole.HOUSEKEEPING,
        },
        {
            "username": "housekeeping2",
            "password": "house123",
            "full_name": "พนักงานทำความสะอาด 2",
            "role": UserRole.HOUSEKEEPING,
        },
        {
            "username": "maintenance1",
            "password": "maint123",
            "full_name": "พนักงานซ่อมบำรุง",
            "role": UserRole.MAINTENANCE,
        }
    ]

    created_users = []
    for user_data in users_data:
        user = User(
            username=user_data["username"],
            password_hash=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"],
            is_active=True
        )
        db.add(user)
        created_users.append(user)
        print(f"   + {user_data['username']} ({user_data['role'].value})")

    await db.commit()

    # Refresh to get IDs
    for user in created_users:
        await db.refresh(user)

    print(f"   Total: {len(created_users)} users created")
    return created_users


async def seed_room_types(db):
    """Create room types"""
    print("\n" + "-" * 40)
    print("Creating Room Types...")
    print("-" * 40)

    room_types_data = [
        {
            "name": "Standard",
            "description": "ห้องพักมาตรฐาน พร้อมสิ่งอำนวยความสะดวกครบครัน",
            "amenities": ["TV", "แอร์", "ตู้เย็น", "น้ำอุ่น"],
            "max_guests": 2,
            "bed_type": "เตียงคู่",
            "room_size_sqm": 25.00
        },
        {
            "name": "Deluxe",
            "description": "ห้องพักระดับ Deluxe พื้นที่กว้างขวางกว่า พร้อมสิ่งอำนวยความสะดวกเพิ่มเติม",
            "amenities": ["TV", "แอร์", "ตู้เย็น", "น้ำอุ่น", "โซฟา", "โต๊ะทำงาน"],
            "max_guests": 2,
            "bed_type": "เตียงควีนไซส์",
            "room_size_sqm": 35.00
        },
        {
            "name": "VIP",
            "description": "ห้องพักระดับ VIP พื้นที่กว้างพิเศษ พร้อมสิ่งอำนวยความสะดวกครบครัน",
            "amenities": ["TV", "แอร์", "ตู้เย็น", "น้ำอุ่น", "โซฟา", "โต๊ะทำงาน", "อ่างอาบน้ำ", "ระเบียง"],
            "max_guests": 3,
            "bed_type": "เตียงคิงไซส์",
            "room_size_sqm": 45.00
        },
        {
            "name": "Suite",
            "description": "ห้องสวีท ห้องนอนแยก ห้องนั่งเล่นกว้างขวาง พร้อมสิ่งอำนวยความสะดวกครบครันที่สุด",
            "amenities": ["TV 2 เครื่อง", "แอร์", "ตู้เย็น", "น้ำอุ่น", "โซฟา", "โต๊ะทำงาน", "อ่างจากุซซี่", "ระเบียงใหญ่", "ห้องแต่งตัว"],
            "max_guests": 4,
            "bed_type": "เตียงคิงไซส์ + โซฟาเบด",
            "room_size_sqm": 60.00
        }
    ]

    created_room_types = []
    for rt_data in room_types_data:
        room_type = RoomType(**rt_data, is_active=True)
        db.add(room_type)
        created_room_types.append(room_type)
        print(f"   + {rt_data['name']} ({rt_data['room_size_sqm']} sqm, max {rt_data['max_guests']} guests)")

    await db.commit()

    # Refresh to get IDs
    for rt in created_room_types:
        await db.refresh(rt)

    print(f"   Total: {len(created_room_types)} room types created")
    return created_room_types


async def seed_rooms(db, room_types):
    """Create rooms across 3 floors"""
    print("\n" + "-" * 40)
    print("Creating Rooms...")
    print("-" * 40)

    room_types_map = {rt.name: rt for rt in room_types}

    rooms_data = []

    # Floor 1: 10 rooms (101-110) - 6 Standard, 4 Deluxe
    for i in range(1, 11):
        room_number = f"10{i}"
        room_type = "Standard" if i <= 6 else "Deluxe"
        rooms_data.append({
            "room_number": room_number,
            "floor": 1,
            "room_type_id": room_types_map[room_type].id,
            "status": RoomStatus.AVAILABLE
        })

    # Floor 2: 10 rooms (201-210) - 4 Standard, 4 Deluxe, 2 VIP
    for i in range(1, 11):
        room_number = f"20{i}"
        if i <= 4:
            room_type = "Standard"
        elif i <= 8:
            room_type = "Deluxe"
        else:
            room_type = "VIP"
        rooms_data.append({
            "room_number": room_number,
            "floor": 2,
            "room_type_id": room_types_map[room_type].id,
            "status": RoomStatus.AVAILABLE
        })

    # Floor 3: 10 rooms (301-310) - 2 Deluxe, 6 VIP, 2 Suite
    for i in range(1, 11):
        room_number = f"30{i}"
        if i <= 2:
            room_type = "Deluxe"
        elif i <= 8:
            room_type = "VIP"
        else:
            room_type = "Suite"
        rooms_data.append({
            "room_number": room_number,
            "floor": 3,
            "room_type_id": room_types_map[room_type].id,
            "status": RoomStatus.AVAILABLE
        })

    created_rooms = []
    for room_data in rooms_data:
        room = Room(**room_data, is_active=True)
        db.add(room)
        created_rooms.append(room)

    await db.commit()

    # Count by floor
    floor_counts = {}
    for r in rooms_data:
        floor_counts[r["floor"]] = floor_counts.get(r["floor"], 0) + 1

    for floor, count in sorted(floor_counts.items()):
        print(f"   + Floor {floor}: {count} rooms")

    print(f"   Total: {len(created_rooms)} rooms created")
    return created_rooms


async def seed_room_rates(db, room_types):
    """Create room rates for each room type"""
    print("\n" + "-" * 40)
    print("Creating Room Rates...")
    print("-" * 40)

    rates_data = {
        "Standard": {
            StayType.OVERNIGHT: 800.00,
            StayType.TEMPORARY: 300.00
        },
        "Deluxe": {
            StayType.OVERNIGHT: 1200.00,
            StayType.TEMPORARY: 450.00
        },
        "VIP": {
            StayType.OVERNIGHT: 1800.00,
            StayType.TEMPORARY: 650.00
        },
        "Suite": {
            StayType.OVERNIGHT: 2500.00,
            StayType.TEMPORARY: 900.00
        }
    }

    today = date.today()

    created_rates = []
    for room_type in room_types:
        for stay_type, rate_amount in rates_data[room_type.name].items():
            rate = RoomRate(
                room_type_id=room_type.id,
                stay_type=stay_type,
                rate=rate_amount,
                effective_from=today,
                effective_to=None,
                is_active=True
            )
            db.add(rate)
            created_rates.append(rate)
            print(f"   + {room_type.name} - {stay_type.value}: {rate_amount:,.0f} THB")

    await db.commit()
    print(f"   Total: {len(created_rates)} rates created")
    return created_rates


async def seed_products(db):
    """Create products (amenities & F&B)"""
    print("\n" + "-" * 40)
    print("Creating Products...")
    print("-" * 40)

    products_data = [
        # Room Amenities
        {"name": "ผ้าเช็ดตัวเพิ่ม", "category": ProductCategoryEnum.ROOM_AMENITY, "price": 50.00, "is_chargeable": True, "description": "ผ้าเช็ดตัวเพิ่มเติม"},
        {"name": "ผ้าห่มเพิ่ม", "category": ProductCategoryEnum.ROOM_AMENITY, "price": 100.00, "is_chargeable": True, "description": "ผ้าห่มเพิ่มเติม"},
        {"name": "หมอนเพิ่ม", "category": ProductCategoryEnum.ROOM_AMENITY, "price": 80.00, "is_chargeable": True, "description": "หมอนเพิ่มเติม"},
        {"name": "ชุดอาบน้ำ", "category": ProductCategoryEnum.ROOM_AMENITY, "price": 150.00, "is_chargeable": True, "description": "แชมพู ครีมนวดผม สบู่"},
        # Food & Beverage
        {"name": "น้ำดื่ม (ขวดเล็ก)", "category": ProductCategoryEnum.FOOD_BEVERAGE, "price": 15.00, "is_chargeable": True, "description": "น้ำดื่มขวด 600ml"},
        {"name": "น้ำดื่ม (ขวดใหญ่)", "category": ProductCategoryEnum.FOOD_BEVERAGE, "price": 25.00, "is_chargeable": True, "description": "น้ำดื่มขวด 1.5L"},
        {"name": "กาแฟสำเร็จรูป", "category": ProductCategoryEnum.FOOD_BEVERAGE, "price": 30.00, "is_chargeable": True, "description": "กาแฟ 3 in 1"},
        {"name": "ชาเขียว", "category": ProductCategoryEnum.FOOD_BEVERAGE, "price": 25.00, "is_chargeable": True, "description": "ชาเขียวพร้อมดื่ม"},
        {"name": "ขนมขบเคี้ยว", "category": ProductCategoryEnum.FOOD_BEVERAGE, "price": 35.00, "is_chargeable": True, "description": "ขนมอบกรอบ"},
        {"name": "มาม่า", "category": ProductCategoryEnum.FOOD_BEVERAGE, "price": 20.00, "is_chargeable": True, "description": "บะหมี่กึ่งสำเร็จรูป"},
        {"name": "ไข่ต้มกึ่งสุก (2 ฟอง)", "category": ProductCategoryEnum.FOOD_BEVERAGE, "price": 25.00, "is_chargeable": True, "description": "ไข่ต้มกึ่งสุก 2 ฟอง"},
        {"name": "โค้ก", "category": ProductCategoryEnum.FOOD_BEVERAGE, "price": 20.00, "is_chargeable": True, "description": "น้ำอัดลมโคคา-โคล่า"},
        {"name": "เป๊ปซี่", "category": ProductCategoryEnum.FOOD_BEVERAGE, "price": 20.00, "is_chargeable": True, "description": "น้ำอัดลมเป๊ปซี่"},
        {"name": "สไปรท์", "category": ProductCategoryEnum.FOOD_BEVERAGE, "price": 20.00, "is_chargeable": True, "description": "น้ำอัดลมสไปรท์"},
    ]

    amenity_count = 0
    fb_count = 0

    for product_data in products_data:
        product = Product(**product_data, is_active=True)
        db.add(product)
        if product_data["category"] == ProductCategoryEnum.ROOM_AMENITY:
            amenity_count += 1
        else:
            fb_count += 1

    await db.commit()
    print(f"   + Room Amenities: {amenity_count}")
    print(f"   + Food & Beverage: {fb_count}")
    print(f"   Total: {amenity_count + fb_count} products created")


async def seed_system_settings(db):
    """Create system settings"""
    print("\n" + "-" * 40)
    print("Creating System Settings...")
    print("-" * 40)

    settings_data = [
        {"key": "temporary_stay_duration_hours", "value": "3", "data_type": SettingDataTypeEnum.NUMBER, "description": "ระยะเวลาการพักชั่วคราว (ชั่วโมง)"},
        {"key": "overnight_checkin_time", "value": "14:00", "data_type": SettingDataTypeEnum.STRING, "description": "เวลาเช็คอินมาตรฐานสำหรับค้างคืน"},
        {"key": "overnight_checkout_time", "value": "12:00", "data_type": SettingDataTypeEnum.STRING, "description": "เวลาเช็คเอาท์มาตรฐานสำหรับค้างคืน"},
        {"key": "overtime_charge_rate", "value": "100", "data_type": SettingDataTypeEnum.NUMBER, "description": "อัตราค่าเกินเวลาต่อชั่วโมง (บาท)"},
        {"key": "booking_deposit_percentage", "value": "30", "data_type": SettingDataTypeEnum.NUMBER, "description": "เปอร์เซ็นต์เงินมัดจำการจอง (%)"},
        {"key": "booking_no_show_grace_period_minutes", "value": "60", "data_type": SettingDataTypeEnum.NUMBER, "description": "ระยะเวลาผ่อนผันสำหรับ No-Show (นาที)"},
        {"key": "telegram_enabled", "value": "false", "data_type": SettingDataTypeEnum.BOOLEAN, "description": "เปิดใช้งาน Telegram notifications"},
        {"key": "hotel_name", "value": "Flying Hotel", "data_type": SettingDataTypeEnum.STRING, "description": "ชื่อโรงแรม"},
        {"key": "hotel_address", "value": "123 ถนนพระราม 1 เขตปทุมวัน กรุงเทพฯ 10330", "data_type": SettingDataTypeEnum.STRING, "description": "ที่อยู่โรงแรม"},
        {"key": "hotel_phone", "value": "02-123-4567", "data_type": SettingDataTypeEnum.STRING, "description": "เบอร์โทรโรงแรม"},
        {"key": "hotel_email", "value": "info@flyinghotel.com", "data_type": SettingDataTypeEnum.STRING, "description": "อีเมลโรงแรม"},
    ]

    for setting_data in settings_data:
        setting = SystemSetting(**setting_data)
        db.add(setting)
        print(f"   + {setting_data['key']} = {setting_data['value']}")

    await db.commit()
    print(f"   Total: {len(settings_data)} settings created")


async def main():
    """Main function to reset and reseed database"""
    print("\n")
    print("=" * 60)
    print("    FlyingHotelApp - Database Reset & Reseed Script")
    print("=" * 60)
    print("\n*** WARNING: This will DELETE all existing data! ***\n")

    # Confirmation prompt (can be bypassed with --force flag)
    if len(sys.argv) < 2 or sys.argv[1] != "--force":
        confirm = input("Type 'yes' to confirm: ").strip().lower()
        if confirm != 'yes':
            print("\nOperation cancelled.")
            return

    async with AsyncSessionLocal() as db:
        try:
            # Step 1: Clear all data
            await clear_all_tables(db)

            # Step 2: Reseed all data
            print("\n" + "=" * 60)
            print("STEP 2: Seeding fresh data...")
            print("=" * 60)

            users = await seed_users(db)
            room_types = await seed_room_types(db)
            rooms = await seed_rooms(db, room_types)
            room_rates = await seed_room_rates(db, room_types)
            await seed_products(db)
            await seed_system_settings(db)

            # Summary
            print("\n" + "=" * 60)
            print("    DATABASE RESET COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("\n  Summary:")
            print(f"    - Users: {len(users)}")
            print(f"    - Room Types: {len(room_types)}")
            print(f"    - Rooms: {len(rooms)}")
            print(f"    - Room Rates: {len(room_rates)}")
            print(f"    - Products: 14")
            print(f"    - System Settings: 11")

            print("\n  Default Login Credentials:")
            print("    Admin:        admin / admin123")
            print("    Reception:    reception1 / reception123")
            print("    Housekeeping: housekeeping1 / house123")
            print("    Maintenance:  maintenance1 / maint123")

            print("\n  IMPORTANT: Change default passwords in production!")
            print("=" * 60 + "\n")

        except Exception as e:
            print(f"\nERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(main())
