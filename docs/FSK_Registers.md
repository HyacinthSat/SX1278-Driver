# FSK/OOK 模式下的寄存器定义

### REG_FIFO 寄存器位定义 (0x00)
```
Bit 7~0 (FIFO) : FIFO 数据输入/输出
```
FSK/OOK 模式下为线性移位寄存器, 共计 64 位
无需设置基地址, 直接顺序写入数据即可

**********

## 常规设置寄存器 (0x01~0x08)

### REG_OP_MODE 寄存器位定义 (0x01)
```
Bit 7   (LongRangeMode)  : 调制模式 0 = FSK/OOK 模式
Bit 6~5 (ModulationType) : 调制模式 00 = FSK, 01 = OOK, 10/11 = 保留
Bit 4   (reserved)       : 保留
Bit 3   (LowFreqModeOn)  : 频段选择 0 = 高频段 (HF) , 1 = 低频段 (LF) 
Bit 2~0 (Mode)           : 模式选择
                           000 = 睡眠模式
                           001 = 待机模式
                           010 = FSTx (频率合成器发送准备) 
                           011 = TX (发射模式) 
                           100 = FSRx (频率合成器接收准备) 
                           101 = Rx (接收模式) 
                           110 = 保留
                           111 = 保留
```

**********

### Reg_Bitrate 寄存器位定义 (MSB:0x02, LSB:0x03)
```
Bit 7~0 (BitRate(15:8)) : 比特率最高有效位
Bit 7~0 (BitRate(7:0))  : 比特率最低有效位
```
若启用曼彻斯特编码法，则为码片速率。
bitrate_reg_value = round(F_XOSC / bps)

**********

### REG_Fdev 寄存器位定义 (MSB:0x04, LSB:0x05)
```
Bit 7~0 (Fdev(15:8)) : 频率偏移最高有效位
Bit 7~0 (Fdev(7:0))  : 频率偏移最低有效位
```
Fdev_reg_value = round(freqdev_hz / (F_XOSC / 2**19))

**********

### REG_Frf 寄存器位定义 (MSB:0x06, MID:0x07, LSB:0x08)
```
Bit 7~0 (Frf(23:16)) : 频率最高有效位
Bit 7~0 (Frf(15:8))  : 频率中间有效位
Bit 7~0 (Frf(7:0))   : 频率最低有效位
```
Frf_reg_value = round(freq_hz / (F_XOSC / 2**19))

**********

## 发射机寄存器 (0x09~0x0B)

### REG_PA_CONFIG 寄存器位定义 (0x09)
```
Bit 7   (PaSelrct) : 0 = RFO, 1 = PA_BOOST
Bit 6~4 (MaxPower) : 最大功率 Pmax = 10.8 + 0.6 * MaxPower(dBm)
Bit 3~0 (OutPower) : 输出功率 (对最大功率的衰减)
                     PaSelect=0: Pout=Pmax-(15-OutputPower)
                     PaSelect=1: Pout=17-(15-OutputPower) 
```

**********

### REG_PaRamp 寄存器位定义 (0x0A)
```
Bit 7   (unused)            : 0 未使用
Bit 6~5 (ModulationShaping) : FSK 模式 00 = 无整形, 01 = 高斯滤波器BT = 1.0, 10 = 高斯滤波器BT = 0.5, 11 = 高斯滤波器BT=0.3 
                              OOK 模式 00 = 无整形, 01 = 截止频率滤波 = baud, 10 = 截止频率滤波 = 2*baud(<125kb/s), 11 = 预留
Bit 4   (reserved)          : 0 = 预留
Bit 3~0 (PaRamp)            : FSK 模式下斜升/斜降时间
                              0000 = 3.4ms
                              0001 = 2ms
                              0010 = 1ms
                              0011 = 500us
                              0100 = 250us
                              0101 = 125us
                              0110 = 100us
                              0111 = 62us
                              1000 = 50us
                              1001 = 40us
                              1010 = 31us
                              1011 = 25us
                              1100 = 20us
                              1101 = 15us
                              1110 = 12us
                              1111 = 10us
```
如果 ModulationShaping 发生了变化, 必须重启发射机, 从而重新校准内置滤波器

**********

### REG_Ocp 寄存器位定义 (0x0B)
```
Bit 7~6 (unused)  : 00 未使用
Bit 5   (OcpOn)   : PA过流保护 0 = 关闭, 1 = 开启
Bit 4~0 (OcpTrim) : OCP电流微调:
                    若 OcpTrim <=15 (120mA) , 则Imax=45 + 5 * OcpTrim(mA); 
                    若 15<OcpTrim<=27 (130~240mA) , 则Imax=-30 + 10 * OcpTrim(mA); 
                    更高时, Imax=240mA;
                    缺省时, Imax=100mA
```
