import logging
from transformers import AutoTokenizer, AutoModelForCausalLM

logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None  # 单例实例

    def __new__(cls, model_path):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model_path = model_path
            cls._instance.load_model()
        return cls._instance

    def load_model(self):
        """加载模型和 Tokenizer"""
        logger.info("⏳ Loading model and tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path, 
            device_map="auto"
        )
        logger.info("✅ Model and tokenizer loaded!")

# 全局单例实例
MODEL_LOADER = ModelLoader(
    model_path="/data1/songxiaoyong/lhr/hfmodels/best_0912_lr_1.25e-4_epoch_12_140"
)
