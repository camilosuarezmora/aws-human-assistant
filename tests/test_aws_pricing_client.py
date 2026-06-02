import json
from unittest.mock import MagicMock

from backend.aws_pricing_client import (
    extraer_precio_on_demand_usd,
    filtros_ec2,
    filtros_rds,
    get_products,
    precio_on_demand_hora,
)


def test_extraer_precio_on_demand_usd(ec2_product):
    assert extraer_precio_on_demand_usd(ec2_product) == 0.0104


def test_extraer_precio_sin_on_demand():
    assert extraer_precio_on_demand_usd({}) is None


def test_filtros_ec2_incluyen_region_e_instancia():
    filtros = filtros_ec2('t3.micro', 'us-east-1')
    fields = {f['Field']: f['Value'] for f in filtros}
    assert fields['regionCode'] == 'us-east-1'
    assert fields['instanceType'] == 't3.micro'
    assert fields['operatingSystem'] == 'Linux'


def test_filtros_rds_mysql_single_az():
    filtros = filtros_rds('db.t3.micro', 'eu-west-1')
    fields = {f['Field']: f['Value'] for f in filtros}
    assert fields['databaseEngine'] == 'MySQL'
    assert fields['deploymentOption'] == 'Single-AZ'


def test_get_products_parsea_price_list(ec2_product):
    client = MagicMock()
    client.get_products.return_value = {
        'PriceList': [json.dumps(ec2_product)],
    }
    products = get_products('AmazonEC2', filtros_ec2('t3.micro', 'us-east-1'), client=client)
    assert len(products) == 1
    assert products[0]['terms']['OnDemand']


def test_get_products_api_error_devuelve_vacio():
    from botocore.exceptions import ClientError

    client = MagicMock()
    client.get_products.side_effect = ClientError(
        {'Error': {'Code': 'AccessDenied', 'Message': 'denied'}},
        'GetProducts',
    )
    assert get_products('AmazonEC2', [], client=client) == []


def test_precio_on_demand_hora(ec2_product):
    client = MagicMock()
    client.get_products.return_value = {'PriceList': [json.dumps(ec2_product)]}
    precio = precio_on_demand_hora(
        'AmazonEC2',
        filtros_ec2('t3.micro', 'us-east-1'),
        client=client,
    )
    assert precio == 0.0104
