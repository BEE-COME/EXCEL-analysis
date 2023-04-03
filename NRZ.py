# -*- coding: GB2312 -*-
import pandas as pd
# 导包
import configparser


def crc8(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for i in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07
            else:
                crc <<= 1
    return crc&0xff



def crc16(data):
    crc = 0
    for byte in data:
        crc ^= (byte << 8)
        for i in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
    crc &= 0xFFFF
    return crc

# 标准曼彻斯特编码解码函数
def manchester_decode(signal):
    # 将输入信号划分为等长的比特位
    bits = [signal[i:i+2] for i in range(0, len(signal), 2)]
    # 解码每个比特位的数字信号
    decoded_bits = []
    
    for bit in bits:
        if bit[0] == 0 and bit[1] == 1:
            decoded_bits.append(0)
        elif bit[0] == 1 and bit[1] == 0:
            decoded_bits.append(1)
        else:
            continue
            # raise ValueError()
    return decoded_bits



config = configparser.ConfigParser() # 类实例化


NRZ= 1#NRZ编码
MCS= 0#曼切斯特编码
path = r'config.ini'
if(config.read(path)):
    BM = int(config['select']['bm'])#编码格式
    BPS = int(config['select']['bps'])#波特率
    
else:
    config.add_section("select")
    config.set("select","bm","1")
    config.set("select","bps","19200")
    config.write(open(path,"w"))
    BM=1
    BPS=19200



# 读取Excel数据
data = pd.read_excel('1.xlsx', header=None)

# # 将每行数据存储为一个数组
signal = []
signal.append(data.iloc[:,0])#获取N行：M列
# 语法格式：df.iloc[row_start:row_end , column_start:column_end]
# 其中，row_start和row_end表示需要选择的行的开始和结束位置，column_start和column_end表示需要选择的列的开始和结束位置。

# print(signal)
# 对信号做第一次处理
signal_bak_g=[]
signal_bak=signal[0]

avg=0
for i in range(0,len(signal[0])):
    avg+=signal[0][i]
avg=avg/len(signal[0])
print("平均数",avg)
# avg=220000
for i in range(0,len(signal[0])):
    if(signal[0][i]>avg):##############根据实际纵坐标设置
        signal_bak_g.append(1)
    else:
        signal_bak_g.append(0)
##############
signal_bak=signal_bak_g[0]
bin_signal = []
bin_signal.append(signal_bak)
signal_count=0


bps = BPS  ###########设置波特率
bit_time = 1 / bps
total_time=10/1000#设置屏幕总时间(s)50ms,
total_count=1000#总点数10000个点
excel_bit_time=total_time/total_count
bps_count = bit_time / excel_bit_time
half_bps_count=bps_count//2
# ##看bps决定
count_add=[]
for n in range(1,50):
        count_add.append(int(n*bps_count-half_bps_count))

for i in range(0,len(signal_bak_g)):  

    if(signal_bak!=signal_bak_g[i]):#如果与上次不一样
        signal_bak=signal_bak_g[i]
        signal_count=0
    signal_count+=1

    for j in count_add:
        if(j==signal_count):
            bin_signal.append(signal_bak)
            break


data_mg=[1,0,1]
data_sg=[1,2,3,4,5,6,7,8]
data=[]
state=0
print('原始数据：',bin_signal)
print('原始数据长度：',len(bin_signal))

if(BM==MCS):#曼码#按位获取
    #寻找到七个连续的01，加上10,一共16个数
    state=0
    seach_count=0
    bin_signal_bak=bin_signal
    for i in range(0,len(bin_signal_bak)):
        if(state==0):
            if(bin_signal_bak[i]==0):
                state=1
            else:
                seach_count=0
        elif(state==1):
            if(bin_signal_bak[i]==1):
                state=0
                seach_count+=1
                if(seach_count>=15):#前15个数都是0
                    state=2                    
            else:
                state=1#转回1，重新计数
                seach_count=0
        elif(state==2):
            if(bin_signal_bak[i]==1):
                state=3
            else:
                state=1#不对就继续判转回1
        elif(state==3):
            if(bin_signal_bak[i]==0):#第16个数是1
                state=0
                bin_signal=bin_signal_bak[i-31:i-31+162]
                print(bin_signal)
                print(i)
                break
            else:
                state=0
        if(i==len(bin_signal_bak)-1):#超出就清空
            bin_signal.clear()
    


    if(len(bin_signal)%2!=0):
        bin_signal.pop()
    bin_signal=manchester_decode(bin_signal)
    
    print('曼码转换数据：',bin_signal)
    print('曼码转换数据长度：',len(bin_signal))
    for i in range(0,len(bin_signal)):       
        data_sg[i%8]=bin_signal[i]
        if(i%8==0):
            byte_value = (data_sg[0]<<7) + (data_sg[1]<<6) + (data_sg[2]<<5) + (data_sg[3]<<4) + (data_sg[4]<<3) + (data_sg[5]<<2) + (data_sg[6]<<1) + data_sg[7]   #前高后低
            if(i!=0):
                data.append(byte_value)

elif(BM==NRZ):#NRZ
    for i in range(0,len(bin_signal)):
        if(state==0):#判断起始位
            if(bin_signal[i]==data_mg[0]):#等于1
                if(i>0):                
                    if((bin_signal[i-1]==data_mg[2])):#等于1
                        state=1
                        continue
                    else:
                        state=0
                else:
                    state=1
                    continue
        if(state==1):
            if(bin_signal[i]==data_mg[1]):
                state=2
                continue
            else:
                state=0
                continue
        if((state>=2)and(state<10)):
            data_sg[state-2]=bin_signal[i]
            state+=1
            continue
        if(state>(9)):#判断停止位
            if(bin_signal[i]!=1):#停止位错误
                #planA，继续将错就错
                # state+=1

                #planB,回退i-9,重新来
                i-=9
                state=0
            else:          
                byte_value = (data_sg[7]<<7) + (data_sg[6]<<6) + (data_sg[5]<<5) + (data_sg[4]<<4) + (data_sg[3]<<3) + (data_sg[2]<<2) + (data_sg[1]<<1) + data_sg[0]  #前低后高
                # byte_value = (data_sg[0]<<7) + (data_sg[1]<<6) + (data_sg[2]<<5) + (data_sg[3]<<4) + (data_sg[4]<<3) + (data_sg[5]<<2) + (data_sg[6]<<1) + data_sg[7]   #前高后低
                data.append((byte_value))
                state=0
data_hex=[]
for i in range(0,len(data)):
    data_hex.append(hex(data[i]))
print('解析数据：',data_hex)

crc_flag=0#crc标志符
if(len(data)>9):#大才行
    if(BM==MCS):#曼码解码
        #解析数据
        data_msg=data[2:2+8]
        print("曼码解码数据：",data_msg)
        if((crc8(data_msg)==0) and (len(data_msg)>0)):
            crc_flag=1
            print("CRC校验通过！")
            print("可用数据",data_msg[:7])
            print("ID:  ",data_msg[:4])
            print("PRE: ",data_msg[4:5][0]*5.5,"Kpa")
            print("TEMP:",data_msg[5:6][0]-50,"℃")
            flag=data_msg[6:7][0]
            print("Flag:",flag)
            if(flag==0xd7):
                print("特殊学习码！")
            elif(flag==0x81):
                print("快漏！")
            elif(flag==0x82):
                print("LF触发响应报文！")
            else:
                print("信息类型:    ",flag%1)
                print("传感器模式:  ",(flag&0xe)>>1)
                print("接收信息:    ",(flag&0x20)>>5)
        else:
            print("校验失败！")

    else:#NRZ解码
        #解析数据
        data_msg=[]
        state=0
        for i in range(0,len(data)):
            if(state==0):
                if(data[i]==0x5a):
                    state=1
            elif(state==1):
                if(data[i]==0xaa):
                    state=2
                else:
                    state=0
            elif(state==2):
                data_msg=data[i:i+9]
                break
        if((crc16(data_msg)==0) and (len(data_msg)>0)):
            crc_flag=1
            print("CRC校验通过！")
            print("可用数据",data_msg[:7])
            print("ID:  ",data_msg[:4])
            print("PRE: ",data_msg[4:5][0]*5.5,"Kpa")
            print("TEMP:",data_msg[5:6][0]-50,"℃")
            flag=data_msg[6:7][0]
            print("Flag:",flag)
            if(flag==0xd7):
                print("特殊学习码！")
            elif(flag==0x81):
                print("快漏！")
            elif(flag==0x82):
                print("LF触发响应报文！")
            else:
                print("信息类型:    ",flag%1)
                print("传感器模式:  ",(flag&0xe)>>1)
                print("接收信息:    ",(flag&0x20)>>5)
        else:
            print("校验失败！")

# print(data_hex)
# 将逻辑信号保存到文件
with open('result.txt', 'w') as f:
    f.write("报文解析：")
    for sublist in data_hex:
        for item in sublist:
            f.write(str(item))
        f.write(",")
    f.write("\n")
    if(crc_flag==1):
        str1="可用数据"+str(data_msg[:7])
        f.write(str1+"\n")
        str1="ID:  "+str(data_msg[:4])
        f.write(str1+"\n")
        str1="PRE: "+str(data_msg[4:5][0]*5.5)+"Kpa"
        f.write(str1+"\n")
        str1="TEMP:"+str(data_msg[5:6][0]-50)+"℃"
        f.write(str1+"\n")
        str1="Flag:"+str(flag)
        f.write(str1+"\n")
        if(flag==0xd7):
            str1="特殊学习码！"
            f.write(str1+"\n")
        elif(flag==0x81):
            str1="快漏！"
            f.write(str1+"\n")
        elif(flag==0x82):
            str1="LF触发响应报文！"
            f.write(str1+"\n")
        else:
            str1="信息类型:    "+str(flag%1)
            f.write(str1+"\n")
            str1="传感器模式:  "+str((flag&0xe)>>1)
            f.write(str1+"\n")
            str1="接收信息:    "+str((flag&0x20)>>5)
            f.write(str1+"\n")

