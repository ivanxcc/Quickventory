'''
Camera Example
==============

This example demonstrates a simple use of the camera. It shows a window with
a buttoned labelled 'play' to turn the camera on and off. Note that
not finding a camera, perhaps because gstreamer is not installed, will
throw an exception during the kv language processing.

'''

# Uncomment these lines to see all the messages
# from kivy.logger import Logger
# import logging
# Logger.setLevel(logging.TRACE)
import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
import time
import cv2
import pandas as pd
from kivy.properties import StringProperty
from kivy import platform
from androidstorage4kivy import SharedStorage

if platform == "android":
    is_android = True

Builder.load_string('''
<CameraClick>:
    orientation: 'vertical'
    Camera:
        id: camera
        play: False
        canvas.before:
            PushMatrix
            Rotate:
                angle: -90
                origin: self.center
        canvas.after:
            PopMatrix
    ToggleButton:
        text: 'Play'
        on_press: camera.play = not camera.play
        size_hint_y: None
        height: '48dp'
    Button:
        text: 'Capture'
        size_hint_y: None
        height: '48dp'
        on_press: root.capture()
    Button:
        text: 'Export to Excel'
        size_hint_y: None
        height: '48dp'
        on_press: root.export_to_excel()
    Label:
        id: label1
        text: root.data
        height: '48dp'
''')


class CameraClick(BoxLayout):
    data = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inventory = []
        self.image = None

    def capture(self):
        '''
        Function to capture the images and give them the names
        according to their captured time and date, and scan for QR codes.
        '''
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        filename = "IMG_{}.png".format(timestr)
        path = os.path.join(SharedStorage().get_cache_dir(),
                            filename)

        camera.export_to_png(path)
        SharedStorage().copy_to_shared(private_file=path)
        detect = cv2.QRCodeDetector()
        img = cv2.imread(path)
        # Update Previous Image Widget
        if self.image: self.remove_widget(self.image)
        self.image = Image(source=path)
        self.add_widget(self.image)
        # decode the qr code
        data, bbox, _ = detect.detectAndDecode(img)
        print(bbox)

        if data:
            item_data = data.split(',')
            if len(item_data) == 4: # Expected 4 data points
                self.inventory.append(item_data)
                self.data = f"Captured: {data}"
            else:
                self.data = "Invalid QR code format"

        else:
            self.data = "QR code not detected."

        print(self.data)

    def export_to_excel(self):
        '''
        Exports the inventory data to an Excel file.
        '''
        if self.inventory:
            df = pd.DataFrame(self.inventory, columns=['Item ID', 'Name', 'Description', 'Item Cost'])
            # This needs to be changed based on local Excel file name
            file_name = 'QuickInventory.xlsx'
            file_path = os.path.join(SharedStorage().get_cache_dir(),
                                     file_name)
            # Check if sheet exists, if no create sheet, otherwise use "append" mode
            if os.path.exists(file_path):
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    df.to_excel(writer, startrow=0, index=False)
                self.data = f'Exported to {file_path}'
                SharedStorage().copy_to_shared(private_file=file_path)
            else:
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, startrow=0, index=False)
                self.data = f'Exported to {file_path}'
                SharedStorage().copy_to_shared(private_file=file_path)
        else:
            self.data = 'No inventory to export'

class TestCamera(App):

    def build(self):
        return CameraClick()




TestCamera().run()
