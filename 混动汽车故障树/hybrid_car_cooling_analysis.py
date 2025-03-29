import pandas as pd
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
import os
import sys
import ctypes
from anytree import PreOrderIter  # 添加到文件顶部的导入部分

# 初始化输出目录
os.makedirs("d:\\PythonProject\\混动汽车故障树\\output", exist_ok=True)

def build_fault_tree():
    """构建完整的冷却系统故障树"""
    root = Node("冷却系统失效")
    
    # 第一层故障模式
    pump_failure = Node("水泵故障", parent=root)
    fan_failure = Node("散热风扇故障", parent=root)
    sensor_failure = Node("温度传感器故障", parent=root)
    leak_failure = Node("冷却液泄漏", parent=root)
    
    # 水泵故障子节点
    Node("电机烧毁", parent=pump_failure)
    Node("叶轮损坏", parent=pump_failure)
    Node("电路短路", parent=pump_failure)
    Node("轴承磨损", parent=pump_failure)
    
    # 风扇故障子节点
    Node("电机故障", parent=fan_failure)
    Node("轴承磨损", parent=fan_failure)
    Node("控制模块失效", parent=fan_failure)
    
    # 传感器故障子节点
    Node("信号漂移", parent=sensor_failure)
    Node("连接器松动", parent=sensor_failure)
    
    # 泄漏故障子节点
    Node("管路破裂", parent=leak_failure)
    Node("密封圈老化", parent=leak_failure)
    
    # 生成文本格式故障树
    with open("d:\\PythonProject\\混动汽车故障树\\output\\cooling_fta.txt", "w", encoding="utf-8") as f:
        for pre, _, node in RenderTree(root):
            f.write(f"{pre}{node.name}\n")
    
    # 生成图形格式故障树
    try:
        # 检查Graphviz安装路径
        graphviz_path = r"D:\Graphviz\bin"
        if os.path.exists(graphviz_path):
            if graphviz_path not in os.environ["PATH"]:
                os.environ["PATH"] = graphviz_path + os.pathsep + os.environ["PATH"]
        else:
            raise Exception(f"未找到Graphviz安装路径: {graphviz_path}")
            
        # 验证dot命令是否可用
        try:
            from subprocess import run, PIPE
            result = run(['dot', '-V'], stdout=PIPE, stderr=PIPE)
            if result.returncode != 0:
                raise Exception("Graphviz未正确安装")
        except Exception as e:
            raise Exception(f"Graphviz验证失败: {str(e)}")
            
        # 修改为直接生成到目标文件，避免使用临时文件
        # 设置自定义临时目录
        temp_dir = "d:\\PythonProject\\混动汽车故障树\\temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 显式设置目录权限（完全控制）
        try:
            # 添加额外的权限验证
            if not os.access(temp_dir, os.W_OK | os.X_OK):
                os.system(f'icacls "{temp_dir}" /grant "Everyone:(OI)(CI)F" /T')
                os.system(f'icacls "{temp_dir}" /grant "Users:(OI)(CI)F" /T')
                os.system(f'icacls "{temp_dir}" /grant "*S-1-5-32-545:(OI)(CI)F" /T')
                
                # 再次验证权限
                if not os.access(temp_dir, os.W_OK | os.X_OK):
                    raise Exception("临时目录权限设置失败")
        except Exception as perm_error:
            print(f"权限设置警告: {str(perm_error)}")
            raise Exception("无法设置临时目录权限，请手动设置或使用管理员权限运行")
        
        # 强制设置临时文件位置
        import tempfile
        tempfile.tempdir = temp_dir
        os.environ["TEMP"] = temp_dir
        os.environ["TMP"] = temp_dir
        
        # 测试临时目录是否可写
        test_file = os.path.join(temp_dir, "testfile.tmp")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            print(f"临时目录测试失败: {str(e)}")
            raise Exception("临时目录不可写，请检查权限设置")
            
        # 添加dot命令的显式路径
        dot_path = os.path.join(graphviz_path, "dot.exe")
        if not os.path.exists(dot_path):
            raise Exception(f"未找到dot.exe: {dot_path}")
            
        output_path = "d:\\PythonProject\\混动汽车故障树\\output\\cooling_fta.png"
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except PermissionError:
                print(f"无法删除旧文件 {output_path}，请手动删除")
                return root
                
        # 修改DotExporter调用方式
        dot_file = os.path.join(temp_dir, "temp_graph.dot")
        png_file = "d:\\PythonProject\\混动汽车故障树\\output\\cooling_fta.png"
        
        try:
            # 先导出为dot文件
            DotExporter(
                root,
                nodeattrfunc=lambda node: f'label="{node.name}" fontname="Microsoft YaHei"',
                options=['-Gcharset=utf-8', '-Grankdir=TB']  # 添加布局方向选项
            ).to_dotfile(dot_file)
            
            # 检查生成的DOT文件内容
            with open(dot_file, 'r', encoding='utf-8') as f:
                dot_content = f.read()
                if not dot_content.startswith('digraph'):
                    raise Exception("生成的DOT文件格式不正确")
            
            # 再转换为png
            os.system(f'dot -Tpng "{dot_file}" -o "{png_file}"')
            
            # 清理临时文件
            if os.path.exists(dot_file):
                os.remove(dot_file)
        except Exception as e:
            print(f"图形生成失败: {str(e)}")
            if os.path.exists(dot_file):
                print("生成的DOT文件内容:")
                with open(dot_file, 'r', encoding='utf-8') as f:
                    print(f.read())
                os.remove(dot_file)

        # 手动构建DOT文件内容
        dot_content = 'digraph tree {\n'
        dot_content += '    node [fontname="Microsoft YaHei"];\n'
        dot_content += '    edge [fontname="Microsoft YaHei"];\n'
        
        # 添加节点定义
        for node in PreOrderIter(root):
            dot_content += f'    "{id(node)}" [label="{node.name}"];\n'
        
        # 添加边定义
        for node in PreOrderIter(root):
            if not node.is_root:
                dot_content += f'    "{id(node.parent)}" -> "{id(node)}";\n'
        
        dot_content += '}\n'
        
        # 写入文件
        with open(dot_file, 'w', encoding='utf-8') as f:
            f.write(dot_content)
            
        # 转换为png
        os.system(f'dot -Tpng "{dot_file}" -o "{png_file}"')
            
            # 清理临时文件
            if os.path.exists(dot_file):
                os.remove(dot_file)
        except Exception as e:
            print(f"图形生成失败: {str(e)}")
            if os.path.exists(dot_file):
                print("生成的DOT文件内容:")
                with open(dot_file, 'r', encoding='utf-8') as f:
                    print(f.read())
                os.remove(dot_file)

    except Exception as e:
        print(f"图形生成失败: {str(e)}")
        if "Permission denied" in str(e):
            print("请执行以下操作：")
            print("1. 手动创建目录: d:\\PythonProject\\混动汽车故障树\\temp")
            print("2. 右键该目录 → 属性 → 安全 → 编辑 → 添加当前用户并赋予完全控制权限")
            print("3. 关闭所有可能占用文件的程序")
            print("4. 以管理员身份运行Python脚本")
        print("解决方案：")
        print("1. 从 https://graphviz.org/download/ 下载安装Graphviz")
        print("2. 安装时勾选'Add Graphviz to the system PATH'选项")
        print("3. 或手动将Graphviz的bin目录添加到系统PATH环境变量")
    
    return root

# 创建目录（放在代码开头）
os.makedirs("d:\\PythonProject\\混动汽车故障树\\data", exist_ok=True)
os.makedirs("d:\\PythonProject\\混动汽车故障树\\output", exist_ok=True)

def perform_fmea():
    """执行FMEA分析"""
    fmea_data = [
        {"项目": "电子水泵", "功能": "冷却液循环", "潜在失效模式": "流量不足",
         "潜在影响": "系统过热", "严重度": 8, "频度": 3, "探测度": 4,
         "RPN": 0, "建议措施": "增加流量传感器"},
         
        {"项目": "散热风扇", "功能": "散热器冷却", "潜在失效模式": "转速异常",
         "潜在影响": "散热不足", "严重度": 7, "频度": 4, "探测度": 5,
         "RPN": 0, "建议措施": "改进控制算法"},
         
        {"项目": "温度传感器", "功能": "温度监测", "潜在失效模式": "读数偏差",
         "潜在影响": "误报警", "严重度": 5, "频度": 6, "探测度": 7,
         "RPN": 0, "建议措施": "双传感器冗余设计"},
         
        {"项目": "冷却管路", "功能": "冷却液输送", "潜在失效模式": "泄漏",
         "潜在影响": "冷却不足", "严重度": 9, "频度": 2, "探测度": 3,
         "RPN": 0, "建议措施": "定期检查更换"}
    ]
    
    # 计算RPN值
    for item in fmea_data:
        item["RPN"] = item["严重度"] * item["频度"] * item["探测度"]
    
    df = pd.DataFrame(fmea_data)
    
    # 修改为输出到output目录
    df.to_excel("d:\\PythonProject\\混动汽车故障树\\output\\cooling_fmea.xlsx", index=False)
    
    return df

def generate_report(fmea_df):
    """生成完整的分析报告"""
    report = f"""
    混动汽车电动冷却系统可靠性分析报告
    =================================
    
    1. 系统概述
    ----------
    本报告针对混动车型的电动冷却系统进行可靠性分析，
    包含水泵、散热风扇、温度传感器和冷却管路等关键部件。
    """
    
    # 添加故障树分析结果
    report += "\n2. 故障树分析\n-----------\n"
    root = build_fault_tree()
    for pre, _, node in RenderTree(root):
        report += f"{pre}{node.name}\n"
    
    # 添加FMEA分析结果
    report += "\n3. FMEA分析结果\n------------\n"
    report += fmea_df.sort_values("RPN", ascending=False).to_markdown()
    
    # 添加改进建议
    report += """
    
    4. 改进建议
    ----------
    1) 优先处理RPN>100的失效模式
    2) 对关键部件实施预防性维护
    3) 增加系统监控和报警功能
    """
    
    with open("d:\\PythonProject\\混动汽车故障树\\output\\analysis_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    print("开始执行混动汽车冷却系统可靠性分析...")
    
    # 执行FMEA分析
    fmea_results = perform_fmea()
    
    # 生成报告
    generate_report(fmea_results)
    
    print("分析完成，结果已保存在output目录")