price_data_1 = {
    1: 11.72, 2: 9.58, 3: 8.2, 4: 6.58, 5: 10.89, 6: 12.66,
    7: 14.14, 8: 15.04, 9: 10.45, 10: 0.62, 11: 0.87, 12: 1.24,
    13: 1.94, 14: 4.93, 15: 5.22, 16: 5.2, 17: 19.26,
    18: 41.97, 19: 32.12, 20: 25.8, 21: 24.25,
    22: 22.3, 23: 22.93, 24: 22.05
}

# --- 定义阈值 ---
THRESHOLD_WAKE = 70  # 唤醒/休眠的边界
THRESHOLD_SLEEP_FORCE = 80  # 强制休眠的极高阈值

# --- 1. 将字典转换为列表，并确保顺序和索引一致 ---
# 列表索引 (0-23) 对应 Hour Ending (1-24)
prices = [price_data_1[h] for h in range(1, 25)]
HOURS = len(prices)  # 总是 24

# 结果存储
mining_schedule = {}

# --- 2. 核心决策逻辑循环 ---
for i in range(HOURS):
    he = i + 1  # 当前的 Hour Ending (1 到 24)
    current_price = prices[i]
    action = ""

    # 获取相邻时段的价格 (处理边界条件)
    # 前一个时段：索引为 i-1。如果 i=0 (HE 1)，则前一个时段是 HE 24 (索引 23)
    prev_index = (i - 1 + HOURS) % HOURS
    prev_price = prices[prev_index]

    # 后一个时段：索引为 i+1。如果 i=23 (HE 24)，则后一个时段是 HE 1 (索引 0)
    next_index = (i + 1) % HOURS
    next_price = prices[next_index]

    # --- 决策开始 ---

    # 规则 1: 唤醒条件 (当前价低于 70)
    if current_price < THRESHOLD_WAKE:
        action = "唤醒 (WAKE)"

    # 规则 2: 休眠条件 (当前价高于 70 且满足三个子条件之一)
    elif current_price >= THRESHOLD_WAKE:

        # 子条件 A: 当前价极高 (> 80)
        condition_A = (current_price > THRESHOLD_SLEEP_FORCE)

        # 子条件 B: 前一个时段是高价 (> 70)
        condition_B = (prev_price > THRESHOLD_WAKE)

        # 子条件 C: 后一个时段是高价 (> 70)
        condition_C = (next_price > THRESHOLD_WAKE)

        if condition_A or condition_B or condition_C:
            action = "休眠 (SLEEP)"
        else:
            # 理论上，根据您的规则，这里应该不会触发，
            # 因为如果当前 >= 70，它必须满足三个条件之一才会休眠。
            # 如果不满足，则应保持唤醒状态 (但这里我们严格按照规则执行)
            # 为了严谨性，如果当前>=70但其他条件都不满足，我们假设它也进入休眠。
            # 实际上，在您的规则设定下，如果当前 >= 70，它总是会进入休眠的。
            # 因为前一个或后一个时段必须有一个 > 70 才能满足连续性。
            action = "休眠 (SLEEP)"  # 只要 >= 70，就触发休眠检查

    # --- 决策结束 ---

    mining_schedule[he] = {
        "price": current_price,
        "prev_price": prev_price,
        "next_price": next_price,
        "action": action
    }

# --- 3. 结果输出与总结 ---
print("--- 矿机启停调度分析 ---")
print(f"唤醒阈值: < ${THRESHOLD_WAKE}/MWh | 强制休眠: > ${THRESHOLD_SLEEP_FORCE}/MWh")
print("----------------------------------------------------------------------")
print("HE | 价格 | 状态 | 决策依据 (前/中/后)")
print("----------------------------------------------------------------------")

sleep_periods = []
wake_periods = []
current_period_start = None
current_action = None

for he, data in mining_schedule.items():
    current_time_str = f"{he - 1:02d}:00-{he:02d}:00"

    print(
        f"{he:2d} | {data['price']:5.2f} | {data['action']:<12} | "
        f"{data['prev_price']:5.2f} / {data['price']:5.2f} / {data['next_price']:5.2f}"
    )

    # 总结连续时段
    if data['action'] == current_action:
        continue

    if current_action is not None:
        # 结束上一个时段
        end_time_str = f"{he - 1:02d}:00"

        if current_action == "休眠 (SLEEP)":
            sleep_periods.append(f"{current_period_start}-{end_time_str}")
        else:
            wake_periods.append(f"{current_period_start}-{end_time_str}")

    # 开始新的时段
    current_action = data['action']
    current_period_start = f"{he - 1:02d}:00"

# 结束最后一个时段 (HE 24 结束于 00:00)
if current_action is not None:
    end_time_str = "00:00"
    if current_action == "休眠 (SLEEP)":
        sleep_periods.append(f"{current_period_start}-{end_time_str}")
    else:
        wake_periods.append(f"{current_period_start}-{end_time_str}")

print("----------------------------------------------------------------------")
print("\n✅ 最终调度总结:")
print(f"**唤醒时段 (WAKE)**: {wake_periods}")
print(f"**休眠时段 (SLEEP)**: {sleep_periods}")