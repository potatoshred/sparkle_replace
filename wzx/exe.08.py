import cv2
import numpy as np

# 读取图像
image = cv2.imread('./resource/9.jpg')

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
star = cv2.imread('C:/Users/86189/PycharmProjects/untitled/img/R-C.png', -1)

# 过滤并绘制发光点
for i, stat in enumerate(stats):
    # 过滤条件可以根据需求调整
    if stat[cv2.CC_STAT_AREA] > 100 and stat[cv2.CC_STAT_AREA] < 1000:
        # 在发光点处绘制星星
        x = int(stat[cv2.CC_STAT_LEFT] + stat[cv2.CC_STAT_WIDTH]/2)
        y = int(stat[cv2.CC_STAT_TOP] + stat[cv2.CC_STAT_HEIGHT]/2)
        image[y:y+star.shape[0], x:x+star.shape[1]] = star

# 显示识别结果
cv2.imshow("Detected Light Points", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
