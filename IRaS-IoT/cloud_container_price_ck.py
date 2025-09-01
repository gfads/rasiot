import requests
import json
import boto3

# ----------- AWS Fargate (us-east-1) ----------------
def get_aws_fargate_price(region='US East (N. Virginia)'):
    client = boto3.client('pricing', region_name='us-east-1')  # AWS Pricing API só disponível na us-east-1

    def get_price(usage_type):
        resp = client.get_products(
            ServiceCode='AmazonECS',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': region},
                {'Type': 'TERM_MATCH', 'Field': 'usageType', 'Value': usage_type},
            ],
            MaxResults=1
        )
        data = json.loads(resp['PriceList'][0])
        terms = data['terms']['OnDemand']
        for term in terms.values():
            dims = term['priceDimensions']
            for dim in dims.values():
                return float(dim['pricePerUnit']['USD'])
        return None

    price_cpu = get_price('Fargate-vCPU-Hours')
    price_mem = get_price('Fargate-GB-Hours')
    return round(price_cpu + price_mem, 5) if price_cpu and price_mem else None
def get_aws_fargate_price_manual():
    """
        Exemplo baseado no plano VPS S da Contabo:
        €6.99/mês para 4 vCPU e 8 GB → aprox. €0.000243/vCPU+RAM/hora
        Convertido proporcionalmente para 1 vCPU, 1 GB: 0.00137 USD/hora
        """
    preco_usd_por_hora = 0.0137  # Valor proporcional estimado
    return round(preco_usd_por_hora, 5)




# ----------- Google Cloud Run -----------------------
def get_gcp_cloud_run_price():
    url = "https://cloudpricingcalculator.appspot.com/static/data/pricelist.json"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        cpu_price_per_sec = float(data['CP-COMPUTEENGINE-CLOUDRUN-CPU']['us'])  # USD/s
        mem_price_per_sec = float(data['CP-COMPUTEENGINE-CLOUDRUN-MEM']['us'])  # USD/s
        total = (cpu_price_per_sec + mem_price_per_sec) * 3600  # USD/hora
        return round(total, 5)
    except Exception as e:
        return f"GCP erro: {str(e)}"
def get_gcp_cloud_run_price_manual():
    """
           Exemplo baseado no plano VPS S da Contabo:
           €6.99/mês para 4 vCPU e 8 GB → aprox. €0.000243/vCPU+RAM/hora
           Convertido proporcionalmente para 1 vCPU, 1 GB: 0.00137 USD/hora
           """
    preco_usd_por_hora = 0.0127  # Valor proporcional estimado
    return round(preco_usd_por_hora, 5)


# ----------- Azure Container Instances (ACI) --------


import requests

def get_prices_by_product_and_region(product_name: str, region_name: str):
    url = "https://prices.azure.com/api/retail/prices"
    # Filtro combinado: productName e armRegionName
    params = {
        "$filter": f"productName eq '{product_name}' and armRegionName eq '{region_name}'"
    }

    prices = []
    next_link = url

    while next_link:
        response = requests.get(next_link, params=params if next_link == url else {})
        if response.status_code != 200:
            print(f"Erro na requisição: {response.status_code}")
            break

        data = response.json()
        for item in data.get("Items", []):
            prices.append({
                "region": item.get("armRegionName"),
                "meterName": item.get("meterName"),
                "retailPrice": item.get("retailPrice"),
                "unitOfMeasure": item.get("unitOfMeasure")
            })

        next_link = data.get("NextPageLink")

    return prices

def get_azure_cloud_run_price_manual():
    """
              Exemplo baseado no plano VPS S da Contabo:
              €6.99/mês para 4 vCPU e 8 GB → aprox. €0.000243/vCPU+RAM/hora
              Convertido proporcionalmente para 1 vCPU, 1 GB: 0.00137 USD/hora
              """
    preco_usd_por_hora = 0.0927  # Valor proporcional estimado
    return round(preco_usd_por_hora, 5)


# ----------- Contabo (manual) -----------------------
def get_contabo_price():
    """
    Exemplo baseado no plano VPS S da Contabo:
    €6.99/mês para 4 vCPU e 8 GB → aprox. €0.000243/vCPU+RAM/hora
    Convertido proporcionalmente para 1 vCPU, 1 GB: 0.00137 USD/hora
    """
    preco_usd_por_hora = 0.00137  # Valor proporcional estimado
    return round(preco_usd_por_hora, 5)

# ----------- Comparador geral -----------------------


def select_best_provider():
    aws = get_aws_fargate_price_manual()
    gcp = get_gcp_cloud_run_price_manual()
    azure = get_azure_cloud_run_price_manual()
    contabo = get_contabo_price()

    price = {
        "AWS Fargate": aws,
        "GCP Cloud Run": gcp,
        "Azure ACI": azure,
        "Contabo (manual)": contabo
    }

    best = None
    best_price = float('inf')
    for name, price in price.items():
        if isinstance(price, float) and price < best_price:
            best_price = price
            best = name

    return {
        "best_option": best,
        "price_usd_hour": price
    }

# ----------- Executar -------------------------------
if __name__ == "__main__":
    resultado = select_best_provider()
    print(json.dumps(resultado, indent=4))

