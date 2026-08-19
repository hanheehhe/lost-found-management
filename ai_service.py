"""
AI 智能匹配服务
================

集成阿里云百炼 DashScope 两个模型，实现失物招领的智能查找：

1. 视觉理解模型 (qwen-vl-plus)
   输入图片，输出结构化标签：类别、颜色、材质、品牌、显著特征

2. 多模态 Embedding (multimodal-embedding-v1)
   融合图片 + 文字，生成 1024 维匹配向量

匹配逻辑：发布物品时生成向量入库，查找时生成查询向量，
与库中「相反状态」的物品做余弦相似度排序，返回 Top-K。

降级策略：未配置 DASHSCOPE_API_KEY 或调用失败时，AI 功能自动跳过，
不影响物品的正常发布与浏览。
"""

import os
import json
import math
from pathlib import Path

# 加载 .env 环境变量（若尚未被 app.py 加载）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# DashScope SDK 为可选依赖，未安装时降级
try:
    import dashscope
    from dashscope import MultiModalConversation, MultiModalEmbedding
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False


# 模型名称
VISION_MODEL = "qwen-vl-plus"
EMBEDDING_MODEL = "multimodal-embedding-v1"


def _is_enabled():
    """判断 AI 功能是否可用（SDK 已装 且 已配置 API Key）。"""
    if not DASHSCOPE_AVAILABLE:
        return False
    key = os.getenv("DASHSCOPE_API_KEY", "")
    return bool(key.strip())


def _set_api_key():
    if DASHSCOPE_AVAILABLE:
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY", "")


def _file_uri(path):
    """把本地图片路径转成绝对 file:// URI，供 DashScope 多模态接口读取。"""
    return Path(path).resolve().as_uri()


# ---------------------------------------------------------------------------
# 模型一：视觉理解
# ---------------------------------------------------------------------------

def analyze_image(image_path):
    """调用视觉理解模型，返回结构化标签字典。

    返回: {"category": str, "color": str, "material": str,
           "brand": str, "features": str}
    失败或未配置时返回 None。
    """
    if not _is_enabled():
        return None

    _set_api_key()

    prompt = (
        "请分析这张图片中的物品，只输出一个 JSON 对象，不要输出任何其他文字。"
        "JSON 必须包含以下字段（全部使用中文）：\n"
        '{"category": "物品类别，从[证件卡类,电子产品,书籍资料,衣物饰品,生活用品,其他]中选一个",'
        '"color": "主要颜色",'
        '"material": "材质",'
        '"brand": "品牌，无法识别则填未知",'
        '"features": "一句话显著特征描述，便于失物匹配"}'
    )

    try:
        response = MultiModalConversation.call(
            model=VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"image": _file_uri(image_path)},
                    {"text": prompt},
                ],
            }],
        )
        if response.status_code != 200:
            print(f"[AI] 视觉理解失败: {response.code} {response.message}")
            return None

        text = response.output.choices[0].message.content[0]["text"]
        return _parse_json(text)
    except Exception as e:
        print(f"[AI] 视觉理解异常: {e}")
        return None


def _parse_json(text):
    """从模型输出中稳健地提取 JSON 对象。"""
    if not text:
        return None
    text = text.strip()
    # 去掉可能的 markdown 代码块围栏
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        data = json.loads(text[start:end + 1])
        return {
            "category": str(data.get("category", "")).strip(),
            "color": str(data.get("color", "")).strip(),
            "material": str(data.get("material", "")).strip(),
            "brand": str(data.get("brand", "")).strip(),
            "features": str(data.get("features", "")).strip(),
        }
    except (json.JSONDecodeError, AttributeError):
        return None


# ---------------------------------------------------------------------------
# 模型二：多模态 Embedding
# ---------------------------------------------------------------------------

def _build_text_blob(name, description, tags):
    """把物品的文字信息拼成一段描述，用于 embedding 融合。"""
    parts = []
    if name:
        parts.append(f"物品名称:{name}")
    if tags:
        tag_text = " ".join(
            f"{k}:{v}" for k, v in tags.items() if v
        )
        parts.append(tag_text)
    if description:
        parts.append(f"描述:{description}")
    return "。".join(parts)


def generate_embedding(text=None, image_path=None):
    """融合文字与图片生成 1024 维向量。

    返回: list[float]，失败或未配置时返回 None。
    """
    if not _is_enabled():
        return None

    _set_api_key()

    inputs = []
    if image_path and os.path.exists(image_path):
        inputs.append({"image": _file_uri(image_path)})
    if text:
        inputs.append({"text": text})

    if not inputs:
        return None

    try:
        result = MultiModalEmbedding.call(
            model=EMBEDDING_MODEL,
            input=inputs,
        )
        if result.status_code != 200:
            print(f"[AI] embedding 失败: {result.code} {result.message}")
            return None
        return result.output["embeddings"][0]["embedding"]
    except Exception as e:
        print(f"[AI] embedding 异常: {e}")
        return None


# ---------------------------------------------------------------------------
# 匹配
# ---------------------------------------------------------------------------

def cosine_similarity(a, b):
    """计算两个向量的余弦相似度。"""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def match_items(query_vector, candidates, top_k=5):
    """在候选物品中按余弦相似度返回 Top-K。

    candidates: [(item, vector)] 列表
    返回: [(item, similarity)] 按相似度降序，仅保留相似度 > 0 的结果。
    """
    scored = []
    for item, vector in candidates:
        if vector is None:
            continue
        sim = cosine_similarity(query_vector, vector)
        if sim > 0:
            scored.append((item, sim))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
