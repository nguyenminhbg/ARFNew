import sys
import pyvisa
from PyQt6.QtWidgets import (QMainWindow, QApplication, QHBoxLayout, QVBoxLayout, QCheckBox,
                             QLabel, QComboBox, QLineEdit, QWidget, QMessageBox)
from PyQt6.uic import loadUi
import os
from PyQt6.QtCore import Qt
import  arfmodel
from arfmodel import ARFModel
import re

class main_window(QMainWindow):
    # Địa chỉ IP của thiết bị
    Device_ip = "192.168.99.66"
    Device_name = "inst0"
    # Tạo VISA Resource string
    VISA_RESOURCE = f"TCPIP0::{Device_ip}::{Device_name}::INSTR"
    my_dict = {}
    def __init__(self):
        super(main_window, self).__init__()
        current_directory = os.path.dirname(os.path.abspath(__file__))
        print(current_directory)
        loadUi(os.path.join(current_directory, "main.ui"), self)
        self.checkAll.stateChanged.connect(self.on_checkbox_state_changed)
        self.qh_layout = QVBoxLayout()
        self.loadLayout()
        self.scrollAreaWidgetContents.setLayout(self.qh_layout)
        self.sendAll.clicked.connect(self.send_allCommand)
        self.send.clicked.connect(self.send_singleCommand)
        self.edIPDevice.setText(self.Device_ip)
        self.edIPDevice.textChanged.connect(self.device_on_text_changed)
        self.edDevice.setText(self.Device_name)
        self.edDevice.textChanged.connect(self.name_on_text_changed)
        self.checkConnect.clicked.connect(self.check_connect)


    def name_on_text_changed(self, text):
        self.Device_name = text

    def device_on_text_changed(self, text):
        self.Device_ip = text
        print(self.Device_ip)


    def show_diaglog(self, status, message):
            msg = QMessageBox()
            msg.setWindowTitle(status)
            msg.setText(message)
            msg.exec()
            return


    def check_connect(self):
        try:
            if self.Device_name == "" or self.Device_ip == "":
                self.show_diaglog("error", "Please input Device IP or Name")
            self.VISA_RESOURCE = f"TCPIP0::{self.Device_ip}::{self.Device_name}::INSTR"
            # Khởi tạo ResourceManager
            rm = pyvisa.ResourceManager()
            # Mở kết nối đến thiết bị chỉ một lần
            instrument = rm.open_resource(self.VISA_RESOURCE)
            # Thiết lập timeout (nếu cần)
            instrument.timeout = 5000  # Đặt timeout là 5 giây
            idn = instrument.query("*IDN?")
            if idn:
                self.show_diaglog("Ok", "Connected")
            else:
                self.show_diaglog("erro", "Disconnected")

            instrument.close()
        except Exception as e:
            print("Loi")
            self.show_diaglog("erro", "Disconnected")

    def send_singleCommand(self):
        try:
            if self.Device_name == "" or self.Device_ip == "":
               self.show_diaglog("error", "Please input Device IP or Name")
            if self.singleCmd.text() == "":
                self.show_diaglog("erro", "Please input command")
                return
            self.VISA_RESOURCE = f"TCPIP0::{self.Device_ip}::{self.Device_name}::INSTR"
            # Khởi tạo ResourceManager
            rm = pyvisa.ResourceManager()
            # Mở kết nối đến thiết bị chỉ một lần
            instrument = rm.open_resource(self.VISA_RESOURCE)
            # Thiết lập timeout (nếu cần)
            instrument.timeout = 5000  # Đặt timeout là 5 giây
            response1 = instrument.query(self.singleCmd.text())
                    # instrument.write("CONF:VPEAK")  # Cấu hình chế độ đo điện áp Peak
            instrument.close()
        except Exception as e:
            print("Loi")


    def send_allCommand(self):
        try:
            if self.Device_name == "" or self.Device_ip == "":
                self.show_diaglog("error", "Please input Device IP or Name")
            # Khởi tạo ResourceManager
            rm = pyvisa.ResourceManager()
            # Mở kết nối đến thiết bị chỉ một lần
            instrument = rm.open_resource(self.VISA_RESOURCE)
            # Thiết lập timeout (nếu cần)
            instrument.timeout = 5000  # Đặt timeout là 5 giây
            for i in reversed(range(self.scrollAreaWidgetContents.layout().count())):
                layout = self.scrollAreaWidgetContents.layout().itemAt(i).layout()
                #print(layout)
                for it in range(layout.count()):
                    item = layout.itemAt(it)
                    #sub_layout = item.layout()
                    key = ""
                    for ii in range(item.count()):
                        widget = item.itemAt(ii).widget()
                        if widget:
                            if isinstance(widget, QCheckBox):
                                if not widget.isChecked():
                                    break
                            if isinstance(widget, QLabel):
                                key = widget.text()
                            if isinstance(widget, QComboBox):
                                self.my_dict[key] = widget.currentText()
                                print(self.my_dict[key])
                            if isinstance(widget, QLineEdit):
                                self.my_dict[key] = self.my_dict[key].replace("value", widget.text())
                                print(self.my_dict[key])
            for key, value in self.my_dict.items():
                #instrument.write(value)  # Ví dụ: chuyển thiết bị sang chế độ remote
                response = instrument.query(value)
                print("Thiết bị trả về:", response)
            instrument.close()
        except Exception as e:
            print("Loi")
            self.show_diaglog("erro", "Disconnected")



    def loadLayout(self):
        current_layout = self.scrollAreaWidgetContents.layout()
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path =os.path.join(current_directory, "commandlist.txt")
        data_temp = []
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                values = line.strip().split(",")
                data_temp.append(values)
            # for i in range(0, len(data_temp), 4):
            #     chunk = data_temp[i:i + 4]
            #     self.create_item(chunk)
            while True:
                if len(data_temp) >= 4:
                    print(f"len: {len(data_temp)}")
                    chunk = data_temp[:4]  # Lấy 4 phần tử đầu tiên
                    self.create_item(chunk)  # Xử lý nhóm 4 phần t
                    data_temp = data_temp[4:]  # Xóa 4 phần tử đầu tiên
                elif len(data_temp) >= 3:
                    chunk = data_temp[:3]  # Lấy 4 phần tử đầu tiên
                    self.create_item(chunk)  # Xử lý nhóm 4 phần t
                    data_temp = data_temp[3:]  # Xóa 4 phần tử đầu tiên
                    break
                elif len(data_temp) >= 2:
                    chunk = data_temp[:2]  # Lấy 4 phần tử đầu tiên
                    self.create_item(chunk)  # Xử lý nhóm 4 phần t
                    data_temp = data_temp[2:]  # Xóa 4 phần tử đầu tiên
                    break
                else:
                    chunk = data_temp[:1]  # Lấy 4 phần tử đầu tiên
                    self.create_item(chunk)  # Xử lý nhóm 4 phần t
                    data_temp = data_temp[1:]  # Xóa 4 phần tử đầu tiên
                    break


    def create_item(self, chunk):
        layout = QHBoxLayout()
        layout.setSpacing(25)
        for idx, item in enumerate(chunk):
            if idx ==0:
                qhLayout1 = QHBoxLayout()
                checkbox1 = QCheckBox()
                #checkbox1.setFixedSize(35, 35)
                checkbox1.setChecked(True)
                label1 = QLabel(item[0])
                label1.setFixedWidth(75)
                label1.setMaximumWidth(75)
                #label1.setFixedSize(125,35)
                label1.setAlignment(Qt.AlignmentFlag.AlignLeft)
                if "drop" in item[3]:
                    combobox1 = QComboBox(self)
                    combobox1.setStyleSheet("""
                        QComboBox {
                            border-top: 1px solid gray;
                            border-right: 1px solid gray;
                            border-left: 1px solid gray;
                            border-bottom: 1px solid gray;
                        }
                    """)
                    #combobox1.setFixedSize(125, 35)
                    for cmd in item[1].split("|"):
                        combobox1.addItem(cmd)
                    qhLayout1.addWidget(checkbox1)
                    qhLayout1.addWidget(label1)
                    qhLayout1.addWidget(combobox1)
                if "input" in item[3]:
                    line_edit1 = QLineEdit(self)
                    line_edit1.setStyleSheet("""
                        QLineEdit {
                            border-top: 1px solid gray;
                            border-right: 1px solid gray;
                            border-left: 1px solid gray;
                            border-bottom: 1px solid gray;
                        }
                    """)
                    #line_edit1.setFixedSize(125, 35)
                    # model1.inputcommand = item[1]
                    # numbers = re.findall(r'\d+\.?\d*', item[1])
                    qhLayout1.addWidget(checkbox1)
                    qhLayout1.addWidget(label1)
                    qhLayout1.addWidget(line_edit1)
                    self.my_dict[item[0]] = item[1]
                qhLayout1.setStretch(0,1)
                qhLayout1.setStretch(1, 4)
                qhLayout1.setStretch(2, 6)
                layout.addLayout(qhLayout1)
                self.qh_layout.addLayout(layout)
            if idx == 1:
                qhLayout2 = QHBoxLayout()
                checkbox2 = QCheckBox()
                #checkbox2.setFixedSize(35, 35)
                checkbox2.setChecked(True)
                label2 = QLabel(item[0])
                label2.setFixedWidth(75)
                label2.setMaximumWidth(75)
                #label2.setFixedSize(125, 35)
                label2.setAlignment(Qt.AlignmentFlag.AlignLeft)
                print(f"item0: {item[0]}")
                if "drop" in item[3]:
                    combobox2 = QComboBox(self)
                    combobox2.setStyleSheet("""
                        QComboBox {
                            border-top: 1px solid gray;
                            border-right: 1px solid gray;
                            border-left: 1px solid gray;
                            border-bottom: 1px solid gray;
                        }
                    """)
                    #combobox2.setFixedSize(125, 35)
                    v = item[1].split("|")
                    for item in v:
                        combobox2.addItem(item)
                    qhLayout2.addWidget(checkbox2)
                    qhLayout2.addWidget(label2)
                    qhLayout2.addWidget(combobox2)
                if "input" in item[3]:
                    line_edit2 = QLineEdit(self)
                    line_edit2.setStyleSheet("""
                        QLineEdit {
                            border-top: 1px solid gray;
                            border-right: 1px solid gray;
                            border-left: 1px solid gray;
                            border-bottom: 1px solid gray;
                            }
                    """)
                    #line_edit2.setFixedSize(125, 35)
                    # numbers = re.findall(r'\d+\.?\d*', item[1])
                    # model2.inputvalue = numbers[0]
                    line_edit2.setText(item[2])
                    qhLayout2.addWidget(checkbox2)
                    qhLayout2.addWidget(label2)
                    qhLayout2.addWidget(line_edit2)
                    self.my_dict[item[0]] = item[1]
                qhLayout2.setStretch(0,1)
                qhLayout2.setStretch(1, 4)
                qhLayout2.setStretch(2, 6)
                layout.addLayout(qhLayout2)
                self.qh_layout.addLayout(layout)
            if idx == 2:
                qhLayout3 = QHBoxLayout()
                checkbox3 = QCheckBox()
                #checkbox3.setFixedSize(35, 35)
                checkbox3.setChecked(True)
                label3 = QLabel(item[0])
                label3.setFixedWidth(75)
                label3.setMaximumWidth(75)
                model3 = ARFModel(True, item[0], "", item[2], "","")
                #label3.setFixedSize(125, 35)
                label3.setAlignment(Qt.AlignmentFlag.AlignLeft)
                if "drop" in item[3]:
                    combobox3 = QComboBox(self)
                    combobox3.setStyleSheet("""
                        QComboBox {
                            border-top: 1px solid gray;
                            border-right: 1px solid gray;
                            border-left: 1px solid gray;
                            border-bottom: 1px solid gray;
                        }
                    """)
                    #checkbox3.setFixedSize(125, 35)
                    for cmd in item[1].split("|"):
                        combobox3.addItem(cmd)
                    self.my_dict[item[0]] = combobox3.currentText()
                    qhLayout3.addWidget(checkbox3)
                    qhLayout3.addWidget(label3)
                    qhLayout3.addWidget(combobox3)
                if "input" in item[3]:
                    line_edit3 = QLineEdit(self)
                    line_edit3.setStyleSheet("""
                        QLineEdit {
                            border-top: 1px solid gray;
                            border-right: 1px solid gray;
                            border-left: 1px solid gray;
                            border-bottom: 1px solid gray;
                        }
                    """)
                    #line_edit3.setFixedSize(125, 35)
                    # numbers = re.findall(r'\d+\.?\d*', item[1])
                    model3.inputvalue = item[2]
                    line_edit3.setText(model3.inputvalue)
                    qhLayout3.addWidget(checkbox3)
                    qhLayout3.addWidget(label3)
                    qhLayout3.addWidget(line_edit3)
                    self.my_dict[item[0]] = item[1]
                qhLayout3.setStretch(0, 1)
                qhLayout3.setStretch(1, 4)
                qhLayout3.setStretch(2, 6)
                layout.addLayout(qhLayout3)
                self.qh_layout.addLayout(layout)
            if idx == 2:
                qhLayout4 = QHBoxLayout()
                checkbox4 = QCheckBox()
                # checkbox3.setFixedSize(35, 35)
                checkbox4.setChecked(True)
                label4 = QLabel(item[0])
                label4.setFixedWidth(75)
                label4.setMaximumWidth(75)
                # label3.setFixedSize(125, 35)
                label4.setAlignment(Qt.AlignmentFlag.AlignLeft)
                if "drop" in item[3]:
                    combobox4 = QComboBox(self)
                    combobox4.setStyleSheet("""
                        QComboBox {
                            border-top: 1px solid gray;
                            border-right: 1px solid gray;
                            border-left: 1px solid gray;
                            border-bottom: 1px solid gray;
                        }
                    """)
                    # checkbox3.setFixedSize(125, 35)
                    for cmd in item[1].split("|"):
                        combobox4.addItem(cmd)
                    self.my_dict[item[0]] = combobox4.currentText()
                    qhLayout4.addWidget(checkbox4)
                    qhLayout4.addWidget(label4)
                    qhLayout4.addWidget(combobox4)
                if "input" in item[3]:
                    line_edit4 = QLineEdit(self)
                    line_edit4.setStyleSheet("""
                        QLineEdit {
                            border-top: 1px solid gray;
                            border-right: 1px solid gray;
                            border-left: 1px solid gray;
                            border-bottom: 1px solid gray;
                        }
                    """)
                    # line_edit3.setFixedSize(125, 35)
                    # numbers = re.findall(r'\d+\.?\d*', item[1])
                    qhLayout4.addWidget(checkbox4)
                    qhLayout4.addWidget(label4)
                    qhLayout4.addWidget(line_edit4)
                    self.my_dict[item[0]] = item[1]
                qhLayout4.setStretch(0, 1)
                qhLayout4.setStretch(1, 4)
                qhLayout4.setStretch(2, 6)
                layout.addLayout(qhLayout4)
                self.qh_layout.addLayout(layout)
        layout.setStretch(0, 1)
        layout.setStretch(1, 1)
        layout.setStretch(2, 1)
        layout.setStretch(3, 1)
        layout.setStretch(4, 1)
        layout.setStretch(5, 1)
        layout.setStretch(6, 1)
        layout.setStretch(7, 1)
        layout.setStretch(8, 1)

    def on_checkbox_state_changed(self, state):
        for i in reversed(range(self.scrollAreaWidgetContents.layout().count())):
            layout = self.scrollAreaWidgetContents.layout().itemAt(i).layout()
            for it in range(layout.count()):
                    item = layout.itemAt(it)
                    #sub_layout = item.layout()
                    for ii in range(item.count()):
                        widget = item.itemAt(ii).widget()
                        if isinstance(widget, QCheckBox):
                            if state:
                                widget.setChecked(True)
                                # for item in self.listcommand:
                                #     item.status = True
                            else:
                                widget.setChecked(False)
                                # for item in self.listcommand:
                                #     item.status = False
                        # if isinstance(widget, QComboBox):
                        #     print(widget.currentText())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = main_window()
    window.setWindowTitle('Resizable Window')
    window.show()  # Hiển thị cửa sổ
    sys.exit(app.exec())  # Đúng trong PyQt6
