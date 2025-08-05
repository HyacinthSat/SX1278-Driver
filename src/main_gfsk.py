# 接口与引脚定义
"""
3.3V    --------> 3.3V
GND     --------> GND
NSS     --------> GP13 (SPI1 CSN)
SCK     --------> GP10 (SPI1 SCK)
MOSI    --------> GP11 (SPI1 TX)
MISO    --------> GP12 (SPI1 RX)
RST     --------> GP8
DIO0    --------> GP9
"""

from machine import Pin, SPI
import random
import time

# SX1278 寄存器通用地址定义
## FIFO 操作
REG_FIFO            =  0x00  # FIFO 读/写访问
## 基础设置
REG_OP_MODE         =  0x01  # 运行模式/调制模式选择
REG_BITRATE_MSB     =  0x02  # 比特率设置（高 8 位）
REG_BITRATE_LSB     =  0x03  # 比特率设置（低 8 位）
REG_FDEV_MSB        =  0x04  # 频偏设置（高 8 位）
REG_FDEV_LSB        =  0x05  # 频偏设置（低 8 位）
REG_FRF_MSB         =  0x06  # 频率设置（高 8 位）
REG_FRF_MID         =  0x07  # 频率设置（中 8 位）
REG_FRF_LSB         =  0x08  # 频率设置（低 8 位）
## 发射机设置
REG_PA_CONFIG       =  0x09  # PA 选择和输出功率控制
REG_PA_RAMP         =  0x0A  # PA 斜升/斜降时间和低相噪PLL的控制 
REG_OCP             =  0x0B  # 过电流保护设置
## RC 振荡器
REG_OSC             =  0x24  # RC 振荡器控制
## 数据包设置
REG_PREAMBLE_MSB    =  0x25  # 前导码长度（高 8 位）
REG_PREAMBLE_LSB    =  0x26  # 前导码长度（低 8 位）
REG_SYNC_CONFIG     =  0x27  # 同步字长度和同步头检测模式
REG_SYNC_VALUE1     =  0x28  # 同步字（字节 1）
REG_SYNC_VALUE2     =  0x29  # 同步字（字节 2）
REG_SYNC_VALUE3     =  0x2A  # 同步字（字节 3）
REG_SYNC_VALUE4     =  0x2B  # 同步字（字节 4）
REG_SYNC_VALUE5     =  0x2C  # 同步字（字节 5）
REG_SYNC_VALUE6     =  0x2D  # 同步字（字节 6）
REG_SYNC_VALUE7     =  0x2E  # 同步字（字节 7）
REG_SYNC_VALUE8     =  0x2F  # 同步字（字节 8）
REG_PACKET_CONFIG1  =  0x30  # 数据包模式设置
REG_PACKET_CONFIG2  =  0x31  # 数据包模式设置
REG_PAYLOAD_LENGTH  =  0x32  # 数据包长度
REG_NODE_ADRS       =  0x33  # 节点地址 (过滤用)
REG_BROADCAST_ADRS  =  0x34  # 广播地址 (过滤用)
REG_FIFO_THRESH     =  0x35  # FIFO 发送阈值
## 状态寄存器
REG_IRQ_FLAGS1      =  0x3E  # 中断标志 1
REG_IRQ_FLAGS2      =  0x3F  # 中断标志 2
## 版本寄存器
REG_VERSION         =  0x42  # 版本寄存器

# 硬件基本定义
F_XOSC   = 32000000 # 晶体振荡器频率
SPI_BAUD = 5000000  # SPI通信波特率

# 定义基本引脚
nss  = Pin(13, Pin.OUT)
rst  = Pin(8, Pin.OUT)
sck  = Pin(10)
mosi = Pin(11)
miso = Pin(12)


"""基本操作函数"""

# 写寄存器
def write_reg(addr, value):
    nss.value(0)
    spi.write(bytearray([addr | 0x80, value]))
    nss.value(1)

# 读寄存器
def read_reg(addr):
    nss.value(0)
    spi.write(bytearray([addr & 0x7F]))
    data = spi.read(1)
    nss.value(1)
    return data[0]

# 硬件复位
def sx1278_reset():
    rst.value(0)
    time.sleep_ms(100)
    rst.value(1)
    time.sleep_ms(100)

# 写寄存器位
def write_reg_bit(address, bit_pos, value):
    if not 0 <= bit_pos <= 7:
        raise ValueError("Bit position must be between 0 and 7 for an 8-bit register")
    if value not in (0, 1):
        raise ValueError("Value must be 0 or 1")
    
    # 读取寄存器当前值
    current_value = read_reg(address)
    
    # 根据 value 进行修改
    if value == 1:
        # 置 1 操作：使用按位或
        new_value = current_value | (1 << bit_pos)
    else: # value == 0
        # 置 0 操作：使用按位与和按位取反
        new_value = current_value & ~(1 << bit_pos)

    # 将新值写入寄存器
    write_reg(address, new_value)

# 读寄存器位
def read_reg_bit(address, bit_pos):
    value = read_reg(address)
    return (value >> bit_pos) & 0x01

"""功能函数"""

# 设置载波频率（Hz）
def sx1278_set_frequency(freq_hz):

    # 计算寄存器值
    F_STEP = F_XOSC / 2**19
    F_rf = int(freq_hz / F_STEP)
    
    write_reg(REG_FRF_MSB, (F_rf >> 16) & 0xFF)
    write_reg(REG_FRF_MID, (F_rf >> 8) & 0xFF)
    write_reg(REG_FRF_LSB, F_rf & 0xFF)
    
    # 读取回频率寄存器以验证
    msb = read_reg(REG_FRF_MSB)
    mid = read_reg(REG_FRF_MID)
    lsb = read_reg(REG_FRF_LSB)
    F_rf_read = (msb << 16) | (mid << 8) | lsb
    actual_freq = F_rf_read * F_STEP

    print("设定频率：", freq_hz, "Hz")
    print("读取频率：", int(actual_freq), "Hz")
    print(f"寄存器写入值：0x{F_rf:04X}")
    print(f"寄存器读取值：0x{F_rf_read:06X}\n")

# 设置频偏频率（Hz）
def sx1278_set_freqdev(freqdev_hz):

    # 计算寄存器值
    F_STEP = F_XOSC / 2**19
    F_dev = int(freqdev_hz / F_STEP)

    write_reg(REG_FDEV_MSB, (F_dev >> 8) & 0xFF)
    write_reg(REG_FDEV_LSB, F_dev & 0xFF)

    # 读取回频率偏移寄存器以验证
    msb = read_reg(REG_FDEV_MSB)
    lsb = read_reg(REG_FDEV_LSB)
    F_dev_read = (msb << 8) | lsb
    actual_freqdev = F_dev_read * F_STEP

    print("设定频偏：", freqdev_hz, "Hz")
    print("实际频偏：", int(actual_freqdev), "Hz")
    print(f"寄存器写入值：0x{F_dev:04X}")
    print(f"寄存器读取值：0x{F_dev_read:04X}\n")

# 设置空中比特率
def sx1278_set_bitrate(bps):

    # 计算寄存器值
    bitrate_reg_value = round(F_XOSC / bps)

    # 写入比特率寄存器的MSB和LSB
    write_reg(REG_BITRATE_MSB, (bitrate_reg_value >> 8) & 0xFF)
    write_reg(REG_BITRATE_LSB, bitrate_reg_value & 0xFF)

    # 读取回频率偏移寄存器以验证
    msb = read_reg(REG_BITRATE_MSB)
    lsb = read_reg(REG_BITRATE_LSB)
    read_bitrate_reg_value = (msb << 8) | lsb
    actual_bps = F_XOSC / read_bitrate_reg_value

    print("设定空中比特率：", bps, "bps")
    print("实际空中比特率：", int(actual_bps), "bps")
    print(f"寄存器写入值：0x{bitrate_reg_value:04X}")
    print(f"寄存器读取值：0x{read_bitrate_reg_value:04X}\n")

# SX1278 初始化
def sx1278_init(air_frequency, air_bitrate, module_depth):

    """
    # 设置 REG_OP_MODE 寄存器，进入 Sleep 模式
    print("尝试设置为睡眠模式")
    write_reg_bit(REG_OP_MODE, 2, 0)  # 设置为睡眠模式
    write_reg_bit(REG_OP_MODE, 1, 0)  # 设置为睡眠模式
    write_reg_bit(REG_OP_MODE, 0, 0)  # 设置为睡眠模式
    # 读取 IRQ_FLAGS1 寄存器中的第 7 位验证是否准备完成
    n = 0
    while (read_reg_bit(REG_IRQ_FLAGS1, 7)) == 0 and n <= 20:
        time.sleep_ms(100)
        n = n + 1
    if n >= 10:
        print("未进入睡眠模式：", hex(read_reg(REG_IRQ_FLAGS1)))
    else:
        print("已进入睡眠模式\n")
    """
    
    # 设置 REG_OP_MODE 寄存器，进入 FSK 模式
    write_reg_bit(REG_OP_MODE, 7, 0)  # 设置为 FSK/OOK 模式
    write_reg_bit(REG_OP_MODE, 6, 0)  # 设置为 FSK 模式
    write_reg_bit(REG_OP_MODE, 5, 0)  # 设置为 FSK 模式
    write_reg_bit(REG_OP_MODE, 3, 0)  # 设置为 LF 低频段 (UHF 低)

    # 设置波特率
    sx1278_set_bitrate(air_bitrate)

    # 设置频偏
    sx1278_set_freqdev((air_bitrate * module_depth)/2)

    # 设置载波频率
    sx1278_set_frequency(air_frequency)

    # 设置 REG_PA_CONFIG 寄存器，调整功放配置
    write_reg_bit(REG_PA_CONFIG, 7, 1)  # 设置输出为 PA_BOOST
    write_reg_bit(REG_PA_CONFIG, 3, 1)  # 设置输出功率衰减为 2 dBm (15dBm)
    write_reg_bit(REG_PA_CONFIG, 2, 1)  # 设置输出功率衰减为 2 dBm (15dBm)
    write_reg_bit(REG_PA_CONFIG, 1, 1)  # 设置输出功率衰减为 2 dBm (15dBm)
    write_reg_bit(REG_PA_CONFIG, 0, 1)  # 设置输出功率衰减为 2 dBm (15dBm)

    # 设置 REG_Pa_Ramp 寄存器，调整功率放大器整形与斜升/斜降时间
    write_reg_bit(REG_PA_RAMP, 6, 1)  # FSK 高斯滤波器BT = 0.5
    write_reg_bit(REG_PA_RAMP, 5, 0)  # FSK 高斯滤波器BT = 0.5
    write_reg_bit(REG_PA_RAMP, 3, 1)  # 斜升/斜降时间 40us
    write_reg_bit(REG_PA_RAMP, 2, 0)  # 斜升/斜降时间 40us
    write_reg_bit(REG_PA_RAMP, 1, 0)  # 斜升/斜降时间 40us
    write_reg_bit(REG_PA_RAMP, 0, 1)  # 斜升/斜降时间 40us

    # 设置 REG_OCP 寄存器，调整过流保护
    write_reg_bit(REG_OCP, 5, 1)  # 开启过流保护
    write_reg_bit(REG_OCP, 4, 0)  # 设置最大电流限制为 120mA
    write_reg_bit(REG_OCP, 3, 1)  # 设置最大电流限制为 120mA
    write_reg_bit(REG_OCP, 2, 1)  # 设置最大电流限制为 120mA
    write_reg_bit(REG_OCP, 1, 1)  # 设置最大电流限制为 120mA
    write_reg_bit(REG_OCP, 0, 1)  # 设置最大电流限制为 120mA

    # 接收机暂不处理

    # 设置 REG_OSC 寄存器，校准 RC 振荡器
    write_reg_bit(REG_OSC, 3, 1)  # 触发 RC 振荡器校准

    # 设置 REG_PREAMBLE_MSB 寄存器，设置前导码长度
    write_reg_bit(REG_PREAMBLE_MSB, 7, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_MSB, 6, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_MSB, 5, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_MSB, 4, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_MSB, 3, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_MSB, 2, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_MSB, 1, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_MSB, 0, 0)  # 设置前导码长度为 8 字节

    # 设置 REG_PREAMBLE_LSB 寄存器，设置前导码长度
    write_reg_bit(REG_PREAMBLE_LSB, 7, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_LSB, 6, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_LSB, 5, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_LSB, 4, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_LSB, 3, 1)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_LSB, 2, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_LSB, 1, 0)  # 设置前导码长度为 8 字节
    write_reg_bit(REG_PREAMBLE_LSB, 0, 0)  # 设置前导码长度为 8 字节

    # 设置 REG_SYNC_CONFIG 寄存器，设置同步字
    write_reg_bit(REG_SYNC_CONFIG, 7, 0)  # 收到完整数据包后 RestartRxWithoutPllLock
    write_reg_bit(REG_SYNC_CONFIG, 6, 1)  # 收到完整数据包后 RestartRxWithoutPllLock
    write_reg_bit(REG_SYNC_CONFIG, 5, 1)  # 设置前导码极性为 0x55
    write_reg_bit(REG_SYNC_CONFIG, 4, 1)  # 设置同步字状态为 启用
    write_reg_bit(REG_SYNC_CONFIG, 2, 1)  # 设置同步字长度为 8 字节
    write_reg_bit(REG_SYNC_CONFIG, 1, 1)  # 设置同步字长度为 8 字节
    write_reg_bit(REG_SYNC_CONFIG, 0, 1)  # 设置同步字长度为 8 字节

    # 设置 REG_SYNC_VALUE 寄存器，设置同步字
    # CCSDS 建议的同步字(ASM)为 0x1ACFFC1D, 按规定扰码后为 0x56C4D06BDAA431FE
    write_reg(REG_SYNC_VALUE1, 0x56)
    write_reg(REG_SYNC_VALUE2, 0xC4)
    write_reg(REG_SYNC_VALUE3, 0xD0)
    write_reg(REG_SYNC_VALUE4, 0x6B)
    write_reg(REG_SYNC_VALUE5, 0xDA)
    write_reg(REG_SYNC_VALUE6, 0xA4)
    write_reg(REG_SYNC_VALUE7, 0x31)
    write_reg(REG_SYNC_VALUE8, 0xFE)

    # 设置 REG_PACKET_CONFIG1 寄存器，设置数据包参数
    write_reg_bit(REG_PACKET_CONFIG1, 7, 0)  # 设置数据包格式为 固定长度
    write_reg_bit(REG_PACKET_CONFIG1, 6, 0)  # 设置 DC 消除编解码方式为 无
    write_reg_bit(REG_PACKET_CONFIG1, 5, 0)  # 设置 DC 消除编解码方式为 无
    write_reg_bit(REG_PACKET_CONFIG1, 4, 0)  # 设置 CRC 校验使能为 关闭
    write_reg_bit(REG_PACKET_CONFIG1, 2, 0)  # 设置地址过滤为 无过滤
    write_reg_bit(REG_PACKET_CONFIG1, 1, 0)  # 设置地址过滤为 无过滤

    # 设置 REG_PACKET_CONFIG2 寄存器，设置数据包参数
    write_reg_bit(REG_PACKET_CONFIG2, 6, 1)  # 设置数据处理模式为 数据包模式
    write_reg_bit(REG_PACKET_CONFIG2, 2, 0)  # 设置数据包长度为 255 字节
    write_reg_bit(REG_PACKET_CONFIG2, 1, 0)  # 设置数据包长度为 255 字节
    write_reg_bit(REG_PACKET_CONFIG2, 0, 0)  # 设置数据包长度为 255 字节

    # 设置 REG_PAYLOAD_LENGTH 寄存器，设置数据包长度
    write_reg(REG_PAYLOAD_LENGTH, 0xFF)      # 设置数据包长度为 255 字节

    # 设置 REG_FIFO_THRESH 寄存器，设置 FIFO 门限
    write_reg_bit(REG_FIFO_THRESH, 7, 0)  # 设置 FIFO 触发条件为 FifoLevel
    write_reg_bit(REG_FIFO_THRESH, 5, 1)  # 设置 FifoLevel 中断门限为 32 字节
    write_reg_bit(REG_FIFO_THRESH, 4, 0)  # 设置 FifoLevel 中断门限为 32 字节
    write_reg_bit(REG_FIFO_THRESH, 3, 0)  # 设置 FifoLevel 中断门限为 32 字节
    write_reg_bit(REG_FIFO_THRESH, 2, 0)  # 设置 FifoLevel 中断门限为 32 字节
    write_reg_bit(REG_FIFO_THRESH, 1, 0)  # 设置 FifoLevel 中断门限为 32 字节
    write_reg_bit(REG_FIFO_THRESH, 0, 0)  # 设置 FifoLevel 中断门限为 32 字节
    
    # 设置 REG_OP_MODE 寄存器，进入 Standby 模式  
    print("尝试进入待机模式")
    write_reg_bit(REG_OP_MODE, 2, 0)  # 设置为待机模式
    write_reg_bit(REG_OP_MODE, 1, 0)  # 设置为待机模式
    write_reg_bit(REG_OP_MODE, 0, 1)  # 设置为待机模式
    # 读取 IRQ_FLAGS1 寄存器中的第 7 位验证是否准备完成
    n = 0
    while (read_reg_bit(REG_IRQ_FLAGS1, 7)) == 0 and n <= 20:
        time.sleep_ms(100)
        n = n + 1
    if n >= 10:
        print("未进入待机模式：", hex(read_reg(REG_IRQ_FLAGS1)))
    else:
        print("待机模式：晶体振荡器正在运行\n")

# 发送一段数据
def sx1278_send(data):

    # 设置 REG_OP_MODE 寄存器，进入 FSTx 模式
    print("尝试进入 FSTX 模式")
    write_reg_bit(REG_OP_MODE, 2, 0)  # 设置为 FSTx 模式
    write_reg_bit(REG_OP_MODE, 1, 1)  # 设置为 FSTx 模式
    write_reg_bit(REG_OP_MODE, 0, 0)  # 设置为 FSTx 模式
    # 读取 IRQ_FLAGS1 寄存器中的第 7 位验证是否准备完成
    n = 0
    while (read_reg_bit(REG_IRQ_FLAGS1, 7)) == 0 and n <= 20:
        time.sleep_ms(100)
        n = n + 1
    if n >= 10:
        print("未进入 FSTx 模式：", hex(read_reg(REG_IRQ_FLAGS1)))
    else:
        print("FSTX 模式：PLL 成功被锁定\n")

    # 设置 REG_OP_MODE 寄存器，进入 TX 模式
    print("尝试进入 TX 模式")
    write_reg_bit(REG_OP_MODE, 2, 0)  # 设置为 TX 模式
    write_reg_bit(REG_OP_MODE, 1, 1)  # 设置为 TX 模式
    write_reg_bit(REG_OP_MODE, 0, 1)  # 设置为 TX 模式
    # 读取 IRQ_FLAGS1 寄存器中的第 7 位验证是否准备完成
    n = 0
    while (read_reg_bit(REG_IRQ_FLAGS1, 7)) == 0 and n <= 20:
        time.sleep_ms(100)
        n = n + 1
    if n >= 10:
        print("未进入 TX 模式：", hex(read_reg(REG_IRQ_FLAGS1)))
    else:
        print("TX 模式：PA 斜升完成\n")

    # 写入所有数据字节到 FIFO
    for b in data:
        write_reg(REG_FIFO, b)

    # 设置有效数据长度
    write_reg(REG_PAYLOAD_LENGTH, len(data))
    # 读取 IRQ_FLAGS2 寄存器中的第 3 位验证是否发送完成
    n = 0
    while (read_reg_bit(REG_IRQ_FLAGS2, 3)) == 0 and n <= 20:
        time.sleep_ms(100)
        n = n + 1
    if n >= 10:
        print("完成指示超时：", hex(read_reg(REG_IRQ_FLAGS2)))
    else:
        print("数据已发送完成\n")

    # 发送完成后，回到 Standby 模式
    
    print("尝试进入待机模式")
    write_reg_bit(REG_OP_MODE, 2, 0)  # 设置为待机模式
    write_reg_bit(REG_OP_MODE, 1, 0)  # 设置为待机模式
    write_reg_bit(REG_OP_MODE, 0, 1)  # 设置为待机模式
    # 读取 IRQ_FLAGS1 寄存器中的第 7 位验证是否准备完成
    n = 0
    while (read_reg_bit(REG_IRQ_FLAGS1, 7)) == 0 and n <= 20:
        time.sleep_ms(100)
        n = n + 1
    if n >= 10:
        print("未进入待机模式：", hex(read_reg(REG_IRQ_FLAGS1)))
    else:
        print("待机模式：晶体振荡器正在运行\n")

""" 主程序 """

# 上电后等待稳定
time.sleep(2)

# 完全硬复位
print("芯片硬复位")
sx1278_reset()

# 等待复位完成
time.sleep(2)

# 初始化SPI通信
print("尝试建立 SPI 通信")
spi = SPI(1, baudrate=SPI_BAUD, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)

# 验证通信是否成功
ver = read_reg(REG_VERSION)
if ver != 0x00 and ver != 0xFF:
    print("SPI 通信建立成功\n")
else:
    raise RuntimeError("错误：SPI通信建立失败")

# 输出基本信息
print(f"芯片版本号: 0x{ver:X}")
print(f"芯片完整修订版本号: {ver >> 4}")
print(f"金属掩膜修订版本号: {ver & 0x0F}\n")

print("工作初始化\n")
sx1278_init(air_frequency=435400000, air_bitrate=4800, module_depth=1.0)

print("开始测试发送随机数据包\n")
while True:
    
    # 生成一个包含255个随机字节的列表
    random_bytes = [random.randint(0, 255) for _ in range(255)]
    # 将列表转换为bytes类型
    msg = bytes(random_bytes)
    # 打印发送的随机数据，方便调试
    print("\n发送的数据:", msg.hex(), "\n")
    
    sx1278_send(msg)

    time.sleep(0)
