"""Stub de siembra (sin-op) — la siembra real de catálogos y datos base llega en C-19.

C-01 necesita que el job `migrate` del Compose (`alembic upgrade head && python -m app.seed`)
termine con éxito desde el día 1; este módulo garantiza ese contrato ejecutando sin error.
"""


def main() -> None:
    pass  # C-19 reemplaza este cuerpo con la siembra real.


if __name__ == "__main__":
    main()