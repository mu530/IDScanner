import qrcode
import urllib.parse
from io import BytesIO
from django.core.files import File


def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # url = 'http://10.139.191.133:8000/view_card/?' + \
    #     urllib.parse.urlencode(data)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    image = File(buf, name=f"{data}.png")
    return image
