*********************************************************************
THIS PROGRAM IS CODED IN C AND CAN BE UPLOADED ON AN ARDUINO BOARD VIA THE ARDUINO IDE


*********************************************************************

Here are some hardware and software instructions to follow:

1) Connect the “SCL” and “SDA” I2C pins of the IMUs respectively to the “A5” and “A6” pins of the Arduino board.

2) Connect the EMGs on analog pins of the Arduino board. The code is only developed for having one EMG connected to the A0 pin of the Arduino. To use more EMGs, one could add a piece of code to read and send the data from the other remaining analog pins of the Arduino board.

3) All the data are sent by serially printing data for each sensor. Each data package begins with a label containing “EMG” or “IMU” followed by a number, specific to the sensor.

4) To execute the program, simply upload it on the Arduino board and connect it to an USB port of the computer. Then follow the instructions contained in the “Readme” file of the arm model.

