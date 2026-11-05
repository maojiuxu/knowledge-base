from abc import ABC
from pathlib import Path

from kb.flow_process.nodes.base import BaseNode
from kb.flow_process.state import KBGraphState
from kb.flow_process.tool.logger import logger


class NodeEntry(BaseNode):
    """
    该节点用户来初始化文档，辨别文档是什么类型，以此来判断下一步该怎么走
    注意：该节点之前，用户已经上传了文档，所以该节点可以从state中获取到 local_file_path 属性
    """
    name = "entry_node"
    def node_process(self, state: KBGraphState):
        local_file_path = state.get("local_file_path")
        # 判断 local_file_path 是否存在，不存在则报错：
        if not local_file_path:
            logger.error("原始文件的路径为空！")
            raise Exception("原始文件的路径为空！")

        # 在判断原始文件的路径是否正确
        local_file_path_obj = Path(local_file_path)
        if not local_file_path_obj.exists():
            logger.error("原始文件的路径不存在！")
            raise Exception("原始文件的路径不存在！")

        # 文件存在，所以可以判断文件的类型
        if local_file_path_obj.suffix.lower() == ".pdf":
            # 是pdf文件，所以保存相应的内容并返回
            logger.info(f"文件：{local_file_path_obj.name}是PDF文件")
            return {
                "is_pdf_read_enable": True,
                "file_title": local_file_path_obj.stem,
                "pdf_path": str(local_file_path_obj)
            }
        elif local_file_path_obj.suffix.lower() == ".md":
            logger.info(f"文件：{local_file_path_obj.name}是MD文件")
            return {
                "is_md_read_enable": True,
                "file_title": local_file_path_obj.stem,
                "md_path": str(local_file_path_obj)
            }
        else:
            logger.error("目前只支持pdf、md类型的文件，上传文件暂不支持，抱歉~~~")
            raise Exception("目前只支持pdf、md类型的文件，上传文件暂不支持，抱歉~~~")

if __name__ == '__main__':
    entry_node = NodeEntry()
    state = KBGraphState(
        local_file_path=r"E:\SZ_AIAgent\260817\project\ProductionGradeKnowledgeBase\output\hak180产品安全手册.pdf"
    )
    entry_node(state=state)

