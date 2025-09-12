from urllib.parse import quote_plus
import hmac
import hashlib



class vnpay:
    def __init__(self):
        self.requestData = {}
        self.responseData = {}

    def get_payment_url(self, vnpay_payment_url, secret_key):
        # 1. Sắp xếp inputData theo key
        inputData = sorted(self.requestData.items())

        # 2. Build query string (dùng quote, KHÔNG dùng quote_plus)
        queryString = '&'.join(
            f"{key}={quote_plus(str(val))}"
            for key, val in inputData
        )

        # 3. Sinh mã hash từ query string
        hashValue = self.__hmacsha512(secret_key, queryString)

        # 4. Trả về link thanh toán đầy đủ
        paymentUrl = f"{vnpay_payment_url}?{queryString}&vnp_SecureHash={hashValue}"

        print("Raw data for hash:", queryString)
        print("HashValue:", hashValue)
        return paymentUrl

    def validate_response(self, secret_key):
        vnp_SecureHash = self.responseData.get("vnp_SecureHash")
        self.responseData.pop("vnp_SecureHash", None)
        self.responseData.pop("vnp_SecureHashType", None)

        # 1. Build data giống hệt lúc request
        inputData = sorted(self.responseData.items())
        hasData = '&'.join(
            f"{key}={quote_plus(str(val))}"  # SỬA LỖI: dùng quote_plus
            for key, val in inputData if key.startswith("vnp_")
        )

        # 2. Hash lại
        hashValue = self.__hmacsha512(secret_key, hasData)

        print("Validate debug:")
        print("Raw data for hash:", hasData)
        print("Our Hash:", hashValue)
        print("InputHash:", vnp_SecureHash)

        return vnp_SecureHash == hashValue

    @staticmethod
    def __hmacsha512(key, data):
        byteKey = key.encode("utf-8")
        byteData = data.encode("utf-8")
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def verify_return(query_params, secret_key):
    # Convert to dict
    vnp_data = dict(query_params)

    # Lấy SecureHash ra riêng
    vnp_secure_hash = vnp_data.pop("vnp_SecureHash", None)
    vnp_data.pop("vnp_SecureHashType", None)

    # Sắp xếp và mã hóa lại giá trị
    sorted_keys = sorted(vnp_data.keys())

    # Sửa lỗi ở đây: Sử dụng quote_plus để mã hóa giá trị
    raw_data = "&".join([f"{key}={quote_plus(str(vnp_data[key]))}" for key in sorted_keys])

    # Tính hash
    hmac_obj = hmac.new(secret_key.encode("utf-8"), raw_data.encode("utf-8"), hashlib.sha512)
    calculated_hash = hmac_obj.hexdigest()

    print("Raw data to hash:", raw_data)
    print("Calculated hash :", calculated_hash)
    print("Received hash   :", vnp_secure_hash)

    return calculated_hash == vnp_secure_hash