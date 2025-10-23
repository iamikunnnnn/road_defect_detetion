# encoding:UTF-8
import json
import requests

# 请替换XXXXXXXXXX为您的 APIpassword, 获取地址：https://console.xfyun.cn/services/bmx1
api_key = "Bearer vPcixoLwqWexNPDLRBqe:BwSelHaiiJLWJJBUYHyV"
url = "https://spark-api-open.xf-yun.com/v1/chat/completions"



# 请求模型，并将结果输出
def get_answer(message):
    #初始化请求体
    headers = {
        'Authorization':api_key,
        'content-type': "application/json"
    }
    body = {
        "model": "lite",
        "user": "user_id",

        "messages": message,
        # 下面是可选参数
        "stream": True,
        "tools": [
            {
                "type": "web_search",
                "web_search": {
                    "enable": True,
                    "search_mode":"deep"
                }
            }
        ]
    }
    full_response = ""  # 存储返回结果
    isFirstContent = True  # 首帧标识

    response = requests.post(url=url,json= body,headers= headers,stream= True)
    # print(response)
    for chunks in response.iter_lines():
        # 打印返回的每帧内容
        # print(chunks)
        if (chunks and '[DONE]' not in str(chunks)):
            data_org = chunks[6:]

            chunk = json.loads(data_org)
            text = chunk['choices'][0]['delta']

            # 判断最终结果状态并输出
            if ('content' in text and '' != text['content']):
                content = text["content"]
                if (True == isFirstContent):
                    isFirstContent = False
                print(content, end="")
                full_response += content
    return full_response


# 管理对话历史，按序编为列表
def getText(text,role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

# 获取对话中的所有角色的content长度
def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

# 判断长度是否超长，当前限制8K tokens
def checklen(text):
    while (getlength(text) > 11000):
        del text[0]
    return text

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
    prompt = f"请根据以下要求返回分析的列表- 统计每一个时间点的缺陷检出量，判断检测设备在某一时刻（如0分2秒）集中检出大量缺陷的原因（是该路段缺陷密集，还是设备在此处停留/减速导致检测频率升高）；- 分析同一时间点内重复或近似坐标的缺陷（如0分2秒内多个接近的X/Y值），推测是同一缺陷被多次识别（需优化检测算法去重），还是该位置存在密集连续的块裂（需重点养护）。数据如下：{data_str}"
    # Step 4: 管理上下文并调用模型
    question = checklen(getText(chatHistory, "user", prompt))
    print("\n星火:", end="")
    # Step 5: 保存模型回答到上下文
    answer = getText(chatHistory, "assistant", get_answer(question))
    print("\n")
    return answer
if __name__ == '__main__':

    answer = main()
    print(answer)