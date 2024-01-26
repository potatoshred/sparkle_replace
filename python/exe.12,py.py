import cv2
import numpy as np

# 读取图像
image = cv2.imread('C:/Users/86189/PycharmProjects/untitled/img/3.png')

# 获取图像尺寸
height, width, _ = image.shape

# 创建窗口并调整大小
cv2.namedWindow("Detected Light Points", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Detected Light Points", width, height)

# 将图像转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 设定阈值，进行二值化
_, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

# 进行噪声消除
kernel = np.ones((3, 3), np.uint8)
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

# 寻找连通区域
_, labels, stats, _ = cv2.connectedComponentsWithStats(opening)

# 加载星星图像
star = cv2.imread('C:/Users/86189/PycharmProjects/untitled/img/lens_flare01.png', -1)

# 过滤并绘制发光点
for i, stat in enumerate(stats):
    # 过滤条件可以根据需求调整
    if stat[cv2.CC_STAT_AREA] > 100 and stat[cv2.CC_STAT_AREA] < 1000:
        # 在发光点处绘制星星
        x = int(stat[cv2.CC_STAT_LEFT] + stat[cv2.CC_STAT_WIDTH] / 2)
        y = int(stat[cv2.CC_STAT_TOP] + stat[cv2.CC_STAT_HEIGHT] / 2)

        # 获取星星图像的透明通道
        star_alpha = star[:, :, 3]

        # 根据发光点的宽度调整星星图像的大小
        star_resized = cv2.resize(star_alpha, (stat[cv2.CC_STAT_WIDTH], stat[cv2.CC_STAT_HEIGHT]))

        # 将星星图像和原图像叠加在一起
        overlay = cv2.bitwise_and(image[y:y + stat[cv2.CC_STAT_HEIGHT], x:x + stat[cv2.CC_STAT_WIDTH]], image[y:y + stat[cv2.CC_STAT_HEIGHT], x:x + stat[cv2.CC_STAT_WIDTH]], mask=star_resized)
        background = cv2.bitwise_and(image[y:y + stat[cv2.CC_STAT_HEIGHT], x:x + stat[cv2.CC_STAT_WIDTH]], image[y:y + stat[cv2.CC_STAT_HEIGHT], x:x + stat[cv2.CC_STAT_WIDTH]], mask=cv2.bitwise_not(star_resized))
        result = cv2.add(background, overlay)

        # 将星星特效添加到原图上
        image[y:y + stat[cv2.CC_STAT_HEIGHT], x:x + stat[cv2.CC_STAT_WIDTH]] = result

# 显示识别结果
cv2.imshow("Detected Light Points", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
