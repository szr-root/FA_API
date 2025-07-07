import base64
import json

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

decrypt_body = """
# 1.大小写转换
text = text.swapcase()
# print("======1..text",text)

# 2. 逆序
text = text[::-1]
# print("======2..text",text)

# 3. ASCII码-2
text = ''.join(chr(ord(c) - 2) for c in text)
# print("=======3..text",text)

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
# print("6..text",json_data)

"""

text = r"""?oVvdC[Zlf[\8kqlLu\dx{W|XGgeDp|kSoWFMCK1|I2l;5fW5Gi|DHZu{kw2iZXseWct8;NVMCZL|LxJX3ExkfDR[:pt49nJ;9[c1LRxrQ:P\FwfGDq-lpK2Tm[7GZg9XvOY\[SoQw|m6PgFzxTWtgFR[FC3voEk1dU76iCRIL|Cpm\1{7hp4H1:WpEQ;iEZ7kMkfW-qW22Yw5vUmI{3wQQfs\MqhD4GmFg[-Pgr5TF5;jG[{SLkvUy6i1\rMPEc6fiL7TW5ztt{IdCiOcWgfpEpWhVSoHG;3HLT4x9MPwJ2j{mhyq{xNYUJ8LP9eDlZyp4Zu5gJECc7ZTxDYrvTCeYH57ZSXYK{:N15NVy\hLkNZSNof9-2fP-lSvIUDi;ox-QIZzfE{5tnFVPE-KYe9M4EX7RcoQfv8{nrMmOL-w88ujN32Fh-E2s1|fSdWXWKhOet5Zn2eW2sk|TPmnUO{Y\h8DLKOSuY8Ky|yh2x76FivW6Svnu7QU2yKGoE;UG{MT;NhjfReHzhXpVEejp|UeR3-MJxjcXdSCunlZlpmG;PjTd:RFTo7f2Vn\fNFkNpd{px2g{t9XzCq\6:y|[;nwq5vlKPOOkZr[sz|nWXSpCpG1\dIx|ry6T|WnIpZtqTh|ClOs1qD[4gwIFl-VnfzNXUg5MdE13wpdU6c5h\|YSl"""

# 定义一个命名空间字典用于存储 exec 执行后的变量
namespace = {'text': text}

exec(decrypt_body, globals(), namespace)

# 从命名空间中获取 json_data
json_data_result = namespace.get('json_data', None)

# 输出结果
print(json_data_result)
