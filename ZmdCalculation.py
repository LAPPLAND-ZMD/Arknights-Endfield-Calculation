import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QFormLayout, QGroupBox, QLabel, 
                               QLineEdit, QComboBox, QPushButton, QTextEdit, 
                               QScrollArea, QMessageBox, QDoubleSpinBox, QSpinBox)

class RPGDamageCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RPG 伤害计算工具 - 竖向段数版")
        self.resize(1200, 650)  # 适当加大窗口尺寸

        # 创建主界面布局（横向排列）
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # ================== 左侧模块：角色属性 + 敌人抗性 ==================
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 5, 0)

        # 1. 角色基础属性
        base_group = QGroupBox("🛡️ 角色基础属性")
        base_layout = QFormLayout()
        input_width = 110
        self.attack_input = QLineEdit("1000"); self.attack_input.setFixedWidth(input_width)
        self.atk_bonus_input = QLineEdit("30"); self.atk_bonus_input.setFixedWidth(input_width)
        self.base_dmg_bonus_input = QLineEdit("20"); self.base_dmg_bonus_input.setFixedWidth(input_width)
        self.elemental_bonus_input = QLineEdit("15"); self.elemental_bonus_input.setFixedWidth(input_width)
        self.fragile_bonus_input = QLineEdit("10"); self.fragile_bonus_input.setFixedWidth(input_width)
        self.crit_rate_input = QLineEdit("50"); self.crit_rate_input.setFixedWidth(input_width)
        self.crit_dmg_input = QLineEdit("150"); self.crit_dmg_input.setFixedWidth(input_width)
        self.pen_resist_input = QLineEdit("10"); self.pen_resist_input.setFixedWidth(input_width)

        base_layout.addRow("基础攻击力:", self.attack_input)
        base_layout.addRow("攻击力提升%:", self.atk_bonus_input)
        base_layout.addRow("基础增幅%:", self.base_dmg_bonus_input)
        base_layout.addRow("属性伤害增幅%:", self.elemental_bonus_input)
        base_layout.addRow("脆弱% (特殊增幅):", self.fragile_bonus_input)
        base_layout.addRow("暴击率%:", self.crit_rate_input)
        base_layout.addRow("暴击伤害%:", self.crit_dmg_input)
        base_layout.addRow("无视敌方抗性%:", self.pen_resist_input)
        base_group.setLayout(base_layout)
        left_layout.addWidget(base_group)

        # 2. 敌人抗性 (移动到下方)
        resist_group = QGroupBox("👹 敌人抗性选择")
        resist_layout = QVBoxLayout() # 改为竖向布局
        self.resist_combo = QComboBox()
        self.resist_combo.addItems(["SSS级 (95%)", "SS级 (90%)", "S级 (75%)", 
                                    "A级 (60%)", "B级 (45%)", "C级 (35%)", "D级 (25%)"])
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("抗性等级:"))
        h_layout.addWidget(self.resist_combo)
        resist_layout.addLayout(h_layout)
        resist_group.setLayout(resist_layout)
        left_layout.addWidget(resist_group)
        
        left_layout.addStretch() # 弹性空间，让左侧控件靠上
        main_layout.addWidget(left_column)

        # ================== 中间模块：技能配置 (加大空间) ==================
        middle_column = QWidget()
        middle_layout = QVBoxLayout(middle_column)
        middle_layout.setContentsMargins(5, 0, 5, 0)

        skill_group = QGroupBox("⚔️ 技能配置")
        skill_outer_layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.skill_widgets = {}
        skills = [("普攻", 9), ("战技", 12), ("连携技", 4), ("终结技", 20)]
        
        for skill_name, max_hits in skills:
            group = QGroupBox(f"{skill_name} (最多{max_hits}段)")
            layout = QVBoxLayout() # 技能内部也改为竖向布局
            
            # 顶部控制栏
            top_control = QHBoxLayout()
            dmg_bonus = QLineEdit("20")
            dmg_bonus.setFixedWidth(80)
            hits_spin = QSpinBox()
            hits_spin.setRange(1, max_hits)
            hits_spin.setValue(1)
            hits_spin.setFixedWidth(60)
            hits_spin.valueChanged.connect(lambda val, s=skill_name: self.update_multipliers(s, val, max_hits))
            
            top_control.addWidget(QLabel("增伤%:"))
            top_control.addWidget(dmg_bonus)
            top_control.addWidget(QLabel("段数:"))
            top_control.addWidget(hits_spin)
            top_control.addStretch()
            
            layout.addLayout(top_control)
            
            # 存放倍率输入框的容器
            multiplier_container = QVBoxLayout()
            self.skill_widgets[skill_name] = {'hits': hits_spin, 'multipliers': []}
            self.update_multipliers(skill_name, 1, max_hits, multiplier_container) # 初始化
            
            layout.addLayout(multiplier_container)
            group.setLayout(layout)
            scroll_layout.addWidget(group)
            
            self.skill_widgets[skill_name]['dmg_bonus'] = dmg_bonus
            self.skill_widgets[skill_name]['layout'] = multiplier_container

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        skill_outer_layout.addWidget(scroll)
        skill_group.setLayout(skill_outer_layout)
        middle_layout.addWidget(skill_group)
        main_layout.addWidget(middle_column) # 中间区域会自动拉伸占满空间

        # ================== 右侧模块：操作与结果 ==================
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(5, 0, 0, 0)
        right_column.setFixedWidth(320) # 限制右侧宽度，让中间更宽敞

        self.calc_btn = QPushButton("🚀 开始计算伤害")
        self.calc_btn.setStyleSheet("font-size: 16px; padding: 12px; background-color: #4CAF50; color: white; font-weight: bold;")
        self.calc_btn.clicked.connect(self.calculate_damage)

        result_group = QGroupBox("📊 计算结果")
        result_layout = QVBoxLayout()
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("点击左侧的计算按钮，伤害结果将显示在这里...")
        result_layout.addWidget(self.result_output)
        result_group.setLayout(result_layout)

        right_layout.addWidget(self.calc_btn)
        right_layout.addWidget(result_group)
        main_layout.addWidget(right_column)

    def update_multipliers(self, skill_name, hits, max_hits, layout=None):
        """动态更新倍率输入框，改为竖向排列"""
        if layout is None:
            layout = self.skill_widgets[skill_name]['layout']
        
        # 清除旧的输入框
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.skill_widgets[skill_name]['multipliers'] = []
        for i in range(hits):
            h_layout = QHBoxLayout()
            label = QLabel(f"第 {i+1} 段:")
            label.setFixedWidth(50)
            spin = QDoubleSpinBox()
            spin.setRange(0, 100)
            spin.setValue(1.5)
            spin.setSingleStep(0.1)
            
            h_layout.addWidget(label)
            h_layout.addWidget(spin)
            h_layout.addStretch()
            
            layout.addLayout(h_layout)
            self.skill_widgets[skill_name]['multipliers'].append(spin)

    def get_float(self, line_edit):
        """安全获取浮点数"""
        try:
            return float(line_edit.text()) / 100
        except:
            return 0.0

    def calculate_damage(self):
        try:
            # 获取基础属性
            attack = float(self.attack_input.text())
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

            output_text = f"【战斗简报】\n敌人最终抗性: {final_resist*100:.2f}%\n角色最终攻击力: {final_attack:.2f}\n" + "=" * 40 + "\n"

            # 遍历计算各技能伤害
            for skill_name, data in self.skill_widgets.items():
                specific_dmg_bonus = self.get_float(data['dmg_bonus'])
                multipliers = [spin.value() for spin in data['multipliers']]
                
                total_non_crit = 0
                total_crit = 0

                for mult in multipliers:
                    base_dmg = final_attack * mult
                    total_bonus = 1 + base_dmg_bonus + elemental_bonus + fragile_bonus + specific_dmg_bonus
                    non_crit = base_dmg * total_bonus * resist_factor
                    crit = non_crit * (1 + crit_damage)
                    total_non_crit += non_crit
                    total_crit += crit

                expected_dmg = total_non_crit * (1 + crit_rate * crit_damage)

                output_text += f"\n【{skill_name}】 (共 {len(multipliers)} 段):\n"
                output_text += f"  总非暴击伤害: {total_non_crit:,.2f}\n"
                output_text += f"  总暴击伤害:   {total_crit:,.2f}\n"
                output_text += f"  伤害期望值:   {expected_dmg:,.2f}\n"

            self.result_output.setText(output_text)

        except Exception as e:
            QMessageBox.critical(self, "输入错误", f"请检查输入是否为有效数字！\n报错信息: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RPGDamageCalculator()
    window.show()
    sys.exit(app.exec())
