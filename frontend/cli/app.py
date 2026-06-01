"""Interfaz de línea de comandos interactiva."""

import asyncio

from backend.services.calculator import crear_sesion, procesar_mensaje
from frontend.formatters import formatear_estimacion_texto

EXIT_COMMANDS = frozenset({'salir', 'exit', 'quit', 'q'})


def imprimir_banner() -> None:
    print('=' * 80)
    print('CALCULADORA DE COSTOS AWS con Pydantic AI')
    print('=' * 80)
    print('\nEjemplos de preguntas:')
    print('  - Cuantas cuestan 3 instancias t3.medium?')
    print('  - Necesito 1 RDS db.t3.small con 100GB de storage')
    print('  - Calcula: 2x t3.micro, 50GB S3, 1 RDS t3.small')
    print('  - App con Lambda + API Gateway + DynamoDB')
    print("\nEscribe 'salir' para terminar")
    print('Para la interfaz grafica: streamlit run gui.py\n')
    print('-' * 80)


async def run() -> None:
    """Bucle principal de la CLI."""
    imprimir_banner()
    sesion = crear_sesion()

    while True:
        try:
            user_input = input('\nTu: ').strip()
            if user_input.lower() in EXIT_COMMANDS:
                print('\nHasta luego!')
                break
            if not user_input:
                continue

            print('\nValidando y calculando...')
            resultado = await procesar_mensaje(sesion, user_input)

            if resultado.advertencia:
                print(f'\nAdvertencia: {resultado.advertencia}')
                continue
            if resultado.error:
                print(f'\nError: {resultado.error}')
                continue
            if resultado.estimacion:
                print('\n' + formatear_estimacion_texto(resultado.estimacion))

        except KeyboardInterrupt:
            print('\n\nHasta luego!')
            break
