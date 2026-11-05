import time
from pathlib import Path
from time import sleep

from kb.flow_process.config.config import MineruConfig
from kb.flow_process.nodes.base import BaseNode
from kb.flow_process.state import KBGraphState
from kb.flow_process.tool.logger import logger


class NodePdfToMd(BaseNode):
    name = "node_pdf_to_md"
    def node_process(self, state: KBGraphState):
        # 1、先从state中拿到数据，并校验数据
        pdf_path = state.get("pdf_path")
        local_dir = state.get("local_dir")

        if not pdf_path:
            logger.error("pdf文档路径为空！！！")
            raise Exception("pdf文档路径为空！！！")
        if not local_dir:
            logger.error("pdf文档输出路径为空！！！")
            raise Exception("pdf文档输出路径为空！！！")

        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            logger.error("pdf文档路径不存在！！！")
            raise Exception("pdf文档路径不存在！！！")
        local_dir_obj = Path(local_dir)
        if not local_dir_obj.exists():
            logger.error("pdf文档输出路径不存在！！！")
            raise Exception("pdf文档输出路径不存在！！！")

        # MineruConfig.token
        # 1、准备向mineru发送请求转换文档格式
        import requests

        token = MineruConfig.token
        url = "https://mineru.net/api/v4/file-urls/batch"
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "files": [
                {"name": f"{pdf_path_obj.name}", "data_id": "abcd"}
            ],
            "model_version": "vlm"
        }
        file_path = [pdf_path_obj] # 注意：这里是路径，不是文件名！！！
        try:
            response = requests.post(url, headers=header, json=data)
            if response.status_code == 200:
                result = response.json()
                logger.info('响应成功。 result:{}'.format(result))
                if result["code"] == 0:
                    batch_id = result["data"]["batch_id"]
                    urls = result["data"]["file_urls"]
                    for i in range(0, len(urls)):
                        with open(file_path[i], 'rb') as f:
                            res_upload = requests.put(urls[i], data=f)
                            if res_upload.status_code == 200:
                                logger.info(f"{urls[i]} 上传成功")
                            else:
                                logger.error(f"{urls[i]} 上传失败")
                else:
                    logger.error('应用上传url失败,reason:{}'.format(result["msg"]))
                    raise Exception("应用上传url失败")
            else:
                logger.error('响应不成功。 status:{} ,result:{}'.format(response.status_code, response))
                raise Exception("响应不成功")
        except Exception as err:
            logger.error(err)
            raise Exception(err)

        # 2、请求结束，现在需要轮询等待转换结果
        # import requests
        #
        # token = "API管理页面自定创建的token"
        # batch_id = "上一步批量提交返回的 batch_id"
        url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        # 这里需要轮询查询返回的结果
        timeout = 300 # 等待五分钟
        start_time = time.time()
        while True:
            # 官方文档中明确写了，获取结果时有限流，每分钟不得超过1000次，所以这里也要做个限流：取每分钟800次
            # 因为是800次/每分钟，所以每次调用的平均间隔时间为：60/800=0.075秒，所以每次调用的时候停顿0.075秒
            sleep(0.075)
            try:
                res = requests.get(url, headers=header)
                if res.status_code != 200:
                    logger.error("获取mineru转换文档的请求出错！！！")
                    raise Exception("获取mineru转换文档的请求出错！！！")
                if res.json().get("code") != 0:
                    logger.error("获取mineru转换文档的返回数据出错！！！")
                    raise Exception("获取mineru转换文档的返回数据出错！！！")
                if res.json().get("data").get("extract_result")[0].get("state") == "waiting-file":
                    logger.info("等待文件上传排队提交解析任务中")
                elif res.json().get("data").get("extract_result")[0].get("state") == "pending":
                    logger.info("文件排队中...")
                elif res.json().get("data").get("extract_result")[0].get("state") == "running":
                    logger.info("文件正在解析...")
                elif res.json().get("data").get("extract_result")[0].get("state") == "converting":
                    logger.info("文件格式转换中...")
                elif res.json().get("data").get("extract_result")[0].get("state") == "failed":
                    logger.error("文件解析失败！！！")
                    raise Exception("mineru解析文件失败！！！")
                elif res.json().get("data").get("extract_result")[0].get("state") == "done":
                    logger.info("文件解析完成！")
                    full_zip_url = res.json().get("data").get("extract_result")[0].get("full_zip_url")
                    break
                if time.time() - start_time > timeout:
                    logger.error("文件解析超时！！！")
                    raise Exception("文件解析超时！！！")
            except Exception as err:
                logger.error("获取mineru转换文档的结果报错！！！")
                raise Exception(err)

        # 轮询结束，拿到url，发起下载请求，并将其放在本地指定目录
        response = requests.get(full_zip_url)
        if response.status_code != 200:
            logger.error("mineru转换的md文档下载失败！！！")
            raise Exception("mineru转换的md文档下载失败！！！")

        local_dir_obj_zip = local_dir_obj / f"{pdf_path_obj.stem}.zip"
        with open(local_dir_obj_zip, "wb") as f:
            f.write(response.content)

if __name__ == '__main__':
    node_pdf_to_md = NodePdfToMd()
    state = {
        "local_dir": r"E:\SZ_AIAgent\260817\project\ProductionGradeKnowledgeBase\output\op",
        "pdf_path": r"E:\SZ_AIAgent\260817\project\ProductionGradeKnowledgeBase\output\万用表RS-12的使用.pdf"
    }
    node_pdf_to_md(state)

