import qrcode
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A5
from reportlab.lib.utils import ImageReader


def generate_member_card_pdf(member):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A5))
    width, height = landscape(A5)

    # Background
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.rect(0, 0, width, height, fill=1)

    # Header bar
    p.setFillColorRGB(0.2, 0.6, 0.3)
    p.rect(0, height - 50, width, 50, fill=1)

    # Title
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(20, height - 35, "MY GYM - Membership Card")

    # Member details
    p.setFont("Helvetica-Bold", 13)
    p.setFillColorRGB(0.2, 0.8, 0.4)
    p.drawString(20, height - 80, f"{member.first_name} {member.last_name}")

    p.setFont("Helvetica", 11)
    p.setFillColorRGB(0.9, 0.9, 0.9)
    details = [
        f"ID:       {member.cin}",
        f"Phone:    {member.phone_number}",
        f"Gender:   {member.gender}",
        f"Birthday: {member.birthday}",
        f"Sport:    {member.sport_type.name if member.sport_type else 'N/A'}",
        f"Trainer:  {member.trainer.first_name + ' ' + member.trainer.last_name if member.trainer else 'N/A'}",
        f"Valid Until: {member.membership_end or 'N/A'}",
    ]
    y = height - 105
    for line in details:
        p.drawString(20, y, line)
        y -= 20

    # QR Code
    qr_data = f"GYM-MEMBER|{member.cin}|{member.first_name} {member.last_name}"
    qr = qrcode.make(qr_data)
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_image = ImageReader(qr_buffer)
    p.drawImage(qr_image, width - 130, height - 190, width=110, height=110)

    p.showPage()
    p.save()
    return buffer.getvalue()


def generate_invoice_pdf(payment):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, 800, "MY GYM - Payment Invoice")

    p.setFont("Helvetica", 12)
    p.drawString(50, 760, f"Invoice Date: {payment.date.strftime('%Y-%m-%d') if payment.date else 'N/A'}")
    p.drawString(50, 740, f"Member: {payment.member.first_name} {payment.member.last_name}")
    p.drawString(50, 720, f"Member ID: {payment.member.cin}")
    p.drawString(50, 700, f"Sport Type: {payment.sport_type.name if payment.sport_type else 'N/A'}")
    p.drawString(50, 680, f"Months: {payment.months}")
    p.drawString(50, 660, f"Amount Paid: ${payment.amount}")
    p.drawString(50, 640, f"Remaining Credit: ${payment.credit}")
    p.drawString(50, 620, f"Payment Type: {payment.payment_type.upper()}")
    p.drawString(50, 600, f"Status: {payment.status.upper()}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 560, "Thank you for your payment!")

    p.showPage()
    p.save()
    return buffer.getvalue()
