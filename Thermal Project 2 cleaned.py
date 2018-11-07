# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 12:11:13 2018

@author: kpett
"""
import matplotlib.pyplot as plt
import cantera as ct
  
def h_OutPump(n_pump, h_OutIs, h_In):
    h_OutAct = ((h_OutIs - h_In)/n_pump)+h_In
    return h_OutAct

def h_OutCompressor(n_compressor, h_OutIs, h_In):
    h_OutAct = ((h_OutIs - h_In)/n_compressor)+h_In
    return h_OutAct

def h_OutTurbine(n_turb, h_OutIs, h_In):
    h_OutAct = -(n_turb)*(h_In-h_OutIs)+h_In
    return h_OutAct

#Define Arrays
aPressureRatios = []    
aMDotRatios = []
aCycleEfficiency = []
aNetPower = []
aQin=[]
aQout =[]

#Define Fluid States
air5 = ct.Solution('air.cti')
air6 = ct.Solution('air.cti')
air7 = ct.Solution('air.cti')
air8 = ct.Solution('air.cti')
air9 = ct.Solution('air.cti')
water1 = ct.Water()
water2 = ct.Water()
water3 = ct.Water()
water4 = ct.Water()

#Define Efficiencies
n_compressor = 0.8
n_turbineAir = 0.85
n_HRSG = 0.86
n_pump = 0.9
n_turb_w = 0.9

for pr in range(3,20):
    
    "State 5 - AIR - Inlet to Compressor"
    P5 = 101325
    T5 = 300             
    air5.TP = T5, P5    
    s5 = air5.s
    h5 = air5.h
    
    "State 6 - AIR - Outlet of Compressor/Inlet to Combustion Chamber"
    P6 = 101325*pr
    s6_is = s5
    air6.SP = s6_is, P6
    h6_is= air6.h
    h6 = h_OutCompressor(n_compressor, h6_is, h5)
    air6.HP = h6,P6
    
    "State 7 - AIR - Outlet of Combustion Chamber/Inlet to Turbine"    
    P7 = P6
    T7 = 1400
    air7.TP = T7,P7
    s7 = air7.s
    h7 = air7.h
     
    "State 8 - AIR - Outlet of Turbine/Inlet to HRSG"
    P8 = P5
    s8_is = s7
    air8.SP = s8_is, P8
    h8_is = air8.h
    h8 = h_OutTurbine(n_turbineAir, h8_is, h7)
    air8.HP = h8,P8
    T8 = air8.T
    
    "State 9 - AIR - Outlet of HRSG"
    T9 = 450
    P9 = P8
    air9.TP = T9, P9
    h9 = air9.h
        
    "State 1 - WATER - Outlet of Condenser/Inlet to pump"
    P1 = 5*10**3
    water1.PX = P1, 0
    h1 = water1.h
    s1 = water1.s
    
    "State 2 - WATER - Outlet of Pump/Inlet to HRSG"
    P2 = 70*10**6
    s2_is = s1
    water2.SP = s2_is, P2
    h2_is = water2.h
    h2 = h_OutPump(n_pump, h2_is, h1)
    water2.HP = h2,P2
    T2 = water2.T
    
    "State 3 - WATER - Outlet of HRSG/Inlet to Turbine"
    P3 = P2
    c_minWater = water2.cp_mass
    q_max =  c_minWater*(T8-T2)
    q_act = n_HRSG * q_max
    h3 = q_act+h2
    water3.HP = h3,P3
    mDotRatio = (h8-h9)/(h3-h2)
    s3 = water3.s
    
    "State 4 -WATER - Outlet of Turbine/Inlet to Condenser"
    P4 = P1
    s4_is =  s3
    water4.SP = s4_is,P4
    h4_is = water4.h
    h4 = h_OutTurbine(n_turb_w, h4_is, h3)
    water4.HP = h4, P4
    
    #Remaining Variables
    T1 = water1.T
    T3 = water3.T
    T4 = water4.T
    T6 = air6.T
    s2 = water2.s
    s3 = water3.s
    s4 = water4.s
    s6 = air6.s
    s8 = air8.s
    s9 = air9.s
    
    #Works and Heats
    WturbAir = (h7-h8)/1000
    WturbWater = mDotRatio*(h3-h4)/1000 
    WpumpWater = mDotRatio*(h2_is-h1)/1000
    WcompAir = (h6_is-h5)/1000
    Qin = (h7-h6)/1000
    Qout = mDotRatio*(h4-h1)/1000
    Wtot = WturbAir+WturbWater-WpumpWater-WcompAir
    
    #Arrays for plots
    aPressureRatios.append(pr)    
    aMDotRatios.append(mDotRatio)
    aCycleEfficiency.append(Wtot/Qin)
    aNetPower.append(Wtot)
    aQin.append(Qin)
    aQout.append(Qout)
    
    
fig = plt.figure(figsize=(10, 10))
sub1 = fig.add_subplot(221) # instead of plt.subplot(2, 2, 1)
sub1.set_title('CoGen Cycle Efficiency') # non OOP: plt.title('The function f')
sub1.plot(aPressureRatios, aCycleEfficiency)
sub2 = fig.add_subplot(222)
sub2.set_title('Mass Flow Ratios')
sub2.plot(aPressureRatios, aMDotRatios)
sub3 = fig.add_subplot(223)
sub3.set_title('Net Output')
sub3.plot(aPressureRatios, aNetPower)
sub4 = fig.add_subplot(224)
sub4.set_title('Qin')
sub4.plot(aPressureRatios, aQin)
plt.tight_layout()
plt.show()


#    vals = ([['State', 'Temperature   ', 'Pressure', 'Enthalpy','Entropy','Quality'],[ '1',water1.T,water1.P,water1.h,water1.s,water1.X],['2',water2.T,water2.P,water2.h,water2.s,water2.X],['3',water3.T,water3.P,water3.h,water3.s,water3.X],['4',water4.T,water4.P,water4.h,water4.s,water4.X],['5',air5.T,air5.P,air5.h,air5.s,air5.X],['6',air6.T,air6.P,air6.h,air6.s,air6.X],['7',air7.T,air7.P,air7.h,air7.s,air7.X],['8',air8.T,air8.P,air8.h,air8.s,air8.X]])
#    vals = np.array(vals, dtype=object)
#    shapedVals = np.reshape(vals,(9,6))
#    shapedVals.round(2)
#    print(shapedVals)
    
#fig, ax1 = plt.subplots()
#ax1.plot(prs, ben, lw=2, color="blue")
#ax1.set_ylabel(r"Net Power per Air Mass Flow Rate $(J/kg)$", fontsize=16, color="blue")
#for label in ax1.get_yticklabels():
#    label.set_color("blue")
#    
#ax2 = ax1.twinx()
#ax2.plot(prs, n_cc, lw=2, color="red")
#ax2.set_ylabel(r"Thermal Efficiency $()$", fontsize=16, color="red")
#for label in ax2.get_yticklabels():
#    label.set_color("red")