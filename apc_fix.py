import apc
from datetime import datetime


def settoday():
    return print (ups.editdatebatteryreplacement(datetime.today().strftime('%m/%d/%y')))


ups = apc.apc(port="COM1", debug=False)
ups.terminalmode_sm()
print('UPS info:')
print(f'Name: {ups.getName()}')
print(f'Model: {ups.getModel()}')
print(f'Date Manufacture: {ups.getDateManufacture()}')
print(f'Temperature: {ups.getTemperature()}')
print(f'S/N: {ups.getSN()}')
print(f'Old Model: {ups.getOldModel()}')
print(f'SoftVersion: {ups.getSoftVersion()}')

print('Line info:')
print(f'Load: {ups.getLoadPower()}')
print(f'Frequency: {ups.getInputFrequency()}')
print(f'Input Voltage: {ups.getInputVoltage()}')
print(f'- Max Voltage: {ups.getinputvoltageMax()}')
print(f'- Min Voltage: {ups.getInputVoltageMin()}')
print(f'Sensitivity: {ups.getSensitivity()}')



print('Battery info:')
print(f'Nominal Voltage : {ups.getNominalBatVoltage()}')
print(f'Voltage: {ups.getBatVoltage()}')
print(f'Charge: {ups.getBatLevel()}')
print(f'Date replacement: {ups.getDateBatReplacement()}')

print('Reg info:')
print(f'0: {ups.getReg0()}')
print(f'1: {ups.getReg1()}')
print(f'2: {ups.getReg2()}')
print(f'4: {ups.getReg4()}')
print(f'5: {ups.getReg5()}')

input()

ups.editreg(0, 'A1')
print (settoday())
ups.terminalmode_off()