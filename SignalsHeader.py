import sconfig
import struct
import os
from datetime import timedelta, datetime

class SignalHeader:
    def __init__(self):
        self.Signature = ''  # сигнатура файла
        self.Version = 0  # версия формата файла
        self.DataCRC32 = 0  # проверка данных
        self.HeaderCRC32 = 0  # проверка заголовка
        self.DataOffset = 0  # смещение данных от начала файла
        self.Compressed = False  # флаг компрессии
        self.ExtendedCanals = 0  # АЦП сопровождается расширенными данными
        self.Platforms = 0  # количество платформ
        self.Canals = []  # количество датчиков на платформе
        self.StartDateTime = None  # дата и время начала взвешивания
        self.Firm = ''  # название фирмы
        self.ScalesName = ''  # весовая
        self.ScalesType = ''  # тип весов
        self.ConverterType = ''  # тип преобразователя
        self.PacketsPerSecond = 0  # скорость пакетов в секунду
        self.Platform = []
        self.ExtendedNames = []
        self.XorSeedIndex = 0
        self.CRC32Bytes = []
        self.GetCRC32Bytes()
        self.FileSize = 0

    def ParseHeader(self, pathfile):
        self.FileSize = os.path.getsize(pathfile)
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
        dt = datetime(1899, 12, 30)
        dt = dt + timedelta(days=data[18])
        self.StartDateTime = dt
        self.Firm = data[19].decode('cp1251')
        self.ScalesName = data[20].decode('cp1251')
        self.ScalesType = data[21].decode('cp1251')
        self.ConverterType = data[22].decode('cp1251')
        self.PacketsPerSecond = data[23]
        for i in range(0, sconfig.MaxPlatforms):
            self.Platform.append(self.GetPlatformCalcDataRec(header[s.size + sconfig.PlatformCalcDataRecSize * i:
                                                                    s.size + sconfig.PlatformCalcDataRecSize * (
                                                                            i + 1)]))
        offset = header[s.size + sconfig.PlatformCalcDataRecSize * sconfig.MaxPlatforms: sconfig.HeaderSize]
        for i in range(0, sconfig.MaxExtendedCanals):
            self.ExtendedNames.append(offset[sconfig.ShortStringMaxSize * i:
                                             sconfig.ShortStringMaxSize * (i + 1)].decode('cp1251'))
        return True

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
            pr.Alpha.append(data[21 + i * 7:21 + (i + 1) * 7])
        pr.Chk = data[49:53]
        return pr

    def GetCRC32Bytes(self):
        # создание массива байт для учета позиции при расчете CRC32
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
        self.Length = 0  # длинна ГПУ
        self.NearLeftCanal = 0  # № канала левого ближнего датчика
        self.FarLeftCanal = 0  # № канала левого дальнего датчика
        self.FarRightCanal = 0  # № канала правого дальнего датчика
        self.NearRightCanal = 0  # № канала правого ближнего датчика
        self.Canal1NullCode = 0  # текущий код нуля канала №1
        self.Canal2NullCode = 0  # текущий код нуля канала №2
        self.Canal3NullCode = 0  # текущий код нуля канала №3
        self.Canal4NullCode = 0  # текущий код нуля канала №4
        self.Canal1ExemplaryNullCode = 0  # образцовый код нуля канала №1
        self.Canal2ExemplaryNullCode = 0  # образцовый код нуля канала №2
        self.Canal3ExemplaryNullCode = 0  # образцовый код нуля канала №3
        self.Canal4ExemplaryNullCode = 0  # образцовый код нуля канала №4
        self.ChTK = []  # массив коэффициентов по каналам
        self.ChTN = []  # массив коэффициентов по каналам
        self.Alpha = []  # массив коэффициентов по каналам
        self.Chk = []  # массив коэффициентов по каналам


class AsiSignalItem:
    def __init__(self):
        self.FPlatforms = 0  # количество платформ в сигнале
        self.FCanals = []  # количество датчиков на платформе
        self.FBuffer = []  # буфер
        self.FBufferSize = 0  # размер буфера
        self.FOffsets = []  # таблица смещений начала данных по платформам
        self.FExtended = []  # последняя дискретная информация, бывшая в обработке
        self.FExtendedCanals = 0  # количество дискретных каналов
        self.FHaveExtended = False  # найдены ли дискретные данные (для ускорения)
        self.Values = [] # массив кодов АЦП
        self.Extended = [] #массив дискретной информации
        self.Point = [] # данные точки целиком
        self.PointSize = 0 # размер массива точки
        self.Platforms = 0 # количество платформ
        self.Canals = [] # количество датчиков
        self.ExtendedCanals = 0 # количество дискретных каналов
        self.HaveExtended = False # наличие дискретной информации
        for i in range(0, sconfig.MaxCanals):
            self.FCanals.append(sconfig.DefaultCanals)

    def init(self):
        if self.FPlatforms > 0:
            self.FOffsets = []
            self.FOffsets.append(0)
            for i in range(0, self.FPlatforms):
                self.FOffsets.append(self.FOffsets[i - 1] + sconfig.BytesPerData * self.FCanals[i - 1])
            self.FBufferSize = self.FOffsets[self.FPlatforms - 1] + \
                               sconfig.BytesPerData * self.FCanals[self.FPlatforms - 1]
            self.FBuffer = [0 for _ in range(self.FBufferSize)]
            self.Point = self.FBuffer
            self.PointSize = self.FBufferSize
        else:
            self.FBufferSize = 0

    def getvalue(self, platform, canal):
        if platform >= self.FPlatforms:
            return
        if platform < 0:
            return
        if canal >= self.FCanals[platform]:
            return
        if canal < 0:
            return
        # определение смещения
        index = int(self.FOffsets[platform] / sconfig.BytesPerData) + canal
        return self.FBuffer[index]

    def getvalueex(self, platform, canal):
        # чтение кода АЦП и дискреных данных
        if platform >= self.Platforms:
            return
        if platform < 0:
            return
        if canal >= self.Canals[platform]:
            return
        if canal < 0:
            return
        # определение смещения
        index = self.FOffsets[platform] + canal * sconfig.BytesPerData
        result = self.FBuffer[index]
        # если есть дискретные данных по платформе, сигналу
        if self.FHaveExtended:
            for i in range(0, sconfig.MaxExtendedDataSize):
                if self.FExtended[platform][canal][i]:
                    if self.Extended:
                        extended = self.FExtended[platform][canal]
                        return result, extended
        return result, None


class AsiExtendedData:
    def __init__(self):
        self.Index = 0
        self.Platform = 0
        self.Canal = 0
        self.Id = 0
        self.Value = 0


class AsiReferenceFrame:
    def __init__(self):
        self.Signature = 0
        self.Id = 0
        self.Value = 0

class AsiSignal:
    def __init__(self):
        self.Header = SignalHeader()
        self.PointBuffer = []
        self.Diff = []
        self.PointIndex = 0
        self.Point = []
        self.Extended = []
        self.Item = AsiSignalItem()
        self.PointBufferSize = 0
        self.PointBufferIntSize = 0
        self.FileBufferSize = 0
        self.FileBufferStart = 0
        self.FileHandle = None
        self.FileBuffer = None
        self.FilePosition = 0
        self.EOF = False
        self.FileSize = 0

    def getdata(self, pathfile):
        if not self.readheader(pathfile):
            return None
        self.readadcdata(pathfile)

    def readheader(self, pathfile):
        if self.Header.ParseHeader(pathfile):
            self.setextendedcanals(self.Header.ExtendedCanals)
            self.setplatforms(self.Header.Platforms)
            self.FilePosition = self.Header.DataOffset
            self.FileSize = self.Header.FileSize
            return True
        return False

    def readadcdata(self, pathfile):
        pointindex = 0
        f = open(pathfile, 'rb')
        f.seek(self.FilePosition)
        self.FileHandle = f
        while not self.EOF:
            if self.getpoint():
                for k in range(0, self.Header.Platforms):
                    for j in range(0, self.Header.Canals[k]):
                        print(k, j, self.Item.getvalue(k, j))
        self.FileHandle.close()

    def setextendedcanals(self, value):
        if value > sconfig.MaxExtendedCanals - 1:
            print(sconfig.CannotChangeExtendedCanals)
        if self.Item.FExtendedCanals == value:
            return
        self.Item.FExtendedCanals = value
        self.itemreinit()

    def setplatforms(self, value):
        if value < 0 or value > sconfig.MaxPlatforms:
            print(sconfig.CannotChangePlatforms)
            return
        if self.Item.FPlatforms == value:
            return
        self.Item.FPlatforms = value
        self.itemreinit()

    def itemreinit(self):
        self.Item.init()
        self.PointBuffer = self.Item.Point
        self.PointBufferSize = self.Item.PointSize
        self.PointBufferIntSize = round(self.PointBufferSize / sconfig.BytesPerData)
        self.Diff = []

    def fetchfrombuffer(self, buffer, size):
        result = True
        canfetch = self.FileBufferSize - self.FileBufferStart
        fetched = 0
        if canfetch > 0:
            if canfetch >= size:
                fetched = size
            else:
                fetched = canfetch
            curpos = self.FileBufferStart
            for i in range(curpos, curpos+fetched):
                buffer.append(self.FileBuffer[i])
            self.FileBufferStart += fetched
        if canfetch < size:
            self.cleanbuffer()
            curpos = self.FileBufferStart
            size -= fetched
            curpos += fetched
            self.FileBufferSize = self.readfrombuffer()
            canfetch = self.FileBufferSize - self.FileBufferStart
            if canfetch > 0:
                if canfetch < size:
                    fetched = canfetch
                    result = False
                else:
                    fetched = size
                for i in range(curpos, curpos + fetched):
                    buffer.append(self.FileBuffer[i])
                self.FileBufferStart += fetched
            else:
                result = False
        return result

    def cleanbuffer(self):
        self.FileBufferSize = 0
        self.FileBufferStart = 0

    def getpoint(self):
        result = True
        source = self.PointBuffer
        ind = 0
        for i in range(0, self.PointBufferIntSize):
            extpacket = []
            valuefound = False
            while not valuefound:
                size = 1
                self.FilePosition += size
                if not self.fetchfrombuffer(extpacket, size):
                    return False
                if extpacket[0] == sconfig.ReferenceFrameSignature:
                    size = sconfig.SizeAsiReferenceFrame - 1
                    self.FilePosition += size
                    if not self.fetchfrombuffer(extpacket, size):
                        return False
                    if extpacket[1] == sconfig.ReferenceFrameID:
                        s = struct.Struct('<i')
                        value = s.unpack_from(bytearray(extpacket[2:6]))
                        source[ind] = value[0]
                        valuefound = True
                    else:
                        pass
                else:
                    dx = self.bytetosigned(extpacket[0])
                    source[ind] = self.Diff[ind] + dx
                    valuefound = True
                ind += 1
        self.Diff[0:self.PointBufferSize] = source[0:self.PointBufferSize]
        if self.FilePosition >= self.FileSize:
            self.EOF = True
        return result

    def readfrombuffer(self):
        if self.FileHandle:
            self.FileBuffer = bytearray(self.FileHandle.read(sconfig.DefaultFileBufferSize))
            return sconfig.DefaultFileBufferSize


    def bytetosigned(self, byte):
        if byte > 127:
            return (256 - byte) * (-1)
        else:
            return byte







