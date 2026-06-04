"""Excepciones cuando la AWS Price List API no devuelve un precio."""


class PricingUnavailableError(Exception):
    """No se pudo obtener un precio desde la API de AWS."""

    def __init__(
        self,
        *,
        servicio: str,
        region: str | None = None,
        detalle: str = '',
    ) -> None:
        self.servicio = servicio
        self.region = region
        self.detalle = detalle
        partes = [f'Precio no disponible para {servicio}']
        if region:
            partes.append(f'región={region}')
        if detalle:
            partes.append(detalle)
        super().__init__('. '.join(partes) + '.')
