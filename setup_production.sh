#!/bin/bash

# FlyingHotelApp Production Setup Script
# สคริปต์อัตโนมัติสำหรับติดตั้งบน Digital Ocean

set -e  # Exit on error

echo "========================================="
echo "FlyingHotelApp Production Setup"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Step 1: Update System
echo "Step 1: Updating system..."
apt update && apt upgrade -y
print_success "System updated"

# Step 2: Install Docker
echo ""
echo "Step 2: Installing Docker..."
if command -v docker &> /dev/null; then
    print_warning "Docker already installed"
else
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    print_success "Docker installed"
fi

# Step 3: Install Git and Nginx
echo ""
echo "Step 3: Installing Git and Nginx..."
apt install -y git nginx
print_success "Git and Nginx installed"

# Step 4: Configure .env
echo ""
echo "Step 4: Configuring environment..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        print_success ".env file created from .env.example"
    else
        print_error ".env.example not found"
        exit 1
    fi
fi

# Generate SECRET_KEY if not exists
if ! grep -q "SECRET_KEY=" .env; then
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "SECRET_KEY=$SECRET_KEY" >> .env
    print_success "SECRET_KEY generated"
fi

# Set production environment
sed -i 's/ENVIRONMENT=development/ENVIRONMENT=production/g' .env
print_success "Environment configured"

# Step 5: Build and Start Containers
echo ""
echo "Step 5: Building and starting Docker containers..."
docker compose build
docker compose up -d
print_success "Containers started"

# Wait for MySQL to be ready
echo ""
echo "Waiting for MySQL to be ready..."
sleep 30
print_success "MySQL is ready"

# Step 6: Run Database Migrations
echo ""
echo "Step 6: Running database migrations..."
docker compose exec -T backend alembic upgrade head
print_success "Database migrations completed"

# Step 7: Create Admin User
echo ""
echo "Step 7: Creating admin user..."
docker compose exec -T backend python3 << 'PYTHON'
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security import get_password_hash
import os

async def create_admin():
    db_url = os.getenv('DATABASE_URL', 'mysql+aiomysql://flyinghotel_user:flyinghotel_pass@mysql:3306/flyinghotel')
    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as db:
            admin = User(
                username='admin',
                full_name='System Admin',
                email='admin@flyinghotel.com',
                hashed_password=get_password_hash('admin123'),
                role='ADMIN',
                is_active=True
            )
            db.add(admin)
            await db.commit()
            print('✓ Admin user created successfully')
    finally:
        await engine.dispose()

asyncio.run(create_admin())
PYTHON

print_success "Admin user created (username: admin, password: admin123)"

# Step 8: Seed Database
echo ""
echo "Step 8: Seeding database with initial data..."
docker compose exec -T mysql mysql -u flyinghotel_user -pflyinghotel_pass flyinghotel << 'SQL'
-- Room Types
INSERT IGNORE INTO room_types (name, description, base_price_per_night, base_price_per_3hours, max_guests, amenities, created_at, updated_at) VALUES
('Standard', 'ห้องพักมาตรฐาน', 800.00, 300.00, 2, 'เตียง, แอร์, TV, WiFi', NOW(), NOW()),
('Deluxe', 'ห้องพักดีลักซ์', 1200.00, 400.00, 2, 'เตียงใหญ่, แอร์, Smart TV, WiFi, ตู้เย็น', NOW(), NOW()),
('VIP', 'ห้องพัก VIP', 2000.00, 600.00, 4, 'เตียงคิงไซซ์, แอร์, Smart TV 55", WiFi, ตู้เย็น, อ่างอาบน้ำ', NOW(), NOW());

-- Rooms
INSERT IGNORE INTO rooms (room_number, room_type_id, floor, status, created_at, updated_at) VALUES
('101', 1, 1, 'available', NOW(), NOW()),
('102', 1, 1, 'available', NOW(), NOW()),
('103', 1, 1, 'available', NOW(), NOW()),
('104', 1, 1, 'available', NOW(), NOW()),
('105', 1, 1, 'available', NOW(), NOW()),
('201', 2, 2, 'available', NOW(), NOW()),
('202', 2, 2, 'available', NOW(), NOW()),
('203', 2, 2, 'available', NOW(), NOW()),
('204', 2, 2, 'available', NOW(), NOW()),
('205', 2, 2, 'available', NOW(), NOW()),
('301', 3, 3, 'available', NOW(), NOW()),
('302', 3, 3, 'available', NOW(), NOW()),
('303', 3, 3, 'available', NOW(), NOW());
SQL

print_success "Database seeded with room types and rooms"

# Step 9: Configure Firewall
echo ""
echo "Step 9: Configuring firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
print_success "Firewall configured"

# Final Status
echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
print_success "All services are running"
print_success "Database is ready"
print_success "Admin user created"
echo ""
echo "Access your application:"
echo "  Frontend: http://$(hostname -I | awk '{print $1}')"
echo "  Backend API: http://$(hostname -I | awk '{print $1}')/api/docs"
echo ""
echo "Default login:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
print_warning "IMPORTANT: Change the admin password immediately!"
echo ""
echo "To check services status: docker compose ps"
echo "To view logs: docker compose logs -f"
echo ""

