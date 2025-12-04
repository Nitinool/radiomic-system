# radiomics_tool.py
import os
import logging
import yaml
import numpy as np
from PIL import Image
import SimpleITK as sitk
from radiomics import featureextractor

# 配置日志（消除GLCM冗余提示）
logging.getLogger('radiomics').setLevel(logging.WARNING)


class RadiomicsTool:
    def __init__(self, config_path="settings.yaml"):
        """初始化工具：加载配置文件"""
        self.config_path = config_path
        self.extractor = self._load_config()
        self.target_classes = {'shape2D', 'firstorder', 'glcm', 'glrlm', 'glszm', 'ngtdm', 'gldm'}

    def _load_config(self):
        """加载YAML配置，返回特征提取器"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在：{self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return featureextractor.RadiomicsFeatureExtractor(config)

    def preprocess(self, image_path_or_file, is_mask=False):
        """
        预处理图片：支持路径（本地文件）或UploadFile（API上传）
        返回：ITK图像 + numpy数组
        """
        try:
            # 处理本地文件路径
            if isinstance(image_path_or_file, str):
                img = Image.open(image_path_or_file).convert('L')
            # 处理API上传的文件（UploadFile）
            else:
                img = Image.open(image_path_or_file.file).convert('L')

            img_np = np.array(img, dtype=np.int16)

            # 掩码处理：非0区域转为1（适配label=1）
            if is_mask:
                img_np = np.where(img_np > 0, 1, 0)

            itk_image = sitk.GetImageFromArray(img_np)
            itk_image.SetSpacing((1, 1))  # 2D像素间距
            return itk_image, img_np
        except Exception as e:
            raise ValueError(f"预处理失败：{str(e)}")

    def extract_single(self, image_path_or_file, mask_path_or_file):
        """提取单张影像的特征（支持本地路径或UploadFile）"""
        # 预处理
        image_itk, image_np = self.preprocess(image_path_or_file, is_mask=False)
        mask_itk, mask_np = self.preprocess(mask_path_or_file, is_mask=True)

        # 校验
        if image_np.shape != mask_np.shape:
            raise ValueError(f"尺寸不匹配：影像{image_np.shape} vs 掩码{mask_np.shape}")

        roi_count = np.sum(mask_np > 0)
        if roi_count == 0:
            raise ValueError("掩码中无有效ROI区域")

        # 提取特征
        raw_features = self.extractor.execute(image_itk, mask_itk)

        # 过滤特征
        useful_features = {
            k: v for k, v in raw_features.items()
            if any(cls in k for cls in self.target_classes)
        }

        # 关键修复：将 numpy 类型转为 Python 基本类型
        converted_features = {}
        for key, value in useful_features.items():
            # 处理 numpy 标量（如 numpy.float64）
            if isinstance(value, np.generic):
                converted_features[key] = value.item()  # 转为 Python 原生类型
            # 处理其他可能的非序列化类型（如列表中的 numpy 元素）
            elif isinstance(value, (list, np.ndarray)):
                converted_features[key] = [
                    x.item() if isinstance(x, np.generic) else x
                    for x in value
                ]
            else:
                converted_features[key] = value

        return {
            "image_shape": image_np.shape,
            "roi_pixel_count": roi_count,
            "features": converted_features  # 返回转换后的特征
        }

    def extract_batch(self, image_mask_pairs):
        """
        批量提取特征
        image_mask_pairs：列表，每个元素是元组 (image_path, mask_path)
        返回：列表，每个元素是单张的提取结果
        """
        batch_results = []
        for idx, (image_path, mask_path) in enumerate(image_mask_pairs):
            try:
                result = self.extract_single(image_path, mask_path)
                batch_results.append({
                    "index": idx,
                    "image_path": image_path,
                    "mask_path": mask_path,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                batch_results.append({
                    "index": idx,
                    "image_path": image_path,
                    "mask_path": mask_path,
                    "status": "failed",
                    "error": str(e)
                })
        return batch_results

# 在 radiomics_tool.py 末尾添加
if __name__ == "__main__":
    try:
        tool = RadiomicsTool("pyradiomics_settings.yaml")
        # 用本地文件测试单张提取
        result = tool.extract_single(
            "test_pic/benign (1).png",
            "test_pic/benign (1)_mask.png"
        )
        print(f"测试成功，特征数：{len(result['features'])}")
    except Exception as e:
        print(f"工具测试失败：{str(e)}")