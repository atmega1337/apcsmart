import serial
import logging
import time
import logging

logging.basicConfig(level=logging.DEBUG, filename="serial.log",filemode="w", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger().addHandler(logging.StreamHandler())


class apcemu:
      def __init__(self):
            self.emuconfig={
                  'port': 'COM3',
                  'debug': True,
                  'voltagecalc': False
            }
            self.upscvar={
                  'mode': 0, # 0 - off, 1 - monitormode, 2 - progmode
                  'upspower': True,
                  'Reg1': b'80',
                  'Reg2': b'08',
                  'Reg3': b'04',
                  'FlagStatus': b'08',
                  'RunTime': b'0700',

            }
            self.eeprom={
                  'upsname': b'Smart-UPS 0000',
                  'upsusername': b'UPS_IDEN',
                  'BatReplacement': b'MM/DD/YY',
                  'DateManufacture': b'MM/DD/YY',
                  'sn': b'AAYYWW123456',
                  'Reg0': b'BC',
                  'Reg4': b'07',
                  'Reg5': b'B5',
                  'Reg6': b'13',
                  'BatPcs': b'00',
                  'VoltageRestart': b'00',
                  'DelayBeep': b'01',
                  'MinVoltage': b'01',
                  'OutVoltage': b'02',
                  'DelayOff': b'00',
                  'Warn': b'00',
                  'MaxVoltage': b'01',
                  'Revision': b'07',
            }
            self.outcvar={

                  'InV': b'230.0',
                  'MaxInV': b'240.0',
                  'MinInV': b'230.0',
                  'OutV': b'230.0',
                  'BatV': b'24.00',
                  'Bat': b'100.0',
                  'Temperature': b'25.0',
                  'Frequency': b'50.00',
                  'Load': b'50.0',
            }
            
            self.cmdlist={
                        b"\x01": lambda: self.eeprom['upsname'],
                        b"\x1A": lambda: b'Capabilities',
                        b"\x42": lambda: self.outcvar['BatV'],
                        b"\x43": lambda: self.outcvar['Temperature'],
                        b"\x46": lambda: self.outcvar['Frequency'],
                        b"\x47": lambda: b'S',
                        b"\x4C": lambda: self.outcvar['InV'],
                        b"\x4D": lambda: self.outcvar['MaxInV'],
                        b"\x4E": lambda: self.outcvar['MinInV'],
                        b"\x4F": lambda: self.outcvar['OutV'],
                        b"\x50": lambda: self.outcvar['Load'],
                        b"\x51": lambda: self.upscvar['FlagStatus'],
                        b"\x63": lambda: self.eeprom['upsusername'],
                        b"\x64": lambda: self.eeprom['VoltageRestart'],
                        b"\x65": lambda: self.eeprom['VoltageRestart'],
                        b"\x66": lambda: self.outcvar['Bat'],
                        b"\x67": lambda: b'24',
                        b"\x6B": lambda: self.eeprom['DelayBeep'],
                        b"\x6A": lambda: self.upscvar['RunTime'],
                        b"\x6D": lambda: self.eeprom['DateManufacture'],
                        b"\x6E": lambda: self.eeprom['sn'],
                        b"\x30": lambda: self.eeprom['Reg0'],
                        b"\x34": lambda: self.eeprom['Reg4'],
                        b"\x35": lambda: self.eeprom['Reg5'],
                        b"\x36": lambda: self.eeprom['Reg6'],
                        b"\x78": lambda: self.eeprom['BatReplacement'],

                        

                        b"\x56": lambda: b"GWI", # Номер версии UPS.
                        b"\x62": lambda: b"450.9.I", # Номер версии UPS.
                        b"~": lambda: self.upscvar['Reg1'],
                        b"'": lambda: self.upscvar['Reg2'],
                        b"8": lambda: self.upscvar['Reg3'],
                  }

            self.ser = serial.serial_for_url(self.emuconfig['port'], baudrate=2400, timeout=2)
            logging.debug('start init')

      def configups(self, **args):
            """
            Конфиг ИБП (EEPROM).
            """
            self.eeprom.update(args)
      
      def configoutcvar(self, **args):
            """
            Конфиг внешних параметров.
            """
            self.outcvar.update(args)

      def cmdinterafce(self, cmd):


            if cmd==b"Y":
                  logging.debug('UPS MODE: monitormode') #debug
                  self.upscvar['mode']=1
                  return b'SM'
            if cmd==b"R":
                  logging.debug('UPS MODE: OFF') #debug
                  self.upscvar['mode']=0
                  return b'BYE'
            # monitormode
            if self.upscvar['mode']==1:
                  if cmd in self.cmdlist:
                        return self.cmdlist[cmd]()
                  # Progmode
                  if cmd==b"\x31":
                        time.sleep(1)
                        self.ser.reset_input_buffer()
                        data = self.ser.readline(1)
                        logging.debug(f'Read: {data}') #debug
                        if  data==b"\x31":
                              logging.debug('UPS MODE: PROG') #debug
                              self.upscvar['mode']=2
                              return b'PROG'
            # Progmode
            if self.upscvar['mode']==2:
                  if cmd == b'\x30':
                        while 1:
                              reg0=self.eeprom['Reg0']
                              logging.debug(f'Send: {reg0}') #debug
                              self.ser.write(reg0)
                              self.ser.reset_input_buffer()
                              cmd = self.ser.readline(1)
                              logging.debug(f'Read: {cmd}') #debug
                              if cmd == b'\x2b':
                                    newreg=int(reg0, 16)+1
                                    self.eeprom['Reg0']=hex(newreg)[2:].encode().upper()
                                    continue
                              if cmd == b'\x2D':
                                    newreg=int(reg0, 16)-1
                                    self.eeprom['Reg0']=hex(newreg)[2:].encode().upper()
                                    continue
                              break
                              

                                    
                              

                  if cmd in self.cmdlist:
                        return self.cmdlist[cmd]()
                  
            logging.debug(f'CMD not found: {cmd}')
            # return b'NA'

      def start(self):
            
            while 1:
                  self.ser.reset_input_buffer()
                  data = self.ser.readline(1)
                  if data:
                        logging.debug(f'Read: {data}') #debug
                        returndata = self.cmdinterafce(data)
                        if returndata:
                              returndata=returndata+b'\x0D\x0A'
                              logging.debug(f'Send: {returndata}') #debug
                              self.ser.write(returndata)




if __name__ == "__main__": 
      apc1000i = {
            'upsname': b'Smart-UPS 1000',
            'upsusername': b'UPS_IDEN',
            'BatReplacement': b'13/12/01',
            'DateManufacture': b'13/12/01',
            'sn': b'AB0123456789',
            'Reg0': b'80',
            'Reg4': b'07',
            'Reg5': b'B5',
            'Reg6': b'13',
            'BatPcs': b'00',
            'VoltageRestart': b'00',
            'DelayBeep': b'01',
            'MinVoltage': b'01',
            'OutVoltage': b'02',
            'DelayOff': b'00',
            'Warn': b'00',
            'MaxVoltage': b'01',
            'Revision': b'07',
            'CoefficientW': b'AD',
            'CoefficientV': b'F0',
            'CoefficientBatV': b'F3'
      }

      apc700 = {
            'upsname': b'SMART-UPS700',
            'upsusername': b'UPS_IDEN',
            'BatReplacement': b'13/12/01',
            'DateManufacture': b'13/12/01',
            'sn': b'AB0123456789',
            'Reg0': b'30',
            'Reg4': b'28',
            'Reg5': b'EE',
            'Reg6': b'F8',
            'BatPcs': b'00',
            'VoltageRestart': b'00',
            'DelayBeep': b'01',
            'MinVoltage': b'01',
            'OutVoltage': b'02',
            'DelayOff': b'00',
            'Warn': b'00',
            'MaxVoltage': b'01',
            'Revision': b'07',
            'CoefficientW': b'AD',
            'CoefficientV': b'F0',
            'CoefficientBatV': b'F3'
      }

      upstest = apcemu()

      upstest.configups(**apc1000i)
      # upstest.configups()


      upstest.start()