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
若启用曼彻斯特编码法, 则为码片速率。
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
                    若 OcpTrim <= 15 (120mA) , 则Imax = 45 + 5 * OcpTrim(mA)
                    若 15 < OcpTrim <= 27 (130~240mA) , 则Imax = -30 + 10 * OcpTrim(mA)
                    更高时, Imax = 240mA
                    缺省时, Imax = 100mA
```

**********

## 接收机寄存器 (0x0C~0x23)

### REG_LNA 寄存器位定义 (0x0C)
```
Bit 7~5 (LnaGain)    : LNA 增益设置 000=未使用, 001=G1=最大增益, 010=G2, 011=G3, 100=G4, 101=G5, 110=G6=最小增益, 111=未使用
Bit 4~3 (LnaBoostLf) : 低频 LNA电流 00 = 缺省LNA电流, Other = 预留 
Bit 2   (reserved)   : 0 = 预留
Bit 1~0 (LnaBoostHf) : 高频 LNA电流 00 = 缺省LNA电流, 11 = 150% LNA电流
```
当位PacketFormat的值设置为0且PayloadLength值大于0时, 即为固定长度数据包格式。

**********

## RC 振荡器寄存器 (0x24)

**********

## 数据包处理寄存器 (0x25~0x35)

### Reg_Preamble 寄存器位定义 (MSB:0x25, LSB:0x26)
```
Bit 7~0 (PreambleSize(15:8)) : 待发送的前导码长度 (最高有效位字节) 
Bit 7~0 (PreambleSize(7:0))  : 待发送的前导码长度 (最低有效位字节)
```

**********

### Reg_Sync_Config 寄存器位定义 (0x27)
```
Bit 7~6 (AutoRestartRxMode)   : 接收到有效数据包后控制接收机自动重启 (以 PayloadReady 或 CrcOk 为准)： 
                                00 = 关闭 
                                01 = 开启, 不等待PLL重新锁定 
                                10 = 开启, 等待PLL锁定（频率发生变化） 
                                11 = 预留
Bit 5   (PreamblePolarity)    : 前导码极性 0 = 0xAA, 1 = 0x55
Bit 4   (SyncOn)              : 同步字使能 0 = 关闭, 1 = 开启 (开启同步字生成和检测)
Bit 3   (Reserved)            : 0 = 预留
Bit 2~0 (SyncSize)            : 同步字长度 SyncSize + 1 字节 (若ioHomeOn=1, 则为SyncSize字节)
```

**********

### Reg_Sync_Value 寄存器位定义 (1:0x28, 2:0x29, 3:0x2A, 4:0x2B, 5:0x2C, 6:0x2D, 7:0x2E, 8:0x2F)
```
Bit 7~0 SyncValue(63:56)    : 同步字第一字节 (最高有效位字节), 在设置了 SyncOn 的情况下使用
Bit 7~0 SyncValue(55:48)    : 同步字第二字节, 在设置了 SyncOn 且 (SyncSize+1) >=2 情况下使用
Bit 7~0 SyncValue(47:40)    : 同步字第三字节, 在设置了 SyncOn 且 (SyncSize+1) >=3 情况下使用
Bit 7~0 SyncValue(39:32)    : 同步字第四字节, 在设置了 SyncOn 且 (SyncSize+1) >=4 情况下使用
Bit 7~0 SyncValue(31:24)    : 同步字第五字节, 在设置了 SyncOn 且 (SyncSize+1) >=5 情况下使用
Bit 7~0 SyncValue(23:16)    : 同步字第六字节, 在设置了 SyncOn 且 (SyncSize+1) >=6 情况下使用
Bit 7~0 SyncValue(15:8)     : 同步字第七字节, 在设置了 SyncOn 且 (SyncSize+1) >=7 情况下使用
Bit 7~0 SyncValue(7:0)      : 同步字第八字节, 在设置了 SyncOn 且 (SyncSize+1) >=8 情况下使用
```

**********

### Reg_Packet_Config1  寄存器位定义 (0x30)
```
Bit 7   (PacketFormat)     : 数据包格式 0 = 固定长度, 1 = 可变长度
Bit 6~5 (DcFree)           ：DC消除编解码方式 00 = 无（关闭）, 01 = 曼彻斯特, 10 = 白化, 11 = 预留
Bit 4   (CrcOn)            : CRC校验使能 0 = 关闭, 1 = 开启
Bit 3   (CrcAutoClearOff)  : CRC校验失败时 0 = 清空FIFO并不产生中断, 1 = 不清空FIFO并产生中断
Bit 2~1 (AddressFiltering) : 地址过滤 00 = 无过滤, 01 = 只接收发给自己的数据, 10 = 接收发给自己的数据及广播数据, 11 = 预留
Bit 0   (CrcWhiteningType) : CRC与加扰方法 0 = CCITT CRC + 标准白化, 1 = IBM CRC + 交替白化
```

**********

### RegPacketConfig2 寄存器位定义 (0x31)
```
Bit 7   (unused)              : 0 未使用
Bit 6   (DateMode)            : 数据处理模式 0 = 连续模式, 1 = 数据包模式
Bit 5   (IoHomeOn)            : iohomectrl兼容使能 0 = 无效, 1 = 使能
Bit 4   (IOHomeOnPowerframe)  : 预留——链接到 io-homecontrol 兼容模式
Bit 3   (BeaconOn)            : 以固定数据包格式启动信标模式
Bit 2~0 (PayloadLength(10:8)) : 数据包长度最高有效位
```

**********

### Reg_Payload_Length 寄存器位定义 (0x32)
```
Bit 7~0 (PayloadLength(7:0))  : 若PacketFormat=0 (固定长度), 则为负载长度
                                若PacketFormat=1 (可变长度), 则为Rx模式下最大长度, 不用于Tx模式。 
```

**********

### Reg_Node_Adrs  寄存器位定义 (0x33)
```
Bit 7~0 (NodeAddress) : 地址过滤中使用的节点地址
```

**********

### Reg_Broadcast_Adrs 寄存器位定义 (0x34)
```
Bit 7~0 (BroadcastAddress) : 地址过滤中使用的广播地址
```

**********

### Reg_Fifo_Thresh 寄存器位定义 (0x35)
```
Bit 7  (TxStartCondition) : 定义开始数据包传输的条件
                            0 = FifoLevel触发 (即FIFO中的字节数超出了 FifoThreshold 的设定值)
                            1 = FifoEmpty变低 (即FIFO中至少有一个字节)
Bit 6  (unused)           : 未使用
Bit 5~0 (FifoThreshold)   : 当FIFO中字节数 >= FifoThreshold + 1 时, 触发 FifoLevel 中断 
```

**********

## 定序器寄存器 (0x36~0x3D)