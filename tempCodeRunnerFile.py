byte_value = (data_sg[7]<<7) + (data_sg[6]<<6) + (data_sg[5]<<5) + (data_sg[4]<<4) + (data_sg[3]<<3) + (data_sg[2]<<2) + (data_sg[1]<<1) + data_sg[0]  #前低后高
            # byte_value = (data_sg[0]<<7) + (data_sg[1]<<6) + (data_sg[2]<<5) + (data_sg[3]<<4) + (data_sg[4]<<3) + (data_sg[5]<<2) + (data_sg[6]<<1) + data_sg[7]   #前高后低
            data.append((byte_value))
            state=0