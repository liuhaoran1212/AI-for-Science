import queue
import threading
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.streamers import BaseStreamer


# 加载模型和分词器
model_name = "/data1/songxiaoyong/lhr/hfmodels/best_0912_lr_1.25e-4_epoch_12_140"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")


class CustomStreamer(BaseStreamer):
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.generated_tokens = []

    def put(self, tokens):
        # 解码当前 token 并输出
        for token in tokens:
            token_text = self.tokenizer.decode(token, skip_special_tokens=True)
            self.generated_tokens.append(token_text)
            return self.generated_tokens
            #print(token_text, end="", flush=True)  # 流式输出到控制台

    def end(self):
        # 生成完成后的处理
        return "\n生成完成"
       # print("\n生成完成。")


# 使用自定义流式处理器
custom_streamer = CustomStreamer(tokenizer)


def generate_response(prompt, max_length=1000):
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    model.generate(
            inputs["input_ids"],
            max_length=max_length,
            streamer=custom_streamer,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7
            )

# 测试
prompt_template = r"""
Below is an operations research question. Build a mathematical model and corresponding python code using `coptpy` that appropriately addresses the question.

# Question:
{Question}

# Response:
"""

question = ""
prompt = prompt_template.format(Question=question)
