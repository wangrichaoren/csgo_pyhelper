import time

import cv2
import numpy as np
import onnxruntime

CLASSES = ['head', 'body']


def preproc(img, input_size, swap=(2, 0, 1)):
    if len(img.shape) == 3:
        padded_img = np.ones((input_size[0], input_size[1], 3), dtype=np.uint8) * 114
    else:
        padded_img = np.ones(input_size, dtype=np.uint8) * 114

    r = min(input_size[0] / img.shape[0], input_size[1] / img.shape[1])
    resized_img = cv2.resize(
        img,
        (int(img.shape[1] * r), int(img.shape[0] * r)),
        interpolation=cv2.INTER_LINEAR,
    ).astype(np.uint8)
    padded_img[: int(img.shape[0] * r), : int(img.shape[1] * r)] = resized_img

    padded_img = padded_img.transpose(swap)
    padded_img = np.ascontiguousarray(padded_img, dtype=np.float32)
    return padded_img, r


def data_process(output):
    m_out = []
    scores = output[0][..., -1].flatten()  # 获取分数列
    boxes = output[0][..., :4][0]  # 获取框的坐标
    labels = output[1].flatten()  # 获取标签
    for i in range(len(scores)):
        cur_label = labels[i]
        cur_score = scores[i]
        cur_box = boxes[i]
        new_array = np.concatenate((cur_box, np.array([cur_score, cur_label])))
        m_out.append(new_array)
    return m_out


def nms(dets, thresh):
    # dets:x1 y1 x2 y2 score class
    # x[:,n]就是取所有集合的第n个数据
    x1 = dets[:, 0]
    y1 = dets[:, 1]
    x2 = dets[:, 2]
    y2 = dets[:, 3]
    # -------------------------------------------------------
    #   计算框的面积
    #	置信度从大到小排序
    # -------------------------------------------------------
    areas = (y2 - y1 + 1) * (x2 - x1 + 1)
    scores = dets[:, 4]
    # print(scores)
    keep = []
    index = scores.argsort()[::-1]  # np.argsort()对某维度从小到大排序
    # [::-1] 从最后一个元素到第一个元素复制一遍。倒序从而从大到小排序

    while index.size > 0:
        i = index[0]
        keep.append(i)
        # -------------------------------------------------------
        #   计算相交面积
        #	1.相交
        #	2.不相交
        # -------------------------------------------------------
        x11 = np.maximum(x1[i], x1[index[1:]])
        y11 = np.maximum(y1[i], y1[index[1:]])
        x22 = np.minimum(x2[i], x2[index[1:]])
        y22 = np.minimum(y2[i], y2[index[1:]])

        w = np.maximum(0, x22 - x11 + 1)
        h = np.maximum(0, y22 - y11 + 1)

        overlaps = w * h
        # -------------------------------------------------------
        #   计算该框与其它框的IOU，去除掉重复的框，即IOU值大的框
        #	IOU小于thresh的框保留下来
        # -------------------------------------------------------
        ious = overlaps / (areas[i] + areas[index[1:]] - overlaps)
        idx = np.where(ious <= thresh)[0]
        index = index[idx + 1]
    return keep


def filter_box(org_box, conf_thres, iou_thres):  # 过滤掉无用的框
    # -------------------------------------------------------
    #   删除为1的维度
    #	删除置信度小于conf_thres的BOX
    # -------------------------------------------------------
    org_box = np.squeeze(org_box)  # 删除数组形状中单维度条目(shape中为1的维度)
    # (25200, 9)
    # […,4]：代表了取最里边一层的所有第4号元素，…代表了对:,:,:,等所有的的省略。此处生成：25200个第四号元素组成的数组
    conf = org_box[..., 4] > conf_thres  # 0 1 2 3 4 4是置信度，只要置信度 > conf_thres 的
    box = org_box[conf == True]  # 根据objectness score生成(n, 9)，只留下符合要求的框
    print('box:符合要求的框')
    print(box.shape)

    # -------------------------------------------------------
    #   通过argmax获取置信度最大的类别
    # -------------------------------------------------------
    cls_cinf = box[..., 5:]  # 左闭右开（5 6 7 8），就只剩下了每个grid cell中各类别的概率
    cls = []
    for i in range(len(cls_cinf)):
        # cls.append(int(np.argmax(cls_cinf[i])))  # 剩下的objecctness score比较大的grid cell，分别对应的预测类别列表
        cls.append(int(cls_cinf[i]))  # 剩下的objecctness score比较大的grid cell，分别对应的预测类别列表
    all_cls = list(set(cls))  # 去重，找出图中都有哪些类别
    # set() 函数创建一个无序不重复元素集，可进行关系测试，删除重复数据，还可以计算交集、差集、并集等。
    # -------------------------------------------------------
    #   分别对每个类别进行过滤
    #   1.将第6列元素替换为类别下标
    #	2.xywh2xyxy 坐标转换
    #	3.经过非极大抑制后输出的BOX下标
    #	4.利用下标取出非极大抑制后的BOX
    # -------------------------------------------------------
    output = []
    for i in range(len(all_cls)):
        curr_cls = all_cls[i]
        curr_cls_box = []
        curr_out_box = []

        for j in range(len(cls)):
            if cls[j] == curr_cls:
                box[j][5] = curr_cls
                curr_cls_box.append(box[j][:6])  # 左闭右开，0 1 2 3 4 5

        curr_cls_box = np.array(curr_cls_box)  # 0 1 2 3 4 5 分别是 x y w h score class
        # curr_cls_box_old = np.copy(curr_cls_box)
        # curr_cls_box = xywh2xyxy(curr_cls_box)  # 0 1 2 3 4 5 分别是 x1 y1 x2 y2 score class
        curr_out_box = nms(curr_cls_box, iou_thres)  # 获得nms后，剩下的类别在curr_cls_box中的下标

        for k in curr_out_box:
            output.append(curr_cls_box[k])
    output = np.array(output)
    return output


def draw(image, box_data):
    # -------------------------------------------------------
    #	取整，方便画框
    # -------------------------------------------------------

    boxes = box_data[..., :4].astype(np.int32)  # x1 x2 y1 y2
    scores = box_data[..., 4]
    classes = box_data[..., 5].astype(np.int32)
    for box, score, cl in zip(boxes, scores, classes):
        top, left, right, bottom = box
        if cl == 0:
            color = (0, 0, 255)
        elif cl == 1:
            color = (0, 255, 0)
        else:
            raise Exception('bug: 未知分类属性...')

        print('class: {}, score: {}'.format(CLASSES[cl], score))
        print('box coordinate left,top,right,down: [{}, {}, {}, {}]'.format(top, left, right, bottom))
        cv2.rectangle(image, (top, left), (right, bottom), color, 1)
        # cv2.putText(image, '{0} {1:.2f}'.format(CLASSES[cl], score),
        #             (top, left),
        #             1,
        #             1, (255, 0, 0), 1)
    return image


def filter_max_area_box(img, boxs, ratio=8):
    """
    只有body大于面积阈值
    :param img:
    :param boxs:
    :param ratio:
    :return:
    """
    h, w = img.shape[:2]
    total_area = h * w
    res = []
    for i in boxs:
        x1, y1, x2, y2 = i[:4]
        width = x2 - x1
        height = y2 - y1
        area = width * height
        if area <= total_area / ratio:
            res.append(list(i))
    return res


if __name__ == '__main__':
    input_shape = (416, 416)
    imgs_path = '/home/wrc/Desktop/mmdetection/test_datas/images/'
    session = onnxruntime.InferenceSession('/home/wrc/Desktop/mmdeploy/onnx-out/yolox-s-2023-7-18.onnx')
    cv2.namedWindow('test', cv2.WINDOW_NORMAL)

    cap = cv2.VideoCapture('/home/wrc/Desktop/mmdetection/test_datas/2023-07-17 23-23-32.mp4')

    while True:
        f, frame = cap.read()
        if not f:
            print('video end...')
            break
        origin_img = frame.copy()
        det_st = time.time()
        # 获取图像的宽度和高度
        height, width, _ = origin_img.shape
        # 计算截取区域的起始坐标
        start_x = int((width - 416) / 2)
        start_y = int((height - 416) / 2)
        # 截取图像的中心部分
        origin_img = origin_img[start_y:start_y + 416, start_x:start_x + 416]

        img, ratio = preproc(origin_img, input_shape)
        ort_inputs = {session.get_inputs()[0].name: img[None, :, :, :]}
        output = session.run(None, ort_inputs)

        output_datas = data_process(output)  # [[x1,y1,x2,y2,score,class]...]

        outbox = filter_box(output_datas, 0.6, 0.5)  # 最终剩下的Anchors：0 1 2 3 4 5 分别是 x1 y1 x2 y2 score class
        print('=========================')
        print(outbox)
        print('=========================')
        outbox = filter_max_area_box(origin_img, outbox)
        print('---------------------')
        print(outbox)
        print('---------------------')
        print('det cost time: {}'.format(time.time() - det_st))
        if (len(outbox) == 0):
            print('scence empty...')
            cv2.imshow('test', origin_img)
            key = cv2.waitKey(1)
            continue
        # draw
        origin_img = draw(origin_img, np.array(outbox))

        cv2.imshow('test', origin_img)
        key = cv2.waitKey(1)

    cv2.destroyAllWindows()
