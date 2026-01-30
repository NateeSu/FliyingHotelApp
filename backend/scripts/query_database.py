"""
Quick Database Query Script
ดูข้อมูลในฐานข้อมูลแบบรวดเร็ว

Usage:
    docker-compose exec backend python scripts/query_database.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.room import Room, RoomStatus
from app.models.room_type import RoomType
from app.models.room_rate import RoomRate, StayType
from app.models.check_in import CheckIn, CheckInStatusEnum
from app.models.customer import Customer
from app.models.product import Product, ProductCategoryEnum
from app.models.system_setting import SystemSetting
from app.models.booking import Booking
from app.models.housekeeping_task import HousekeepingTask
from app.models.maintenance_task import MaintenanceTask


async def main():
    """Main function to query and display database statistics"""
    async with AsyncSessionLocal() as db:
        print("=" * 70)
        print("🏨 FlyingHotelApp - Database Overview")
        print("=" * 70)

        # ========== USERS ==========
        print("\n👥 USERS by Role:")
        stmt = select(User.role, func.count(User.id)).group_by(User.role)
        result = await db.execute(stmt)
        total_users = 0
        for role, count in result:
            print(f"   {role.value:15s}: {count:3d} users")
            total_users += count
        print(f"   {'TOTAL':15s}: {total_users:3d} users")

        # ========== ROOM TYPES ==========
        print("\n🏨 ROOM TYPES:")
        stmt = select(RoomType).where(RoomType.is_active == True)
        result = await db.execute(stmt)
        room_types = result.scalars().all()
        for rt in room_types:
            size_str = f"{rt.room_size_sqm:5.0f} ㎡" if rt.room_size_sqm else "N/A"
            bed_str = rt.bed_type if rt.bed_type else "N/A"
            print(f"   {rt.name:12s}: {rt.max_guests} guests, {size_str}, {bed_str}")

        # ========== ROOMS BY STATUS ==========
        print("\n🏠 ROOMS by Status:")
        stmt = select(Room.status, func.count(Room.id)).group_by(Room.status)
        result = await db.execute(stmt)
        total_rooms = 0
        for status, count in result:
            print(f"   {status.value:20s}: {count:3d} rooms")
            total_rooms += count
        print(f"   {'TOTAL':20s}: {total_rooms:3d} rooms")

        # ========== ROOMS BY FLOOR ==========
        print("\n📍 ROOMS by Floor:")
        stmt = select(Room.floor, func.count(Room.id)).group_by(Room.floor).order_by(Room.floor)
        result = await db.execute(stmt)
        for floor, count in result:
            print(f"   Floor {floor}:   {count:3d} rooms")

        # ========== ROOM RATES ==========
        print("\n💰 ROOM RATES:")
        stmt = select(RoomRate).options(
            selectinload(RoomRate.room_type)
        ).where(RoomRate.is_active == True).order_by(RoomRate.room_type_id, RoomRate.stay_type)
        result = await db.execute(stmt)
        rates = result.scalars().all()

        print(f"   {'Room Type':12s} {'Stay Type':12s} {'Rate':>10s}")
        print(f"   {'-'*12} {'-'*12} {'-'*10}")
        for rate in rates:
            print(f"   {rate.room_type.name:12s} {rate.stay_type.value:12s} ฿{rate.rate:>9,.2f}")

        # ========== PRODUCTS ==========
        print("\n🛍️ PRODUCTS:")
        stmt = select(Product.category, func.count(Product.id)).group_by(Product.category)
        result = await db.execute(stmt)
        total_products = 0
        for category, count in result:
            print(f"   {category.value:15s}: {count:3d} products")
            total_products += count
        print(f"   {'TOTAL':15s}: {total_products:3d} products")

        # ========== CUSTOMERS ==========
        print("\n👤 CUSTOMERS:")
        stmt = select(func.count(Customer.id))
        result = await db.execute(stmt)
        customer_count = result.scalar() or 0
        print(f"   Total Customers: {customer_count}")

        # ========== CHECK-INS ==========
        print("\n✅ CHECK-INS:")
        stmt = select(CheckIn.status, func.count(CheckIn.id)).group_by(CheckIn.status)
        result = await db.execute(stmt)
        checkins_data = list(result)

        if checkins_data:
            for status, count in checkins_data:
                print(f"   {status.value:15s}: {count:3d}")
        else:
            print("   No check-ins yet")

        # Active check-ins by stay type
        stmt = select(CheckIn.stay_type, func.count(CheckIn.id)).where(
            CheckIn.status == CheckInStatusEnum.CHECKED_IN
        ).group_by(CheckIn.stay_type)
        result = await db.execute(stmt)
        active_checkins = list(result)
        if active_checkins:
            print("\n   Active by Stay Type:")
            for stay_type, count in active_checkins:
                print(f"   - {stay_type.value:10s}: {count}")

        # ========== BOOKINGS ==========
        print("\n📅 BOOKINGS:")
        stmt = select(func.count(Booking.id))
        result = await db.execute(stmt)
        booking_count = result.scalar() or 0
        print(f"   Total Bookings: {booking_count}")

        if booking_count > 0:
            stmt = select(Booking.status, func.count(Booking.id)).group_by(Booking.status)
            result = await db.execute(stmt)
            for status, count in result:
                print(f"   - {status.value:15s}: {count}")

        # ========== HOUSEKEEPING TASKS ==========
        print("\n🧹 HOUSEKEEPING TASKS:")
        stmt = select(func.count(HousekeepingTask.id))
        result = await db.execute(stmt)
        hk_count = result.scalar() or 0
        print(f"   Total Tasks: {hk_count}")

        if hk_count > 0:
            stmt = select(HousekeepingTask.status, func.count(HousekeepingTask.id)).group_by(HousekeepingTask.status)
            result = await db.execute(stmt)
            for status, count in result:
                print(f"   - {status.value:15s}: {count}")

        # ========== MAINTENANCE TASKS ==========
        print("\n🔧 MAINTENANCE TASKS:")
        stmt = select(func.count(MaintenanceTask.id))
        result = await db.execute(stmt)
        mt_count = result.scalar() or 0
        print(f"   Total Tasks: {mt_count}")

        if mt_count > 0:
            stmt = select(MaintenanceTask.status, func.count(MaintenanceTask.id)).group_by(MaintenanceTask.status)
            result = await db.execute(stmt)
            for status, count in result:
                print(f"   - {status.value:15s}: {count}")

        # ========== SYSTEM SETTINGS ==========
        print("\n⚙️ SYSTEM SETTINGS:")
        stmt = select(func.count(SystemSetting.id))
        result = await db.execute(stmt)
        settings_count = result.scalar() or 0
        print(f"   Total Settings: {settings_count}")

        # Show some important settings
        important_keys = [
            'hotel_name',
            'temporary_stay_duration_hours',
            'overnight_checkout_time',
            'overtime_charge_rate'
        ]
        stmt = select(SystemSetting).where(SystemSetting.key.in_(important_keys))
        result = await db.execute(stmt)
        settings = result.scalars().all()

        if settings:
            print("\n   Key Settings:")
            for setting in settings:
                print(f"   - {setting.key:35s}: {setting.value}")

        print("\n" + "=" * 70)
        print("✅ Query completed successfully!")
        print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Query interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
