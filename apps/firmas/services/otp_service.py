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

    def solicitar_codigo(self, email, nombre):
        """
        Genera y envía el código OTP mediante el endpoint /generate/
        """
        url = f"{self.base_url}/generate/"
        payload = {
            "email": email,
            "system_name": self.system_name,
            "nombre": nombre
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )

            # Si la respuesta es exitosa (200 o 201)
            if response.status_code in (200, 201):
                return response.json()

            # Si devuelve error controlado (ej: 400, 404 correo suspendido)
            return f"Error en servicio OTP: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            return f"Error de conexión con servicio OTP: {str(e)}"

    def validar_codigo(self, email, codigo):
        """
        Valida el código de 6 dígitos con el endpoint /verify/
        """
        url = f"{self.base_url}/verify/"
        
        headers = {
            "Content-Type": "application/json",
            "X-System-Token": self.system_token
        }
        
        # Mapeo exacto según tu estructura
        payload = {
            "email": email,
            "system_name": self.system_name,
            "otp": str(codigo)
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                # Leemos los campos devueltos por tu microservicio OTP
                status_val = str(data.get('status', '')).upper()
                msg_val = str(data.get('message', '')).lower()

                # Comprobamos la respuesta exacta: "VERIFIED"
                if status_val == 'VERIFIED' or 'verificado' in msg_val:
                    return True
                
                # Evaluaciones adicionales de respaldo
                if status_val in ['OK', 'SUCCESS', 'TRUE'] or data.get('valid') is True:
                    return True

            return False
            
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión en validar_codigo: {e}")
            return False