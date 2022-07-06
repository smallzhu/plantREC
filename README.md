i creat GUI for Distinguish plant 利用摄像头采集的图像来识别，并显示在GUI窗口上

use tensorflow & pyqt5
使用了pyqt5的多线程，解决了python的伪多线程的队列执行问题


一共三个线程：动态条显示进程，摄像头显示窗口进程，植物识别进程

训练部分可以参考tensorflow官网


显示效果：


未点开始按钮


![image](https://github.com/smallzhu/plantREC/blob/master/Screenshot_1.png)


识别中


![image](https://github.com/smallzhu/plantREC/blob/master/Screenshot_3.png)
