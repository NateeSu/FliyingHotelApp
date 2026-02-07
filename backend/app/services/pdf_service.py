"""
PDF Service (Phase 4)
Handles PDF receipt generation for check-outs
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from typing import Optional
import os
import logging

from app.models import CheckIn, Customer, Room, RoomType, User
from app.schemas.check_in import CheckOutSummary

logger = logging.getLogger(__name__)


class PDFService:
    """Service for generating PDF receipts"""

    def __init__(self):
        """Initialize PDF service with Thai font support"""
        # Register Thai font (using Sarabun from Thai TLWG fonts)
        try:
            # Try Sarabun first (best for Thai)
            font_paths = [
                "/usr/share/fonts/truetype/tlwg/Sawasdee.ttf",
                "/usr/share/fonts/truetype/tlwg/Garuda.ttf",
                "/usr/share/fonts/truetype/tlwg/Laksaman.ttf",
            ]

            font_loaded = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('ThaiFont', font_path))
                    self.thai_font = 'ThaiFont'
                    font_loaded = True
                    logger.info("Loaded Thai font from: %s", font_path)
                    break

            if not font_loaded:
                logger.warning("No Thai font found, using Helvetica")
                self.thai_font = 'Helvetica'
        except Exception as e:
            logger.warning("Could not load Thai font: %s", e)
            self.thai_font = 'Helvetica'

    def generate_receipt(
        self,
        check_in: CheckIn,
        customer: Customer,
        room: Room,
        room_type: RoomType,
        checkout_summary: CheckOutSummary,
        checked_out_by: Optional[User] = None,
        hotel_name: str = "Flying Hotel",
        hotel_address: str = "123 ถนนสุขุมวิท กรุงเทพฯ 10110",
        hotel_phone: str = "02-123-4567"
    ) -> BytesIO:
        """
        Generate PDF receipt for check-out

        Args:
            check_in: CheckIn record
            customer: Customer record
            room: Room record
            room_type: RoomType record
            checkout_summary: CheckOutSummary with calculated amounts
            checked_out_by: User who processed the check-out
            hotel_name: Hotel name for receipt header
            hotel_address: Hotel address for receipt header
            hotel_phone: Hotel phone for receipt header

        Returns:
            BytesIO: PDF file as bytes
        """
        # Create BytesIO buffer
        buffer = BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )

        # Container for the 'Flowable' objects
        elements = []

        # Styles
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=self.thai_font,
            fontSize=20,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=10,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=self.thai_font,
            fontSize=14,
            textColor=colors.HexColor('#424242'),
            spaceAfter=10,
            spaceBefore=10
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=self.thai_font,
            fontSize=11,
            alignment=TA_LEFT
        )

        center_style = ParagraphStyle(
            'CustomCenter',
            parent=styles['Normal'],
            fontName=self.thai_font,
            fontSize=11,
            alignment=TA_CENTER
        )

        # Header - Hotel Info
        elements.append(Paragraph(hotel_name, title_style))
        elements.append(Paragraph(f"{hotel_address}", center_style))
        elements.append(Paragraph(f"โทร: {hotel_phone}", center_style))
        elements.append(Spacer(1, 10*mm))

        # Receipt Title
        elements.append(Paragraph("ใบเสร็จรับเงิน / RECEIPT", heading_style))
        elements.append(Spacer(1, 5*mm))

        # Receipt Info
        receipt_no = f"R{check_in.id:06d}"
        checkout_date = check_in.actual_check_out_time or datetime.now()

        receipt_info_data = [
            ["เลขที่ใบเสร็จ / Receipt No:", receipt_no],
            ["วันที่ / Date:", checkout_date.strftime("%d/%m/%Y %H:%M")],
        ]

        if checked_out_by:
            receipt_info_data.append(["ผู้ออกใบเสร็จ / Issued by:", checked_out_by.full_name])

        receipt_info_table = Table(receipt_info_data, colWidths=[80*mm, 80*mm])
        receipt_info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.thai_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        elements.append(receipt_info_table)
        elements.append(Spacer(1, 8*mm))

        # Customer & Room Info
        elements.append(Paragraph("ข้อมูลลูกค้า / Customer Information", heading_style))

        customer_data = [
            ["ชื่อ / Name:", customer.full_name],
            ["เบอร์โทร / Phone:", customer.phone_number or "-"],
            ["ห้อง / Room:", f"{room.room_number} ({room_type.name})"],
            ["เช็คอิน / Check-in:", check_in.check_in_time.strftime("%d/%m/%Y %H:%M")],
            ["เช็คเอาท์ / Check-out:", checkout_date.strftime("%d/%m/%Y %H:%M")],
        ]

        # Add stay type
        stay_type_thai = "ค้างคืน" if check_in.stay_type == "overnight" else "ชั่วคราว"
        customer_data.append(["ประเภท / Stay Type:", stay_type_thai])

        if check_in.stay_type == "overnight" and check_in.number_of_nights:
            customer_data.append(["จำนวนคืน / Nights:", str(check_in.number_of_nights)])

        customer_table = Table(customer_data, colWidths=[60*mm, 100*mm])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.thai_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(customer_table)
        elements.append(Spacer(1, 8*mm))

        # Charges breakdown
        elements.append(Paragraph("รายการค่าใช้จ่าย / Charges", heading_style))

        # Build charges table
        charges_data = [
            ["รายการ / Description", "จำนวนเงิน / Amount"]
        ]

        # Base amount
        base_desc = "ค่าห้องพัก / Room Charge"
        if check_in.stay_type == "overnight" and check_in.number_of_nights:
            base_desc += f" ({check_in.number_of_nights} คืน / nights)"
        charges_data.append([base_desc, f"฿{checkout_summary.base_amount:,.2f}"])

        # Overtime charges
        if checkout_summary.is_overtime and checkout_summary.overtime_charge > 0:
            overtime_desc = f"ค่าล่วงเวลา / Overtime ({checkout_summary.overtime_hours:.1f} ชม./hrs)"
            charges_data.append([overtime_desc, f"฿{checkout_summary.overtime_charge:,.2f}"])

        # Extra charges
        if check_in.extra_charges and check_in.extra_charges > 0:
            charges_data.append(["ค่าใช้จ่ายเพิ่มเติม / Extra Charges", f"฿{check_in.extra_charges:,.2f}"])

        # Discount
        if check_in.discount_amount and check_in.discount_amount > 0:
            discount_desc = "ส่วนลด / Discount"
            if check_in.discount_reason:
                discount_desc += f" ({check_in.discount_reason})"
            charges_data.append([discount_desc, f"-฿{check_in.discount_amount:,.2f}"])

        # Separator line
        charges_data.append(["", ""])

        # Total
        charges_data.append(["รวมทั้งสิ้น / TOTAL", f"฿{check_in.total_amount:,.2f}"])

        charges_table = Table(charges_data, colWidths=[120*mm, 40*mm])
        charges_table.setStyle(TableStyle([
            # Header row
            ('FONTNAME', (0, 0), (-1, 0), self.thai_font),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E3F2FD')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (1, 0), self.thai_font),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -3), self.thai_font),
            ('FONTSIZE', (0, 1), (-1, -3), 10),
            ('ALIGN', (0, 1), (0, -3), 'LEFT'),
            ('ALIGN', (1, 1), (1, -3), 'RIGHT'),

            # Separator line
            ('LINEABOVE', (0, -2), (-1, -2), 1, colors.grey),

            # Total row
            ('FONTNAME', (0, -1), (-1, -1), self.thai_font),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1976D2')),
            ('ALIGN', (0, -1), (0, -1), 'LEFT'),
            ('ALIGN', (1, -1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (1, -1), self.thai_font),

            # Grid
            ('BOX', (0, 0), (-1, -3), 1, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.grey),
        ]))
        elements.append(charges_table)
        elements.append(Spacer(1, 8*mm))

        # Payment method
        payment_method_thai = {
            "cash": "เงินสด",
            "transfer": "โอนเงิน",
            "credit_card": "บัตรเครดิต"
        }.get(check_in.payment_method, check_in.payment_method)

        payment_info = f"วิธีชำระเงิน / Payment Method: {payment_method_thai}"
        elements.append(Paragraph(payment_info, normal_style))
        elements.append(Spacer(1, 10*mm))

        # Footer
        elements.append(Spacer(1, 15*mm))
        footer_text = "ขอบคุณที่ใช้บริการ / Thank you for your stay!"
        elements.append(Paragraph(footer_text, center_style))

        footer_note = "*** ใบเสร็จฉบับนี้สร้างโดยระบบอัตโนมัติ / This receipt is computer generated ***"
        elements.append(Paragraph(footer_note, center_style))

        # Build PDF
        doc.build(elements)

        # Get PDF content
        buffer.seek(0)
        return buffer
