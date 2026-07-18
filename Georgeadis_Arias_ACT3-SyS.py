import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import signal

"""
codigo_actividad3.py
GUI para generar señales, diseñar filtros (Butterworth, Chebyshev I, FIR por ventana),
aplicar los filtros y comparar señales antes/después en dominio tiempo y frecuencia.

Notas:
- Ejecutar este script abrirá una ventana con controles y un área de graficado embebida.
- Evita ejecutar código adicional al cerrar la GUI; el script termina cuando cierras la ventana.
Fecha: 2024-06-12
Dia de entrega: 2024-06-12
"""


def generar_senal(tipo, Fs, L, f1=50, f2=120, ruido_amp=0.2):
    """Genera señales de prueba.

    Parámetros:
    - tipo: cadena que indica el tipo de señal
    - Fs: frecuencia de muestreo (Hz)
    - L: número de muestras
    - f1, f2: frecuencias usadas en señales senoidales
    - ruido_amp: amplitud del ruido para la señal ruidosa

    Retorna: (t, x) donde t es el vector de tiempo y x la señal.
    """
    T = 1.0 / Fs
    t = np.arange(L) * T
    if tipo == 'Senoidal (2 tonos)':
        # Suma de dos senos a f1 y f2
        x = np.sin(2 * np.pi * f1 * t) + 0.5 * np.sin(2 * np.pi * f2 * t)
    elif tipo == 'Pulso rectangular':
        # Pulso centrado con ancho fijo
        ancho = 0.05
        x = np.where(np.abs(t - t.mean()) <= ancho / 2, 1.0, 0.0)
    elif tipo == 'Ruidosa (seno + ruido)':
        # Seno contaminado con ruido blanco
        x = np.sin(2 * np.pi * f1 * t) + ruido_amp * np.random.randn(L)
    elif tipo == 'Cuadrada':
        # Señal cuadrada
        x = signal.square(2 * np.pi * f1 * t)
    else:
        x = np.zeros(L)
    return t, x


def diseno_filtro(tipo_filtro, orden, btype, cutoff, Fs, ripple=1.0, window='hamming'):
    """Diseña y devuelve coeficientes (b, a) para el filtro solicitado.

    Soporta:
    - Butterworth (IIR)
    - Chebyshev I (IIR)
    - FIR por ventana (usar 'window' para seleccionar)

    El parámetro `cutoff` puede ser un número (low/high) o una lista [low, high] para bandpass.
    """
    nyq = 0.5 * Fs
    if btype == 'bandpass' and isinstance(cutoff, (list, tuple)):
        Wn = [c / nyq for c in cutoff]
    else:
        Wn = cutoff / nyq

    if tipo_filtro == 'Butterworth (IIR)':
        b, a = signal.butter(orden, Wn, btype=btype)
    elif tipo_filtro == 'Chebyshev I (IIR)':
        b, a = signal.cheby1(orden, ripple, Wn, btype=btype)
    elif tipo_filtro == 'FIR (ventana)':
        # firwin expects numtaps y cutoff normalizado
        numtaps = orden if orden % 2 == 1 else orden + 1
        if btype == 'bandpass' and isinstance(cutoff, (list, tuple)):
            Wn_fir = [c / nyq for c in cutoff]
        else:
            Wn_fir = cutoff / nyq
        # pass_zero=True => pasa bajos, False => pasa banda/alto según Wn
        b = signal.firwin(numtaps, Wn_fir, window=window, pass_zero=('lowpass' == btype))
        a = np.array([1.0])
    else:
        raise ValueError('Tipo de filtro desconocido')
    return b, a


def aplicar_filtro(b, a, x):
    try:
        y = signal.filtfilt(b, a, x)
    except Exception:
        # fallback a filter forward-backward simple if filtfilt falla
        y = signal.lfilter(b, a, x)
    return y


def plot_signals(fig, canvas, t, x, y, Fs):
    # Limpia la figura embebida y vuelve a dibujar dos subplots
    fig.clear()
    axs = fig.subplots(2, 1)
    axs[0].plot(t, x, label='Original')
    axs[0].plot(t, y, label='Filtrada', linestyle='--')
    axs[0].set_title('Dominio del tiempo')
    axs[0].set_xlabel('Tiempo (s)')
    axs[0].legend()
    axs[0].grid(True)

    # Espectro
    L = len(x)
    freqs = np.fft.rfftfreq(L, 1.0 / Fs)
    Xf = np.abs(np.fft.rfft(x) / L)
    Yf = np.abs(np.fft.rfft(y) / L)
    axs[1].plot(freqs, Xf, label='Original')
    axs[1].plot(freqs, Yf, label='Filtrada', linestyle='--')
    axs[1].set_xlim([0, Fs/2])
    axs[1].set_title('Espectro (magnitud)')
    axs[1].set_xlabel('Frecuencia (Hz)')
    axs[1].legend()
    axs[1].grid(True)

    fig.tight_layout()
    canvas.draw()


def plot_original_only(fig, canvas, t, x, Fs):
    """Dibuja solo la señal original (tiempo + espectro), sin la curva 'Filtrada'."""
    fig.clear()
    axs = fig.subplots(2, 1)
    axs[0].plot(t, x, label='Original', color='blue')
    axs[0].set_title('Dominio del tiempo (Original)')
    axs[0].set_xlabel('Tiempo (s)')
    axs[0].legend()
    axs[0].grid(True)

    # Espectro solo original
    L = len(x)
    freqs = np.fft.rfftfreq(L, 1.0 / Fs)
    Xf = np.abs(np.fft.rfft(x) / L)
    axs[1].plot(freqs, Xf, label='Original', color='blue')
    axs[1].set_xlim([0, Fs/2])
    axs[1].set_title('Espectro (magnitud) - Original')
    axs[1].set_xlabel('Frecuencia (Hz)')
    axs[1].legend()
    axs[1].grid(True)

    fig.tight_layout()
    canvas.draw()


def crear_gui():
    root = tk.Tk()
    root.title('Señales y Sistemas - Actividad 3')

    mainfrm = ttk.Frame(root, padding=8)
    mainfrm.pack(fill=tk.BOTH, expand=True)

    controlfrm = ttk.Frame(mainfrm)
    controlfrm.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

    # Parámetros de señal
    ttk.Label(controlfrm, text='Generar señal').pack(anchor=tk.W)
    tipo_signal = tk.StringVar(value='Senoidal (2 tonos)')
    ttk.Combobox(controlfrm, textvariable=tipo_signal, values=['Senoidal (2 tonos)', 'Ruidosa (seno + ruido)', 'Cuadrada', 'Pulso rectangular'], state='readonly').pack(fill=tk.X)

    ttk.Label(controlfrm, text='Fs (Hz)').pack(anchor=tk.W, pady=(8,0))
    Fs_var = tk.StringVar(value='1000')
    ttk.Entry(controlfrm, textvariable=Fs_var).pack(fill=tk.X)

    ttk.Label(controlfrm, text='L (muestras)').pack(anchor=tk.W, pady=(8,0))
    L_var = tk.StringVar(value='2048')
    ttk.Entry(controlfrm, textvariable=L_var).pack(fill=tk.X)

    ttk.Label(controlfrm, text='f1 (Hz)').pack(anchor=tk.W, pady=(8,0))
    f1_var = tk.StringVar(value='50')
    ttk.Entry(controlfrm, textvariable=f1_var).pack(fill=tk.X)

    ttk.Label(controlfrm, text='f2 (Hz)').pack(anchor=tk.W, pady=(8,0))
    f2_var = tk.StringVar(value='120')
    ttk.Entry(controlfrm, textvariable=f2_var).pack(fill=tk.X)

    ttk.Button(controlfrm, text='Generar señal', command=lambda: generar_evento()).pack(fill=tk.X, pady=(10,4))

    ttk.Separator(controlfrm, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

    # Parámetros de filtro
    ttk.Label(controlfrm, text='Diseño de filtro').pack(anchor=tk.W)
    tipo_filtro_var = tk.StringVar(value='Butterworth (IIR)')
    ttk.Combobox(controlfrm, textvariable=tipo_filtro_var, values=['Butterworth (IIR)', 'Chebyshev I (IIR)', 'FIR (ventana)'], state='readonly').pack(fill=tk.X)

    ttk.Label(controlfrm, text='Tipo banda').pack(anchor=tk.W, pady=(8,0))
    btype_var = tk.StringVar(value='lowpass')
    ttk.Combobox(controlfrm, textvariable=btype_var, values=['lowpass', 'highpass', 'bandpass'], state='readonly').pack(fill=tk.X)

    ttk.Label(controlfrm, text='Orden (int)').pack(anchor=tk.W, pady=(8,0))
    orden_var = tk.StringVar(value='4')
    ttk.Entry(controlfrm, textvariable=orden_var).pack(fill=tk.X)

    ttk.Label(controlfrm, text='Cutoff (Hz) — para bandpass use: low,high').pack(anchor=tk.W, pady=(8,0))
    cutoff_var = tk.StringVar(value='80')
    ttk.Entry(controlfrm, textvariable=cutoff_var).pack(fill=tk.X)
    ttk.Label(controlfrm, text="Nota: si eliges 'bandpass' introduce dos valores separados por coma (ej.: 40,120).\nSi introduces un único número se usará tal cual para filtros low/high.", foreground='gray').pack(anchor=tk.W, pady=(4,0))

    ttk.Label(controlfrm, text='Ripple (dB) — Chebyshev I').pack(anchor=tk.W, pady=(8,0))
    ripple_var = tk.StringVar(value='1')
    ttk.Entry(controlfrm, textvariable=ripple_var).pack(fill=tk.X)

    ttk.Label(controlfrm, text='Ventana FIR').pack(anchor=tk.W, pady=(8,0))
    window_var = tk.StringVar(value='hamming')
    ttk.Combobox(controlfrm, textvariable=window_var, values=['hamming', 'hann', 'blackman', 'rectangular'], state='readonly').pack(fill=tk.X)

    ttk.Button(controlfrm, text='Aplicar filtro', command=lambda: aplicar_evento()).pack(fill=tk.X, pady=(10,4))

    # Botón para limpiar el filtro y restaurar la vista original
    ttk.Button(controlfrm, text='Limpiar filtro', command=lambda: limpiar_filtro()).pack(fill=tk.X, pady=(4,6))

    ttk.Separator(controlfrm, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

    ttk.Button(controlfrm, text='Guardar figura (PNG)', command=lambda: guardar_figura()).pack(fill=tk.X)

    # Canvas para figuras
    fig = Figure(figsize=(8, 6))
    canvas = FigureCanvasTkAgg(fig, master=mainfrm)
    canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    state = {'t': None, 'x': None, 'y': None, 'Fs': None, 'L': None}


    def generar_evento():
        try:
            Fs = float(Fs_var.get())
            L = int(float(L_var.get()))
            f1 = float(f1_var.get())
            f2 = float(f2_var.get())
        except ValueError:
            messagebox.showerror('Error', 'Parámetros de señal inválidos')
            return
        tipo = tipo_signal.get()
        t_vals, x_vals = generar_senal(tipo, Fs, L, f1=f1, f2=f2)
        state.update({'t': t_vals, 'x': x_vals, 'y': None, 'Fs': Fs, 'L': L})
        # Mostrar solo la señal original al generar
        plot_original_only(fig, canvas, t_vals, x_vals, Fs)


    def aplicar_evento():
        if state['x'] is None:
            messagebox.showwarning('Atención', 'Genera primero una señal')
            return
        try:
            tipo_filtro = tipo_filtro_var.get()
            orden = int(float(orden_var.get()))
            btype = btype_var.get()
            Fs = float(Fs_var.get())
            ripple = float(ripple_var.get())
            window = window_var.get()
        except ValueError:
            messagebox.showerror('Error', 'Parámetros de filtro inválidos')
            return

        cutoff_text = cutoff_var.get()
        try:
            if btype == 'bandpass':
                parts = cutoff_text.split(',')
                cutoff = [float(parts[0].strip()), float(parts[1].strip())]
            else:
                cutoff = float(cutoff_text)
        except Exception:
            messagebox.showerror('Error', 'Cutoff inválido. Para bandpass usa: low,high')
            return

        try:
            b, a = diseno_filtro(tipo_filtro, orden, btype, cutoff, Fs, ripple=ripple, window=window)
            y = aplicar_filtro(b, a, state['x'])
            state['y'] = y
            plot_signals(fig, canvas, state['t'], state['x'], y, Fs)
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo diseñar/aplicar filtro:\n{e}')


    def limpiar_filtro():
        """Restaura la vista a la señal original sin filtro aplicado."""
        if state['x'] is None:
            messagebox.showwarning('Atención', 'No hay señal generada para limpiar.')
            return
        state['y'] = None
        plot_original_only(fig, canvas, state['t'], state['x'], state['Fs'])


    def guardar_figura():
        try:
            fig.savefig('filtro_resultado.png')
            messagebox.showinfo('Guardado', 'Figura guardada como filtro_resultado.png')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo guardar:\n{e}')


    root.mainloop()


if __name__ == '__main__':
    # Ejecutar la GUI sólo cuando el script se ejecuta directamente
    crear_gui()
    