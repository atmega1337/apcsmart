import serial
import time





class apc:
    def __init__(self, port, timeout=1, debug=False):
        """
        Инициализация функции.

        - port = 'COM1'
        - timeout = 1
        - debug = False/True - print send and read message
        """
        baudrate = 2400

        self.ser = serial.serial_for_url(port, baudrate=baudrate, timeout=timeout)
        self.debug=debug
        pass
    def __readcmd(self, buffer):
        """Получение ответа"""
        self.ser.reset_input_buffer()
        out = self.ser.readline(32)
        if self.debug:
            print (f'Read: {out}') #debug
        return out.decode("utf-8").strip()
    def __sendcmd(self, cmd):
        """Отпрвка сообщения"""
        if self.debug:
            print (f'Send: {cmd}') #debug
        self.ser.write(cmd)
    def cmd(self, cmd, buffer=0):
        """Отпрвка сообщения и получение ответа"""
        self.__sendcmd(cmd)
        if buffer==0:
            return
        return self.__readcmd(buffer+2)

    def editreg(self, reg=int, value=str):
        """
        Редактор регистров
        """
        setvalue=int(value, 16)
        self.terminalmode_prog()

        origreg = self.cmd(b"\x30", 2)
        while 1:
            if int(origreg, 16) == setvalue:
                self.terminalmode_sm()
                return True
            if int(origreg, 16) < setvalue:
                origreg = self.cmd(b'+', 2)
            if int(origreg, 16) > setvalue:
                origreg = self.cmd(b'-', 2)

            
    def editdatemanufacture(self, date):
        """
        Изменение даты производства 

        MM/DD/YY
        """
        self.terminalmode_prog()
        self.cmd(b'm')
        time.sleep(.1)
        self.cmd(b'-')
        time.sleep(.1)
        for i in date:
            self.cmd(i.encode())
            time.sleep(.1)
    def editdatebatteryreplacement(self, date):
        """
        Изменение даты замены АКБ

        MM/DD/YY
        """
        self.terminalmode_prog()
        self.cmd(b'x')
        time.sleep(.1)
        self.cmd(b'-')
        time.sleep(.1)
        for i in date:
            self.cmd(i.encode())
            time.sleep(.1)
        if self.__readcmd(4) == 'OK':
            return True
        else:
            return False


    def terminalmode_sm(self):
        """Вводит Smart в режим мониторинга."""
        while 1:
            out = self.cmd(b"\x59", 2)
            if out == 'SM':
                return()
            time.sleep(1.5)
    def terminalmode_prog(self):
        """Сервисный режим UPS."""
        self.cmd(b"\x31")
        time.sleep(1.5)
        while 1:
            out = self.cmd(b"\x31", 4)
            if out == 'PROG':
                return()
            time.sleep(1.5)

    def terminalmode_off(self):
        """Выключение режима мониторинга."""
        while 1:
            out = self.cmd(b"\x52", 2)
            if out == 'BYE':
                return()
            time.sleep(1.5)



    def getModel(self):
        """Модель ИБП."""
        data=self.cmd(b"\x01", 116)
        return data
    def cmdPowerOn(self):
        """Включить UPS."""
        data=self.cmd(b"\x0E", 16)
        return data
    def getTestLine(self):
        """
        Оценка UPSом качества сети:

        ### Return:
        - 00 - bad
        - FF - good
        """
        data=self.cmd(b"\x39", 16)
        return data
    def getPcsBat(self):
        """Сообщает о количестве установленных батарей."""
        data=self.cmd(b"\x3E", 16)
        return data    
    def getCommands(self):
        """Cтрока возможностей."""
        data=self.cmd(b"\x0E", 16)
        return data
    def cmdTestBeepAndLed(self):
        """Тест индикации и звука 2 сек."""
        data=self.cmd(b"\x41", 5)
        return data
    def getBatVoltage(self):
        """Напряжение акб."""
        data=self.cmd(b"\x42", 5)
        return data
    def getTemperature(self):
        """Температура внутреннего термодатчика."""
        data=self.cmd(b"\x43", 5)
        return data
    def cmdBatteryCalibration(self):
        """
        Калибровка батарей.

        Cопровождается "!", по завершении "$".
        """
        data=self.cmd(b"\x44", 5)
        return data
    def getSelfTestInterval(self):
        """
        Интервал самотестирования.

        ### Return:
        - 366 - 14дней
        - 168 - 7дней
        - ON - при включении
        - OFF - нет самотестирования
        """
        data=self.cmd(b"\x45", 2)
        return data 
    def getInputFrequency(self):
        """Линейная частота."""
        data=self.cmd(b"\x46", 2)
        return data 
    def getReasonSwitchingToBattery(self):
        """
        Причина перехода на батарею.

        ### Return:
        - H - высокое напряжение
        - L - низкое напряжение
        - T - выравнивание напряжения
        - O - нет переключений от последней проверки
        - S - из-за команды "U"
        """
        data=self.cmd(b"\x47", 2)
        return data 
    def getInputVoltage(self):
        """Входное напряжение."""
        data=self.cmd(b"\x4C", 2)
        return data 
    def getinputvoltageMax(self):
        """Максимальное напряжение от посл. опроса."""
        data=self.cmd(b"\x4D", 2)
        return data 
    def getInputVoltageMin(self):
        """Минимальное напряжение от посл. опроса."""
        data=self.cmd(b"\x4E", 2)
        return data 
    def getOutputVoltage(self):
        """Выходное напряжение, см. при работе от бат."""
        data=self.cmd(b"\x4F", 2)
        return data
    def getLoadPower(self):
        """Мощность нагрузки %."""
        data=self.cmd(b"\x50", 2)
        return data
    def getFlag(self):
        """
        Флаг статуса.

        ### Return:
        - 0x01 - Состояние рабочей калибровки. Не сообщают Smart UPSv/s, Back UPS Pro.
        - 0x02 - Режим Smart Trim. Не сообщается 1 и 2 поколением Smart.
        - 0x04 - Режим Smart Boost.
        - 0x08 - Работа в сети   On Line
        - 0x10 - Работа от батарей  On Battery.
        - 0x20 - UPS перегружен.
        - 0x40 - Батарея разряжена. (battery low)
        - 0x80 - Замените батарею.(replace battery)
        """
        data=self.cmd(b"\x51", 2)
        return data
    def getOldModel(self):
        """
        Cтарая марка изготовления.

        ### Первый символ:
            - 0 - Matrix 3000
            - 5 - Matrix 5000
            - 2 - Smart-UPS 250
            - 3 - Smart-UPS 400
            - 4 - Smart-UPS 400
            - 6 - Smart-UPS 600
            - 7 - Smart-UPS 900
            - 8 - Smart-UPS 1250
            - 9 - Smart-UPS 2000
            - A - Smart-UPS 1400
            - B - Smart-UPS 1000
            - C - Smart-UPS 650
            - D - Smart-UPS 420
            - E - Smart-UPS 280
            - F - Smart-UPS 450
            - G - Smart-UPS 700
            - H - Smart-UPS 700XL
            - I - Smart-UPS 1000
            - J - Smart-UPS 1000XL
            - K - Smart-UPS 1400
            - L - Smart-UPS 1400XL
            - M - Smart-UPS 2200
            - N - Smart-UPS 2200XL
            - O - Smart-UPS 3000
            - P - Smart-UPS 5000
            - Q - Back-UPS

        ### Второй:
            - W - расширенная для 3 поколения Smart-UPS
            - Q - Для второго поколения Smart-UPS
            - T - типовая  для 1 поколения Smart-UPS
            - U - ультра для модульных и наращиваемых UPS

        ### Третий:
            - D - для внутреннего использования (USA)
            - I - выходное напряжение 240в (интернациональная версия)
            - M - выходное напряжение 208в (для военного применения)
            - J - выходное напряжение 100/200в (для Японии)
        """
        data=self.cmd(b"\x56", 2)
        return data
    def cmdSelfTest(self):
        """
        Тест работоспособности батарей.
        """
        data=self.cmd(b"\x57", 2)
        return data
    def GetSelfTestResult(self):
        """
        Результат Selftest.
        
        ### Return:
        - OK - хорошая батарея
        - BT - недостаточная ёмкость батарей
        - NG - тест не прошёл
        - NO - тест не проводился последние пять минут
        """
        data=self.cmd(b"\x58", 2)
        return data
    def GetInfoProtocol(self):
        """
        Информация протокола, показывает три основных раздела разделённых точкой:
        1. Версия протокола
        2. Аварийные сообщения:
            - ! (0x21) - Сбой сети - посылается UPS при переходе на батарею, повторяется каждые 30 секунд.
            - $ (0x24) - Возврат UPS на работу от батарей к сети.
            - % (0x25) - Разряжена батарея. Не для SmartUPSv/s, BackUPS Pro.
            - + (0x2B) - Возврат от предыдущего сигнала при заряде батареи.
            - ? (0x3F) - Аварийное состояние - посылается при выключении по перегрузке или недостаточной ёмкости батарей, так же через 10 минут после выключения.
            - = (0x3D) - Возврат из аварийного состояния. Не работает в SmartUPS v/s, BackUPS Pro.
            - * (0x2A) - Ожидание выключения, посылается когда UPS готовится выключить нагрузку. После этого символа никакие команды не обрабатываются. Не работает в Smart v/s, BackUPS Pro, SmartUPS третьего поколения.
            - # (0x23) - Замена батареи, посылается когда UPS определяет, что необходимо заменить батарею, посылается  каждые пять часов. Не для SmartUPSv/s, BackUPS Pro.
            - & (0x26) - Не определено!!!
            - | (0x7C) - Изменение переменных в EEPROM, посылается при изменении данных в EEPROM. Поддерживается MatrixUPS и SmartUPS третьего поколения.
        3. Используемые команды
        """
        data=self.cmd(b"\x61", 2)
        return data
    def getSoftVersion(self):
        """Ревизия программы."""
        data=self.cmd(b"\x62", 2)
        return data  
    def getName(self):
        """Имя ИБП определяемое пользователем."""
        data=self.cmd(b"\x63", 2)
        return data  
    def getMinVoltageBatForStartupUPS(self):
        """
        Минимальный уровень разряда батарей в %, для включения UPS после возврата питающего напряжения. 
        Предотвращает частые переключения в связи со сбоями питания.
        
        ### Return:
        - 00 - 00% (немедленное переключение)
        - 01 - 15%
        - 02 - 50%
        - 03 - 90%
        """
        data=self.cmd(b"\x65", 2)
        return data  
    def getBatLevel(self):
        """Уровень заряда батарей в процентах %."""
        data=self.cmd(b"\x66", 2)
        return data  
    def getNominalBatVoltage(self):
        """Номинальное напряжение батарей."""
        data=self.cmd(b"\x67", 2)
        return data  
    def getRunTime(self):
        """Runtime."""
        data=self.cmd(b"\x6A", 2)
        return data  
    def getBeepDelay(self):
        """
        Задержка подачи звукового сигнала.
        
        ### Return:
        - 0 - 5 секунд
        - T - 30 секунд
        - L - только при разряженных батареях
        - N - сигнал отключен)
        """
        data=self.cmd(b"\x6B", 2)
        return data  
    def getMinVoltage(self):
        """
        Минимальное напряжение переключения UPS на батарею.

        ### Return:
        - 00 - 196v
        - 01 - 188v
        - 02 - 208v
        - 03 - 204v.
        """
        data=self.cmd(b"\x6C", 2)
        return data  
    def getDateManufacture(self):
        """
        Дата производства

        MM/DD/YY
        """
        data=self.cmd(b"\x6D", 8)
        return data
    def getSN(self):
        """Серийный номер"""
        data=self.cmd(b"\x6E", 2)
        return data  
    def getOutputVoltageInvertor(self):
        """
        Выходное напряжение при работе от батарей. 
        
        ### Return:
        - 00 - 230v  
        - 01 - 240v  
        - 02 - 220v
        - 03 - 225v
        """
        data=self.cmd(b"\x6F", 2)
        return data  
    def getDelayOff(self):
        """
        Задержка выключения в сек.
        
        ### Return:
        - 00 - 020 (по умолчанию)
        - 01 - 180c
        - 02 - 300c
        - 03 - 600c
        """
        data=self.cmd(b"\x70", 2)
        return data  
    def getDelayReportLowBattery(self):
        """
        Время сообщения о разряженной батареи перед выключением питания в минутах.

        ### Return:
        - 00 - 02мин (по умолчанию)
        - 01 - 05мин
        - 02 - 07мин
        - 03 - 10мин.
        """
        data=self.cmd(b"\x71", 2)
        return data  
    def getDelayBeeps(self):
        """
        Задержка подачи сигнала в секундах.

        ### Return:
        - 00 - 000с 
        - 01 - 060с
        - 02 - 180с 
        - 03 - 300с
        """
        data=self.cmd(b"\x72", 2)
        return data  
    def getSensitivity(self):
        """
        Чувствительность. 
        
        ### Return:
        - H - высокая
        - M - средняя
        - L - низкая
        - A - автокоррекция только для  Matrix
        """
        data=self.cmd(b"\x73", 2)
        return data  
    def getMaxInputVoltage(self):
        """
        При достижении данного напряжения в сети UPS переходит на батареи.

        ### Return:
        - 00h - 253v (по умолчанию)
        - 01h - 264v
        - 02h - 271v
        - 03h - 280v
        """
        data=self.cmd(b"\x75", 2)
        return data  
    def getDateBatReplacement(self):
        """
        Дата замены акб

        MM/DD/YY
        """
        data=self.cmd(b"\x78", 8)
        return data
    def getCopyright(self):
        """
        (C)APCC Объявление авторского права.

        ### Return: (C)APCC
        """
        data=self.cmd(b"\x79", 2)
        return data  
    def cmdResetUserSettings(self):
        """
        Сброс пользовательских настроек к заводским.
        
        ### Return: CLEAR
        """
        data=self.cmd(b"\x7A", 2)
        return data  
    
    
    def getReg0(self):
        data=self.cmd(b"0", 2)
        return data
    def getReg1(self):
        data=self.cmd(b"\x7E", 2)
        return data
    def getReg2(self):
        data=self.cmd(b"\x27", 2)
        return data
    def getReg3(self):
        data=self.cmd(b"\x28", 2)
        return data
    def getReg4(self):
        data=self.cmd(b"4", 2)
        return data
    def getReg5(self):
        data=self.cmd(b"5", 2)
        return data 
    def getReg6(self):
        data=self.cmd(b"6", 2)
        return data 
