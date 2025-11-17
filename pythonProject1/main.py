from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import numpy as np
from PIL import Image

# 创建 FastAPI 实例
app = FastAPI(title="影像组学 Demo（特征提取占位）")

# 跨域配置（允许前端调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def image_preprocess(image_file):
    """预处理：PNG/JPG 转为 numpy 数组（模拟真实流程）"""
    try:
        # 读取图片并转为灰度图
        img = Image.open(image_file.file).convert('L')
        img_np = np.array(img)
        # 打印图片基本信息（模拟预处理日志）
        print(f"[预处理] 图片尺寸：{img_np.shape}，像素值范围：{img_np.min()}-{img_np.max()}")
        return img_np
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片预处理失败：{str(e)}")


def mock_extract_features(image_np, roi_np):
    """模拟特征提取（用 print 替代真实 PyRadiomics 调用）"""
    # 打印特征提取日志
    print("\n" + "=" * 50)
    print("[模拟特征提取] 开始提取 ROI 区域特征...")
    print(f"[影像信息] 影像尺寸：{image_np.shape}")
    print(f"[ROI 信息] ROI 尺寸：{roi_np.shape}，ROI 像素数：{np.sum(roi_np > 0)}")
    print("\n[模拟提取的核心特征]")
    print("1. 灰度均值：25.68")
    print("2. 纹理熵：3.21")
    print("3. ROI 面积：1256")
    print("4. 灰度标准差：8.92")
    print("5. 纹理对比度：4.57")
    print("=" * 50 + "\n")

    # 返回模拟特征字典（后续可替换为真实提取结果）
    return {
        "灰度均值": 25.68,
        "纹理熵": 3.21,
        "ROI 面积": 1256,
        "灰度标准差": 8.92,
        "纹理对比度": 4.57
    }


# 核心接口：上传影像和掩码，模拟特征提取
@app.post("/mock-extract-radiomics")
async def mock_extract_radiomics(
        image_file: UploadFile = File(..., description="2D影像（PNG/JPG格式）"),
        roi_file: UploadFile = File(..., description="2D掩码（PNG/JPG格式，ROI区域为非0值）")
):
    try:
        # 1. 预处理影像和掩码
        image_np = image_preprocess(image_file)
        roi_np = image_preprocess(roi_file)

        # 2. 校验影像和掩码尺寸一致
        # if image_np.shape != roi_np.shape:
        #     raise HTTPException(status_code=400, detail="影像和掩码尺寸不一致，请检查文件")

        # 3. 模拟特征提取（print 日志+返回模拟结果）
        features = mock_extract_features(image_np, roi_np)

        return {
            "message": "模拟特征提取成功（真实提取函数待替换）",
            "image_info": {
                "尺寸": f"{image_np.shape[0]}×{image_np.shape[1]}",
                "灰度范围": f"{image_np.min()}-{image_np.max()}"
            },
            "roi_info": {
                "尺寸": f"{roi_np.shape[0]}×{roi_np.shape[1]}",
                "有效像素数": int(np.sum(roi_np > 0))
            },
            "extracted_features": features
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败：{str(e)}")


# 健康检查接口
@app.get("/")
async def root():
    return {
        "message": "影像组学 Demo 运行中",
        "tip": "访问 /docs 测试接口，上传 PNG/JPG 格式的影像和掩码"
    }