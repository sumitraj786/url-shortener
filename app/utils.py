import base64
import io

import qrcode

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

#may need refactoring based on the encoding requirements
def encode_base62(n: int) -> str:
    if n == 0:
        return BASE62[0]
    chars = []
    while n > 0:
        n, rem = divmod(n, 62)
        chars.append(BASE62[rem])
    return "".join(reversed(chars))


def generate_qr_code(data: str) -> str:
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()
