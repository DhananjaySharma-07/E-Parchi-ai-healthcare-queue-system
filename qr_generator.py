import qrcode
import os

def generate_qr(hospital_id, output_path='static/qr_codes/', filename=None):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if not filename:
        filename = f"{hospital_id}.png"
    data = f"HOSPITAL_ID:{hospital_id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(os.path.join(output_path, filename))
    return filename