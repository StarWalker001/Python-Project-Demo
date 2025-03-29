def perform_fmea():
    """执行FMEA分析"""
    # ... FMEA数据定义 ...
    
    # 计算RPN值
    for item in fmea_data:
        item["RPN"] = item["严重度"] * item["频度"] * item["探测度"]
    
    df = pd.DataFrame(fmea_data)
    df.to_excel("d:\\PythonProject\\cooling_fmea.xlsx", index=False)
    
    return df