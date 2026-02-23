from pymodbus.client import ModbusTcpClient
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import time

# Conecta ao "CLP"
cliente = ModbusTcpClient('localhost', port=5020)
cliente.connect()
print("🔌 Conectado ao sistema de controle industrial")

# Simula loop de monitoramento (5 ciclos)
for ciclo in range(5):
    print(f"\n--- Ciclo {ciclo+1} ---")
    
    # 1. Lê variáveis de processo
    vib_rms = cliente.read_holding_registers(2, 1, unit=1).registers[0] / 100.0  # Escala
    temp = cliente.read_holding_registers(0, 1, unit=1).registers[0] / 10.0
    pressao = cliente.read_holding_registers(1, 1, unit=1).registers[0] / 10.0
    
    print(f"📈 Lido: Temp={temp:.1f}°C, Press={pressao:.1f}bar, Vib RMS={vib_rms:.3f}")
    
    # 2. Detecta anomalia (simples, com histórico simulado)
    dados = np.array([[temp, pressao, vib_rms]])
    modelo = IsolationForest(contamination=0.1, random_state=42)
    modelo.fit(dados)
    anomalia = modelo.predict(dados)[0] == -1
    
    if anomalia:
        print("🚨 ANOMALIA DETECTADA! Desligando bomba...")
        # 3. Envia comando: desliga coil 1 (bomba)
        cliente.write_coil(0, False, unit=1)
        
        # 4. Lê confirmação
        bomba_status = cliente.read_coils(0, 1, unit=1).bits[0]
        print(f"✅ Comando enviado. Bomba agora: {'OFF' if not bomba_status else 'ON'}")
    else:
        print("✅ Normal. Sem ação.")
    
    time.sleep(3)  # Espera próximo ciclo

cliente.close()
print("🔌 Desconectado")
