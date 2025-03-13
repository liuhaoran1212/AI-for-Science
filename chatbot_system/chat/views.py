#import ollama
import re
import json
import time
import logging
import asyncio
import aiofiles
from threading import Thread
from rest_framework.views import APIView
from chat.model_loader import MODEL_LOADER
from django.http import StreamingHttpResponse
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

from .extract_and_run_python_code import extract_and_execute_code


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()


# model_name = "/data1/songxiaoyong/lhr/hfmodels/best_0912_lr_1.25e-4_epoch_12_140"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")


class CustomStreamer(TextIteratorStreamer):
    def __init__(self, tokenizer, output_file="./model_output.md", **kwargs):
        super().__init__(tokenizer, skip_prompt=True, **kwargs)
        self.stop_signal = "[DONE]"
        self.output_file = output_file  # 新增输出文件路径参数

    async def generate_tokens(self):
        stream_result_template = {
            "id": "chat_123",
            "object": "chat.completion.chunk",
            "created": time.time(),
            "model": "DiscreteOpt",
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": None
                }
            ]
        }
        loop = asyncio.get_event_loop()
        full_output = []  # 使用局部变量存储完整输出
        in_code_block = False  # 标志：是否在代码块内
        while True:
            text = await loop.run_in_executor(None, self.text_queue.get)

            # debug_text = text.replace(" ", "[SPACE]").replace("\n", "[NEWLINE]").replace("\t", "[TAB]").replace("\u00A0", "[NBSP]")
            # logger.info(f"[DEBUG] Model Raw Output: {text} -- {debug_text}")
            # logger.info(f"[DEBUG] Model Raw Output: {text}")
            
            # 处理 token
            processed_text = text
            if "```" in text:
                # 遇到 "```"，切换代码块状态
                in_code_block = not in_code_block
            elif not in_code_block:
                # 不在代码块内，替换四个连续的空格
                processed_text = re.sub(r' {2,}', ' ', text)
                # processed_text = text.replace("    ", "")
            elif in_code_block:
                if "        " in text:
                    processed_text = text.replace("        ", "")
                if text == " ":
                    processed_text = text.replace(" ", "")

            # 处理coptpy
            if "`coptpy`" in text:
                processed_text = text.replace("`coptpy`", "`discoptpy`")
            
            debug_text = processed_text.replace(" ", "[SPACE]").replace("\n", "[NEWLINE]").replace("\t", "[TAB]").replace("\u00A0", "[NBSP]")
            logger.info(f"[DEBUG] Model Raw Output: {text} -- {debug_text}")

            # 收集非终止信号的输出
            if text != self.stop_signal:
                full_output.append(processed_text)

            stream_result = stream_result_template.copy()
            stream_result["choices"][0]["delta"]["content"] = processed_text
            if text == self.stop_signal:
                stream_result["choices"][0]["finish_reason"] = "stop"
                sse_data = f"data: {json.dumps(stream_result)}\n\n"
                yield sse_data.encode("utf-8")
                # 异步写入文件
                async with aiofiles.open(self.output_file, "w", encoding="utf-8") as f:
                    await f.write("".join(full_output))

                result = extract_and_execute_code(self.output_file)
                logger.info(f"[DEBUG] Python Output: {result}")
                execution_result_stream = {
                    "id": "chat_123",
                    "object": "chat.completion.chunk",
                    "created": time.time(),
                    "model": "DiscreteOpt",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": result},
                            "finish_reason": "execution_complete"
                        }
                    ]
                }
                execution_sse_data = f"data: {json.dumps(execution_result_stream)}\n\n"
                yield execution_sse_data.encode("utf-8")
                break
            sse_data = f"data: {json.dumps(stream_result)}\n\n"
            yield sse_data.encode("utf-8")
            self.text_queue.task_done()


class Compute(APIView):
    def post(self, *args, **kwargs):
        # 直接使用全局模型实例
        tokenizer = MODEL_LOADER.tokenizer
        model = MODEL_LOADER.model

        prompt_template = r"""
        Below is an operations research question. Build a mathematical model and corresponding python code using `coptpy` that appropriately addresses the question.

        # Question:
        {Question}

        # Response:
        """

        question = self.request.data.get("messages")[1].get("content")

        streamer = CustomStreamer(tokenizer)

        prompt = prompt_template.format(Question=question)
        logger.info(f"prompt is {prompt}")

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        generation_kwargs = dict(
            inputs,
            streamer=streamer,
            max_new_tokens=1200,
            do_sample=False,
            top_k=1,
            top_p=0.5,
            temperature=0,
        )
        # 在独立线程中运行生成过程
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()

        return StreamingHttpResponse(
            streamer.generate_tokens(),
            content_type='text/event-stream',
        )


# def chat_stream(request):
#     prompt = request.GET.get("message")

#     ollama_url = "http://localhost:11434/api/generate"

#     response = requests.post(
#             ollama_url,
#             json={
#                 "model": "deepseek-r1:7b",
#                 "prompt": prompt,
#                 "stream": True
#                 },
#             stream=True
#             )


#     buffer = []
#     ignore_pattern = re.compile(r'<\/?think>')
#     buffer_threshold = 5

#     def process_chunk(chunk_data):
#         content = chunk_data.get('response', '')

#         content = ignore_pattern.sub('', content)

#         try:
#             decoded = content.encode('utf-8').decode('utf-8')
#         except:
#             decoded = content

#         buffer.append(decoded)

#         if len(buffer) >= buffer_threshold or re.search(r'[\n。！？，]', decoded):
#             combined = ''.join(buffer)
#             buffer.clear()
#             return combined
#         return None

#     def event_stream():
#         for chunk in response.iter_lines():
#             if chunk:
#                 try:
#                     data = json.loads(chunk.decode('utf-8'))
#                     processed = process_chunk(data)
#                     if processed:
#                         yield f"data: {json.dumps({'content': processed}, ensure_ascii=False)}\n\n"
#                 except Exception as e:
#                     print(f"Error processing chunk: {e}")
#         if buffer:
#             yield f"data: {json.dumps({'content': ''.join(buffer)}, ensure_ascii=False)}\n\n"
#         yield "data: [DONE]\n\n"

#     return StreamingHttpResponse(
#             event_stream(),
#             content_type="text/event-stream; charset=utf-8",
#             headers={"X-Accel-Buffering": "no"}
#             )
