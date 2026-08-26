import requests


class OTPService:
    def __init__(self):
        # URL de tu microservicio OTP (ajusta el puerto si corre en otro, ej: 8001/8080)
        self.base_url = "http://127.0.0.1:8000/api/v1/otp"
        self.system_token = "sys_876f57822168cd2c96d199bd426a3bf1900351cf05cf745e1a6c67e8"
        self.system_name = "service_signature"

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "X-System-Token": self.system_token
        }

    def solicitar_codigo(self, email, nombre_firmante):
        url = f"{self.base_url}/generate/"
        
        headers = {
            "Content-Type": "application/json",
            "X-System-Token": self.system_token
        }
        
        payload = {
            "email": email,
            "system_name": self.system_name,
            "nombre": nombre_firmante
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            data = response.json() if response.content else {}

           
            if response.status_code in [200, 201]:
                return {"status": "success", "data": data}

            # CAPTURA ESPECÍFICA DE BLOQUEO (403 / "status": "BLOCKED")
            if response.status_code == 403 or data.get("status") == "BLOCKED":
                mensaje_error = data.get("error", "El correo se encuentra temporalmente bloqueado.")
                retry_seconds = data.get("retry_after_seconds", 0)
                
                return {
                    "status": "error",
                    "blocked": True,
                    "message": mensaje_error,
                    "retry_after_seconds": retry_seconds
                }

            return {
                "status": "error",
                "message": data.get("error") or data.get("message") or f"Error en servicio OTP ({response.status_code})"
            }

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Error de conexión con el servicio OTP: {str(e)}"}

    def validar_codigo(self, email, codigo):
        url = f"{self.base_url}/verify/"
        headers = {
            "Content-Type": "application/json",
            "X-System-Token": self.system_token
        }
        payload = {
            "email": email,
            "system_name": self.system_name,
            "otp": str(codigo)
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            data = response.json() if response.content else {}

            # Caso de Éxito
            if response.status_code in [200, 201]:
                status_val = str(data.get('status', '')).upper()
                msg_val = str(data.get('message', '')).lower()

                if status_val in ['VERIFIED', 'OK', 'SUCCESS'] or 'verificado' in msg_val:
                    return {"valid": True, "status": "VERIFIED"}

            # Caso de Bloqueo (403 Forbidden o status == 'BLOCKED')
            if response.status_code == 403 or data.get('status') == 'BLOCKED':
                return {
                    "valid": False,
                    "blocked": True,
                    "status": "BLOCKED",
                    "message": data.get('error') or data.get('message') or "El correo ha sido bloqueado por reintentos fallidos."
                }

            # Caso de Código Incorrecto estándar
            return {
                "valid": False,
                "blocked": False,
                "message": data.get('error') or data.get('message') or "Código OTP inválido o expirado."
            }

        except requests.exceptions.RequestException as e:
            return {"valid": False, "blocked": False, "message": f"Error de conexión: {str(e)}"}