import base64
import json

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

txt=r"""

"""

# 1.大小写转换
text = txt.swapcase()

# 2. 逆序
text = text[::-1]

# 3. ASCII码-2
text = ''.join(chr(ord(c) - 2) for c in text)

# 4. Base64解码
try:
    decoded_data = base64.b64decode(text)
except Exception as e:
    # 处理Base64解码异常
    print("Base64 decode error:", e)
    decoded_data = b''

# 5. AES解密
try:
    key = base64.b64decode('GvyIymDJv32xXYlkgYzptV==')
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(decoded_data)
    unpadded_data = unpad(decrypted, AES.block_size, style='pkcs7')
    text = unpadded_data.decode('utf-8')
except Exception as e:
    # 处理AES解密异常
    print("AES decrypt error:", e)
    text = ''

# 6. 将字符串转换为JSON对象
try:
    json_data = json.loads(text)
except Exception as e:
    # 处理JSON解析异常
    print("JSON parse error:", e)
    json_data = {}
print("6..text",json_data)
res = []
ip_info = [ip_info for ip_info in json_data['console']['athwartship']]
print([ip['voice'] for ip in ip_info])
print(len(json_data['console']['athwartship']))

cccc = json_data['console']['athwartship']
count = 0
for iiii in cccc:
    if not iiii["thermocouples"]:
        count += 1


print(count)