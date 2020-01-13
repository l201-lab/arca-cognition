# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 00:00:24 2019

@author: Alfieri
"""
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import scipy.io.wavfile as waves
import scipy.io

archivo = 'Hola.wav'


def filtrar(archivo):
    Filtro = scipy.io.loadmat('Filtro.mat')
    muestreo, sonido = waves.read(archivo)
    t = np.linspace(0, (len(sonido) / muestreo) - 1 / muestreo, len(sonido))

    # canales: monofónico o estéreo
    tamano = np.shape(sonido)
    muestras = tamano[0]
    m = len(tamano)
    canales = 1  # monofónico
    if (m > 1):  # estéreo
        canales = tamano[1]
    # experimento con un canal
    if (canales > 1):
        canal = 0
        x = sonido[:, canal]
    else:
        x = sonido
    "Reescalado de la señal"
    x = x / max(x)

    "Filtrado de señal"
    a = [1, 0]
    b0 = Filtro['Num']
    b1 = b0[0]
    filtrado = signal.filtfilt(b1, a, x)

    "Pltotear" "Señal"
    plt.figure
    plt.plot(t, x, 'b')
    plt.plot(t, filtrado, 'r')
    plt.grid(True)
    plt.legend(('Señal original Hola', 'Señal filtrada Hola'), loc='best')
    plt.show()
    return filtrado


filtrado = filtrar(archivo)
