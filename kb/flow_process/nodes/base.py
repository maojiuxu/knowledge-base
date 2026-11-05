from abc import abstractmethod

from kb.flow_process.state import KBGraphState
from kb.flow_process.tool.logger import logger


class BaseNode:
    """
    定义节点的基类，所有节点都继承自此类，所以可以统一处理节点的一些报错等信息
    """

    name = "base_node"
    def __init__(self):
        # 创建节点时保证节点中要有name属性
        if self.name == "base_node":
            node_name = self.__class__.__name__
            # 节点创建失败
            logger.error(f"{node_name}节点没有创建name属性，请在类中添加name属性")
            raise Exception(f"{self.__class__.__name__}节点没有创建name属性，请在类中添加name属性")


    def __call__(self, state: KBGraphState, *args, **kwargs):
        # 当graph底层调用节点时，会把类的实例对象当作方法调用，所以会调用__call__魔法方法
        node_name = self.name
        logger.info(f"节点 **{node_name}** 开始执行~~~")
        try:
            self.node_process(state)
        except Exception as e:
            logger.error(f"节点{self.name}出错了！！！")
            raise Exception(f"节点{self.name}出错了！！！")
        logger.info(f"节点 **{node_name}** 执行结束~~~")

    # 创建抽象方法，保证子类当中重写此方法用来处理节点中业务逻辑
    @abstractmethod
    def node_process(self, state: KBGraphState):
        pass

if __name__ == '__main__':
    class TestNode(BaseNode):
        name = "test_node"
        def node_process(self, state: KBGraphState):
            logger.info(f"{self.name}节点执行中...")
    test_node = TestNode()
    state = KBGraphState()
    test_node(state)