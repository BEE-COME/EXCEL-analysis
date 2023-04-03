# -*- coding: GB2312 -*-
import pandas as pd
# ����
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

# ��׼����˹�ر�����뺯��
def manchester_decode(signal):
    # �������źŻ���Ϊ�ȳ��ı���λ
    bits = [signal[i:i+2] for i in range(0, len(signal), 2)]
    # ����ÿ������λ�������ź�
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



config = configparser.ConfigParser() # ��ʵ����


NRZ= 1#NRZ����
MCS= 0#����˹�ر���
path = r'config.ini'
if(config.read(path)):
    BM = int(config['select']['bm'])#�����ʽ
    BPS = int(config['select']['bps'])#������
    
else:
    config.add_section("select")
    config.set("select","bm","1")
    config.set("select","bps","19200")
    config.write(open(path,"w"))
    BM=1
    BPS=19200



# ��ȡExcel����
data = pd.read_excel('1.xlsx', header=None)

# # ��ÿ�����ݴ洢Ϊһ������
signal = []
signal.append(data.iloc[:,0])#��ȡN�У�M��
# �﷨��ʽ��df.iloc[row_start:row_end , column_start:column_end]
# ���У�row_start��row_end��ʾ��Ҫѡ����еĿ�ʼ�ͽ���λ�ã�column_start��column_end��ʾ��Ҫѡ����еĿ�ʼ�ͽ���λ�á�

# print(signal)
# ���ź�����һ�δ���
signal_bak_g=[]
signal_bak=signal[0]

avg=0
for i in range(0,len(signal[0])):
    avg+=signal[0][i]
avg=avg/len(signal[0])
print("ƽ����",avg)
# avg=220000
for i in range(0,len(signal[0])):
    if(signal[0][i]>avg):##############����ʵ������������
        signal_bak_g.append(1)
    else:
        signal_bak_g.append(0)
##############
signal_bak=signal_bak_g[0]
bin_signal = []
bin_signal.append(signal_bak)
signal_count=0


bps = BPS  ###########���ò�����
bit_time = 1 / bps
total_time=10/1000#������Ļ��ʱ��(s)50ms,
total_count=1000#�ܵ���10000����
excel_bit_time=total_time/total_count
bps_count = bit_time / excel_bit_time
half_bps_count=bps_count//2
# ##��bps����
count_add=[]
for n in range(1,50):
        count_add.append(int(n*bps_count-half_bps_count))

for i in range(0,len(signal_bak_g)):  

    if(signal_bak!=signal_bak_g[i]):#������ϴβ�һ��
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
print('ԭʼ���ݣ�',bin_signal)
print('ԭʼ���ݳ��ȣ�',len(bin_signal))

if(BM==MCS):#����#��λ��ȡ
    #Ѱ�ҵ��߸�������01������10,һ��16����
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
                if(seach_count>=15):#ǰ15��������0
                    state=2                    
            else:
                state=1#ת��1�����¼���
                seach_count=0
        elif(state==2):
            if(bin_signal_bak[i]==1):
                state=3
            else:
                state=1#���Ծͼ�����ת��1
        elif(state==3):
            if(bin_signal_bak[i]==0):#��16������1
                state=0
                bin_signal=bin_signal_bak[i-31:i-31+162]
                print(bin_signal)
                print(i)
                break
            else:
                state=0
        if(i==len(bin_signal_bak)-1):#���������
            bin_signal.clear()
    


    if(len(bin_signal)%2!=0):
        bin_signal.pop()
    bin_signal=manchester_decode(bin_signal)
    
    print('����ת�����ݣ�',bin_signal)
    print('����ת�����ݳ��ȣ�',len(bin_signal))
    for i in range(0,len(bin_signal)):       
        data_sg[i%8]=bin_signal[i]
        if(i%8==0):
            byte_value = (data_sg[0]<<7) + (data_sg[1]<<6) + (data_sg[2]<<5) + (data_sg[3]<<4) + (data_sg[4]<<3) + (data_sg[5]<<2) + (data_sg[6]<<1) + data_sg[7]   #ǰ�ߺ��
            if(i!=0):
                data.append(byte_value)

elif(BM==NRZ):#NRZ
    for i in range(0,len(bin_signal)):
        if(state==0):#�ж���ʼλ
            if(bin_signal[i]==data_mg[0]):#����1
                if(i>0):                
                    if((bin_signal[i-1]==data_mg[2])):#����1
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
        if(state>(9)):#�ж�ֹͣλ
            if(bin_signal[i]!=1):#ֹͣλ����
                #planA����������ʹ�
                # state+=1

                #planB,����i-9,������
                i-=9
                state=0
            else:          
                byte_value = (data_sg[7]<<7) + (data_sg[6]<<6) + (data_sg[5]<<5) + (data_sg[4]<<4) + (data_sg[3]<<3) + (data_sg[2]<<2) + (data_sg[1]<<1) + data_sg[0]  #ǰ�ͺ��
                # byte_value = (data_sg[0]<<7) + (data_sg[1]<<6) + (data_sg[2]<<5) + (data_sg[3]<<4) + (data_sg[4]<<3) + (data_sg[5]<<2) + (data_sg[6]<<1) + data_sg[7]   #ǰ�ߺ��
                data.append((byte_value))
                state=0
data_hex=[]
for i in range(0,len(data)):
    data_hex.append(hex(data[i]))
print('�������ݣ�',data_hex)

crc_flag=0#crc��־��
if(len(data)>9):#�����
    if(BM==MCS):#�������
        #��������
        data_msg=data[2:2+8]
        print("����������ݣ�",data_msg)
        if((crc8(data_msg)==0) and (len(data_msg)>0)):
            crc_flag=1
            print("CRCУ��ͨ����")
            print("��������",data_msg[:7])
            print("ID:  ",data_msg[:4])
            print("PRE: ",data_msg[4:5][0]*5.5,"Kpa")
            print("TEMP:",data_msg[5:6][0]-50,"��")
            flag=data_msg[6:7][0]
            print("Flag:",flag)
            if(flag==0xd7):
                print("����ѧϰ�룡")
            elif(flag==0x81):
                print("��©��")
            elif(flag==0x82):
                print("LF������Ӧ���ģ�")
            else:
                print("��Ϣ����:    ",flag%1)
                print("������ģʽ:  ",(flag&0xe)>>1)
                print("������Ϣ:    ",(flag&0x20)>>5)
        else:
            print("У��ʧ�ܣ�")

    else:#NRZ����
        #��������
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
            print("CRCУ��ͨ����")
            print("��������",data_msg[:7])
            print("ID:  ",data_msg[:4])
            print("PRE: ",data_msg[4:5][0]*5.5,"Kpa")
            print("TEMP:",data_msg[5:6][0]-50,"��")
            flag=data_msg[6:7][0]
            print("Flag:",flag)
            if(flag==0xd7):
                print("����ѧϰ�룡")
            elif(flag==0x81):
                print("��©��")
            elif(flag==0x82):
                print("LF������Ӧ���ģ�")
            else:
                print("��Ϣ����:    ",flag%1)
                print("������ģʽ:  ",(flag&0xe)>>1)
                print("������Ϣ:    ",(flag&0x20)>>5)
        else:
            print("У��ʧ�ܣ�")

# print(data_hex)
# ���߼��źű��浽�ļ�
with open('result.txt', 'w') as f:
    f.write("���Ľ�����")
    for sublist in data_hex:
        for item in sublist:
            f.write(str(item))
        f.write(",")
    f.write("\n")
    if(crc_flag==1):
        str1="��������"+str(data_msg[:7])
        f.write(str1+"\n")
        str1="ID:  "+str(data_msg[:4])
        f.write(str1+"\n")
        str1="PRE: "+str(data_msg[4:5][0]*5.5)+"Kpa"
        f.write(str1+"\n")
        str1="TEMP:"+str(data_msg[5:6][0]-50)+"��"
        f.write(str1+"\n")
        str1="Flag:"+str(flag)
        f.write(str1+"\n")
        if(flag==0xd7):
            str1="����ѧϰ�룡"
            f.write(str1+"\n")
        elif(flag==0x81):
            str1="��©��"
            f.write(str1+"\n")
        elif(flag==0x82):
            str1="LF������Ӧ���ģ�"
            f.write(str1+"\n")
        else:
            str1="��Ϣ����:    "+str(flag%1)
            f.write(str1+"\n")
            str1="������ģʽ:  "+str((flag&0xe)>>1)
            f.write(str1+"\n")
            str1="������Ϣ:    "+str((flag&0x20)>>5)
            f.write(str1+"\n")

