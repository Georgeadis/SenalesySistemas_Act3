# Señales y Sistemas — Actividad 3

Este repositorio contiene `Georgeadis_Arias_ACT3-SyS`, una interfaz gráfica (Tkinter) para:

- Generar señales de prueba (senoidal, cuadrada, pulso, ruidosa).
- Diseñar filtros digitales: Butterworth (IIR), Chebyshev Tipo I (IIR) y FIR por ventana.
- Aplicar filtros a la señal generada y comparar las señales antes y después (dominio del tiempo y espectro).
- Guardar la figura resultante en PNG y limpiar filtros aplicados.

Requisitos:
- Python 3.8+
- numpy
- scipy
- matplotlib
- tkinter (normalmente incluido en Python en Windows)

Uso rápido:

1. Abrir terminal en esta carpeta.
2. Ejecutar:

```powershell
py Georgeadis_Arias_ACT3-SyS
```

3. En la ventana: pulse **Generar señal** para ver la señal original; luego configure el filtro y pulse **Aplicar filtro**.

Nota: Para filtros `bandpass` introduce `Cutoff` como `low,high` (ej.: `40,120`).

Autor: Georgeadis Arias
