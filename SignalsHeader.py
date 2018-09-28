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
        self.ExtendedNames = []
        self.XorSeedIndex = 0
        self.CRC32Bytes = []
        self.GetCRC32Bytes()

    def ParseHeader(self, pathfile):
        f = open(pathfile, 'rb')
        header = bytearray(f.read(sconfig.HeaderSize))
        f.close()
        if len(header) < len(sconfig.FileSignature):
            print(sconfig.CannotReadHeader)
            return False
        signature = "".join(map(chr, header[0:4]))
        if signature != sconfig.FileSignature:
            print(sconfig.UnknownFormat)
            return False
        self.ResetXorIndex()
        start = sconfig.SizeHeaderSignature + sconfig.SizeHeaderVersion + sconfig.SizeHeaderDataCRC32
        for idx in range(start, sconfig.HeaderSize):
            header[idx] = header[idx] ^ self.GetXorByte()
        s = struct.Struct('<4s b I I I b b b ' + str(sconfig.MaxCanals) + 'b d ' +
                          str(sconfig.LongStringMaxSize) + 's ' + str(sconfig.LongStringMaxSize) + 's ' +
                          str(sconfig.ShortStringMaxSize) + 's ' + str(sconfig.ShortStringMaxSize) + 's i')
        data = s.unpack_from(header)
        headeroffset = sconfig.SizeHeaderSignature + sconfig.SizeHeaderVersion + \
                        sconfig.SizeHeaderDataCRC32 + sconfig.SizeHeaderHeaderCRC32

        crc32header = self.CRC32FromBuffer(header[headeroffset:sconfig.HeaderSize])
        if data[3] != crc32header:
            print(sconfig.BrokenHeader)
            return False
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
                self.Platform.append(self.GetPlatformCalcDataRec(header[s.size + sconfig.PlatformCalcDataRecSize*i:
                                                   s.size + sconfig.PlatformCalcDataRecSize*(i+1)]))
        offset = header[s.size + sconfig.PlatformCalcDataRecSize*sconfig.MaxPlatforms : sconfig.HeaderSize]
        for i in range(0, sconfig.MaxExtendedCanals):
            self.ExtendedNames.append(offset[sconfig.ShortStringMaxSize*i:
                                             sconfig.ShortStringMaxSize*(i+1)].decode('cp1251'))
        return True

    def ReadADCData(self, pathfile):
        f = open(pathfile, 'rb')
        f.seek(self.DataOffset)

        f.close()

    def GetXorByte(self):
        xor = int(ord(sconfig.XORSeed[self.XorSeedIndex].encode('cp1251')) ^ sconfig.XORMask)
        self.XorSeedIndex += 1
        if self.XorSeedIndex >= len(sconfig.XORSeed):
            self.XorSeedIndex = 0
        return xor

    def ResetXorIndex(self):
        self.XorSeedIndex = 0


    def GetPlatformCalcDataRec(self, buff):
        s = struct.Struct('<i i i i i i i i i i i i i 4d 4d 28d 4d')
        data = s.unpack_from(buff)
        pr = PlatformCalcDataRec()
        pr.Length = data[0]
        pr.NearLeftCanal = data[1]
        pr.FarLeftCanal = data[2]
        pr.FarRightCanal = data[3]
        pr.NearRightCanal = data[4]
        pr.Canal1NullCode = data[5]
        pr.Canal2NullCode = data[6]
        pr.Canal3NullCode = data[7]
        pr.Canal4NullCode = data[8]
        pr.Canal1ExemplaryNullCode = data[9]
        pr.Canal2ExemplaryNullCode = data[10]
        pr.Canal3ExemplaryNullCode = data[11]
        pr.Canal4ExemplaryNullCode = data[12]
        pr.ChTK = data[13:17]
        pr.ChTN = data[17:21]
        for i in range(0, 4):
            pr.Alpha.append(data[21+i*7:21+(i+1)*7])
        pr.Chk = data[49:53]
        return pr

    def GetCRC32Bytes(self):
        #создание массива байт для учета позиции при расчете CRC32
        for byte in range(256):
            crc = 0
            for bit in range(8):
                if (byte ^ crc) & 1:
                    crc = (crc >> 1) ^ sconfig.CRC32Poly
                else:
                    crc >>= 1
                byte >>= 1
            self.CRC32Bytes.append(crc)

    def CRC32FromBuffer(self, buffer):
        value = 0xffffffff
        for ch in buffer:
            value = self.CRC32Bytes[(ch ^ value) & 0x000000ff] ^ (value >> 8)
        value = ~value & 0xffffffff
        return value

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

