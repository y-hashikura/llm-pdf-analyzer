import os
import base64
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict

# OpenAI APIキーを環境変数から取得
api_key = ""

# ステートの型定義
class MyState(TypedDict, total=False):
    image_bytes: bytes
    extracted_text: str
    title_type: str
    result: str

# 画像→テキスト抽出ノード
def extract_text_node(state):
    image_bytes = state["image_bytes"]
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=api_key)
    response = llm.invoke([
        {"role": "system", "content": "画像に写っている文書を読み取り、タイトルと要点をテキストで出力してください"},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        }
    ])
    return {"extracted_text": response.content}

def classify_title_node(state):
    text = state["extracted_text"]
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=api_key)
    prompt = (
        "次のテキストのタイトルが『納品書』か『請求書』かを判定してください。"
        "納品書なら『納品書』、請求書なら『請求書』だけを出力してください。\n"
        f"テキスト: {text}"
    )
    response = llm.invoke(prompt)
    return {"title_type": response.content.strip()}


def process_delivery_note_node(state):
    return {"result": f"納品書として処理しました: {state['extracted_text']}"}


def process_invoice_node(state):
    return {"result": f"請求書として処理しました: {state['extracted_text']}"}

# LangGraphグラフ構築
graph = StateGraph(state_schema=MyState)
graph.add_node("extract_text", extract_text_node)
graph.add_node("classify_title", classify_title_node)
graph.add_node("delivery_note", process_delivery_note_node)
graph.add_node("invoice", process_invoice_node)
graph.set_entry_point("extract_text")
graph.add_edge("extract_text", "classify_title")
graph.add_conditional_edges(
    "classify_title",
    lambda s: s["title_type"],
    {
        "納品書": "delivery_note",
        "請求書": "invoice"
    }
)
graph.add_edge("delivery_note", END)
graph.add_edge("invoice", END)

# グラフをビルド
built_graph = graph.compile()

def analyze_image_with_langgraph(image_bytes: bytes) -> dict:
    result = built_graph.invoke({"image_bytes": image_bytes})
    # image_bytesを含まないdictを返す
    result.pop("image_bytes", None)
    return result 