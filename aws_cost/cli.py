"""Interfaz de línea de comandos interactiva."""

from pydantic_ai.messages import ModelMessage

from aws_cost.agent import crear_agente
from aws_cost.models import EstimadoCostoAWS
from aws_cost.prompt_validator import crear_validador, mensaje_advertencia, validar_prompt

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
    print("\nEscribe 'salir' para terminar\n")
    print('-' * 80)


def imprimir_estimacion(estimacion: EstimadoCostoAWS) -> None:
    print('\n' + '=' * 80)
    print(f'ESTIMACION DE COSTOS AWS (Region: {estimacion.region})')
    print('=' * 80)
    print(f"\n{'Servicio':<25} {'Descripcion':<35} {'Qty':<5} {'Mensual':<12}")
    print('-' * 80)
    for item in estimacion.items:
        print(
            f'{item.servicio:<25} {item.descripcion:<35} '
            f'{item.cantidad:<5} ${item.costo_total_mensual:.2f}'
        )
    print('-' * 80)
    print(f"{'TOTAL MENSUAL':<63} ${estimacion.total_mensual:.2f}")
    print(f"{'TOTAL ANUAL':<63} ${estimacion.total_anual:.2f}")
    print('=' * 80)
    if estimacion.notas:
        print('\nNOTAS:')
        for nota in estimacion.notas:
            print(f'  - {nota}')
    print('=' * 80)


async def main() -> None:
    """Bucle principal de la CLI."""
    imprimir_banner()
    agent = crear_agente()
    validador = crear_validador()
    history: list[ModelMessage] = []

    while True:
        try:
            user_input = input('\nTu: ').strip()
            if user_input.lower() in EXIT_COMMANDS:
                print('\nHasta luego!')
                break
            if not user_input:
                continue

            print('\nValidando pregunta...')
            validacion = await validar_prompt(
                validador,
                user_input,
                es_seguimiento=bool(history),
            )
            if not validacion.es_relevante:
                print(f'\nAdvertencia: {mensaje_advertencia(validacion)}')
                continue

            print('\nAgente calculando costos...')
            resultado = await agent.run(user_input, message_history=history)
            history += resultado.new_messages()
            imprimir_estimacion(resultado.output)

        except KeyboardInterrupt:
            print('\n\nHasta luego!')
            break
        except Exception as e:
            print(f'\nError: {e}')
            print("Intenta de nuevo o escribe 'salir' para terminar.")
