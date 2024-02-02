from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

import cv2
import numpy as np


class StarApp(App):
    image = Image(source='../resource/9.jpg')
    star = Image(source='../resource/lens_flare01.png')

    def build(self):
        # 创建主布局
        layout = BoxLayout(orientation='vertical')

        # 创建按钮
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, .1))

        buttonRead = Button(text='Import', size_hint=(None, None))
        buttonRead.bind(on_press=self.show_image_chooser)

        buttonProc = Button(text='Process', size_hint=(None, None))
        buttonProc.bind(on_press=self.process_image)

        buttonWrite = Button(text='Save', size_hint=(None, None))
        buttonWrite.bind(on_press=self.save_image)

        button_layout.add_widget(buttonRead)
        button_layout.add_widget(buttonProc)
        button_layout.add_widget(buttonWrite)

        layout.add_widget(button_layout)

        # 创建大小滑动条
        self.slider = Slider(min=0, max=3, value=1, orientation='horizontal')
        # 创建标签用于显示滑动条的值
        label_size = Label(text=f"Star Size: {self.slider.value}")
        # 绑定事件处理程序以更新标签的文本
        self.slider.bind(value=lambda instance, value: setattr(label_size, 'text', f"Star Size: {round(value, 2)}"))
        # 添加到窗口
        slider_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, .1))
        slider_layout.add_widget(label_size)
        slider_layout.add_widget(self.slider)
        layout.add_widget(slider_layout)

        # 创建阈值滑动条
        self.slider_thred = Slider(min=0, max=255, value=220, orientation='horizontal')
        # 创建标签用于显示滑动条的值
        label_thred = Label(text=f"Thredshold: {self.slider_thred.value}")
        # 绑定事件处理程序以更新标签的文本
        self.slider_thred.bind(value=lambda instance, value: setattr(label_thred, 'text', f"Thredshold: {int(value)}"))
        # 添加到窗口
        slider_layout_thred = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, .1))
        slider_layout_thred.add_widget(label_thred)
        slider_layout_thred.add_widget(self.slider_thred)
        layout.add_widget(slider_layout_thred)

        # 创建图像显示区域
        image_layout = BoxLayout(orientation='horizontal', spacing=10)
        self.image_widget_raw = Image(size=(640, 480),allow_stretch=True, keep_ratio=True)
        self.image_widget = Image(size=(640, 480),allow_stretch=True, keep_ratio=True)

        image_layout.add_widget(self.image_widget_raw)
        image_layout.add_widget(self.image_widget)
        layout.add_widget(image_layout)
        
        return layout

    def show_image_chooser(self, instance):
        file_chooser = FileChooserListView(
            filters=["*.png", "*.jpg", "*.jpeg"],
            path="../resource/")
        file_chooser.bind(on_submit=self.on_file_selected)

        self.popup = Popup(title='Choose an image file', content=file_chooser,
                      size_hint=(None, None), size=(400, 800))
        self.popup.open()

    def show_save_notification(self, instance, outname):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=''))

        popup = Popup(
            title=f'File Saved at {outname}',
            content=content,
            size_hint=(None, None),
            size=(300, 100)
        )
        popup.open()

    def save_image(self, instance):
        tmp = self.image.source.rsplit(".")
        out_name = tmp[0]+"_proc."+tmp[1]
        # print(tmp, out_name)
        cv2.imwrite(out_name, self.cvimg)
        self.show_save_notification(instance, out_name)

    def on_file_selected(self, instance, value,_):
        selected_image_path = value[0]
        # processed_image = self.process_image(selected_image_path)
        self.image.source = selected_image_path
        # 在选择文件后关闭Popup
        self.popup.dismiss()
        self.show_raw()

    def show_raw(self):
        # 读取图像
        print("Reading:",self.image.source)
        image = cv2.imread(self.image.source)

        # 获取图像尺寸
        height, width, _ = image.shape

        # 显示原图
        image_raw = cv2.resize(image, (width // 4, height // 4))[::-1]
        texture = Texture.create(
            size=(image_raw.shape[1], image_raw.shape[0]), colorfmt='bgr')
        texture.blit_buffer(image_raw.tobytes(), colorfmt='bgr', bufferfmt='ubyte')
        self.image_widget_raw.texture = texture

    def process_image(self, instance):
        print("Processing")
        # 读取图像
        image = cv2.imread(self.image.source)

        # 获取图像尺寸
        height, width, _ = image.shape

        # 将图像转换为灰度图像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 设定阈值，进行二值化
        _, thresh = cv2.threshold(gray, int(self.slider_thred.value), 255, cv2.THRESH_BINARY)

        # 进行噪声消除
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # 寻找连通区域
        retval, labels, stats, centroids = cv2.connectedComponentsWithStats(opening)

        # 加载星星图像
        star = cv2.imread(self.star.source, -1)

        # 调整星星的大小
        desired_star_size = (int(64*self.slider.value), int(64*self.slider.value))
        resized_star = cv2.resize(
            star, desired_star_size[:2], interpolation=cv2.INTER_AREA)

        # 过滤并绘制发光点
        for i, stat in enumerate(stats):
            # 过滤条件可以根据需求调整
            if stat[cv2.CC_STAT_AREA] > 32 and stat[cv2.CC_STAT_AREA] < 800:
                # 在发光点处绘制星星
                x = int(centroids[i][0])
                y = int(centroids[i][1])

                # 计算星星的位置
                x_start = max(0, x - desired_star_size[1] // 2)
                x_end = min(width, x + desired_star_size[1] // 2)
                y_start = max(0, y - desired_star_size[0] // 2)
                y_end = min(height, y + desired_star_size[0] // 2)

                # 处理边界情况
                star_width = x_end - x_start
                star_height = y_end - y_start

                if star_width > 0 and star_height > 0:
                    # 将星星图像和原图像叠加在一起
                    overlay = resized_star[:star_height, :star_width, :3]
                    background = cv2.bitwise_and(image[y_start:y_end, x_start:x_end],
                                                 image[y_start:y_end,
                                                       x_start:x_end],
                                                 mask=cv2.bitwise_not(resized_star[:star_height, :star_width, 3]))
                    result = cv2.add(background, overlay)

                    # 将星星特效添加到原图上
                    image[y_start:y_end, x_start:x_end] = result
        print("Process Complete")

        self.cvimg = image
        # 显示识别结果
        image = cv2.resize(image, (width // 4, height // 4))[::-1]
        texture = Texture.create(
            size=(image.shape[1], image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(image.tobytes(), colorfmt='bgr', bufferfmt='ubyte')
        self.image_widget.texture = texture


if __name__ == '__main__':
    StarApp().run()
