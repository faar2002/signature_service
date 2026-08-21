import requests

class OTPService:
    def __init__(self):
        self.base_url = "https://tu-microservicio-otp.com/api"
        self.api_token = "TU_BEARER_TOKEN"

    def solicitar_codigo(self, email, app_source):
        payload = {"email": email, "app_source": app_source}
        try:
            response = requests.post(
                f"{self.base_url}/generate/", 
                json=payload,
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return f"Error en servicio OTP: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error de conexión OTP: {str(e)}"

    def validar_codigo(self, email, codigo, app_source):
        payload = {"email": email, "otp_code": codigo, "app_source": app_source}
        try:
            response = requests.post(
                f"{self.base_url}/validate/", 
                json=payload,
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False