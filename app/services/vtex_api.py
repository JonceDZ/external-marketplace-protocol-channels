import requests
from app.config.settings import settings

class VTEXAPI:
    def validate_headers(self):
        print('====================================================================================================================================================================================')
        print("App Key:", self.app_key)
        print("App Token:", self.app_token)
        print("Nombre de la cuenta:", self.account_name)
        print("Base URL:", self.base_url)
        print("Headers:", self.headers)
        print('====================================================================================================================================================================================')
        
    def __init__(self):
        self.app_key = settings.vtex_app_key
        self.app_token = settings.vtex_app_token
        self.account_name = settings.vtex_account_name
        self.environment = "vtexcommercestable"
        self.base_url = f"https://{self.account_name}.{self.environment}.com.br"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-VTEX-API-AppKey": self.app_key,
            "X-VTEX-API-AppToken": self.app_token
        }

    def get_sku_ids_by_sales_channel(self, sales_channel_id):
        endpoint = f"{self.base_url}/api/catalog_system/pvt/sku/stockkeepingunitidsbysaleschannel/{sales_channel_id}"
        response = requests.get(endpoint, headers=self.headers)
        if response.status_code == 200:
            return response.json()  # Retorna una lista de SKU IDs
        else:
            raise Exception(f"Error al obtener SKUs: {response.status_code} - {response.text}")

    def get_sku_and_context(self, sku_id):
        endpoint = f"{self.base_url}/api/catalog_system/pvt/sku/stockkeepingunitbyid/{sku_id}"
        response = requests.get(endpoint, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error al obtener detalles del SKU {sku_id}: {response.status_code} - {response.text}")

    def simulate_fulfillment(self, items, sales_channel, affiliate_id=None):
        endpoint = f"{self.base_url}/api/checkout/pub/orderForms/simulation"
        params = {"sc": sales_channel}
        if affiliate_id:
            params["affiliateId"] = affiliate_id
        payload = {"items": items}
        response = requests.post(endpoint, headers=self.headers, json=payload, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error en la simulación de fulfillment: {response.status_code} - {response.text}")
               
