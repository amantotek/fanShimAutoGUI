# fanShimAutoGUI
Controls Pimoroni Fan SHIM on Raspberry Pi4 using Xubuntu 20.04 LTS running Python3 plus PySimpleGUI 

https://github.com/pimoroni/fanshim-python/tree/master/examples has files for the Pimoroni Fan SHIM aimed at the Rasbian Operating System. Several Python3 command line files are listed here to operate/test fan features including automatic.py upon which this software is built. This software has been developed using Xubuntu 20.04 LTS operating system with added feature of GUI screen operation.

![image](https://user-images.githubusercontent.com/7591528/101183540-8fea3180-3647-11eb-8c69-5b3095b46bec.png)

The plot above shows the fan on in red and off in green.

To run use: sudo python3 fanShimAuto.py

Inspect the code for import PySimpleGUI, the date we added to show when issued.

Under Xubuntu on Pi4 we used 'Settings/Session and Startup/Application Autostart' to start the fan controller on powering up the Pi4.

PySimpleGUI allows fairly easy intuitive changes to be made to the screen layout and is extremely well documented https://pysimplegui.readthedocs.io/en/latest/

The tabbing system would allow other programs in the Pimoroni folder (referenced above) to have their own new tabs. Currently the min/max thresholds to switch the FanSHIM are hard-coded (45 +/- 5 degC) but GUI controls to set a mean target temperature and +/- degrees C band wanted above and below might want to be added. The restart feature is useful for testing modifications.
