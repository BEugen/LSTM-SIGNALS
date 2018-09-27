import sconfig
import struct


class SignalHeader:
    def __init__(self):
        self.Signature = '' # сигнатура файла
        self.Version = 0 # версия формата файла
        self.DataCRC32 = 0 # проверка данных
        self.HeaderCRC32 =  0 # проверка заголовка
        self.DataOffset = 0 # смещение данных от начала файла
        self.Compressed = False # флаг компрессии
        self.ExtendedCanals = 0 # АЦП сопровождается расширенными данными
        self.Platforms = 0 # количество платформ
        self.Canals = [] # количество датчиков на платформе
        self.StartDateTime = None # дата и время начала взвешивания
        self.Firm = '' # название фирмы
        self.ScalesName = '' # весовая
        self.ScalesType = '' # тип весов
        self.ConverterType = '' # тип преобразователя
        self.PacketsPerSecond = 0 # скорость пакетов в секунду
        self.Platform = []
        self.ExtendedNames = ''

    def ParseHeader(self, pathfile):
        f = open(pathfile, 'rb')
        header =f.read(sconfig.HeaderSize)
        if len(header) < len(sconfig.FileSignature):
            print(sconfig.CannotReadHeader)
            return False
        signature = "".join(map(chr, header[0:4]))
        if signature != sconfig.FileSignature:
            print(sconfig.UnknownFormat)
            return False
        s = struct.Struct('<4s b I I I b b b ' + str(sconfig.MaxCanals) + 'b d ' +
                          str(sconfig.LongStringMaxSize) + 's ' + str(sconfig.LongStringMaxSize) + 's ' +
                          str(sconfig.ShortStringMaxSize) + 's ' + str(sconfig.ShortStringMaxSize) + 's i')
        print(len(header))
        data = s.unpack_from(header)
        return True



class PlatformCalcDataRec:
    def __init__(self):
    # структура с данными для рассчета по платформе
        self.Length = 0 # длинна ГПУ
        self.NearLeftCanal = 0 # № канала левого ближнего датчика
        self.FarLeftCanal = 0 # № канала левого дальнего датчика
        self.FarRightCanal = 0 # № канала правого дальнего датчика
        self.NearRightCanal = 0 # № канала правого ближнего датчика
        self.Canal1NullCode = 0 # текущий код нуля канала №1
        self.Canal2NullCode = 0 # текущий код нуля канала №2
        self.Canal3NullCode = 0 # текущий код нуля канала №3
        self.Canal4NullCode = 0 # текущий код нуля канала №4
        self.Canal1ExemplaryNullCode = 0 # образцовый код нуля канала №1
        self.Canal2ExemplaryNullCode = 0 # образцовый код нуля канала №2
        self.Canal3ExemplaryNullCode = 0 # образцовый код нуля канала №3
        self.Canal4ExemplaryNullCode = 0 # образцовый код нуля канала №4
        self.ChTK = [] # массив коэффициентов по каналам
        self.ChTN = [] # массив коэффициентов по каналам
        self.Alpha = [] # массив коэффициентов по каналам
        self.Chk = [] # массив коэффициентов по каналам

