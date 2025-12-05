import requests
import pandas as pd
from io import StringIO


def get_ercot_hb_west_prices(url: str) -> dict:
    """
    抓取 ERCOT 网页上的 DAM 结算点价格，并提取 HB_WEST 节点每小时的电价。

    Args:
        url: ERCOT 日内市场价格页面的 URL。

    Returns:
        一个字典，包含小时（Hour Ending）和对应的 HB_WEST 电价。
        如果抓取或解析失败，则返回空字典。
    """
    try:
        # 1. 使用 requests 获取网页内容
        response = requests.get(url, timeout=15)
        response.raise_for_status()  # 检查请求是否成功

        # 2. 使用 pandas 的 read_html 解析表格
        # read_html 会自动查找页面中的 <table> 标签并将其转换为 DataFrame 列表
        # 由于表格可能包含 HTML 实体（如 &nbsp;），使用 lxml 解析器更稳定
        tables = pd.read_html(StringIO(response.text), flavor='lxml')

        # 3. 识别正确的表格 (通常是页面上的第一个大表格)
        # 我们寻找列名中包含 'HB_WEST' 的表格
        target_df = None
        for df in tables:
            if 'HB_WEST' in df.columns:
                target_df = df
                break

        if target_df is None:
            print("错误：未在页面中找到包含 'HB_WEST' 数据的表格。")
            return {}

        # 4. 数据清洗和提取
        # 确保 'Hour Ending' 和 'HB_WEST' 列存在
        if 'Hour Ending' not in target_df.columns or 'HB_WEST' not in target_df.columns:
            print("错误：表格中缺失必要的列 ('Hour Ending' 或 'HB_WEST')。")
            return {}

        # 筛选出我们需要的两列，并将它们转换为字典
        price_data = target_df[['Hour Ending', 'HB_WEST']].set_index('Hour Ending').to_dict()['HB_WEST']

        # 5. 格式化输出（将键转换为整数小时，值转换为浮点数，并移除可能的 NaN）
        # 注意：数据抓取时值可能是字符串，需要转换
        final_prices = {}
        for hour, price_str in price_data.items():
            try:
                hour_int = int(hour)
                price_float = float(price_str)
                final_prices[hour_int] = price_float
            except ValueError:
                # 忽略无法转换的数据（例如表头或无效行）
                continue

        return final_prices

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return {}
    except Exception as e:
        print(f"解析或处理数据时发生错误: {e}")
        return {}


# 您的目标 URL
url = "https://www.ercot.com/content/cdr/html/20251205_dam_spp.html"

# 执行抓取
hb_west_prices = get_ercot_hb_west_prices(url)
if __name__ == "__main__":
# 打印结果
    if hb_west_prices:
        print(f"--- ERCOT HB_WEST 20251205 每小时电价 ---")
        for hour, price in hb_west_prices.items():
            print(f"小时 {hour:02d}: ${price:.2f}")
    else:
        print("未能成功获取电价数据。")

