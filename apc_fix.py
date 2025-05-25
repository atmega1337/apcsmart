import apc
from datetime import datetime




def findreg0(reg4, reg5, reg6, fw):
    import csv
    with open('reglist.csv', newline='') as csvfile:
        # reglist = [UPS Model,4,5,6,0,Hex,Firmware]
        reglist = list(csv.reader(csvfile, delimiter=','))[1:]

    upslist=[]
    for i in reglist:
        upslist.append({
            'model': i[0],
            'originfo': {
                'reg0': i[4],
                'reg4': i[1],
                'reg5': i[2],
                'reg6': i[3],
                'hex': i[5],
                'fw': i[6],
            }
        })
    del reglist

    # test reg4,5,6
    for i in range(len(upslist)):
        upslist[i]['test']={
                'reg4': True if upslist[i]['originfo']['reg4'] == reg4 else False,
                'reg5': True if upslist[i]['originfo']['reg5'] == reg5 else False,
                'reg6': True if upslist[i]['originfo']['reg6'] == reg6 else False,
        }
    for i in range(len(upslist)):
        upslist[i]['testcalc']=sum(1 for value in upslist[i]['test'].values() if value)

    upslist.sort(key=lambda x: x['testcalc'], reverse=True)
    # max testcalc
    max_value = max(upslist, key=lambda x: x['testcalc'])['testcalc']
    # all max item
    max_elements = [item for item in upslist if item['testcalc'] == max_value]

    for i in range(len(max_elements)):
        print(f'{i}) Model: {max_elements[i]['model']}\n - Reg 4: {upslist[i]['originfo']['reg4']} ({upslist[i]['test']['reg4']})\n - Reg 5: {upslist[i]['originfo']['reg5']} ({upslist[i]['test']['reg5']})\n - Reg 6: {upslist[i]['originfo']['reg6']} ({upslist[i]['test']['reg6']})\n')
    
    while 1:
        choice = input("Select UPS [0]: ")
        try:
            if choice == '':
                return max_elements[0]['originfo']['reg0']
            if 0 <= int(choice) < len(max_elements):
                return max_elements[int(choice)]['originfo']['reg0']
            else:
                print("Incorrect select")
        except ValueError:
            print("Incorrect select")

# newreg0=findreg0('29','A0','13','653.4.I')
# print(newreg0)
# input()


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