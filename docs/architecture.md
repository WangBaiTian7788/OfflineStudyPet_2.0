OfflineStudyPet/
├── main.py                    # 程序入口：启动桌宠、初始化Agent系统
├── run.py                     # 运行脚本
├── core/                      # 核心模块
│   ├── __init__.py
│   ├── agent/                # Agent智能系统
│   │   ├── __init__.py
│   │   ├── central_executive.py     # 中央执行系统
│   │   ├── emotion_system.py        # 情感系统
│   │   ├── goal_system.py           # 目标系统
│   │   ├── metacognition.py         # 元认知
│   │   ├── personality.py           # 个性系统
│   │   ├── reasoning.py             # 推理系统
│   │   ├── skill_tree.py            # 技能树
│   │   ├── social_norms.py          # 社交规范
│   │   ├── study_pet_agent.py       # 主Agent类
│   │   └── theory_of_mind.py        # 心智理论
│   ├── memory/               # 记忆系统
│   │   ├── __init__.py
│   │   ├── hierarchical_memory.py   # 分层记忆
│   │   ├── memory_network.py        # 记忆网络
│   │   └── episodic_memory.py       # 情景记忆
│   ├── knowledge/           # 知识处理
│   │   ├── __init__.py
│   │   ├── match_engine.py          # 匹配引擎
│   │   ├── weight_manager.py        # 权重管理
│   │   ├── exploration_engine.py    # 探索引擎
│   │   └── learning_strategy.py     # 学习策略
│   ├── perception/          # 感知系统
│   │   ├── __init__.py
│   │   ├── context_analyzer.py      # 上下文分析
│   │   └── intent_recognizer.py     # 意图识别
│   └── config.py            # 配置文件
├── ui/                      # 用户界面
│   ├── __init__.py
│   ├── main_window.py      # 桌宠主窗口
│   ├── chat_dialog.py      # 聊天对话框
│   ├── settings_dialog.py  # 设置对话框
│   ├── rating_panel.py     # 评分面板
│   ├── agent_monitor.py    # Agent监控面板（新增）
│   └── emotion_display.py  # 情感显示组件（新增）
├── resources/              # 资源文件
│   ├── images/            # 图片资源
│   │   ├── idle.png
│   │   ├── chat.png
│   │   ├── happy.png
│   │   ├── sad.png
│   │   ├── thinking.png
│   │   └── sleeping.png
│   ├── knowledge.json     # 原始知识库
│   ├── learned.json       # 用户学习内容
│   ├── emotions.json      # 情感配置（新增）
│   └── personalities.json # 个性模板（新增）
├── data/                  # 数据存储
│   ├── chat_history.json  # 聊天记录
│   ├── rating_record.json # 评分记录
│   ├── dialog_weights.json # 对话权重
│   ├── settings.json      # 用户设置
│   ├── agent_state.json   # Agent状态（新增）
│   ├── skill_progress.json # 技能进度（新增）
│   ├── memory_archive.json # 记忆存档（新增）
│   ├── exploration_history.json
│   ├── exploration_memory.json
│   ├── user_interests.json
│   └── logs/              # 日志目录
│       ├── interactions.log
│       ├── learning.log
│       └── errors.log
├── utils/                 # 工具模块
│   ├── __init__.py
│   ├── file_helper.py    # 文件操作
│   ├── data_loader.py    # 数据加载器（新增）
│   ├── logger.py         # 日志系统（新增）
│   ├── validator.py      # 数据验证（新增）
│   └── scheduler.py      # 任务调度（新增）
├── services/             # 服务层
│   ├── __init__.py
│   ├── interaction_service.py    # 交互服务（新增）
│   ├── learning_service.py       # 学习服务（新增）
│   ├── memory_service.py         # 记忆服务（新增）
│   └── emotion_service.py        # 情感服务（新增）
├── models/               # 数据模型
│   ├── __init__.py
│   ├── conversation.py   # 对话模型
│   ├── memory.py         # 记忆模型
│   ├── skill.py          # 技能模型
│   └── emotion.py        # 情感模型
├── tests/                # 测试目录
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_memory.py
│   └── test_ui.py
├── scripts/              # 脚本目录
│   ├── setup.py          # 安装脚本
│   ├── backup.py         # 备份脚本
│   └── stats.py          # 统计脚本
├── docs/                 # 文档
│   ├── api.md           # API文档
│   ├── architecture.md  # 架构文档
│   └── user_guide.md    # 用户指南
├── requirements.txt      # 依赖包
├── setup.py             # 安装配置
├── config.yaml          # 配置文件（新增）
└── README.md            # 项目说明