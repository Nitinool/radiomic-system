# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from radiomics_tool import RadiomicsTool  # 导入工具类

# 初始化FastAPI
app = FastAPI(title="影像组学特征提取 API（支持批量处理）")

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化工具（全局单例）
try:
    radiomics_tool = RadiomicsTool(config_path="pyradiomics_settings.yaml")
    print("工具初始化成功")
except Exception as e:
    print(f"工具初始化失败：{str(e)}")
    radiomics_tool = None


# 1. 单张提取API
@app.post("/extract-single", summary="提取单张影像特征")
async def extract_single(
        image_file: UploadFile = File(..., description="影像文件（PNG/JPG）"),
        mask_file: UploadFile = File(..., description="掩码文件（PNG/JPG）")
):
    if radiomics_tool is None:
        raise HTTPException(status_code=500, detail="工具未初始化")

    try:
        result = radiomics_tool.extract_single(image_file, mask_file)
        return {
            "status": "success",
            "image_info": {
                "尺寸": f"{result['image_shape'][0]}×{result['image_shape'][1]}"
            },
            "roi_info": {
                "有效像素数": int(result['roi_pixel_count'])
            },
            "features": result['features']
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败：{str(e)}")


# 2. 批量提取API（接收本地路径列表，适合后端调用）
@app.post("/extract-batch", summary="批量提取特征（需提供本地文件路径）")
async def extract_batch(
        image_mask_pairs: list  # 格式：[("image1.png", "mask1.png"), ("image2.png", "mask2.png")]
):
    if radiomics_tool is None:
        raise HTTPException(status_code=500, detail="工具未初始化")

    # 校验输入格式
    for pair in image_mask_pairs:
        if len(pair) != 2 or not isinstance(pair[0], str) or not isinstance(pair[1], str):
            raise HTTPException(status_code=400, detail="输入格式错误，应为[(image_path, mask_path), ...]")

    # 执行批量提取
    try:
        batch_results = radiomics_tool.extract_batch(image_mask_pairs)
        return {
            "total": len(batch_results),
            "success_count": sum(1 for r in batch_results if r["status"] == "success"),
            "results": batch_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量处理失败：{str(e)}")


# 3. 健康检查
@app.get("/", summary="服务状态")
async def root():
    return {
        "status": "running",
        "tool_initialized": radiomics_tool is not None,
        "docs": "/docs"
    }


# 4. 批量处理命令行入口（可选，方便本地运行）
if __name__ == "__main__":
    # 示例：本地批量处理
    if radiomics_tool is not None:
        # 待处理的影像-掩码对（本地路径）
        test_pairs = [
            ("test_pic/benign (1).png", "test_pic/benign (1)_mask.png"),
            ("test_pic/benign (2).png", "test_pic/benign (2)_mask.png")
        ]
        # 执行批量提取
        results = radiomics_tool.extract_batch(test_pairs)
        # 打印结果
        for res in results:
            print(f"索引 {res['index']}：{res['status']}")
            if res['status'] == "failed":
                print(f"错误：{res['error']}")