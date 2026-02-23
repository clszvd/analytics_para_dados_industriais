from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext
from pymodbus.pdu.device import ModbusDeviceIdentification
import time
import random

# Configuração do datastore (memória do "CLP")
# Holding Registers: 40001 = Temp (°C), 40002 = Pressão (bar), 40003 = Vibração RMS, 40004 = Setpoint Temp
hr = ModbusSequentialDataBlock(0, [25.0, 5.2, 0.02, 28.0] * 3)  # x3 para mais registros
# Coils: 00001=Bomba ON, 00002=Válvula Aberta
co = ModbusSequentialDataBlock(0, [False, False, True] * 3)

# Contextos
slave_context = ModbusDeviceContext(
    co=co, hr=hr,
    di=None, ir=None
)
context = ModbusServerContext(devices=slave_context, single=True)

# Identificação do "dispositivo"
identity = ModbusDeviceIdentification()
identity.VendorName = 'Simulador Planta Industrial'
identity.ProductCode = 'PLANTA001'
identity.VendorUrl = 'http://industrial.local'
identity.ProductName = 'CLP Planta XYZ'
identity.ModelName = 'SimCLP-2026'
identity.MajorMinorRevision = '1.0'

print("🚀 Servidor Modbus TCP iniciado em localhost:5020")
print("Holding Registers (ex: 40001=Temp, 40002=Pressão)")
print("Coils (ex: 00001=Bomba ON/OFF)")

# Simula dinâmica da planta (atualiza valores automaticamente)
def update_process():
    while True:
        time.sleep(2)  # Ciclo de 2s
        # Lógica simples: se bomba ligada (coil 1=True), temp sobe; vibração varia
        bomba_status = co.getValues(0, 1)[0]
        if bomba_status:
            hr.setValues(0, [hr.getValues(0, 1)[0] + random.uniform(-0.5, 1.0)])  # Temp sobe
            hr.setValues(2, [hr.getValues(2, 1)[0] + random.uniform(0, 0.01)])   # Vibração aumenta
        print(f"📊 Temp: {hr.getValues(0,1)[0]:.1f}°C | Vib: {hr.getValues(2,1)[0]:.3f} | Bomba: {bomba_status}")

import threading
threading.Thread(target=update_process, daemon=True).start()

# Inicia servidor
StartTcpServer(context, identity=identity, address=("localhost", 5020))
