

FileNameExtension = '.sig' # стандартное расширение
DefaultCanals = 4 # количество датчиков на платформе по умолчанию
DefaultPlatforms = 1 # количество платформ по умолчанию
DefaultExtendedCanals = 0 # количество дискретных каналов по умолчанию
#
# изменение этих констант может привести к несовместимости форматов!
#
FileSignature = 'SGNL' # сигнатура файла
FileVersion = 0 # версия файла
BytesPerData = 4 # количество байт в элементе данных
MaxPlatforms = 4 # максимальное количество платформ
MaxCanals = 10 # максимальное количество каналов (изменять с особой осторожностью!)
MaxExtendedCanals = 10 # максимальное количество дискретных каналов
MaxFileSize = 100000000 # максимальный размер файла
LongStringMaxSize = 100
ShortStringMaxSize = 50
MaxExtendedDataSize = 2 # количество дискретных дачтиков MaxExtendedDataSize <= MaxExtendedCanals
ReferenceFrameID = 0xff # идентификатор дискретного пекета
ReferenceFrameSignature = 0x80 # сигнатура опорного кадра в дискретном пакете

# *******************************************
#    идентификаторы дискретных каналов
# *******************************************

IDTemperatureSensor = 0 # температурный датчик
IDTrackSensor = 1 # путевой датчик

