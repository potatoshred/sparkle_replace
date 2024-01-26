import cv2
import numpy as np

# 读取图像
image = cv2.imread('../resource/8.jpg')

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
retval, labels, stats, centroids = cv2.connectedComponentsWithStats(opening)

# 加载星星图像
star = cv2.imread('../resource/lens_flare01.png', -1)

# 调整星星的大小
desired_star_size = (64, 64)
resized_star = cv2.resize(star, desired_star_size[:2], interpolation=cv2.INTER_AREA)

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
            # overlay = cv2.bitwise_and(image[y_start:y_end, x_start:x_end],
            #                           image[y_start:y_end, x_start:x_end],
            #                           mask=resized_star[:star_height, :star_width, 3])
            overlay = resized_star[:star_height, :star_width, :3]
            background = cv2.bitwise_and(image[y_start:y_end, x_start:x_end],
                                         image[y_start:y_end, x_start:x_end],
                                         mask=cv2.bitwise_not(resized_star[:star_height, :star_width, 3]))
            result = cv2.add(background, overlay)
            

            # 将星星特效添加到原图上
            image[y_start:y_end, x_start:x_end] = result


# 显示识别结果
cv2.imshow("Detected Light Points", image[::4, ::4])
cv2.waitKey(0)
cv2.destroyAllWindows()
