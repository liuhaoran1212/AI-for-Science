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
        self.queue = queue.Queue()
        self.stop_signal = object()
        self._is_streaming = True
        #self.generated_tokens = []

    def put(self, tokens):
        # 解码当前 token 并输出
        if not self._is_streaming:
            return

        for token in tokens.cpu().numpy():
            token_text = self.tokenizer.decode(token, skip_special_tokens=True)
            self.queue.put(token_text)
            #self.generated_tokens.append(token_text)
            #print(token_text, end="", flush=True)  # 流式输出到控制台

    def end(self):
        # 生成完成后的处理
        self._is_streaming = False
        self.queue.put(self.stop_signal)
        #print("\n生成完成。")

    def __iter__(self):
        while self._is_streaming:
            try:
                item = self.queue.get(timeout=30)
                if item is self.stop_signal:
                    break
                yield item
            except queue.Empty:
                break


# 使用自定义流式处理器
#custom_streamer = CustomStreamer(tokenizer)


def generate_response(prompt, max_length=1000):
    custom_streamer = CustomStreamer(tokenizer)

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    generation_thread = threading.Thread(
        target = model.generate,
        kwargs={
            "inputs": inputs["input_ids"],
            "max_new_tokens": max_length,
            "attention_mask": inputs["attention_mask"],
            "streamer": custom_streamer,  # 使用自定义流式处理器
            "do_sample": True,
            "top_k": 50,
            "top_p": 0.95,
            "temperature": 0.7
            }
    )
    generation_thread.start()
    return custom_streamer



# 测试
prompt_template = r"""
Below is an operations research question. Build a mathematical model and corresponding python code using `coptpy` that appropriately addresses the question.

# Question:
{Question}

# Response:
"""

question = ""
prompt = prompt_template.format(Question=question)
