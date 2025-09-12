from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from app import app

import qrcode
from io import BytesIO

def cart_stats(cart):
    total, total_ticket = 0, 0
    if cart:
        for c in cart.values():
            total += c['quantity'] * c['price']
            total_ticket += c['quantity']
        return {
            'total': total,
            'total_ticket': total_ticket
        }
    else:
        return {
            'total': 0,
            'total_ticket': 0
        }


def generate_qr_code_bytes(data: str) -> bytes:
    """Tạo QR code và trả về raw bytes."""
    qr_img = qrcode.make(data)
    img_io = BytesIO()
    qr_img.save(img_io, format="PNG")
    img_io.seek(0)
    return img_io.read()


def send_invoice(to_email, bill, cart):

    qr_bytes = generate_qr_code_bytes(f"BillID:{bill.id}|User:{bill.user_id}")

    msg = MIMEMultipart('related')  # Để hỗ trợ inline images
    msg['Subject'] = f"Hóa đơn #{bill.id} - Thanh toán thành công"
    msg['From'] = app.config['MAIL_USERNAME']
    msg['To'] = to_email


    # Nội dung email (HTML)
    try:
        items_html = "".join(
            f"<li>{item['type']} - SL: {item['quantity']} - Giá: {item['price']} VND</li>"
            for item in cart.values()
        )
    except AttributeError:
        items_html = "".join(
            f"<li>{item['type']} - SL: {item['quantity']} - Giá: {item['price']} VND</li>"
            for item in cart
        )

    html_body = f"""
            <h3>Cảm ơn bạn đã mua vé!</h3>
            <p>Mã hóa đơn: <b>{bill.id}</b></p>
            <p>Tổng tiền: <b>{bill.total_price} VND</b></p>
            <p>Chi tiết:</p>
            <ul>{items_html}</ul>
            <p>Quét mã QR này để check-in sự kiện:</p>
            <img src="cid:qrimage" alt="QR Code" style="width: 200px; height: 200px;"/>
        """
    msg.attach(MIMEText(html_body, 'html'))

    # --- Gắn QR code inline ---
    image = MIMEImage(qr_bytes, 'png')
    image.add_header('Content-ID', '<qrimage>')
    image.add_header('Content-Disposition', 'inline', filename="qr_code.png")
    msg.attach(image)

    try:
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.sendmail(app.config['MAIL_USERNAME'], to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
