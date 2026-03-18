import openai
import requests
import json
from abc import ABC, abstractmethod

class LLMInterface(ABC):
    """
    大语言模型接口抽象基类
    """
    @abstractmethod
    def generateText(self, prompt, **kwargs):
        """
        生成文本
        :param prompt: 提示词
        :param kwargs: 其他参数
        :return: 生成的文本
        """
        pass

    @abstractmethod
    def chatCompletion(self, messages, **kwargs):
        """
        对话补全
        :param messages: 对话历史
        :param kwargs: 其他参数
        :return: 补全的文本
        """
        pass

class OpenAIClient(LLMInterface):
    """
    OpenAI大语言模型客户端
    """
    def __init__(self, api_key, model="gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key

    def generateText(self, prompt, **kwargs):
        try:
            response = openai.Completion.create(
                engine=self.model,
                prompt=prompt,
                **kwargs
            )
            return response.choices[0].text.strip()
        except Exception as e:
            return f"生成文本失败: {e}"

    def chatCompletion(self, messages, **kwargs):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            return f"对话补全失败: {e}"

class BaiduERNIE(LLMInterface):
    """
    百度文心一言大语言模型客户端
    """
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = self.getAccessToken()

    def getAccessToken(self):
        """
        获取访问令牌
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            raise Exception(f"获取访问令牌失败: {response.text}")

    def generateText(self, prompt, **kwargs):
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "access_token": self.access_token
        }
        data = {
            "messages": [{"role": "user", "content": prompt}],
            **kwargs
        }
        response = requests.post(url, headers=headers, params=params, json=data)
        if response.status_code == 200:
            return response.json()['result']
        else:
            return f"生成文本失败: {response.text}"

    def chatCompletion(self, messages, **kwargs):
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "access_token": self.access_token
        }
        data = {
            "messages": messages,
            **kwargs
        }
        response = requests.post(url, headers=headers, params=params, json=data)
        if response.status_code == 200:
            return response.json()['result']
        else:
            return f"对话补全失败: {response.text}"

class LLMFactory:
    """
    大语言模型工厂类
    """
    @staticmethod
    def createClient(provider, **kwargs):
        if provider == "openai":
            return OpenAIClient(
                api_key=kwargs.get("api_key"),
                model=kwargs.get("model", "gpt-3.5-turbo")
            )
        elif provider == "ernie":
            return BaiduERNIE(
                api_key=kwargs.get("api_key"),
                secret_key=kwargs.get("secret_key")
            )
        else:
            raise ValueError(f"不支持的大语言模型提供商: {provider}")