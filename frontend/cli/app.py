"""Interfaz de línea de comandos interactiva."""

import asyncio

from backend.services.calculator import crear_sesion, procesar_mensaje
from frontend.formatters import formatear_estimacion_texto, formatear_propuesta_markdown

EXIT_COMMANDS = frozenset({'salir', 'exit', 'quit', 'q'})


def imprimir_banner() -> None:
    print('=' * 80)
    print('ASESOR AWS con Pydantic AI')
    print('=' * 80)
    print('\nDescribe tu negocio o necesidad en lenguaje cotidiano, por ejemplo:')
    print('  - Tienda online con 500 visitas al dia y poco presupuesto')
    print('  - App de reservas para 20 empleados con login de usuarios')
    print('  - Tambien puedes pedir costos tecnicos: 2x t3.medium y 100GB S3')
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

            print('\nProcesando (arquitectura, costes, hoja de ruta)...')
            resultado = await procesar_mensaje(sesion, user_input)

            if resultado.advertencia:
                print(f'\nAdvertencia: {resultado.advertencia}')
                continue
            if resultado.error:
                print(f'\nError: {resultado.error}')
                continue
            if resultado.propuesta:
                print('\n' + formatear_propuesta_markdown(resultado.propuesta))
            elif resultado.estimacion:
                print('\n' + formatear_estimacion_texto(resultado.estimacion))

        except KeyboardInterrupt:
            print('\n\nHasta luego!')
            break
