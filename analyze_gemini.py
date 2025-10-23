import os
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7000"
def xlsx2txt(xlsx_file="./result.xlsx"):
    import pandas as pd
    # 读取 Excel 并保存为 TXT（制表符分隔）
    df = pd.read_excel(xlsx_file)
    df.to_csv('./result.txt', sep='\t', index=False, header=True)

def read_txt(txt_file="./result.txt"):
    import pandas as pd
    # 读取 TXT 文件（指定分隔符为制表符，与保存时一致）
    df = pd.read_csv(txt_file, sep='\t')  # sep 必须和保存时的分隔符匹配
    return df  # 返回 DataFrame，方便后续处理（如按列提取数据）

def main():
    chatHistory = []

    # Step 1: Excel 转为 TXT
    xlsx2txt()
    # Step 2: 读取 TXT 文件
    txt_data = read_txt()
    data_str = txt_data.to_json(orient='records', force_ascii=False)
    print("读取的 TXT 数据：")
    print(txt_data)
    # Step 3: 组织输入文本
    prompt = f"SYSTEM ROLE:你是一名道路缺陷检测领域的计算机视觉专家，负责根据检测结果表格进行高质量的分析。你只做分析，不进行统计或计算，也不是回答我的问题，而是为你的用户讲解，所以你的语言需要确定一些，不要模棱两可让用户觉得你不专业。TASK DESCRIPTION:输入是一张检测结果表格，字段包括：- 时间- 帧号- 类别- 中心点x坐标(像素)- 中心点y坐标(像素)你的任务是：- 基于输入表格内容，输出对检测结果的逻辑性分析；- 仅进行定性推理，不输出具体统计值；- 禁止复述原表格；- 输出需具备学术性、逻辑清晰、可读性高。ANALYSIS DIMENSIONS:1. 时间维度分析     - 缺陷在时间上的出现规律（集中、分散、周期性、持续性等）。2. 帧序列模式     - 缺陷在帧序列中的持续性或间歇性；   - 是否表现为同一区域的重复检测。3. 空间分布特征     - 缺陷在图像中的相对区域分布（上/下/左/右/中心等）；   - 空间聚集或离散特征。4. 类别间关系（如存在多类缺陷）     - 时间或空间上的共现关系；   - 可能的因果或结构性相关性。OUTPUT FORMAT:仅输出文字分析，不含表格、不含数值统计。分析语言需严谨、简洁、学术化。使用自然段进行分层表达，不使用项目符号或编号。数据如下：{data_str}"


    from google import genai

    client = genai.Client(api_key="AIzaSyBgGUQQpKZX2-wGGvZexzNfWNQUWgfGoko")

    response = client.models.generate_content(
        model="models/gemini-2.0-flash",
        contents=prompt,
    )
    answer = response.text


    return answer
if __name__ == '__main__':

    answer = main()
    print(answer)
