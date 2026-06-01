"""Precios referenciales AWS (us-east-1, aprox. 2024). Pueden variar."""

PRECIOS_EC2_US_EAST_1 = {
    't3.nano': 0.0052,
    't3.micro': 0.0104,
    't3.small': 0.0208,
    't3.medium': 0.0416,
    't3.large': 0.0832,
    't3.xlarge': 0.1664,
    't3.2xlarge': 0.3328,
    't2.micro': 0.0116,
    't2.small': 0.0232,
    't2.medium': 0.0464,
    'm5.large': 0.096,
    'm5.xlarge': 0.192,
    'm5.2xlarge': 0.384,
    'c5.large': 0.085,
    'c5.xlarge': 0.17,
    'c5.2xlarge': 0.34,
}

PRECIOS_RDS_US_EAST_1 = {
    'db.t3.micro': 0.017,
    'db.t3.small': 0.027,
    'db.t3.medium': 0.054,
    'db.t3.large': 0.108,
    'db.m5.large': 0.125,
    'db.m5.xlarge': 0.25,
    'db.c5.large': 0.118,
    'db.c5.xlarge': 0.236,
}

PRECIOS_ELASTICACHE = {
    'cache.t3.micro': 0.012,
    'cache.t3.small': 0.024,
    'cache.t3.medium': 0.048,
    'cache.t3.large': 0.096,
}

PRECIO_S3_POR_GB = 0.023
PRECIO_TRANSFERENCIA_POR_GB = 0.09
PRECIO_LAMBDA_POR_MILLON_REQ = 0.20
PRECIO_LAMBDA_POR_GB_SEGUNDO = 0.0000166667
PRECIO_API_GATEWAY_POR_MILLON = 3.50
PRECIO_DYNAMODB_ESCRITURA = 0.25
PRECIO_DYNAMODB_LECTURA = 0.25
PRECIO_SNS_POR_MILLON = 0.50
PRECIO_SQS_POR_MILLON = 0.40
PRECIO_RDS_STORAGE_POR_GB = 0.115
