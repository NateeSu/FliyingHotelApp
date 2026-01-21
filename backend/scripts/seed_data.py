"""
Seed Data Script - Import initial data to database
Run this script to populate the database with sample data

Usage:
    docker-compose exec backend python scripts/seed_data.py

This script will create:
- Default users (admin, reception, housekeeping, maintenance)
- Room types (Standard, Deluxe, VIP, Suite)
- Rooms (30 rooms across 3 floors)
- Room rates (overnight & temporary for each room type)
- Products (room amenities & food/beverages)
- System settings (default configurations)
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from datetime import date
from app.models.user import User, UserRole
from app.models.room_type import RoomType
from app.models.room import Room, RoomStatus
from app.models.room_rate import RoomRate, StayType
from app.models.product import Product, ProductCategoryEnum
from app.models.system_setting import SystemSetting, SettingDataTypeEnum
from app.core.security import get_password_hash


async def clear_all_data(db):
    """Clear all existing data (optional - use with caution!)"""
    print("⚠️  Clearing existing data...")

    # Delete in order to respect foreign key constraints
    await db.execute("DELETE FROM payments")
    await db.execute("DELETE FROM orders")
    await db.execute("DELETE FROM order_items")
    await db.execute("DELETE FROM housekeeping_tasks")
    await db.execute("DELETE FROM maintenance_tasks")
    await db.execute("DELETE FROM check_ins")
    await db.execute("DELETE FROM bookings")
    await db.execute("DELETE FROM notifications")
    await db.execute("DELETE FROM products")
    await db.execute("DELETE FROM room_rates")
    await db.execute("DELETE FROM rooms")
    await db.execute("DELETE FROM room_types")
    await db.execute("DELETE FROM system_settings")
    await db.execute("DELETE FROM users")

    await db.commit()
    print("✅ All data cleared")


async def seed_users(db):
    """Create default users"""
    print("\n📌 Creating users...")

    users_data = [
        {
            "username": "admin",
            "password": "admin123",  # CHANGE IN PRODUCTION!
            "full_name": "ผู้ดูแลระบบ",
            "role": UserRole.ADMIN,
            "telegram_user_id": None
        },
        {
            "username": "reception1",
            "password": "reception123",
            "full_name": "พนักงานต้อนรับ 1",
            "role": UserRole.RECEPTION,
            "telegram_user_id": None
        },
        {
            "username": "reception2",
            "password": "reception123",
            "full_name": "พนักงานต้อนรับ 2",
            "role": UserRole.RECEPTION,
            "telegram_user_id": None
        },
        {
            "username": "housekeeping1",
            "password": "house123",
            "full_name": "พนักงานทำความสะอาด 1",
            "role": UserRole.HOUSEKEEPING,
            "telegram_user_id": None
        },
        {
            "username": "housekeeping2",
            "password": "house123",
            "full_name": "พนักงานทำความสะอาด 2",
            "role": UserRole.HOUSEKEEPING,
            "telegram_user_id": None
        },
        {
            "username": "maintenance1",
            "password": "maint123",
            "full_name": "พนักงานซ่อมบำรุง",
            "role": UserRole.MAINTENANCE,
            "telegram_user_id": None
        }
    ]

    created_users = []
    for user_data in users_data:
        # Check if user already exists
        stmt = select(User).where(User.username == user_data["username"])
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"   ⚠️  User '{user_data['username']}' already exists, skipping...")
            created_users.append(existing_user)
            continue

        user = User(
            username=user_data["username"],
            password_hash=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"],
            telegram_user_id=user_data["telegram_user_id"],
            is_active=True
        )
        db.add(user)
        created_users.append(user)
        print(f"   ✅ Created user: {user_data['username']} ({user_data['role'].value})")

    await db.commit()
    print(f"✅ Created {len(created_users)} users")
    return created_users


async def seed_room_types(db):
    """Create room types"""
    print("\n📌 Creating room types...")

    room_types_data = [
        {
            "name": "Standard",
            "description": "ห้องพักมาตรฐาน พร้อมสิ่งอำนวยความสะดวกครบครัน",
            "amenities": ["TV", "แอร์", "ตู้เย็น", "น้ำอร้อน"],
            "max_guests": 2,
            "bed_type": "เตียงคู่",
            "room_size_sqm": 25.00
        },
        {
            "name": "Deluxe",
            "description": "ห้องพักระดับ Deluxe พื้นที่กว้างขวางกว่า พร้อมสิ่งอำนวยความสะดวกเพิ่มเติม",
            "amenities": ["TV", "แอร์", "ตู้เย็น", "น้ำอร้อน", "โซฟา", "โต๊ะทำงาน"],
            "max_guests": 2,
            "bed_type": "เตียงควีนไซส์",
            "room_size_sqm": 35.00
        },
        {
            "name": "VIP",
            "description": "ห้องพักระดับ VIP พื้นที่กว้างพิเศษ พร้อมสิ่งอำนวยความสะดวกครบครัน",
            "amenities": ["TV", "แอร์", "ตู้เย็น", "น้ำอร้อน", "โซฟา", "โต๊ะทำงาน", "อ่างอาบน้ำ", "ระเบียง"],
            "max_guests": 3,
            "bed_type": "เตียงคิงไซส์",
            "room_size_sqm": 45.00
        },
        {
            "name": "Suite",
            "description": "ห้องสวีท ห้องนอนแยก ห้องนั่งเล่นกว้างขวาง พร้อมสิ่งอำนวยความสะดวกครบครันที่สุด",
            "amenities": ["TV 2 เครื่อง", "แอร์", "ตู้เย็น", "น้ำอร้อน", "โซฟา", "โต๊ะทำงาน", "อ่างจากุซซี่", "ระเบียงใหญ่", "ห้องแต่งตัว"],
            "max_guests": 4,
            "bed_type": "เตียงคิงไซส์ + โซฟาเบด",
            "room_size_sqm": 60.00
        }
    ]

    created_room_types = []
    for rt_data in room_types_data:
        # Check if room type already exists
        stmt = select(RoomType).where(RoomType.name == rt_data["name"])
        result = await db.execute(stmt)
        existing_rt = result.scalar_one_or_none()

        if existing_rt:
            print(f"   ⚠️  Room type '{rt_data['name']}' already exists, skipping...")
            created_room_types.append(existing_rt)
            continue

        room_type = RoomType(**rt_data, is_active=True)
        db.add(room_type)
        created_room_types.append(room_type)
        print(f"   ✅ Created room type: {rt_data['name']}")

    await db.commit()

    # Refresh to get IDs
    for rt in created_room_types:
        await db.refresh(rt)

    print(f"✅ Created {len(created_room_types)} room types")
    return created_room_types


async def seed_rooms(db, room_types):
    """Create rooms across 3 floors"""
    print("\n📌 Creating rooms...")

    # Room distribution per floor:
    # Floor 1: 10 rooms (101-110) - 6 Standard, 4 Deluxe
    # Floor 2: 10 rooms (201-210) - 4 Standard, 4 Deluxe, 2 VIP
    # Floor 3: 10 rooms (301-310) - 2 Deluxe, 6 VIP, 2 Suite

    room_types_map = {rt.name: rt for rt in room_types}

    rooms_data = []

    # Floor 1
    for i in range(1, 11):
        room_number = f"10{i}"
        room_type = "Standard" if i <= 6 else "Deluxe"
        rooms_data.append({
            "room_number": room_number,
            "floor": 1,
            "room_type_id": room_types_map[room_type].id,
            "status": RoomStatus.AVAILABLE
        })

    # Floor 2
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

    # Floor 3
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
        # Check if room already exists
        stmt = select(Room).where(Room.room_number == room_data["room_number"])
        result = await db.execute(stmt)
        existing_room = result.scalar_one_or_none()

        if existing_room:
            print(f"   ⚠️  Room '{room_data['room_number']}' already exists, skipping...")
            created_rooms.append(existing_room)
            continue

        room = Room(**room_data, is_active=True)
        db.add(room)
        created_rooms.append(room)

    await db.commit()
    print(f"✅ Created {len(rooms_data)} rooms (30 rooms total)")
    return created_rooms


async def seed_room_rates(db, room_types):
    """Create room rates for each room type"""
    print("\n📌 Creating room rates...")

    # Rates structure: {room_type_name: {OVERNIGHT: rate, TEMPORARY: rate}}
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

    # Use today as effective_from date
    today = date.today()

    created_rates = []
    for room_type in room_types:
        for stay_type, rate_amount in rates_data[room_type.name].items():
            # Check if rate already exists
            stmt = select(RoomRate).where(
                RoomRate.room_type_id == room_type.id,
                RoomRate.stay_type == stay_type,
                RoomRate.effective_from == today
            )
            result = await db.execute(stmt)
            existing_rate = result.scalar_one_or_none()

            if existing_rate:
                print(f"   ⚠️  Rate for {room_type.name} ({stay_type.value}) already exists, skipping...")
                created_rates.append(existing_rate)
                continue

            rate = RoomRate(
                room_type_id=room_type.id,
                stay_type=stay_type,
                rate=rate_amount,
                effective_from=today,
                effective_to=None,  # NULL means current active rate
                is_active=True
            )
            db.add(rate)
            created_rates.append(rate)
            print(f"   ✅ Created rate: {room_type.name} - {stay_type.value} (฿{rate_amount})")

    await db.commit()
    print(f"✅ Created {len(created_rates)} room rates")
    return created_rates


async def seed_products(db):
    """Create products (amenities & F&B)"""
    print("\n📌 Creating products...")

    products_data = [
        # Room Amenities
        {
            "name": "ผ้าเช็ดตัวเพิ่ม",
            "category": ProductCategoryEnum.ROOM_AMENITY,
            "price": 50.00,
            "is_chargeable": True,
            "description": "ผ้าเช็ดตัวเพิ่มเติม"
        },
        {
            "name": "ผ้าห่มเพิ่ม",
            "category": ProductCategoryEnum.ROOM_AMENITY,
            "price": 100.00,
            "is_chargeable": True,
            "description": "ผ้าห่มเพิ่มเติม"
        },
        {
            "name": "หมอนเพิ่ม",
            "category": ProductCategoryEnum.ROOM_AMENITY,
            "price": 80.00,
            "is_chargeable": True,
            "description": "หมอนเพิ่มเติม"
        },
        {
            "name": "ชุดอาบน้ำ",
            "category": ProductCategoryEnum.ROOM_AMENITY,
            "price": 150.00,
            "is_chargeable": True,
            "description": "แชมพู ครีมนวดผม สบู่"
        },
        {
            "name": "น้ำดื่ม (ขวดเล็ก)",
            "category": ProductCategoryEnum.FOOD_BEVERAGE,
            "price": 15.00,
            "is_chargeable": True,
            "description": "น้ำดื่มขวด 600ml"
        },
        {
            "name": "น้ำดื่ม (ขวดใหญ่)",
            "category": ProductCategoryEnum.FOOD_BEVERAGE,
            "price": 25.00,
            "is_chargeable": True,
            "description": "น้ำดื่มขวด 1.5L"
        },
        {
            "name": "กาแฟสำเร็จรูป",
            "category": ProductCategoryEnum.FOOD_BEVERAGE,
            "price": 30.00,
            "is_chargeable": True,
            "description": "กาแฟ 3 in 1"
        },
        {
            "name": "ชาเขียว",
            "category": ProductCategoryEnum.FOOD_BEVERAGE,
            "price": 25.00,
            "is_chargeable": True,
            "description": "ชาเขียวพร้อมดื่ม"
        },
        {
            "name": "ขนมขบเคี้ยว",
            "category": ProductCategoryEnum.FOOD_BEVERAGE,
            "price": 35.00,
            "is_chargeable": True,
            "description": "ขนมอบกรอบ ขนมดัดแปลงรูป"
        },
        {
            "name": "มาม่า",
            "category": ProductCategoryEnum.FOOD_BEVERAGE,
            "price": 20.00,
            "is_chargeable": True,
            "description": "บะหมี่กึ่งสำเร็จรูป"
        },
        {
            "name": "ไข่ต้มกึ่งสุก (2 ฟอง)",
            "category": ProductCategoryEnum.FOOD_BEVERAGE,
            "price": 25.00,
            "is_chargeable": True,
            "description": "ไข่ต้มกึ่งสุก 2 ฟอง"
        },
        {
            "name": "โค้ก",
            "category": ProductCategoryEnum.FOOD_BEVERAGE,
            "price": 20.00,
            "is_chargeable": True,
            "description": "น้ำอัดลมโคคา-โคล่า"
        },
        {
            "name": "เป๊ปซี่",
            "category": ProductCategoryEnum.FOOD_BEVERAGE,
            "price": 20.00,
            "is_chargeable": True,
            "description": "น้ำอัดลมเป๊ปซี่"
        },
        {
            "name": "สไปรท์",
            "category": ProductCategoryEnum.FOOD_BEVERAGE,
            "price": 20.00,
            "is_chargeable": True,
            "description": "น้ำอัดลมสไปรท์"
        }
    ]

    created_products = []
    for product_data in products_data:
        # Check if product already exists
        stmt = select(Product).where(Product.name == product_data["name"])
        result = await db.execute(stmt)
        existing_product = result.scalar_one_or_none()

        if existing_product:
            print(f"   ⚠️  Product '{product_data['name']}' already exists, skipping...")
            created_products.append(existing_product)
            continue

        product = Product(**product_data, is_active=True)
        db.add(product)
        created_products.append(product)
        print(f"   ✅ Created product: {product_data['name']} (฿{product_data['price']})")

    await db.commit()
    print(f"✅ Created {len(created_products)} products")
    return created_products


async def seed_system_settings(db):
    """Create system settings"""
    print("\n📌 Creating system settings...")

    settings_data = [
        {
            "key": "temporary_stay_duration_hours",
            "value": "3",
            "data_type": SettingDataTypeEnum.NUMBER,
            "description": "ระยะเวลาการพักชั่วคราว (ชั่วโมง)"
        },
        {
            "key": "overnight_checkin_time",
            "value": "14:00",
            "data_type": SettingDataTypeEnum.STRING,
            "description": "เวลาเช็คอินมาตรฐานสำหรับค้างคืน"
        },
        {
            "key": "overnight_checkout_time",
            "value": "12:00",
            "data_type": SettingDataTypeEnum.STRING,
            "description": "เวลาเช็คเอาท์มาตรฐานสำหรับค้างคืน"
        },
        {
            "key": "overtime_charge_rate",
            "value": "100",
            "data_type": SettingDataTypeEnum.NUMBER,
            "description": "อัตราค่าเกินเวลาต่อชั่วโมง (บาท)"
        },
        {
            "key": "booking_deposit_percentage",
            "value": "30",
            "data_type": SettingDataTypeEnum.NUMBER,
            "description": "เปอร์เซ็นต์เงินมัดจำการจอง (%)"
        },
        {
            "key": "booking_no_show_grace_period_minutes",
            "value": "60",
            "data_type": SettingDataTypeEnum.NUMBER,
            "description": "ระยะเวลาผ่อนผันสำหรับ No-Show (นาที)"
        },
        {
            "key": "telegram_enabled",
            "value": "false",
            "data_type": SettingDataTypeEnum.BOOLEAN,
            "description": "เปิดใช้งาน Telegram notifications"
        },
        {
            "key": "hotel_name",
            "value": "Flying Hotel",
            "data_type": SettingDataTypeEnum.STRING,
            "description": "ชื่อโรงแรม"
        },
        {
            "key": "hotel_address",
            "value": "123 ถนนพระราม 1 เขตปทุมวัน กรุงเทพฯ 10330",
            "data_type": SettingDataTypeEnum.STRING,
            "description": "ที่อยู่โรงแรม"
        },
        {
            "key": "hotel_phone",
            "value": "02-123-4567",
            "data_type": SettingDataTypeEnum.STRING,
            "description": "เบอร์โทรโรงแรม"
        },
        {
            "key": "hotel_email",
            "value": "info@flyinghotel.com",
            "data_type": SettingDataTypeEnum.STRING,
            "description": "อีเมลโรงแรม"
        }
    ]

    created_settings = []
    for setting_data in settings_data:
        # Check if setting already exists
        stmt = select(SystemSetting).where(SystemSetting.key == setting_data["key"])
        result = await db.execute(stmt)
        existing_setting = result.scalar_one_or_none()

        if existing_setting:
            print(f"   ⚠️  Setting '{setting_data['key']}' already exists, skipping...")
            created_settings.append(existing_setting)
            continue

        setting = SystemSetting(**setting_data)
        db.add(setting)
        created_settings.append(setting)
        print(f"   ✅ Created setting: {setting_data['key']} = {setting_data['value']}")

    await db.commit()
    print(f"✅ Created {len(created_settings)} system settings")
    return created_settings


async def main():
    """Main function to seed all data"""
    print("=" * 60)
    print("🌱 FlyingHotelApp - Database Seed Script")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        try:
            # Ask user if they want to clear existing data
            print("\n⚠️  WARNING: Do you want to clear all existing data first?")
            print("   Type 'yes' to clear, or press Enter to skip:")
            # Note: In Docker environment, you might want to comment this out
            # and set clear_data = False directly
            # clear_response = input("   > ").strip().lower()
            # clear_data = clear_response == 'yes'

            # For automated scripts, set this to False
            clear_data = False

            if clear_data:
                await clear_all_data(db)

            # Seed all data
            users = await seed_users(db)
            room_types = await seed_room_types(db)
            rooms = await seed_rooms(db, room_types)
            room_rates = await seed_room_rates(db, room_types)
            products = await seed_products(db)
            settings = await seed_system_settings(db)

            print("\n" + "=" * 60)
            print("✅ Database seeding completed successfully!")
            print("=" * 60)
            print("\n📊 Summary:")
            print(f"   - Users: {len(users)}")
            print(f"   - Room Types: {len(room_types)}")
            print(f"   - Rooms: {len(rooms)}")
            print(f"   - Room Rates: {len(room_rates)}")
            print(f"   - Products: {len(products)}")
            print(f"   - System Settings: {len(settings)}")
            print("\n🔐 Default Login Credentials:")
            print("   Admin: admin / admin123")
            print("   Reception: reception1 / reception123")
            print("   Housekeeping: housekeeping1 / house123")
            print("   Maintenance: maintenance1 / maint123")
            print("\n⚠️  IMPORTANT: Change default passwords in production!")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Error during seeding: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(main())
