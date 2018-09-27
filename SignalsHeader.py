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
        self.XorSeedIndex = 0

    def ParseHeader(self, pathfile):
        f = open(pathfile, 'rb')
        header = bytearray(f.read(sconfig.HeaderSize))
        if len(header) < len(sconfig.FileSignature):
            print(sconfig.CannotReadHeader)
            return False
        signature = "".join(map(chr, header[0:4]))
        if signature != sconfig.FileSignature:
            print(sconfig.UnknownFormat)
            return False
        self.ResetXorIndex()
        #start = size Header Signature + size Header Version + size Header DataCRC32
        start = sconfig.SizeHeaderSignature + sconfig.SizeHeaderVersion + sconfig.SizeHeaderDataCRC32
        for idx in range(start, sconfig.HeaderSize):
            header[idx] = header[idx] ^ self.GetXorByte()
        s = struct.Struct('<4s b I I I b b b ' + str(sconfig.MaxCanals) + 'b d ' +
                          str(sconfig.LongStringMaxSize) + 's ' + str(sconfig.LongStringMaxSize) + 's ' +
                          str(sconfig.ShortStringMaxSize) + 's ' + str(sconfig.ShortStringMaxSize) + 's i')
        data = s.unpack_from(header)
        self.Signature = data[0]
        self.Version = data[1]
        self.DataCRC32 = data[2]
        self.HeaderCRC32 = data[3]
        self.DataOffset = data[4]
        self.Compressed = data[5]
        self.ExtendedCanals = data[6]
        self.Platforms = data[7]
        self.Canals = data[8:18]
        self.StartDateTime = data[18]
        self.Firm = data[19].decode('cp1251')
        self.ScalesName = data[20].decode('cp1251')
        self.ScalesType = data[21].decode('cp1251')
        self.ConverterType = data[22].decode('cp1251')
        self.PacketsPerSecond = data[23]
        for i in range(0, sconfig.MaxPlatforms):
                pass
        return True

    def GetXorByte(self):
        xor = int(ord(sconfig.XORSeed[self.XorSeedIndex].encode('cp1251')) ^ sconfig.XORMask)
        self.XorSeedIndex += 1
        if self.XorSeedIndex >= len(sconfig.XORSeed):
            self.XorSeedIndex = 0
        return xor

    def ResetXorIndex(self):
        self.XorSeedIndex = 0


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

