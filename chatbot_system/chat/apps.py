from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chat"

    def ready(self):
        # 导入模型加载模块，触发预加载
        from chat.model_loader import MODEL_LOADER
        # 验证模型是否加载完成
        if hasattr(MODEL_LOADER, 'model'):
            print("🎯 Model preloaded successfully!")
