import ctypes
import time
import csv
import os
import math

class PowerMeter:
    def __init__(self, dll_path=r"C:\Program Files\Intel\Power Gadget 3.6\EnergyLib64.dll",
                 csv_file="energy_log.csv"):
        # Carrega a DLL
        self.energy_lib = ctypes.WinDLL(dll_path)

        # Inicializa a biblioteca
        if not self.energy_lib.IntelEnergyLibInitialize():
            raise RuntimeError("Falha ao inicializar Intel Power Gadget API")

        # Configura funções
        self.GetNumNodes = self.energy_lib.GetNumNodes
        self.GetNumNodes.restype = ctypes.c_int

        self.ReadSample = self.energy_lib.ReadSample
        self.GetPowerData = self.energy_lib.GetPowerData

        self.num_nodes = self.GetNumNodes()
        self.csv_file = csv_file

        # Prepara arquivo CSV (se não existir)
        if not os.path.exists(self.csv_file):
            headers = ["elapsed_sec"]
            for i in range(self.num_nodes):
                headers.append(f"avg_power_node{i}_W")
                headers.append(f"energy_node{i}_J")
            with open(self.csv_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)

    def _read_all_nodes(self):
        """Lê dados de todos os nós (CPU Package, DRAM, GPU, etc.)"""
        self.ReadSample()
        data = []
        for i in range(self.num_nodes):
            val = ctypes.c_double()
            values = ctypes.c_int()
            self.GetPowerData(i, 1, ctypes.byref(val), ctypes.byref(values))
            data.append(val.value)
        return data

    def measure_block(self, func, *args, **kwargs):
        """
        Mede energia consumida durante a execução de uma função.
        Retorna um dicionário com energia média e salva no CSV.
        """
        start = self._read_all_nodes()
        t0 = time.time()

        func(*args, **kwargs)  # executa o código-alvo

        t1 = time.time()
        end = self._read_all_nodes()

        # Calcula média
        elapsed = t1 - t0
        avg_power = end
        energy = [p * elapsed for p in avg_power]

        # Salva no CSV
        row = [elapsed]
        for p, e in zip(avg_power, energy):
            row.extend([p, e])
        with open(self.csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

def workload():
    total = 0
    for i in range(10**7):
        total += math.sqrt(i)
    return total

def eh_primo(num: int) -> bool:
    if num < 2:
        return False
    for i in range(2, num):
        if num % i == 0:
            return False
    return True

def primos_ate_n():
    primos = []
    for numero in range(2, 25000 + 1):
        if eh_primo(numero):
            primos.append(numero)
    return primos

def fatorial():
    resultado = 1
    for i in range(1, 75000 + 1):
        resultado *= i
    return resultado

# pm = PowerMeter(csv_file="resultados_energia_primos.csv")
#
# for idx in range(100):
#     pm.measure_block(primos_ate_n)
    #print("Resultado:", result)

pm = PowerMeter(csv_file="resultados_energia_fatorial.csv")

for idx in range(100):
    pm.measure_block(fatorial)
    #print("Resultado:", result)

print("Medições salvas com sucesso!")