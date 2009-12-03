#!/usr/bin/env python

#from ESP300StageController import ESP300StageController

from IPSerialBridge import IPSerialBridge

class CNCLinearAxes(IPSerialBridge):
    """
    x: 1: left(-)/right(+) : home=positive
    y: 2: forward(-)/back(+) : home=negative
    z: 3: down(-)/up(+) : home=positive
    
    It is a BAD idea to home these axes automatically. Therefore the homing velocity
    is set to 0.0 on all axes.
    
    y give negative home velocity
    
    minimum 'step' is 0.0127 mm
    """
    
    espConfigCommand="""QM3
        QI2.0
        QV30.0
        SN2
        SU0.0127
        FR0.0127
        QS1000
        VU12.7
        VA6.35
        JH6.35
        JW3.175
        OH0.0
        AU6.35
        AC6.35
        AG6.35
        FE25.3999
        TJ1
        OM3
        SL%g
        SR%g
        ZA323H
        ZB0H
        ZE3H
        ZF2H
        ZH24H
        ZS24H
        QD"""
    
    def __init__(self, address, port, xAxis = 1, yAxis = 2, zAxis = 3,
                xyzLimits=((-355.6, 0.0), (-355.6, 0.0), (-101.6, 0.0))):
        IPSerialBridge.__init__(self, address, port)
        self.connect()
        
        self.xAxis = xAxis
        self.yAxis = yAxis
        self.zAxis = zAxis
        
        self.configure_axis(self.xAxis, *xyzLimits[0])
        self.configure_axis(self.yAxis, *xyzLimits[1])
        self.configure_axis(self.zAxis, *xyzLimits[2])
        self.power_down()
        self.save_settings_to_controller()
    
    def configure_axis(self, axis, leftLimit, rightLimit):
        filledCommand = self.espConfigCommand % (leftLimit, rightLimit)
        for command in filledCommand.splitlines():
            #print "sending:", "%d%s" % (axis, command)
            self.send("%d%s" % (axis, command), 1)
    
    def power_down(self, axis=None):
        if axis == None:
            self.send("1MF", 1)
            self.send("2MF", 1)
            self.send("3MF", 1)
        else:
            self.send("%dMF" % axis, 1)
    
    def power_up(self, axis=None):
        if axis == None:
            self.send("1MO", 1)
            self.send("2MO", 1)
            self.send("3MO", 1)
        else:
            self.send("%dMO" % axis, 1)
    
    def save_settings_to_controller(self):
        self.send("SM",1) # store controller settings to non-volatile memory
    
    def composite_move_relative(self, x, y, z):
        return (move_relative(self.xAxis, x),
                move_relative(self.yAxis, y),
                move_relative(self.zAxis, z))
    
    def move_relative(self, axis, pos):
        self.send("%dPR%.4f" % (axis, float(pos)), 1) # set target as relative position
        self.send("%dWS" % axis, 1) # tell controller to wait till movement ends
        return self.get_position(axis) # report position of axis
    
    def get_position(self, axis=None):
        if axis==None:
            return (self.get_position(self.xAxis),
                    self.get_position(self.yAxis),
                    self.get_position(self.zAxis))
        else:
            return self.send("%dTP" % axis)
    
    def home(self, axis):
        homeVelocity = 5.0
        if axis == self.yAxis:
            homeVelocity *= -1
        # home axis
        self.send("%dOH%g" % (axis, homeVelocity), 1)
        #self.send("%dOR3" % axis, 1)
        #self.send("%dWS" % axis, 1)
        # reset home velocity to 0
        self.send("%dOH0" % axis, 1)

class CNCHeadAxes(IPSerialBridge):
    """
    b: rotation clockwise(-)/counterclockwise(+)
    w: fine Z up(-)/down(+)
    
    minimum 'step' is ?
    """
    def __init__(self, address, port, bAxis = 1, wAxis = 2):
        IPSerialBridge.__init__(self, address, port)
        self.connect()
        
        self.bAxis = bAxis
        self.wAxis = wAxis
        
        #self.configure_axis(self.xAxis, *xyzLimits[0])
        self.power_down()
        #self.save_settings_to_controller()
    
    def configure_axis(self, axis, leftLimit, rightLimit):
        #filledCommand = self.espConfigCommand % (leftLimit, rightLimit)
        #for command in filledCommand.splitlines():
        #    #print "sending:", "%d%s" % (axis, command)
        #    self.send("%d%s" % (axis, command), 1)
        pass
    
    def power_down(self, axis=None):
        if axis == None:
            self.send("1MF", 1)
            self.send("2MF", 1)
            #self.send("3MF", 1)
        else:
            self.send("%dMF" % axis, 1)
    
    def power_up(self, axis=None):
        if axis == None:
            self.send("1MO", 1)
            self.send("2MO", 1)
            #self.send("3MO", 1)
        else:
            self.send("%dMO" % axis, 1)
    
    def save_settings_to_controller(self):
        self.send("SM",1) # store controller settings to non-volatile memory
    
    def composite_move_relative(self, b, w):
        return (move_relative(self.bAxis, x),
                move_relative(self.wAxis, y))
    
    def move_relative(self, axis, pos):
        self.send("%dPR%.4f" % (axis, float(pos)), 1) # set target as relative position
        self.send("%dWS" % axis, 1) # tell controller to wait till movement ends
        return self.get_position(axis) # report position of axis
    
    def get_position(self, axis=None):
        if axis==None:
            return (self.get_position(self.bAxis),
                    self.get_position(self.wAxis))
        else:
            return self.send("%dTP" % axis)
    
    def home(self, axis):
        #homeVelocity = 5.0
        #if axis == self.yAxis:
        #    homeVelocity *= -1
        # home axis
        #self.send("%dOH%g" % (axis, homeVelocity), 1)
        if axis == self.wAxis:
            raise Exception("This should be a notification reminding you to remove the preamp prior to homing the w-axis")
        else:
            self.send("%dOR3" % axis, 1)
            self.send("%dWS" % axis, 1)

# class CNCLinearAxis:
#     espConfigCommand="""QM3
#         QI1.0
#         QV15.0
#         SN2
#         SU0.0127
#         FR0.0127
#         QS1000
#         VU50.8
#         VA25.4
#         JH25.4
#         JW12.7
#         OH25.4
#         AU101.6
#         AC101.6
#         AG50.8
#         FE25.3999
#         TJ1
#         OM3
#         SL%g
#         SR%g
#         ZA323H
#         ZB0H
#         ZE3H
#         ZF2H
#         ZH24H
#         ZS24H
#         QD"""
#     
#     def __init__(self, serialPort, axisIndex, leftLimit, rightLimit):
#         self.axisIndex = axisIndex
#         self.leftLimit = leftLimit
#         self.rightLimit = rightLimit
#         self.serialPort = serialPort
#         self.configureAxis()
#     
#     def send_to_axis(self, message, noresponse = 0):
#         print "%d%s" % (self.axis, message)
#         self.serialPort.send("%d%s" % (self.axis, message), noresponse)
#     
#     def configureAxis(self):
#         filledCommand = self.espConfigCommand % (self.leftLimit, self.rightLimit)
#         for command in filledCommand.splitlines():
#             print "sending:", command
#             self.send_to_axis(command, 1)
#         self.power_down()
#     
#     def move_relative(self, pos):
#         self.send_to_axis("PR%.4f" % float(pos), 1) # set target as relative position
#         self.send_to_axis("WS", 1) # tell controller to wait till movement ends
#         self.send_to_axis("TP") # report position of axis
#     
#     def power_down(self):
#         self.send_to_axis("MF", 1) # power off motor
#     
#     def power_up(self):
#         self.send_to_axis("MO", 1) # power on motor
#     
#     def save_settings_to_controller(self):
#         self.serialPort.send("SM",1) # store current controller settings to non-volatile memory

# class CNCLinearAxisController(IPSerialBridge):
#     """
#     Left-handed coordinate system
#     minimum 'step' is 0.0127 mm
#     """
#     espInitCommand="""QM3
#         QI1.0
#         QV15.0
#         SN2
#         SU0.0127
#         FR0.0127
#         QS1000
#         VU50.8
#         VA25.4
#         JH25.4
#         JW12.7
#         OH25.4
#         AU101.6
#         AC101.6
#         AG50.8
#         FE25.3999
#         TJ1
#         OM3
#         SL%g
#         SR%g
#         ZA323H
#         ZB0H
#         ZE3H
#         ZF2H
#         ZH24H
#         ZS24H
#         QD"""
#     
#     def __init__(self, address, port, axis, leftLimit=-355.6, rightLimit=0.0):
#         self.axis = axis
#         self.leftLimit = leftLimit
#         self.rightLimit = rightLimit
#         IPSerialBridge.__init__(self, address, port)
#   self.setup()
#         #self.connect()
#         #self.setup(leftLimit, rightLimit)
#         #self.power_down()
#     
#     def send_to_axis(self, message, noresponse = 0):
#         print "%d%s" % (self.axis, message)
#         self.send("%d%s" % (self.axis, message), noresponse)
#     
#     def setup(self):
#         self.connect()
#         filledCommand = self.espInitCommand % (self.leftLimit, self.rightLimit)
#         for command in filledCommand.splitlines():
#             print "sending:", command
#             self.send_to_axis(command, 1)
#         self.power_down()
#     
#     def move_relative(self, pos):
#         self.send_to_axis("PR%.4f" % float(pos), 1) # set target as relative position
#         self.send_to_axis("WS", 1) # tell controller to wait till movement ends
#         self.send_to_axis("TP") # report position of axis
#     
#     def power_down(self):
#         self.send_to_axis("MF", 1) # power off motor
#     
#     def power_up(self):
#         self.send_to_axis("MO", 1) # power on motor
#     
#     def save_settings_to_controller(self):
#         self.send("SM",1) # store current controller settings to non-volatile memory
#     
#     # homing might not be a good idea
#     #def home(self, axis):
#     #    self.send("%dOR" % axis, 1)
#     
#     # absolute positioning may be impossible without homing
#     #def move_absolute(self, axis, pos):
#     #    self.send("%dPA%.4f" % (axis, float(pos)), 1)
#     #    self.send("%dWS" % axis, 1)
#     #    self.send("%dTP" % axis)
# 
# # class CNCController:
# #     """
# #     X: left/right
# #     Y: forward/backward
# #     Z: up/down
# #     B: rotation around Y axis
# #     W: fine Z yoked to B
# #     """
# #     def __init__(self):
# #         self.xAxis = CNCLinearAxisController("169.254.0.9", 8003, 1, -355.6, 0.0)
# #         self.yAxis = CNCLinearAxisController("169.254.0.9", 8003, 2, -355.6, 0.0)
# #         self.zAxis = CNCLinearAxisController("169.254.0.9", 8003, 3, -101.6, 0.0)
# #         # self.bAxis
# #         # self.wAxis

if __name__ == '__main__':
    axes = CNCLinearAxes("169.254.0.9", 8003)
    #axes.disconnect()
    #del axes
    # xAxis = CNCLinearAxisController("169.254.0.9", 8003, 1, -355.6, 0.0)
    # yAxis = CNCLinearAxisController("169.254.0.9", 8003, 2, -355.6, 0.0)
    # zAxis = CNCLinearAxisController("169.254.0.9", 8003, 3, -101.6, 0.0)