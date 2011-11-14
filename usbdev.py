#! /usr/bin/env python
import usb.core

#usb control constants
USB_TYPE_VENDOR = (2<<5)
USB_RECIP_DEVICE = 0
USB_ENDPOINT_IN = (1<<7)
USB_ENDPOINT_OUT= (0<<7)

KALMAN_SZ = 1
KALMAN_SW = 0.1

class UsbDev:


    def __init__(self):
        self._dev = None
        self._VID = 0x16c0
        self._PID = 0x5df
        self.adc = bytearray([0,0,0])
        self.filters = [
            Kalman(KALMAN_SZ, KALMAN_SW),
            Kalman(KALMAN_SZ, KALMAN_SW),
            Kalman(KALMAN_SZ, KALMAN_SW)]
        self.connect()

    def connect(self):
        self._dev = usb.core.find(idVendor=self._VID, idProduct=self._PID)
        if self._dev is None:
            print(
            "device not found  PID: 0x{0:X} | VID:0x{1:X}".format(
            self._PID, self._VID))
            return 1
        else:
            return 0

    def update_adc(self):
        if not self._dev: return(0)
        self.adc = self._dev.ctrl_transfer(
            USB_TYPE_VENDOR | USB_RECIP_DEVICE |USB_ENDPOINT_IN,
            2, 0, 0, 3, 1000)
        #print(self.adc)
        for i in range(3): self.filters[i].step(int(self.adc[i]))
    
    def get_adc_int(self):
        return([self.filters[0].x, self.filters[1].x, self.filters[2].x])


class Kalman:


    def __init__(self,Sz, Sw):
        self.Sz = Sz
        self.Sw = Sw
        self.x = 0 
        self.x_last = 0
        self.P = 0
        self.P_last = 0
        
        
    def step(self, value):
        x_temp = self.x_last
        P_temp = self.P_last = self.Sw
        
        K = (1.0 / (P_temp + self.Sz) * P_temp)
        self.x = x_temp + K * (value - x_temp)
        self.P = (1.0 - K) * P_temp
        
        self.x_last = self.x;
        self.P_last = self.P
        
        
        
