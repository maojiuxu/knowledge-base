import os
from abc import ABC

from dotenv import load_dotenv
load_dotenv()

# mineru相关的配置
class MineruConfig(ABC):
    token=os.getenv("MineruToken")