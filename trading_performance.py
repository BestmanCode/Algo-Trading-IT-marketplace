"""

@author: Cheso7

"""

import pandas as pd
import datetime


def measure_performance(trade_data, seconds, trading_summary):
    if len(trade_data) > 0:
        # Strip Currency and , from profitAndLoss
        for i in range(len(trade_data)):
            currency = trade_data["currency"][i]
            trade_data["profitAndLoss"][i] = trade_data["profitAndLoss"][i].strip(
                currency
            )
            trade_data["profitAndLoss"][i] = trade_data["profitAndLoss"][i].replace(
                ",", ""
            )

        trading_duration = seconds / 60
        trading_date = datetime.datetime.today()

        profit_loss = trade_data["profitAndLoss"].astype(float)
        profit_loss_max = profit_loss.max()
        profit_loss_min = profit_loss.min()

        if profit_loss_max > 0:
            max_win = profit_loss_max
        else:
            max_win = 0

        if profit_loss_min < 0:
            max_loss = profit_loss_min
        else:
            max_loss = 0

        net_profit = profit_loss.sum()
        num_win = sum(n > 0 for n in profit_loss)
        num_loss = sum(n < 0 for n in profit_loss)

        def win_loss_sum(dir, profit_loss):
            s = 0
            if dir == "WIN":
                for x in profit_loss:
                    if x > 0:
                        s = s + x
            elif dir == "LOSS":
                for x in profit_loss:
                    if x < 0:
                        s = s + x
            return s

        total_win = win_loss_sum("WIN", profit_loss)
        total_loss = win_loss_sum("LOSS", profit_loss)

        try:
            r = total_win / abs(total_loss)
        except:
            r = 0

        trading_summary_current = pd.DataFrame(
            [
                [
                    trading_date.strftime("%H:%M:%S %d-%m-%Y"),
                    int(trading_duration),
                    net_profit,
                    max_win,
                    max_loss,
                    num_win,
                    num_loss,
                    r,
                ]
            ],
            columns=[
                "Date",
                "Duration (min)",
                "Net Profit",
                "Max Win",
                "Max Loss",
                "Winners",
                "Losers",
                "R Factor",
            ],
        )
        trading_summary = trading_summary.append(
            trading_summary_current, ignore_index=True
        )

    return trading_summary
