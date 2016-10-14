

# uncomment the following two lines for fullscreen view
# from kivy.config import Config
# Config.set('graphics', 'fullscreen', 'auto')

# Uncomment the following three lines to customize the screen size
# from kivy.config import Config
# Config.set('graphics', 'width', '800')
# Config.set('graphics', 'height', '600')


import io
import urllib
import urllib2
import threading
import os
import time
import socket
import json

from kivy.lang import Builder
from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import StringProperty


__author__ = 'DNAPhone S.r.l.'


_SERVER_ADDRESS = '192.168.1.2'
_SERVER_PORT = 1027

BUFFER = 1024

CAMERA_PARAMETERS = {
    "PARAM_BRIGHTNESS": 'br',
    "PARAM_CONTRAST": 'co',
    "PARAM_SATURATION": 'sa',
    "PARAM_SHARPNESS": 'sh',
    "PARAM_SHOOT": 'im'
}

PARAM_BRIGHTNESS = "PARAM_BRIGHTNESS"
PARAM_CONTRAST = "PARAM_CONTRAST"
PARAM_SATURATION = "PARAM_SATURATION"
PARAM_SHARPNESS = "PARAM_SHARPNESS"
PARAM_SHOOT = "PARAM_SHOOT"

PARAM_BRIGHTNESS_DEFAULT = 50
PARAM_CONTRAST_DEFAULT = 0
PARAM_SATURATION_DEFAULT = 0
PARAM_SHARPNESS_DEFAULT = 0

PHOTO_FOLDER_NAME = "WeLabMicroscope"


Builder.load_string('''
<ConfirmPopup>:
    cols:1
    Label:
        text: root.text
    GridLayout:
        cols: 2
        size_hint_y: None
        height: '44sp'
        Button:
            text: 'Yes'
            on_release: root.dispatch('on_turn_off_confirm','yes')
        Button:
            text: 'No'
            on_release: root.dispatch('on_turn_off_confirm', 'no')
''')


class ConfirmPopup(GridLayout):
    text = StringProperty()

    def __init__(self, **kwargs):
        self.register_event_type('on_turn_off_confirm')
        super(ConfirmPopup, self).__init__(**kwargs)

    def on_turn_off_confirm(self, *args):
        pass


class Micro(FloatLayout):

    def __init__(self, microimageoutput='microimage', server_address=_SERVER_ADDRESS):
            super(FloatLayout, self).__init__()
            self.stream_changed_lock = threading.Lock()
            self.set_server_address(server_address)
            self.set_folder()
            self.allow_stretch = False
            self.keep_ratio = False
            self.change_image_param(PARAM_BRIGHTNESS_DEFAULT, PARAM_BRIGHTNESS)
            self.change_image_param(PARAM_CONTRAST_DEFAULT, PARAM_CONTRAST)
            self.change_image_param(PARAM_SATURATION_DEFAULT, PARAM_SATURATION)
            self.change_image_param(PARAM_SATURATION_DEFAULT, PARAM_SHARPNESS)
            self.microimageoutput = microimageoutput
            self.client_socket = None

    def parse_answer(self, answer):

        if not (answer.rstrip() == '{}'):

            try:
                j = json.loads(answer.rstrip())

                if 'contextResponses' in j:
                    contextResponses = j['contextResponses'][0]

                    if 'contextElement' in contextResponses and 'statusCode' in contextResponses:
                        contextElement = contextResponses['contextElement']
                        statusCode = contextResponses['statusCode']

                        if 'type' in contextElement and contextElement['type'] == 'Answer':

                            if 'attributes' in contextElement:

                                attributes = contextElement['attributes'][0]

                                if 'name' in attributes and 'code' in statusCode and 'reasonPhrase' in statusCode:

                                    if attributes['name'] == 'LOCALHOST_SETTING':
                                        print 'Received a host parameters setting answer: ' + statusCode['reasonPhrase']

                                    elif attributes['name'] == 'CHANGE_MICROSCOPE_LED_BRIGHTNESS':
                                        print 'Received a change led intensity answer: ' + statusCode['reasonPhrase']

                                    elif attributes['name'] == 'TURN_OFF':

                                        print 'Received a turn off answer: ' + statusCode['reasonPhrase']

                                        if statusCode['code'] == '200':
                                            self.client_socket = None
                                            print 'Connection closed'

                                else:
                                    print 'Received answer has a bad format: missing name, code or reasonPhrase elements'

                            else:
                                print 'Received answer has a bad format: missing attributes or statusCode elements'

                        else:
                            print 'Received an unknown message: missing type element'

                    else:
                        print 'Received an unknown message: missing contextElement'

                else:
                    print 'Received an unknown message: missing contextResponse'

            except ValueError:
                print 'Decoding JSON has failed'

    def set_ip(self):
        label = self.ids["ip_configuration"].text

        print label

        self.set_server_address(label)

        self.connect_to_microscope_led_server()

        if label == "127.0.0.1":
            try:
                if self.client_socket is not None:
                    self.client_socket.sendall('{"attributes":[{"type":"string","name":"command","value":"LOCALHOST_SETTING","set":"%s"}],"type":"Command"}\n' % True)
                    answer = self.client_socket.recv(BUFFER)
                    self.parse_answer(answer)
            except ValueError:
                print "An error occurred while sending the message to the kit"

        else:
            try:
                if self.client_socket is not None:
                    self.client_socket.sendall('{"attributes":[{"type":"string","name":"command","value":"LOCALHOST_SETTING","set":"%s"}],"type":"Command"}\n' % False)
                    answer = self.client_socket.recv(BUFFER)
                    self.parse_answer(answer)
            except ValueError:
                print "An error occurred while sending the message to the kit"

    def get_current_address(self):

        address = self.ids["ip_configuration"].text

        if address == '':
            address = _SERVER_ADDRESS
        else:
            pass

        return address

    def connect_to_server(self, instance):

        try:
            socket_address = (self.server_address, _SERVER_PORT)
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(3)
            self.client_socket.connect(socket_address)

            self.connecting_popup.dismiss()

        except (socket.timeout, socket.error) as e:

            print "Connection timeout expired"

            self.client_socket = None

            self.connecting_popup.dismiss()

            popup = Popup(title='Connection failed', content=Label(text='Cannot connect to the We-LAB kit.\nPlease check if the ip address is right.'), size_hint=(None, None), size=(350, 200))
            popup.open()

    def connect_to_microscope_led_server(self):
        self.connecting_popup = Popup(title='Connecting', content=Label(text='Please wait....'), size_hint=(None, None), size=(350, 200))
        self.connecting_popup.bind(on_open=self.connect_to_server)
        self.connecting_popup.open()

    def on_turn_off_confirm(self, instance, answer):

        if answer == 'yes':
            print "Turning off the device..."
            try:
                self.client_socket.sendall('{"attributes":[{"type":"string","name":"command","value":"TURN_OFF"}],"type":"Command"}\n')
                answer = self.client_socket.recv(BUFFER)
                self.parse_answer(answer)
            except ValueError:
                print "An error occurred while sending the message to the kit"

        self.popup.dismiss()

    def turn_off_device(self):
        if self.client_socket is not None:
            content = ConfirmPopup(text='Do you really want to turn the device off?')
            content.bind(on_turn_off_confirm=self.on_turn_off_confirm)
            self.popup = Popup(title="Turn off",
                               content=content,
                               size_hint=(None, None),
                               size=(480, 400),
                               auto_dismiss=False)
            self.popup.open()

    def localhost(self):
        label = self.ids["sw1"]
        label2 = self.ids["ip_configuration"]

        if label.active:
            label2.text = "127.0.0.1"
            label2.foreground_color = [1, 1, 1, 1]
            label2.background_color = [0.1, 0.3, .3, 1]
            label2.readonly = True
            self.set_server_address('127.0.0.1')

            self.connect_to_microscope_led_server()

            try:
                if self.client_socket is not None:
                   self.client_socket.sendall('{"attributes":[{"type":"string","name":"command","value":"LOCALHOST_SETTING","set":"%s"}],"type":"Command"}\n' % True)
                   self.parse_answer(self.client_socket.recv(BUFFER))
            except ValueError:
                print "An error occurred while sending the message to the kit"

            print "There is no place like 127.0.0.1 !!\n"

        else:
            label2.text = _SERVER_ADDRESS
            label2.readonly = False
            label2.foreground_color = [0, 0, 0, 1]
            label2.background_color = [1, 1, 1, 1]
            self.set_server_address(_SERVER_ADDRESS)

            self.connect_to_microscope_led_server()

            try:
                if self.client_socket is not None:
                    self.client_socket.sendall('{"attributes":[{"type":"string","name":"command","value":"LOCALHOST_SETTING","set":"%s"}],"type":"Command"}\n' % False)
                    self.parse_answer(self.client_socket.recv(BUFFER))
            except ValueError:
                print "An error occurred while sending the message to the kit"

    def set_folder(self):
        folder = self.ids["folder_configuration"].text
        self.ids["current_folder"].text = 'Current folder:' + os.getcwd()+'/' + folder

        print folder

        if folder == '':
            selected_folder = PHOTO_FOLDER_NAME

        else:
            selected_folder = folder

        return selected_folder

    def print_folder(self):
        current_folder = self.set_folder()
        return current_folder

    def take_picture(self):
        val = 1
        picture_name_prefix = self.ids["picture_prefix"].text
        selected_folder = self.set_folder()
        self.change_image_param(val, PARAM_SHOOT)
        time.sleep(1)
        im_name = urllib2.urlopen("http://" + self.get_current_address() + "/getMediaSaved.php?action=getImages").read().replace('"', '').split('|')[0]

        print im_name

        if not os.path.exists(selected_folder):
            os.makedirs(selected_folder)
        else:
            pass

        date_tag = time.strftime("%Y%m%d-%H%M%S")
        urllib.urlretrieve("http://"+self.get_current_address()+"/media/im_welab.jpg", (os.getcwd()+'/'+selected_folder+'/'+picture_name_prefix+'_'+date_tag+'.jpg'))

        popup = Popup(title='Image saved', content=Label(text='The image has been saved.'), size_hint=(None, None), size=(350, 200))
        popup.open()

    @staticmethod
    def default_values():
        br = PARAM_BRIGHTNESS_DEFAULT
        co = PARAM_CONTRAST_DEFAULT
        sa = PARAM_SATURATION_DEFAULT
        sh = PARAM_SHARPNESS_DEFAULT
        return {'br': br, 'co': co, 'sa': sa, 'sh': sh}

    def set_server_address(self, address):
        self.server_address = address
        self.command_url = 'http://%s/cmd_pipe.php?' % address
        self.stream_url = 'http://%s/cam_pic_new.php?' % address

        with self.stream_changed_lock:
            self.stream_changed = True

    def start(self):
        self._image_lock = threading.Lock()
        self.quit = False
        self._thread = threading.Thread(target=self.read_stream)
        self._thread.daemon = True
        self._thread.start()

        self._image_buffer = None
        Clock.schedule_interval(self.update_image, 1 / 10.)

    def stop(self):
        self.quit = True
        self._thread.join()
        Clock.unschedule(self.update_image)

    def read_stream(self):
        stream = None
        try:
            stream = urllib2.urlopen(self.stream_url, timeout=3)
        except:
            print "Bad stream you gonna see a lot of errors :D"

        bytes = ''

        while not self.quit:
            try:
                if self.stream_changed:
                    stream = urllib2.urlopen(self.stream_url, timeout=3)

                    with self.stream_changed_lock:
                        self.stream_changed = False

                bytes += stream.read(4096)
                a = bytes.find('\xff\xd8')
                b = bytes.find('\xff\xd9')

                if a != -1 and b != -1:
                    jpg = bytes[a:b + 2]
                    bytes = bytes[b + 2:]

                    data = io.BytesIO(jpg)
                    im = CoreImage(
                                    data,
                                    ext="jpeg",
                                    nocache=True)

                    with self._image_lock:
                        self._image_buffer = im

            except:
                sleep_time = 1
                print "Streaming error waiting %d seconds before retrying" % sleep_time
                time.sleep(sleep_time)

    def update_image(self, *args):
        im = None

        with self._image_lock:
            im = self._image_buffer
            self._image_buffer = None

        if im is not None:
            pass
            self.ids[self.microimageoutput].texture = im.texture

    def control_br(self):
        label = self.ids["s2"]
        val = label.value
        self.change_image_param(val, PARAM_BRIGHTNESS)

    def control_co(self):
        label = self.ids["s3"]
        val = label.value
        self.change_image_param(val, PARAM_CONTRAST)

    def control_sa(self):
        label = self.ids["s4"]
        val = label.value
        self.change_image_param(val, PARAM_SATURATION)

    def control_sh(self):
        label = self.ids["s1"]
        val = label.value
        self.change_image_param(val, PARAM_SHARPNESS)

    def control_microscope_led(self):
        label = self.ids["s5"]
        val = int(label.value)

        try:
            if self.client_socket is not None:
                self.client_socket.sendall('{"attributes":[{"type":"string","name":"command","value":"CHANGE_MICROSCOPE_LED_BRIGHTNESS","led_brightness":"%s"}],"type":"Command"}\n' % val)
                self.parse_answer(self.client_socket.recv(BUFFER))
        except ValueError:
            print "An error occurred while sending the message to the kit"


    def change_image_param(self, val, param):
        def call_server():
            try:
                urllib2.urlopen(self.command_url + "cmd=%s\\" % CAMERA_PARAMETERS[param] + str(val))
            except:
                pass

        command_thread=threading.Thread(target=call_server)
        command_thread.setDaemon(True)
        command_thread.start()

if __name__ == "__main__":

    class MicroApp(App):
        @staticmethod
        def build():
            Builder.load_file('Micro.kv')
            viewer = Micro()
            viewer.start()
            return viewer

    MicroApp().run()
