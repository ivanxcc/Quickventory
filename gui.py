import os
import time

import cv2

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.properties import DictProperty
from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.button import Button
from kivy import platform
import pandas as pd
import numpy as np
from numpy import dtype
if platform == "android":
    is_android = True
    from androidstorage4kivy import SharedStorage


# I plan to use this for camera orientation. It seems like on android -90 degrees rotation of camera is good, but on
# my desktop I need -180 degrees. It is also needed for file IO, desktop will have a different filepath for storage.


# Going to need to add camera logic here and image IO
class One(Screen):
    path = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def capture(self):
        """
        Function to capture the images and give them the names
        according to their captured time and date, and scan for QR codes.
        """
        camera = self.ids['camera']
        timestring = time.strftime("%Y%m%d_%H%M%S")
        filename = "IMG_{}.png".format(timestring)
        if is_android:
            One.path = os.path.join(SharedStorage().get_cache_dir(),
                                    filename)

        else:
            One.path = os.path.join(os.getcwd(), filename)

        camera.export_to_png(One.path)
        if is_android:
            SharedStorage().copy_to_shared(private_file=One.path)

    pass


# Probably retrieve image here and do qr decoding
class Two(Screen):
    session_data = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = StringProperty()
        self.img = DictProperty()
        self.bbox = []
        self.temp_data = []

    def save_to_session(self):
        self.session_data.append(self.temp_data)

    def decode(self):
        cs_decode = False
        detect = cv2.QRCodeDetector()
        img = cv2.imread(One.path)
        # decode the qr code
        data, self.bbox, _ = detect.detectAndDecode(img)
        data2, bbox2, _2 = detect.detectAndDecodeCurved(img)
        session_button = self.ids['session_button']
        textinput = self.ids['textinput']

        if data:
            data.strip()
            item_data = data.split(',')
            if len(item_data) == 4:  # Expected 4 data points
                self.temp_data = item_data
                self.message = f"Captured:\n{item_data}"
                textinput.text = self.message
                session_button.disabled = False
            else:
                self.message = f"Invalid QR code format:\n{data}"
                textinput.text = self.message
                session_button.disabled = True

        else:
            self.message = f"Could not parse QR Code:\n{data}"
            textinput.text = self.message
            session_button = self.ids['session_button']
            session_button.disabled = True
            if data2:
                data2.strip()
                item_data2 = data2.split(',')
                if len(item_data2) == 4:  # Expected 4 data points
                    cs_decode = True
                    self.session_data.append(item_data2)
                    self.message.join(f"\nCurved surface decoding success:\n{item_data2}")
                    textinput.text = self.message
                    session_button.disabled = False
                else:
                    cs_decode = True
                    self.message.join(f"\nCurved surface decoding returned invalid QR code format:\n{data2}")
                    textinput.text = self.message
                    session_button.disabled = True

        # Draw a box around the detected qr code in the image that is returned on screen 2
        self.img = self.ids['img']
        cv2img = cv2.imread(One.path)
        height, width, channels = cv2img.shape
        green = (0, 255, 0)
        blue = (255, 0, 0)
        red = (0, 0, 255)
        if self.bbox is not None:
            if self.img and len(self.bbox) != 0:
                # bbox contains points for qr code bounding box
                start = self.bbox[0][0]
                start = (int(start[0]), int(start[1]))
                end = self.bbox[0][2]
                end = (int(end[0]), int(end[1]))
                cv2.imwrite(One.path, cv2.rectangle(cv2img, start, end, green, 5))
                self.img.source = One.path
                # clear bbox for next img.
                self.bbox = []
            # if no qr is detected bbox will be empty and should just display the image without attempting to draw a box
            elif self.img and len(self.bbox) != 0:
                cv2.imwrite(One.path, cv2.rectangle(cv2img, (0, 0), (width, height), red, 5))
                self.img.source = One.path
        if cs_decode:
            if self.img:
                # bbox contains points for qr code bounding box
                start = bbox2[0][0]
                start = (int(start[0]), int(start[1]))
                end = bbox2[0][2]
                end = (int(end[0]), int(end[1]))
                cv2.imwrite(One.path, cv2.rectangle(cv2img, start, end, blue, 5))
                self.img.source = One.path
                # clear bbox for next img.
                self.bbox = []
        else:
            self.img.source = One.path
    pass


# This is probably where we need the Excel Exporting IO
class Three(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = StringProperty()

    def write(self):
        text = self.ids['textinput2']
        text.text = str(Two.session_data)

    def export_to_excel(self):
        """
        Exports the inventory data to an Excel file.
        """
        if Two.session_data:
            # Create the data frame for pandas Excel functions
            df = pd.DataFrame(Two.session_data, columns=['Item ID', 'Name', 'Description', 'Item Cost'])

            # This needs to be changed based on local Excel file name
            file_name = 'QuickInventory.xlsx'

            # get correct filepath based on os
            if is_android:
                file_path = os.path.join(SharedStorage().get_cache_dir(), file_name)
            else:
                file_path = os.path.join(os.getcwd(), file_name)

            # Check if sheet exists, if no create sheet, otherwise use "append" mode
            if os.path.exists(file_path):
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    df.to_excel(writer, startrow=0, index=False)
                self.message = f'Exported to {file_path}'
                SharedStorage().copy_to_shared(private_file=file_path)
            else:
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, startrow=0, index=False)
                self.message = f'Exported to {file_path}'
                SharedStorage().copy_to_shared(private_file=file_path)
            # Clear session data on exporting to excel.
            Two.session_data.clear()
        else:
            self.message = 'No inventory to export'

    pass


class Quickventory(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.one = One()
        self.two = Two()
        self.three = Three()

    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(One(name='One'))
        sm.add_widget(Two(name='Two'))
        sm.add_widget(Three(name='Three'))
        return sm


# When debugging the Camera Widget takes about 10 min to load, replace camera widget with an image maybe in order to
# speed it up. Also, could take out the builder string and make it a file later.
Builder.load_string("""
<One>:
    FloatLayout:
        size_hint: 1,1
        Camera:
            id: camera
            play: True
            fit_mode: "cover"
            canvas.before:
                PushMatrix
                Rotate:
                    angle: -90
                    origin: self.center
            canvas.after:
                PopMatrix
        BoxLayout: 
            orientation: 'horizontal'
            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'bottom'
                padding: [0,0,0,50]
                Button:
                    id: Capture
                    canvas.before:
                        Color:
                            rgba: .3,0,1,.2
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    size: 100,100
                    size_hint: None, None
                    on_press:
                        root.capture()
                        root.manager.current = "Two"
                    background_color: [.4,.4,.4,.3]
                    background_normal: ''
            AnchorLayout:
                anchor_x: 'right'
                anchor_y: 'bottom'
                padding: [0,0,75,0]
                Button:
                    id: 2
                    size: 100,50
                    size_hint: None, None
                    on_press: root.manager.current = "Three"
                    background_color: [.4,.4,.4,.3]
                    background_normal: ''


<Two>:
    on_enter: root.decode()
    BoxLayout:
        spacing: 10
        padding: [50,50,50,50]
        orientation: 'vertical'
        Image:
            id: img
            size: self.texture_size

        TextInput:
            id: textinput
            text: "QR Code Data"
            size_hint: .75, .5
            height: 150
            width: 300
            pos_hint: {'center_x':.5, 'center_y':.5}
        BoxLayout:
            size_hint: 1, .3
            orientation: 'horizontal'
            AnchorLayout:
                anchor_x: 'left'
                anchor_y: 'bottom'
                padding: [0,0,75,0]
                Button:
                    text: 'Back'
                    on_press: 
                        root.manager.current = "One" 
            AnchorLayout:
                anchor_x: 'right'
                anchor_y: 'bottom'
                Button:
                    id: session_button
                    text: 'Save to Session'
                    on_release:
                        root.save_to_session()
                        root.manager.current = "Three"            

<Three>:
    on_enter: root.write()
    BoxLayout:
        orientation: 'vertical'
        padding: [50,50,50,50]
        TextInput:
            id: textinput2
            text: "Session Data"
            size_hint: .8, .9
            height: 600
            width: 300
            pos_hint: {'center_x':.5, 'center_y':.5}
        BoxLayout:
            size_hint: 1, .3
            orientation: 'horizontal'
            AnchorLayout:
                anchor_x: 'left'
                anchor_y: 'bottom'
                padding: [50,50,75,50]
                Button:
                    text: 'Back'
                    on_press: root.manager.current = "One" 
            AnchorLayout:
                anchor_x: 'right'
                anchor_y: 'bottom'
                padding: [50,50,50,50]
                Button:
                    text: 'Save to Excel'
                    on_press: 
                        root.manager.current = "One"
                        root.export_to_excel()

""")

if __name__ == "__main__":
    Quickventory().run()
