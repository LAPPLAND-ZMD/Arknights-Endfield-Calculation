import sys
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QFormLayout, QGroupBox, QLabel, 
                              QLineEdit, QComboBox, QPushButton, QTextEdit, 
                              QScrollArea, QMessageBox, QDoubleSpinBox, QSpinBox,
                              QGridLayout, QToolButton, QSizePolicy, QFrame,
                              QFileDialog)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QPalette

class RPGDamageCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("终末地伤害计算工具 - 作者：拉普兰德")
        self.resize(1280, 720)
        
        # 配置文件路径
        self.config_file = "damage_calculator_config.json"

        # 创建主界面布局（横向排列）
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ================== 左侧模块：角色属性 + 敌人抗性 ==================
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setSpacing(10)

        # 1. 角色基础属性
        base_group = QGroupBox("🛡️ 角色基础属性")
        base_layout = QFormLayout()
        base_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        input_width = 120
        
        # 添加单位标签
        def create_labeled_input(default, tooltip=None):
            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            
            input_field = QLineEdit(default)
            input_field.setFixedWidth(input_width)
            input_field.setAlignment(Qt.AlignRight)
            unit_label = QLabel("%")
            
            h_layout.addWidget(input_field)
            h_layout.addWidget(unit_label)
            h_layout.addStretch()
            
            if tooltip:
                container.setToolTip(tooltip)
                input_field.setToolTip(tooltip)
            return input_field, container

        self.attack_input = QLineEdit("1000")
        self.attack_input.setFixedWidth(input_width)
        self.attack_input.setAlignment(Qt.AlignRight)
        self.attack_input.setToolTip("角色基础攻击力数值")

        self.atk_bonus_input, atk_container = create_labeled_input("30", "攻击力提升百分比")
        self.base_dmg_bonus_input, base_dmg_container = create_labeled_input("20", "基础伤害增幅百分比")
        self.elemental_bonus_input, elem_container = create_labeled_input("15", "属性伤害增幅百分比")
        self.fragile_bonus_input, fragile_container = create_labeled_input("10", "敌人脆弱状态带来的伤害增幅")
        self.crit_rate_input, crit_rate_container = create_labeled_input("50", "暴击发生概率")
        self.crit_dmg_input, crit_dmg_container = create_labeled_input("150", "暴击时额外造成的伤害比例")
        self.pen_resist_input, pen_resist_container = create_labeled_input("10", "无视敌人抗性的百分比")

        base_layout.addRow("基础攻击力:", self.attack_input)
        base_layout.addRow("攻击力提升:", atk_container)
        base_layout.addRow("基础增幅:", base_dmg_container)
        base_layout.addRow("属性增幅:", elem_container)
        base_layout.addRow("脆弱增幅:", fragile_container)
        base_layout.addRow("暴击率:", crit_rate_container)
        base_layout.addRow("暴击伤害:", crit_dmg_container)
        base_layout.addRow("无视抗性:", pen_resist_container)
        base_group.setLayout(base_layout)
        left_layout.addWidget(base_group)

        # 2. 敌人抗性
        resist_group = QGroupBox("👹 敌人抗性选择")
        resist_layout = QVBoxLayout()
        resist_layout.setContentsMargins(10, 10, 10, 10)
        
        self.resist_combo = QComboBox()
        self.resist_combo.addItems([
            "SSS级 (95%)", "SS级 (90%)", "S级 (75%)", 
            "A级 (60%)", "B级 (45%)", "C级 (35%)", "D级 (25%)"
        ])
        resist_layout.addWidget(QLabel("抗性等级:"))
        resist_layout.addWidget(self.resist_combo)
        
        # 添加抗性说明标签
        self.resist_desc = QLabel("最终抗性 = 敌人抗性 - 无视抗性")
        self.resist_desc.setStyleSheet("color: #666; font-size: 12px;")
        resist_layout.addWidget(self.resist_desc)
        
        resist_group.setLayout(resist_layout)
        left_layout.addWidget(resist_group)
        
        # 添加计算器
        calc_group = QGroupBox("🧮 基础计算器")
        calc_layout = QVBoxLayout()
        
        # 显示屏
        self.calc_display = QLineEdit("0")
        self.calc_display.setReadOnly(True)
        self.calc_display.setAlignment(Qt.AlignRight)
        self.calc_display.setFont(QFont("Consolas", 12))
        self.calc_display.setFixedHeight(36)
        calc_layout.addWidget(self.calc_display)
        
        # 按钮网格
        button_grid = QGridLayout()
        button_grid.setSpacing(2)
        
        # 按钮定义
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', 'C', '+'
        ]
        
        positions = [(i, j) for i in range(4) for j in range(4)]
        
        self.calc_buttons = {}
        for position, button_text in zip(positions, buttons):
            button = QToolButton()
            button.setText(button_text)
            button.setMinimumSize(QSize(50, 40))
            
            if button_text in '0123456789.':
                button.setStyleSheet("background-color: #f0f0f0;")
            elif button_text == 'C':
                button.setStyleSheet("background-color: #ff6b6b; color: white;")
            else:
                button.setStyleSheet("background-color: #4ecdc4;")
                
            button.clicked.connect(lambda checked, b=button_text: self.calc_button_clicked(b))
            button_grid.addLayout(self.create_button_layout(button), *position)
        
        calc_layout.addLayout(button_grid)
        
        # 导入目标选择
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("导入到:"))
        
        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "基础攻击力", "攻击力提升", "基础增幅", "属性增幅", 
            "脆弱增幅", "暴击率", "暴击伤害", "无视抗性"
        ])
        target_layout.addWidget(self.target_combo)
        
        import_btn = QPushButton("➡️ 导入")
        import_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        import_btn.clicked.connect(self.import_to_target)
        target_layout.addWidget(import_btn)
        
        calc_layout.addLayout(target_layout)
        calc_group.setLayout(calc_layout)
        left_layout.addWidget(calc_group)
        
        # 保存/加载配置按钮
        config_layout = QHBoxLayout()
        save_btn = QPushButton("💾 保存配置")
        save_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
        save_btn.clicked.connect(self.save_config)
        load_btn = QPushButton("📂 加载配置")
        load_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 5px;")
        load_btn.clicked.connect(self.load_config)
        config_layout.addWidget(save_btn)
        config_layout.addWidget(load_btn)
        left_layout.addLayout(config_layout)
        
        left_layout.addStretch()
        main_layout.addWidget(left_column, 1)

        # ================== 中间模块：技能配置 ==================
        middle_column = QWidget()
        middle_layout = QVBoxLayout(middle_column)
        middle_layout.setSpacing(10)

        skill_group = QGroupBox("⚔️ 技能配置")
        skill_outer_layout = QVBoxLayout()
        
        # 终结技状态选择
        ult_layout = QHBoxLayout()
        ult_layout.addWidget(QLabel("终结技类型:"))
        self.ult_type_combo = QComboBox()
        self.ult_type_combo.addItems([
            "伤害终结技 (正常计算)", 
            "持续性终结技 (增益效果)",
            "终结技模式2 (特殊技能倍率)"
        ])
        self.ult_type_combo.setToolTip("选择终结技类型：\n- 伤害终结技：正常计算终结技伤害\n- 持续性终结技：不计算终结技伤害，但为其他技能提供增益\n- 终结技模式2：隐藏终结技伤害，显示特殊战技/连携/普攻倍率")
        ult_layout.addWidget(self.ult_type_combo)
        ult_layout.addStretch()
        
        # 终结技增益设置（仅在持续性终结技时显示）
        self.ult_buff_group = QGroupBox("✨ 持续性终结技增益效果")
        self.ult_buff_group.setVisible(False)
        buff_layout = QFormLayout()
        
        self.ult_buff_attack = QLineEdit("0")
        self.ult_buff_attack.setFixedWidth(80)
        self.ult_buff_attack.setAlignment(Qt.AlignRight)
        buff_layout.addRow("攻击力提升%:", self.ult_buff_attack)
        
        self.ult_buff_dmg = QLineEdit("0")
        self.ult_buff_dmg.setFixedWidth(80)
        self.ult_buff_dmg.setAlignment(Qt.AlignRight)
        buff_layout.addRow("伤害增幅%:", self.ult_buff_dmg)
        
        self.ult_buff_group.setLayout(buff_layout)
        
        # 终结技模式2设置
        self.ult_mode2_group = QGroupBox("🎯 终结技模式2 - 特殊技能倍率")
        self.ult_mode2_group.setVisible(False)
        
        mode2_layout = QVBoxLayout()
        
        # 特殊战技配置
        special_skill_layout = QVBoxLayout()
        special_skill_layout.addWidget(QLabel("特殊战技 (最多12段):"))
        
        self.special_skill_hits = QSpinBox()
        self.special_skill_hits.setRange(1, 12)
        self.special_skill_hits.setValue(1)
        self.special_skill_hits.setFixedWidth(60)
        self.special_skill_hits.valueChanged.connect(lambda val: self.update_special_multipliers("special", val))
        
        mode2_top_layout = QHBoxLayout()
        mode2_top_layout.addWidget(QLabel("段数:"))
        mode2_top_layout.addWidget(self.special_skill_hits)
        mode2_top_layout.addStretch()
        special_skill_layout.addLayout(mode2_top_layout)
        
        self.special_skill_container = QVBoxLayout()
        self.special_skill_container.setSpacing(5)
        special_skill_layout.addLayout(self.special_skill_container)
        
        # 连携技配置
        chain_skill_layout = QVBoxLayout()
        chain_skill_layout.addWidget(QLabel("连携技 (最多12段):"))
        
        self.chain_skill_hits = QSpinBox()
        self.chain_skill_hits.setRange(1, 12)
        self.chain_skill_hits.setValue(1)
        self.chain_skill_hits.setFixedWidth(60)
        self.chain_skill_hits.valueChanged.connect(lambda val: self.update_special_multipliers("chain", val))
        
        chain_top_layout = QHBoxLayout()
        chain_top_layout.addWidget(QLabel("段数:"))
        chain_top_layout.addWidget(self.chain_skill_hits)
        chain_top_layout.addStretch()
        chain_skill_layout.addLayout(chain_top_layout)
        
        self.chain_skill_container = QVBoxLayout()
        self.chain_skill_container.setSpacing(5)
        chain_skill_layout.addLayout(self.chain_skill_container)
        
        # 普攻配置
        basic_skill_layout = QVBoxLayout()
        basic_skill_layout.addWidget(QLabel("普攻 (最多12段):"))
        
        self.basic_skill_hits = QSpinBox()
        self.basic_skill_hits.setRange(1, 12)
        self.basic_skill_hits.setValue(1)
        self.basic_skill_hits.setFixedWidth(60)
        self.basic_skill_hits.valueChanged.connect(lambda val: self.update_special_multipliers("basic", val))
        
        basic_top_layout = QHBoxLayout()
        basic_top_layout.addWidget(QLabel("段数:"))
        basic_top_layout.addWidget(self.basic_skill_hits)
        basic_top_layout.addStretch()
        basic_skill_layout.addLayout(basic_top_layout)
        
        self.basic_skill_container = QVBoxLayout()
        self.basic_skill_container.setSpacing(5)
        basic_skill_layout.addLayout(self.basic_skill_container)
        
        mode2_layout.addLayout(special_skill_layout)
        mode2_layout.addLayout(chain_skill_layout)
        mode2_layout.addLayout(basic_skill_layout)
        self.ult_mode2_group.setLayout(mode2_layout)
        
        self.ult_type_combo.currentIndexChanged.connect(self.toggle_ult_groups)
        
        skill_outer_layout.addLayout(ult_layout)
        skill_outer_layout.addWidget(self.ult_buff_group)
        skill_outer_layout.addWidget(self.ult_mode2_group)
        
        # 技能配置区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)

        self.skill_widgets = {}
        skills = [
            ("普攻", 9, "基础普通攻击，通常为多段伤害"),
            ("战技", 12, "消耗战技点释放的技能"),
            ("连携技", 4, "特定条件下触发的团队协作技能"),
            ("终结技", 20, "大招/必杀技，消耗能量释放")
        ]
        
        for skill_name, max_hits, tooltip in skills:
            group = QGroupBox(f"{skill_name} (最多{max_hits}段)")
            group.setToolTip(tooltip)
            group.setObjectName(f"skill_group_{skill_name}")
            layout = QVBoxLayout()
            
            # 顶部控制栏
            top_control = QHBoxLayout()
            
            # 增伤输入（百分比显示）
            dmg_bonus_container = QWidget()
            dmg_bonus_layout = QHBoxLayout(dmg_bonus_container)
            dmg_bonus_layout.setContentsMargins(0, 0, 0, 0)
            dmg_bonus_input = QLineEdit("20")
            dmg_bonus_input.setFixedWidth(80)
            dmg_bonus_input.setAlignment(Qt.AlignRight)
            dmg_bonus_layout.addWidget(dmg_bonus_input)
            dmg_bonus_layout.addWidget(QLabel("%"))
            
            # 段数选择
            hits_spin = QSpinBox()
            hits_spin.setRange(1, max_hits)
            hits_spin.setValue(1)
            hits_spin.setFixedWidth(60)
            hits_spin.valueChanged.connect(lambda val, s=skill_name, m=max_hits: self.update_multipliers(s, val, m))
            
            top_control.addWidget(QLabel("增伤:"))
            top_control.addWidget(dmg_bonus_container)
            top_control.addWidget(QLabel("段数:"))
            top_control.addWidget(hits_spin)
            top_control.addStretch()
            
            layout.addLayout(top_control)
            
            # 倍率输入区域
            multiplier_container = QVBoxLayout()
            multiplier_container.setSpacing(5)
            self.skill_widgets[skill_name] = {
                'hits': hits_spin, 
                'multipliers': [], 
                'dmg_bonus': dmg_bonus_input,
                'group': group,
                'max_hits': max_hits
            }
            self.update_multipliers(skill_name, 1, max_hits, multiplier_container)
            
            layout.addLayout(multiplier_container)
            group.setLayout(layout)
            scroll_layout.addWidget(group)
            
            self.skill_widgets[skill_name]['layout'] = multiplier_container

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        skill_outer_layout.addWidget(scroll)
        skill_group.setLayout(skill_outer_layout)
        middle_layout.addWidget(skill_group)
        main_layout.addWidget(middle_column, 2)

        # ================== 右侧模块：操作与结果 ==================
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setSpacing(10)
        right_column.setFixedWidth(360)

        # 计算按钮
        self.calc_btn = QPushButton("🚀 开始计算伤害")
        self.calc_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px; 
                padding: 12px; 
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.calc_btn.clicked.connect(self.calculate_damage)
        right_layout.addWidget(self.calc_btn)

        # 结果展示
        result_group = QGroupBox("📊 计算结果")
        result_layout = QVBoxLayout()
        
        # 结果分为三大区块
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("点击上方的计算按钮，伤害分析结果将显示在这里...")
        self.result_output.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        
        # 添加图表容器
        self.chart_container = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_container)
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加结果区块标题样式
        result_doc = self.result_output.document()
        result_doc.setDefaultStyleSheet("""
            h1 { color: #1e88e5; margin: 10px 0 5px 0; padding-bottom: 3px; border-bottom: 1px solid #e0e0e0; }
            h2 { color: #43a047; margin: 8px 0 3px 0; }
            .total { font-size: 16px; font-weight: bold; color: #d81b60; }
            .highlight { background-color: #e3f2fd; padding: 3px; border-radius: 3px; }
            .skill-row { margin: 2px 0; }
            .skill-name { display: inline-block; width: 80px; }
            .skill-value { display: inline-block; width: 120px; text-align: right; font-weight: bold; }
            .skill-percent { display: inline-block; width: 80px; text-align: right; color: #546e7a; }
            .damage-types { margin: 5px 0; padding: 5px; background-color: #f5f5f5; border-radius: 3px; }
        """)
        
        result_layout.addWidget(self.result_output)
        result_layout.addWidget(self.chart_container)
        result_group.setLayout(result_layout)
        right_layout.addWidget(result_group)
        
        # 添加结果说明
        note_label = QLabel("注：伤害期望 = 非暴击伤害 × (1 + 暴击率 × 暴击伤害)")
        note_label.setStyleSheet("color: #666; font-size: 11px;")
        note_label.setWordWrap(True)
        right_layout.addWidget(note_label)
        
        right_layout.addStretch()
        main_layout.addWidget(right_column, 1)
        
        # 初始化计算器状态
        self.current_calc = "0"
        self.last_operation = ""
        self.reset_next = False
        self.update_calc_display()
        
        # ===== 修复：分离控件引用和数值数据 =====
        # 控件引用（用于UI操作）
        self.special_skill_spins = []  # 存储QDoubleSpinBox控件
        self.chain_skill_spins = []
        self.basic_skill_spins = []
        
        # 数值数据（用于计算和保存配置）
        self.special_skill_values = []  # 存储倍率数值
        self.chain_skill_values = []
        self.basic_skill_values = []
        
        # 初始化默认值
        self.special_skill_values = [150.0]  # 默认150%
        self.chain_skill_values = [150.0]
        self.basic_skill_values = [150.0]
        
        # 初始更新UI
        self.update_special_multipliers("special", 1)
        self.update_special_multipliers("chain", 1)
        self.update_special_multipliers("basic", 1)
        
        # 加载默认配置
        self.load_default_config()

    # ===== 计算器相关方法 =====
    def create_button_layout(self, button):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button)
        return layout

    def calc_button_clicked(self, symbol):
        if symbol == 'C':
            self.current_calc = "0"
            self.last_operation = ""
            self.reset_next = False
        elif symbol in '+-*/':
            if self.reset_next:
                self.current_calc = self.current_calc[:-1] + symbol
            else:
                self.current_calc += symbol
            self.reset_next = False
        elif symbol == '.':
            if '.' not in self.current_calc.split('[-+*/]')[-1]:
                if self.reset_next:
                    self.current_calc = "0."
                    self.reset_next = False
                else:
                    self.current_calc += "."
        else:  # 数字
            if self.reset_next:
                self.current_calc = symbol
                self.reset_next = False
            elif self.current_calc == "0":
                self.current_calc = symbol
            else:
                self.current_calc += symbol
                
        self.update_calc_display()

    def update_calc_display(self):
        try:
            # 尝试计算中间结果（仅用于显示，不存储）
            if any(op in self.current_calc for op in '+-*/'):
                result = eval(self.current_calc.replace('%', '/100'))
                display_text = f"{self.current_calc} = {result:.2f}"
            else:
                display_text = self.current_calc
        except:
            display_text = self.current_calc
            
        self.calc_display.setText(display_text)

    def import_to_target(self):
        try:
            # 获取计算器当前值（尝试计算表达式）
            try:
                value = str(eval(self.current_calc))
            except:
                value = self.current_calc
                
            # 根据目标选择导入
            target_idx = self.target_combo.currentIndex()
            targets = [
                self.attack_input,
                self.atk_bonus_input,
                self.base_dmg_bonus_input,
                self.elemental_bonus_input,
                self.fragile_bonus_input,
                self.crit_rate_input,
                self.crit_dmg_input,
                self.pen_resist_input
            ]
            
            # 只导入数值部分（移除可能的表达式）
            clean_value = ''.join(c for c in value if c.isdigit() or c == '.')
            if not clean_value or clean_value == '.':
                clean_value = "0"
                
            targets[target_idx].setText(clean_value)
            QMessageBox.information(self, "导入成功", 
                                  f"已将值 {clean_value} 导入到 {self.target_combo.currentText()}")
        except Exception as e:
            QMessageBox.warning(self, "导入失败", f"导入过程中出错：{str(e)}")

    def toggle_ult_groups(self, index):
        # 0 = 伤害终结技, 1 = 持续性终结技, 2 = 终结技模式2
        self.ult_buff_group.setVisible(index == 1)
        self.ult_mode2_group.setVisible(index == 2)
        
        # 显示/隐藏终结技组
        if "终结技" in self.skill_widgets:
            self.skill_widgets["终结技"]['group'].setVisible(index != 2)

    # ===== 修复：更新特殊技能倍率的方法 =====
    def update_special_multipliers(self, skill_type, hits):
        if skill_type == "special":
            container = self.special_skill_container
            spins_list = self.special_skill_spins
            values_list = self.special_skill_values
        elif skill_type == "chain":
            container = self.chain_skill_container
            spins_list = self.chain_skill_spins
            values_list = self.chain_skill_values
        else:  # basic
            container = self.basic_skill_container
            spins_list = self.basic_skill_spins
            values_list = self.basic_skill_values
        
        # 清除旧的输入框
        while container.count():
            item = container.takeAt(0)
            if item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                item.layout().deleteLater()
            elif item.widget():
                item.widget().deleteLater()
        
        # 清空控件列表
        spins_list.clear()
        
        # 确保数值列表有足够的元素
        while len(values_list) < hits:
            values_list.append(150.0)  # 添加默认值
        if len(values_list) > hits:
            values_list[:] = values_list[:hits]  # 截断多余值
        
        # 创建新的输入框
        for i in range(hits):
            h_layout = QHBoxLayout()
            h_layout.setSpacing(5)
            
            label = QLabel(f"第 {i+1} 段倍率:")
            label.setFixedWidth(80)
            h_layout.addWidget(label)
            
            spin = QDoubleSpinBox()
            spin.setRange(0, 1000)
            # 使用存储的值或默认值
            spin.setValue(values_list[i] if i < len(values_list) else 150.0)
            spin.setSingleStep(10)
            spin.setSuffix("%")
            spin.setAlignment(Qt.AlignRight)
            spin.setFixedWidth(100)
            
            # 添加值变化的信号连接
            spin.valueChanged.connect(lambda value, idx=i, s_type=skill_type: 
                                     self.update_special_value(s_type, idx, value))
            
            h_layout.addWidget(spin)
            h_layout.addStretch()
            
            container.addLayout(h_layout)
            spins_list.append(spin)

    # ===== 新增：更新特殊技能数值的方法 =====
    def update_special_value(self, skill_type, index, value):
        """当倍率值变化时更新存储的数值"""
        if skill_type == "special":
            values_list = self.special_skill_values
        elif skill_type == "chain":
            values_list = self.chain_skill_values
        else:  # basic
            values_list = self.basic_skill_values
        
        # 确保列表足够长
        while len(values_list) <= index:
            values_list.append(150.0)
        
        # 更新值
        values_list[index] = value

    # ===== 配置保存和加载 =====
    def save_config(self):
        try:
            config = {
                "character": {
                    "attack": self.attack_input.text(),
                    "atk_bonus": self.atk_bonus_input.text(),
                    "base_dmg_bonus": self.base_dmg_bonus_input.text(),
                    "elemental_bonus": self.elemental_bonus_input.text(),
                    "fragile_bonus": self.fragile_bonus_input.text(),
                    "crit_rate": self.crit_rate_input.text(),
                    "crit_damage": self.crit_dmg_input.text(),
                    "pen_resist": self.pen_resist_input.text(),
                },
                "enemy": {
                    "resist_level": self.resist_combo.currentIndex()
                },
                "ult_type": self.ult_type_combo.currentIndex(),
                "ult_buff": {
                    "attack": self.ult_buff_attack.text() if self.ult_buff_group.isVisible() else "0",
                    "damage": self.ult_buff_dmg.text() if self.ult_buff_group.isVisible() else "0"
                },
                "skills": {}
            }
            
            # 保存常规技能配置
            for skill_name, data in self.skill_widgets.items():
                config["skills"][skill_name] = {
                    "hits": data['hits'].value(),
                    "dmg_bonus": data['dmg_bonus'].text(),
                    "multipliers": [spin.value() for spin in data['multipliers']]
                }
            
            # 保存终结技模式2的配置
            if self.ult_mode2_group.isVisible():
                config["ult_mode2"] = {
                    "special_skill": {
                        "hits": self.special_skill_hits.value(),
                        "multipliers": self.special_skill_values  # 使用数值列表
                    },
                    "chain_skill": {
                        "hits": self.chain_skill_hits.value(),
                        "multipliers": self.chain_skill_values  # 使用数值列表
                    },
                    "basic_skill": {
                        "hits": self.basic_skill_hits.value(),
                        "multipliers": self.basic_skill_values  # 使用数值列表
                    }
                }
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存配置", "", "JSON 文件 (*.json);;所有文件 (*)"
            )
            
            if file_path:
                if not file_path.endswith('.json'):
                    file_path += '.json'
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "保存成功", f"配置已保存到：{file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存配置时出错：\n{str(e)}")

    def load_config(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "加载配置", "", "JSON 文件 (*.json);;所有文件 (*)"
            )
            
            if not file_path:
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 加载角色属性
            char = config.get("character", {})
            self.attack_input.setText(char.get("attack", "1000"))
            self.atk_bonus_input.setText(char.get("atk_bonus", "30"))
            self.base_dmg_bonus_input.setText(char.get("base_dmg_bonus", "20"))
            self.elemental_bonus_input.setText(char.get("elemental_bonus", "15"))
            self.fragile_bonus_input.setText(char.get("fragile_bonus", "10"))
            self.crit_rate_input.setText(char.get("crit_rate", "50"))
            self.crit_dmg_input.setText(char.get("crit_damage", "150"))
            self.pen_resist_input.setText(char.get("pen_resist", "10"))
            
            # 加载敌人抗性
            enemy = config.get("enemy", {})
            self.resist_combo.setCurrentIndex(enemy.get("resist_level", 2))
            
            # 加载终结技类型
            ult_type = config.get("ult_type", 0)
            self.ult_type_combo.setCurrentIndex(ult_type)
            
            # 加载终结技增益
            ult_buff = config.get("ult_buff", {})
            if ult_type == 1:  # 持续性终结技
                self.ult_buff_attack.setText(ult_buff.get("attack", "0"))
                self.ult_buff_dmg.setText(ult_buff.get("damage", "0"))
            
            # 加载技能配置
            skills_config = config.get("skills", {})
            for skill_name, data in self.skill_widgets.items():
                if skill_name in skills_config:
                    skill_config = skills_config[skill_name]
                    data['hits'].setValue(skill_config.get("hits", 1))
                    data['dmg_bonus'].setText(skill_config.get("dmg_bonus", "20"))
                    
                    # 更新倍率输入框
                    multipliers = skill_config.get("multipliers", [])
                    if multipliers:
                        current_hits = data['hits'].value()
                        for i, spin in enumerate(data['multipliers']):
                            if i < len(multipliers):
                                spin.setValue(multipliers[i])
            
            # 加载终结技模式2配置
            if ult_type == 2 and "ult_mode2" in config:
                mode2_config = config["ult_mode2"]
                
                # 特殊战技
                special = mode2_config.get("special_skill", {})
                self.special_skill_hits.setValue(special.get("hits", 1))
                self.special_skill_values = special.get("multipliers", [150.0])
                self.update_special_multipliers("special", self.special_skill_hits.value())
                
                # 连携技
                chain = mode2_config.get("chain_skill", {})
                self.chain_skill_hits.setValue(chain.get("hits", 1))
                self.chain_skill_values = chain.get("multipliers", [150.0])
                self.update_special_multipliers("chain", self.chain_skill_hits.value())
                
                # 普攻
                basic = mode2_config.get("basic_skill", {})
                self.basic_skill_hits.setValue(basic.get("hits", 1))
                self.basic_skill_values = basic.get("multipliers", [150.0])
                self.update_special_multipliers("basic", self.basic_skill_hits.value())
            
            QMessageBox.information(self, "加载成功", "配置已成功加载！")
        
        except Exception as e:
            QMessageBox.critical(self, "加载失败", f"加载配置时出错：\n{str(e)}")

    def load_default_config(self):
        """加载默认配置"""
        default_config = {
            "character": {
                "attack": "1000",
                "atk_bonus": "30",
                "base_dmg_bonus": "20",
                "elemental_bonus": "15",
                "fragile_bonus": "10",
                "crit_rate": "50",
                "crit_damage": "150",
                "pen_resist": "10"
            },
            "enemy": {
                "resist_level": 2  # S级 (75%)
            },
            "ult_type": 0,
            "ult_buff": {
                "attack": "0",
                "damage": "0"
            },
            "skills": {
                "普攻": {
                    "hits": 1,
                    "dmg_bonus": "20",
                    "multipliers": [150.0]
                },
                "战技": {
                    "hits": 1,
                    "dmg_bonus": "20",
                    "multipliers": [150.0]
                },
                "连携技": {
                    "hits": 1,
                    "dmg_bonus": "20",
                    "multipliers": [150.0]
                },
                "终结技": {
                    "hits": 1,
                    "dmg_bonus": "20",
                    "multipliers": [150.0]
                }
            }
        }
        
        # 应用默认配置
        self.attack_input.setText(default_config["character"]["attack"])
        self.atk_bonus_input.setText(default_config["character"]["atk_bonus"])
        self.base_dmg_bonus_input.setText(default_config["character"]["base_dmg_bonus"])
        self.elemental_bonus_input.setText(default_config["character"]["elemental_bonus"])
        self.fragile_bonus_input.setText(default_config["character"]["fragile_bonus"])
        self.crit_rate_input.setText(default_config["character"]["crit_rate"])
        self.crit_dmg_input.setText(default_config["character"]["crit_damage"])
        self.pen_resist_input.setText(default_config["character"]["pen_resist"])
        
        self.resist_combo.setCurrentIndex(default_config["enemy"]["resist_level"])
        self.ult_type_combo.setCurrentIndex(default_config["ult_type"])
        
        # 重置特殊技能数值
        self.special_skill_values = [150.0]
        self.chain_skill_values = [150.0]
        self.basic_skill_values = [150.0]
        
        # 更新UI
        self.update_special_multipliers("special", 1)
        self.update_special_multipliers("chain", 1)
        self.update_special_multipliers("basic", 1)

    # ===== 核心功能方法 =====
    def get_float(self, line_edit):
        """安全获取浮点数，处理百分比输入"""
        try:
            text = line_edit.text().replace('%', '')
            return float(text) / 100
        except:
            return 0.0

    def get_int(self, line_edit):
        """安全获取整数值"""
        try:
            return int(line_edit.text())
        except:
            return 0

    def update_multipliers(self, skill_name, hits, max_hits, layout=None):
        """动态更新倍率输入框，显示为百分比形式"""
        if layout is None:
            layout = self.skill_widgets[skill_name]['layout']
        
        # 清除旧的输入框
        while layout.count():
            item = layout.takeAt(0)
            if item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                item.layout().deleteLater()
            elif item.widget():
                item.widget().deleteLater()

        self.skill_widgets[skill_name]['multipliers'] = []
        for i in range(hits):
            h_layout = QHBoxLayout()
            h_layout.setSpacing(5)
            
            label = QLabel(f"第 {i+1} 段倍率:")
            label.setFixedWidth(80)
            h_layout.addWidget(label)
            
            spin = QDoubleSpinBox()
            spin.setRange(0, 1000)
            spin.setValue(150.0)  # 默认150% (1.5倍率)
            spin.setSingleStep(10)
            spin.setSuffix("%")
            spin.setAlignment(Qt.AlignRight)
            spin.setFixedWidth(100)
            
            h_layout.addWidget(spin)
            h_layout.addStretch()
            
            layout.addLayout(h_layout)
            self.skill_widgets[skill_name]['multipliers'].append(spin)

    # ===== 修复：计算特殊战技伤害的方法 =====
    def calculate_special_skill_damage(self, final_attack, base_dmg_bonus, elemental_bonus, fragile_bonus, ult_buff_dmg, resist_factor, crit_damage):
        """计算终结技模式2下的特殊战技伤害"""
        total_non_crit = 0
        total_crit = 0
        
        # 使用存储的数值，而不是控件
        for mult_value in self.special_skill_values:
            mult = mult_value / 100  # 从百分比转换为小数
            base_dmg = final_attack * mult
            total_bonus = 1 + base_dmg_bonus + elemental_bonus + fragile_bonus + ult_buff_dmg
            non_crit = base_dmg * total_bonus * resist_factor
            crit = non_crit * (1 + crit_damage)
            total_non_crit += non_crit
            total_crit += crit
        
        return total_non_crit, total_crit

    # ===== 修复：计算连携技伤害的方法 =====
    def calculate_chain_skill_damage(self, final_attack, base_dmg_bonus, elemental_bonus, fragile_bonus, ult_buff_dmg, resist_factor, crit_damage):
        """计算终结技模式2下的连携技伤害"""
        total_non_crit = 0
        total_crit = 0
        
        for mult_value in self.chain_skill_values:
            mult = mult_value / 100
            base_dmg = final_attack * mult
            total_bonus = 1 + base_dmg_bonus + elemental_bonus + fragile_bonus + ult_buff_dmg
            non_crit = base_dmg * total_bonus * resist_factor
            crit = non_crit * (1 + crit_damage)
            total_non_crit += non_crit
            total_crit += crit
        
        return total_non_crit, total_crit

    # ===== 修复：计算普攻伤害的方法 =====
    def calculate_basic_skill_damage(self, final_attack, base_dmg_bonus, elemental_bonus, fragile_bonus, ult_buff_dmg, resist_factor, crit_damage):
        """计算终结技模式2下的普攻伤害"""
        total_non_crit = 0
        total_crit = 0
        
        for mult_value in self.basic_skill_values:
            mult = mult_value / 100
            base_dmg = final_attack * mult
            total_bonus = 1 + base_dmg_bonus + elemental_bonus + fragile_bonus + ult_buff_dmg
            non_crit = base_dmg * total_bonus * resist_factor
            crit = non_crit * (1 + crit_damage)
            total_non_crit += non_crit
            total_crit += crit
        
        return total_non_crit, total_crit

    def calculate_damage(self):
        try:
            # 获取基础属性
            attack = self.get_int(self.attack_input)
            atk_bonus = self.get_float(self.atk_bonus_input)
            base_dmg_bonus = self.get_float(self.base_dmg_bonus_input)
            elemental_bonus = self.get_float(self.elemental_bonus_input)
            fragile_bonus = self.get_float(self.fragile_bonus_input)
            crit_rate = self.get_float(self.crit_rate_input)
            crit_damage = self.get_float(self.crit_dmg_input)
            pen_resist = self.get_float(self.pen_resist_input)

            # 获取敌人抗性
            resist_map = [0.95, 0.90, 0.75, 0.60, 0.45, 0.35, 0.25]
            enemy_base_resist = resist_map[self.resist_combo.currentIndex()]
            final_resist = max(0, enemy_base_resist - pen_resist)
            resist_factor = 1 - final_resist

            # 最终攻击力
            final_attack = attack * (1 + atk_bonus)
            
            # 终结技类型
            ult_type = self.ult_type_combo.currentIndex()
            ult_buff_attack = 0
            ult_buff_dmg = 0
            
            if ult_type == 1:  # 持续性终结技
                ult_buff_attack = self.get_float(self.ult_buff_attack)
                ult_buff_dmg = self.get_float(self.ult_buff_dmg)
                final_attack *= (1 + ult_buff_attack)

            # 准备技能伤害数据
            skill_damages = {}
            total_damage = 0
            damage_breakdown = {}  # 用于饼图数据
            
            # 遍历计算各技能伤害
            for skill_name, data in self.skill_widgets.items():
                # 跳过终结技在持续性模式或模式2下的伤害计算
                if ult_type in [1, 2] and skill_name == "终结技":
                    continue
                    
                specific_dmg_bonus = self.get_float(data['dmg_bonus'])
                multipliers = []
                
                # 处理百分比倍率输入
                for spin in data['multipliers']:
                    # 从百分比转换回小数 (如150% → 1.5)
                    multipliers.append(spin.value() / 100)
                
                total_non_crit = 0
                total_crit = 0

                for mult in multipliers:
                    base_dmg = final_attack * mult
                    # 应用所有增伤效果（包括持续性终结技增益）
                    total_bonus = 1 + base_dmg_bonus + elemental_bonus + fragile_bonus + specific_dmg_bonus + ult_buff_dmg
                    non_crit = base_dmg * total_bonus * resist_factor
                    crit = non_crit * (1 + crit_damage)
                    total_non_crit += non_crit
                    total_crit += crit

                # 伤害期望 = 非暴击伤害 × (1 + 暴击率 × 暴击伤害)
                expected_dmg = total_non_crit * (1 + crit_rate * crit_damage)
                skill_damages[skill_name] = {
                    'non_crit': total_non_crit,
                    'crit': total_crit,
                    'expected': expected_dmg
                }
                damage_breakdown[skill_name] = expected_dmg
                total_damage += expected_dmg
            
            # 处理终结技模式2的特殊技能
            if ult_type == 2:
                # 特殊战技
                special_non_crit, special_crit = self.calculate_special_skill_damage(
                    final_attack, base_dmg_bonus, elemental_bonus, fragile_bonus, ult_buff_dmg, resist_factor, crit_damage
                )
                special_expected = special_non_crit * (1 + crit_rate * crit_damage)
                
                skill_damages["特殊战技"] = {
                    'non_crit': special_non_crit,
                    'crit': special_crit,
                    'expected': special_expected
                }
                damage_breakdown["特殊战技"] = special_expected
                total_damage += special_expected
                
                # 连携技
                chain_non_crit, chain_crit = self.calculate_chain_skill_damage(
                    final_attack, base_dmg_bonus, elemental_bonus, fragile_bonus, ult_buff_dmg, resist_factor, crit_damage
                )
                chain_expected = chain_non_crit * (1 + crit_rate * crit_damage)
                
                skill_damages["连携技"] = {
                    'non_crit': chain_non_crit,
                    'crit': chain_crit,
                    'expected': chain_expected
                }
                damage_breakdown["连携技"] = chain_expected
                total_damage += chain_expected
                
                # 普攻（终结技模式2下的普攻）
                basic_non_crit, basic_crit = self.calculate_basic_skill_damage(
                    final_attack, base_dmg_bonus, elemental_bonus, fragile_bonus, ult_buff_dmg, resist_factor, crit_damage
                )
                basic_expected = basic_non_crit * (1 + crit_rate * crit_damage)
                
                skill_damages["终结技-普攻"] = {
                    'non_crit': basic_non_crit,
                    'crit': basic_crit,
                    'expected': basic_expected
                }
                damage_breakdown["终结技-普攻"] = basic_expected
                total_damage += basic_expected

            # ===== 生成结构化结果 =====
            html = "<h1>【伤害分析报告】</h1>"
            
            # 区块一：总计伤害
            html += "<h2>📊 区块一：总计伤害</h2>"
            html += f'<div class="total">总期望伤害: <span class="highlight">{total_damage:,.0f}</span></div>'
            
            # 区块二：最高伤害类型
            html += "<h2>🔥 区块二：最高伤害来源</h2>"
            if damage_breakdown:
                max_skill = max(damage_breakdown, key=damage_breakdown.get)
                max_value = damage_breakdown[max_skill]
                html += f'<div class="skill-row"><span class="skill-name">{max_skill}:</span> '
                html += f'<span class="skill-value">{max_value:,.0f}</span> '
                html += f'<span class="skill-percent">({max_value/total_damage:.1%})</span></div>'
            else:
                html += "<div>未计算任何技能伤害</div>"
            
            # 区块三：各技能详细伤害
            html += "<h2>📈 区块三：技能详细伤害</h2>"
            for skill_name, damages in skill_damages.items():
                percent = damages['expected'] / total_damage if total_damage > 0 else 0
                html += f'<div class="skill-row"><span class="skill-name">{skill_name}:</span>'
                html += f'<div class="damage-types">'
                html += f'非暴击: {damages["non_crit"]:,.0f} | '
                html += f'暴击: {damages["crit"]:,.0f} | '
                html += f'期望: {damages["expected"]:,.0f}'
                html += f'</div>'
                html += f'<span class="skill-percent">{percent:.1%}</span></div>'
            
            # 添加战斗简报
            html += "<h2>📝 战斗简报</h2>"
            html += f"<div>敌人最终抗性: {final_resist*100:.2f}%</div>"
            html += f"<div>角色最终攻击力: {final_attack:,.2f}</div>"
            if ult_type == 1:
                html += f"<div>持续性终结技增益: 攻击力+{ult_buff_attack*100:.1f}% | 伤害+{ult_buff_dmg*100:.1f}%</div>"
            elif ult_type == 2:
                html += "<div>当前为终结技模式2：使用特殊技能倍率计算</div>"
            
            self.result_output.setHtml(html)
            
            # 生成饼图
            self.generate_pie_chart(damage_breakdown, total_damage)

        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"伤害计算过程中出错：\n{str(e)}")

    def generate_pie_chart(self, damage_breakdown, total_damage):
        """生成伤害占比饼图"""
        try:
            # 清除旧的图表
            while self.chart_layout.count():
                item = self.chart_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            if not damage_breakdown or total_damage == 0:
                return
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
            
            labels = []
            sizes = []
            explode = []
            
            for skill_name, damage in damage_breakdown.items():
                percent = damage / total_damage
                if percent > 0.01:  # 只显示占比大于1%的技能
                    labels.append(f"{skill_name} ({percent:.1%})")
                    sizes.append(damage)
                    explode.append(0.05 if percent > 0.2 else 0)  # 突出显示主要伤害
            
            if not labels:
                return
            
            # 创建饼图
            colors = plt.cm.Set3(range(len(labels)))
            wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, 
                                             colors=colors, autopct='%1.1f%%',
                                             startangle=90, textprops={'fontsize': 9})
            
            ax.set_title('技能伤害占比', fontsize=12, fontweight='bold')
            ax.axis('equal')  # 确保饼图是圆形
            
            # 调整标签位置
            plt.tight_layout()
            
            # 将图表嵌入到Qt界面
            canvas = FigureCanvas(fig)
            canvas.setMinimumHeight(300)
            self.chart_layout.addWidget(canvas)
            
            # 保存图表配置
            self.current_chart = fig
            
        except Exception as e:
            print(f"生成图表时出错: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置全局样式
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(50, 50, 50))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(50, 50, 50))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(76, 175, 80))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = RPGDamageCalculator()
    window.show()
    sys.exit(app.exec())
