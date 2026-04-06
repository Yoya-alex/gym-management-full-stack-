from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A5


def generate_member_card_pdf(member):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A5))
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 180, "MY GYM - Member Card")
    p.setFont("Helvetica", 12)
    p.drawString(50, 150, f"Name: {member.first_name} {member.last_name}")
    p.drawString(50, 130, f"CIN: {member.cin}")
    p.drawString(50, 110, f"Phone: {member.phone_number}")
    p.drawString(50, 90, f"Birthday: {member.birthday}")
    p.drawString(50, 70, f"Gender: {member.gender}")
    p.showPage()
    p.save()
    return buffer.getvalue()
