import sys
import logging
from PyQt5.QtWidgets import QApplication
from ui.main_window import PetWindow
from utils.logger import setup_logger
from services.interaction_service import InteractionService
from core.agent.study_pet_agent import StudyPetAgent


def main():
    """主函数：初始化并启动桌宠"""
    # 设置日志
    setup_logger()
    logger = logging.getLogger(__name__)

    try:
        # 初始化应用
        app = QApplication(sys.argv)
        app.setApplicationName("智能学习桌宠")
        app.setQuitOnLastWindowClosed(False)

        # 创建Agent
        logger.info("初始化Agent系统...")
        pet_agent = StudyPetAgent(name="小桌")

        # 创建服务层
        interaction_service = InteractionService(pet_agent)

        # 创建主窗口
        logger.info("创建主窗口...")
        window = PetWindow(agent=pet_agent, interaction_service=interaction_service)
        window.show()

        logger.info("桌宠启动完成")

        # 运行应用
        sys.exit(app.exec_())

    except Exception as e:
        logger.error(f"启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()