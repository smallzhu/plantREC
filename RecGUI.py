
import sys
import time
import cv2
import tensorflow as tf
import numpy as np

from spy_image import recongnition
from PyQt5.QtCore import pyqtSlot, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QApplication, QGridLayout, QTextEdit


#GUI
class MyWindow(QWidget):

    sig_abort_workers = pyqtSignal()#关闭信号

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle("智能识别")
        self.resize(800,450)

        self.txt_print = QTextEdit()
        self.start_btn = QPushButton()
        self.stop_btn = QPushButton()
        self.Camera_label = QLabel()
        self.wait_label = QLabel()

        # self.txt_log.setText("点击'开始‘ 开始识别")
        self.start_btn.setText("开始识别")
        self.stop_btn.setText("停止识别")
        self.stop_btn.setDisabled(True)
        self.Camera_label.setText("未开始")
        self.wait_label.setText("等待中")
        self.start_btn.clicked.connect(self.start_workers)
        self.stop_btn.clicked.connect(self.abort_workers)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.start_btn,1,0)
        grid.addWidget(self.stop_btn,2,0)
        grid.addWidget(self.txt_print,4,0)
        grid.addWidget(self.wait_label,3,0)
        grid.addWidget(self.Camera_label,1,1,4,4)
        self.setLayout(grid)

        QThread.currentThread().setObjectName('main')
        self.__workers_done = None
        self.__threads = None

    def start_workers(self):
        self.start_btn.setDisabled(True)
        self.stop_btn.setEnabled(True)
        self.txt_print.clear()
        self.txt_print.append("识别中..")
        self.__workers_done = 0
        self.__threads = []
        self.thread_ID=["txt_print","Camera_label","wait_label"]
        for idx in range(len(self.thread_ID)):
            worker = Worker(idx)
            thread = QThread()
            thread.setObjectName(self.thread_ID[idx])
            self.__threads.append((thread,worker))
            worker.moveToThread(thread)
            worker.sig_working.connect(self.on_woker_working)
            worker.sig_finished.connect(self.on_worker_finished)

            self.sig_abort_workers.connect(worker.abort)
            thread.started.connect(worker.work)
            thread.start()

    @pyqtSlot(str,str)
    def on_woker_working(self,worker_id:str,data:str):

        if(worker_id == 'txt_print'):
            self.txt_print.clear()
            self.txt_print.append(data)
        if(worker_id == 'Camera_label'):
            self.Camera_label.setPixmap(QPixmap("img_data.jpg"))
        if(worker_id == 'wait_label'):
            wait_imag = 'D:\pycharmProject\plantREC\loadImag\\fish-%s.png'%data
            self.wait_label.setPixmap(QPixmap(wait_imag))

    @pyqtSlot()
    def abort_workers(self):
        self.sig_abort_workers.emit()

    @pyqtSlot(int)
    def on_worker_finished(self,worker_id):
        print("wait shutdwon")
        self.__workers_done += 1
        print('shutdown no'+str(self.__workers_done))
        thread,worker = self.__threads[worker_id]
        thread.quit()
        thread.wait()

        if self.__workers_done == len(self.thread_ID):
            self.stop_btn.setDisabled(True)
            self.start_btn.setEnabled(True)
#线程类
class Worker(QObject):

    sig_working = pyqtSignal(str,str)
    sig_finished = pyqtSignal(int)

    def __init__(self,id:int):
        super().__init__()
        self.__id = id
        self.__abort = False
        self.waitTime_falg = 0

    @pyqtSlot()
    def work(self):
        thread_name = QThread.currentThread().objectName()
        while(1):
            #主字显示
            if(thread_name == 'txt_print'):
                rec = Rec()
                output_label,output_proba = rec.rec_work()
                print(output_proba,output_label,'test')

                if output_label == None:
                    self.sig_working.emit(thread_name,"暂时未能识别，调整中")
                elif output_proba == None:
                    self.sig_working.emit(thread_name, "暂时未能识别，调整中")
                else:
                    if output_label == 'diaolan':
                        self.sig_working.emit(thread_name,'     吊兰\n'
                                                          '吊兰为百合科多年生常绿草本花卉。\n'
                                                          '吊兰因根叶似兰，花梗横伸倒悬而得名。\n'
                                                          '吊兰喜半阴的环境，怕强光直射，\n'
                                                          '尤其北方地区，春夏秋三季需遮去50％～70％的阳光，\n'
                                                          '否则易出现日灼病，植株生长严重不良。')
                    elif output_label == 'wenzhu':
                        self.sig_working.emit(thread_name,'     文竹\n'
                                                          '土壤、盆土文竹适合在温暖湿润、富含腐枝、排水良好的土壤中生长。\n'
                                                          '浇水、浇水盆栽文竹如果浇水过多，土壤过于粘重，排水不良，'
                                                          '会使文竹的叶间变成焦黄并脱落，生长寿影响。\n'
                                                          '施肥、施肥文竹虽非好肥植物但也不能缺少肥料\n'
                                                          '光照、文竹栽培切忌烈日暴晒，夏秋炎热季节，应置于荫蔽通风之处\n'
                                                          '温度、冬季盆栽文竹应保持5℃以上的环境温度，以免受冻\n')
                    elif output_label == 'xiuzhenyezi':
                        self.sig_working.emit(thread_name,'     袖珍椰子\n'
                                                          '光照：袖珍椰子喜半荫，'
                                                          '在强烈阳光下叶色会枯黄;如果长期放置在光照不足之处，'
                                                          '植株会变得瘦长。所以在室内最好放在窗边明亮处。\n'
                                                          '温度：袖珍椰子喜温暖，生长适温为18—24摄氏度，'
                                                          '13摄氏度进入休眠。冬季最好不要低于10摄氏度。\n'
                                                          '水：袖珍椰子喜水，在生长期间要保持土壤湿润，'
                                                          '在休眠期要等到三分之二的盆土干后再进行浇水。另外，'
                                                          '袖珍椰子喜高的空气湿度，如果太干燥，'
                                                          '叶尖就会变成棕色。所以在干燥期间如秋季要采取向'
                                                          '叶面经常喷水等措施来提高植株周围的空气湿度。')

                    elif output_label == 'yajiaomu':
                        self.sig_working.emit(thread_name,'     鸭脚木\n'
                                                          '土壤：鸭脚木适合土质深厚、疏松肥沃的土壤。\n'
                                                          '浇水：鸭脚木在土壤水分充足的环境下生长良好，日常及时补充水分，但不要积水。\n'
                                                          '阳光：宜放在明亮散射光充足的地方养护。\n'
                                                          '温度：鸭脚木不耐寒，冬季应保持室温在10℃以上。\n')
                    elif output_label == 'xingfushu':
                        self.sig_working.emit(thread_name,'     幸福树\n'
                                                          '盆与土壤：由于幸福树植株会长的比较高大粗壮，'
                                                          '所以要用大盆来养殖，盆土要用透气，腐殖质多的土壤'
                                                          '田园土：腐叶土：河沙，按照5:3:1混合\n'
                                                          '浇水幸福树除了冬天一周浇水一次，'
                                                          '其他季节均为3天左右浇一次水，夏季干燥，'
                                                          '可以对幸福树叶面进行喷水，增加湿度。\n'
                                                          '温度：幸福树喜欢温暖的环境，适宜温度是20℃-30℃之间。')
                    elif output_label == 'xianrenqiu':
                        self.sig_working.emit(thread_name,'     仙人球\n'
                                                          '土壤：盆栽仙人球可选用腐叶土、园土、粗砂各3份，'
                                                          '再加草木灰与腐熟骨粉1份混匀配制，宜早春上盆\n'
                                                          '施肥：仙人球喜肥，耐肥，肥料充足时生长较快。'
                                                          '春季换盆1个月后开始追肥，'
                                                          '生长季节每20天左右追施腐熟的10倍液肥混合等量的100'
                                                          '0倍磷酸二氢钾液，或1000倍“花多多”通用肥1次。'
                                                          '冬季不施肥。\n'
                                                          '浇水：春夏秋三季是其生长旺季，应及时补充浇水，保持土壤湿润。\n'
                                                          '温度：生长期间正常的室温即可，冬季应将其放置在冷凉的环境之中（3-5℃），'
                                                          '颇为耐寒。如果盆土干燥可耐0℃的低温。')
                print('识别完成')
            #显示摄像头
            elif(thread_name == 'Camera_label'):
                time.sleep(0.005)
                self.sig_working.emit(thread_name,"")
                ret,frame = cap.read()
                cv2.imwrite("img_data.jpg",frame)
            #识别时的加载动画
            elif(thread_name == 'wait_label'):
                time.sleep(0.03)
                self.sig_working.emit(thread_name,str(self.waitTime_falg))
                if self.waitTime_falg == 46:
                    self.waitTime_falg = 0
                else:
                    self.waitTime_falg+=1
            else:
                print("cannot find tartget")
                self.sig_working.emit(thread_name,"未找到")
            app.processEvents()
            if self.__abort:
                break
        self.sig_finished.emit(self.__id)


    def abort(self):
        self.sig_working.emit('txt_print','stop')
        self.__abort = True
#识别类
class Rec():
    def rec_work(self):
        file_name = "D:\pycharmProject\plantREC\img_data.jpg"
        model_file = "D:\pycharmProject\plantREC\output_graph.pb"
        label_file = "D:\pycharmProject\plantREC\output_labels.txt"
        input_layer = 'Placeholder'
        output_layer = 'final_result'
        rec = recongnition(file_name, model_file, label_file)
        graph = rec.load_graph()
        try:
            t = rec.read_tensor_from_image_file()
        except Exception as e:
            return None,None
        input_name = "import/" + input_layer
        output_name = "import/" + output_layer
        input_operation = graph.get_operation_by_name(input_name)
        output_operation = graph.get_operation_by_name(output_name)

        with tf.Session(graph=graph) as sess:
            results = sess.run(output_operation.outputs[0], {input_operation.outputs[0]: t})

        results = np.squeeze(results)
        top_k = results.argsort()[-5:][::-1]

        labels = rec.load_labels()
        for i in top_k:
            return labels[i], results[i]

if __name__=='__main__':
    cap = cv2.VideoCapture(0)
    app = QApplication([])
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())