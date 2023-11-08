import time
import cv2
import numpy as np
import onnxruntime
import os


class Detector(object):
    def __init__(self):
        ist = time.time()
        device_name = onnxruntime.get_device()
        print('运行设备: {} '.format(device_name))
        # 自动导入权重，没有则报错
        current_py_path = os.path.abspath(__file__)
        relative_path = os.path.normpath(os.path.join(current_py_path, "../../"))
        model_path = os.path.join(relative_path, 'model')
        assert len(os.listdir(model_path)) == 1, "model文件夹下必须存在一个权重文件"
        onnx_path = os.path.join(model_path, os.listdir(model_path)[0])
        print('导入onnx: {}'.format(os.path.basename(onnx_path)))

        # gpu - CUDAExecutionProvider  cpu - CPUExecutionProvider
        if device_name == 'GPU':
            self.session = onnxruntime.InferenceSession(onnx_path, providers=['CUDAExecutionProvider'])
        else:
            self.session = onnxruntime.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])

        self.classes = ['head', 'body']
        self.shape = (416, 416)
        print('初始化检测器完成,耗时: {} s'.format(time.time() - ist))

    def getRoiRect(self, mat, crop_w=416, crop_h=416):
        # 获取图像的宽度和高度
        height, width, _ = mat.shape
        # 计算截取区域的起始坐标
        start_x = int((width - crop_w) / 2)
        start_y = int((height - crop_h) / 2)
        # 截取图像的中心部分
        mat = mat[start_y:start_y + crop_h, start_x:start_x + crop_w]
        return mat

    def preproc(self, img, input_size, swap=(2, 0, 1)):
        # # todo yolox 预处理
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
        padded_img = padded_img.transpose((2, 0, 1))
        padded_img = np.ascontiguousarray(padded_img, dtype=np.float32)
        return padded_img, r

        # # todo trmdet 预处理
        # r = min(input_size[0] / img.shape[0], input_size[1] / img.shape[1])
        # img = cv2.resize(
        #     img,
        #     (int(img.shape[1] * r), int(img.shape[0] * r)),
        #     interpolation=cv2.INTER_LINEAR,
        # ).astype(np.uint8)
        # mean = np.array([103.53,
        #                  116.28,
        #                  123.675])
        # std = np.array([57.375,
        #                 57.12,
        #                 58.395])
        # img = (img - mean[None,None,:])/std[None,None,:]
        # # img = np.expand_dims(np.transpose(img, (2,0,1)),axis=0).astype(np.float32)  # H,W,3 -> 1,3,H,W
        # img = img.transpose(swap)
        # img = np.ascontiguousarray(img, dtype=np.float32)
        # return img,r
        # # # todo yolox 预处理
        # if len(img.shape) == 3:
        #     padded_img = np.ones((input_size[0], input_size[1], 3), dtype=np.uint8) * 114
        # else:
        #     padded_img = np.ones(input_size, dtype=np.uint8) * 114
        #
        # r = min(input_size[0] / img.shape[0], input_size[1] / img.shape[1])
        # resized_img = cv2.resize(
        #     img,
        #     (int(img.shape[1] * r), int(img.shape[0] * r)),
        #     interpolation=cv2.INTER_LINEAR,
        # ).astype(np.uint8)
        # padded_img[: int(img.shape[0] * r), : int(img.shape[1] * r)] = resized_img
        #
        # padded_img = padded_img.transpose(swap)
        # padded_img = np.ascontiguousarray(padded_img, dtype=np.float32)
        # return padded_img, r


        # # todo trmdet 预处理
        # r = min(input_size[0] / img.shape[0], input_size[1] / img.shape[1])
        # img = cv2.resize(
        #     img,
        #     (int(img.shape[1] * r), int(img.shape[0] * r)),
        #     interpolation=cv2.INTER_LINEAR,
        # ).astype(np.uint8)
        # mean = np.array([103.53,
        #                  116.28,
        #                  123.675])
        # std = np.array([57.375,
        #                 57.12,
        #                 58.395])
        # img = (img - mean[None,None,:])/std[None,None,:]
        # # img = np.expand_dims(np.transpose(img, (2,0,1)),axis=0).astype(np.float32)  # H,W,3 -> 1,3,H,W
        # img = img.transpose(swap)
        # img = np.ascontiguousarray(img, dtype=np.float32)
        # return img,r

    def data_process(self, output):
        scores = output[0][..., -1].flatten()  # 获取分数列
        boxes = output[0][..., :4][0]  # 获取框的坐标
        labels = output[1].flatten()  # 获取标签

        m_out = np.column_stack((boxes, scores, labels))  # 合并数组列

        return m_out.tolist()

    def nms(self, dets, thresh):
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

    def filter_box(self, org_box, conf_thres, iou_thres):  # 过滤掉无用的框
        # -------------------------------------------------------
        #   删除为1的维度
        #	删除置信度小于conf_thres的BOX
        # -------------------------------------------------------
        org_box = np.squeeze(org_box)  # 删除数组形状中单维度条目(shape中为1的维度)
        # (25200, 9)
        # […,4]：代表了取最里边一层的所有第4号元素，…代表了对:,:,:,等所有的的省略。此处生成：25200个第四号元素组成的数组
        conf = org_box[..., 4] > conf_thres  # 0 1 2 3 4 4是置信度，只要置信度 > conf_thres 的
        box = org_box[conf == True]  # 根据objectness score生成(n, 9)，只留下符合要求的框
        # print('box:符合要求的框')
        # print(box.shape)

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
            curr_out_box = self.nms(curr_cls_box, iou_thres)  # 获得nms后，剩下的类别在curr_cls_box中的下标

            for k in curr_out_box:
                output.append(curr_cls_box[k])
        output = np.array(output)
        return output

    def filter_max_area_box(self, img, boxs, ratio=8):
        """
        只有body大于面积阈值
        :param img:
        :param boxs:
        :param ratio:
        :return:
        """
        h, w = img.shape[:2]
        total_area = h * w
        # print(total_area)
        res = []
        for i in boxs:
            x1, y1, x2, y2 = i[:4]
            width = x2 - x1
            height = y2 - y1
            area = width * height
            if area <= total_area / ratio:
                res.append(list(i))
        return res

    def draw(self, image, best_output):
        best_output = np.array(best_output)
        box = best_output[:4].astype(np.int32)
        # score = best_output[4]
        label = best_output[5].astype(np.int32)
        top, left, right, bottom = box
        if label == 0:
            color = (0, 0, 255)
        elif label == 1:
            color = (0, 255, 0)
        else:
            raise Exception('bug: 未知分类属性...')
        cv2.rectangle(image, (top, left), (right, bottom), color, 1)
        # cv2.putText(image, "{}".format(score), (top, left), 1, 0.5, (255, 0, 0), 1, 1)
        return image

    def get_max_score_box(self, output):
        scores = np.asarray(output)[..., 4]
        max_idx = np.argmax(scores)
        return output[max_idx]

    def get_max_area_box(self, output):
        area_dict = {}
        for i in range(len(output)):
            x1, y1, x2, y2 = output[i][:4]
            width = x2 - x1
            height = y2 - y1
            area = width * height
            area_dict[area] = output[i]
        # 获取最大的键
        max_key = max(area_dict.keys())
        # 获取最大键对应的值
        value = area_dict[max_key]
        return value

    def detect2(self, mat, is_det_c, score_thr=0.6):
        """
        不输出图像，仅仅检测后的坐标
        :param mat:
        :param score_thr:
        :return:
        """
        pre_mat, ratio = self.preproc(mat, self.shape)
        ort_inputs = {self.session.get_inputs()[0].name: pre_mat[None, :, :, :]}
        output = self.session.run(None, ort_inputs)
        data = self.data_process(output)  # x1,y1,x2,y2,score,label
        # 分为c/t两个阵营，c为警察（0）  t为匪徒（1）
        if is_det_c:
            m_label = 0
        else:
            m_label = 1
        filtered_data = [item for item in data if item[4] > score_thr and int(item[5]) == m_label]
        if len(filtered_data) == 0:
            return [],mat
        filtered_data.sort(key=lambda item: (item[2] - item[0]) * (item[3] - item[1]), reverse=True)
        max_area_position = filtered_data[0][:4]

        roi_mat_draw = self.draw(mat, filtered_data[0])

        return max_area_position,roi_mat_draw

    def detect(self, mat, conf_thr=0.6, iou_thr=0.5):
        st = time.time()
        copy_mat = mat.copy()
        roi_mat_origin = self.getRoiRect(copy_mat)

        pre_mat, ratio = self.preproc(roi_mat_origin, self.shape)

        ort_inputs = {self.session.get_inputs()[0].name: pre_mat[None, :, :, :]}
        output = self.session.run(None, ort_inputs)

        output_datas = self.data_process(output)

        outbox = self.filter_box(output_datas, conf_thr,
                                 iou_thr)  # 最终剩下的Anchors：0 1 2 3 4 5 分别是 x1 y1 x2 y2 score class

        # todo 同一场景，只输出一个
        outbox2 = self.filter_max_area_box(roi_mat_origin, outbox)

        print('detect once cost: {} s'.format(time.time() - st))
        if (len(outbox2) == 0):
            return roi_mat_origin, []

        # todo 面积最大那个roi  基本就是body啦。。。
        best_output = self.get_max_area_box(outbox2)

        roi_mat_draw = self.draw(roi_mat_origin, best_output)
        return roi_mat_draw, best_output[:4]


if __name__ == '__main__':
    det = Detector()
    cv2.namedWindow('test', cv2.WINDOW_NORMAL)

    # # image test
    # path = '../datas/images'
    # for i in os.listdir(path):
    #     img_path = os.path.join(path, i)
    #     img = cv2.imread(img_path)
    #     visual_img, res = det.detect(img)
    #     print(res)
    #     cv2.imshow('test', visual_img)
    #     cv2.waitKey(0)

    # video test
    cap = cv2.VideoCapture('../datas/videos/2023-07-17 23-23-32.mp4')
    while True:
        f, frame = cap.read()
        if not f:
            print('video end...')
            break
        max_area_position,roi_mat_draw = det.detect2(frame,is_det_c=True)
        cv2.imshow('test', roi_mat_draw)
        key = cv2.waitKey(1)

    cv2.destroyAllWindows()
