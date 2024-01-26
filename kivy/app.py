from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
import cv2
import numpy as np


class StarApp(App):
    image = Image(source='../resource/8.jpg')
    star = Image(source='../resource/lens_flare01.png')

    def build(self):
        # 创建主布局
        layout = BoxLayout(orientation='vertical')

        # 创建按钮
        buttonRead = Button(text='Import', size_hint=(None, None))
        buttonRead.bind(on_press=self.show_image_chooser)

        buttonProc = Button(text='Process', size_hint=(None, None))
        buttonProc.bind(on_press=self.process_image)

        layout.add_widget(buttonRead)
        layout.add_widget(buttonProc)

        # 创建图像显示区域
        self.image_widget = Image(size=(640, 480))
        layout.add_widget(self.image_widget)

        return layout

    def show_image_chooser(self, instance):
        file_chooser = FileChooserListView(
            filters=["*.png", "*.jpg", "*.jpeg"])
        file_chooser.bind(on_submit=self.on_file_selected)

        popup = Popup(title='Choose an image file', content=file_chooser,
                      size_hint=(None, None), size=(400, 400))
        popup.open()

    def on_file_selected(self, instance, value,_):
        selected_image_path = value[0]
        processed_image = self.process_image(selected_image_path)
        self.image.source = selected_image_path

    def process_image(self, instance):
        # 读取图像
        image = cv2.imread(self.image.source)

        # 获取图像尺寸
        height, width, _ = image.shape

        # 将图像转换为灰度图像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 设定阈值，进行二值化
        _, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)

        # 进行噪声消除
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # 寻找连通区域
        retval, labels, stats, centroids = cv2.connectedComponentsWithStats(
            opening)

        # 加载星星图像
        star = cv2.imread(self.star.source, -1)

        # 调整星星的大小
        desired_star_size = (64, 64)
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

        # 显示识别结果
        image = cv2.resize(image, (width // 4, height // 4))
        texture = Texture.create(
            size=(image.shape[1], image.shape[0]), colorfmt='bgr')
        texture.blit_buffer(image.tobytes(), colorfmt='bgr', bufferfmt='ubyte')
        self.image_widget.texture = texture


if __name__ == '__main__':
    StarApp().run()
