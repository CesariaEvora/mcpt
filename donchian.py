import pandas as pd
import numpy as np

def donchian_breakout(ohlc: pd.DataFrame, lookback: int):
    # input df is assumed to have a 'close' column
    upper = ohlc['close'].rolling(lookback - 1).max().shift(1)
    lower = ohlc['close'].rolling(lookback - 1).min().shift(1)
    signal = pd.Series(np.full(len(ohlc), np.nan), index=ohlc.index)
    signal.loc[ohlc['close'] > upper] = 1
    signal.loc[ohlc['close'] < lower] = -1
    signal = signal.ffill()
    return signal

def optimize_donchian(
    ohlc: pd.DataFrame,
    lookback_min: int = 12,
    lookback_max: int = 168,
):

    best_pf = 0
    best_lookback = -1
    r = np.log(ohlc['close']).diff().shift(-1)
    lookback_min = max(2, int(lookback_min))
    lookback_max = max(lookback_min + 1, int(lookback_max))
    for lookback in range(lookback_min, lookback_max + 1):
        signal = donchian_breakout(ohlc, lookback)
        sig_rets = signal * r
        sig_pf = sig_rets[sig_rets > 0].sum() / sig_rets[sig_rets < 0].abs().sum()

        if sig_pf > best_pf:
            best_pf = sig_pf
            best_lookback = lookback

    return best_lookback, best_pf

def walkforward_donch(
    ohlc: pd.DataFrame,
    train_lookback: int = 24 * 365 * 4,
    train_step: int = 24 * 30,
    lookback_min: int = 12,
    lookback_max: int = 168,
):

    n = len(ohlc)
    wf_signal = np.full(n, np.nan)
    tmp_signal = None
    
    next_train = train_lookback
    for i in range(next_train, n):
        if i == next_train:
            best_lookback, _ = optimize_donchian(
                ohlc.iloc[i-train_lookback:i],
                lookback_min=lookback_min,
                lookback_max=lookback_max,
            )
            tmp_signal = donchian_breakout(ohlc, best_lookback)
            next_train += train_step
        
        wf_signal[i] = tmp_signal.iloc[i]
    
    return wf_signal

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    df = pd.read_parquet('BTCUSD3600.pq')
    df.index = df.index.astype('datetime64[s]')

    df = df[(df.index.year >= 2016) & (df.index.year < 2020)] 
    best_lookback, best_real_pf = optimize_donchian(df)

    # Best lookback = 19, best_real_pf = 1.08
    
    signal = donchian_breakout(df, best_lookback) 

    df['r'] = np.log(df['close']).diff().shift(-1)
    df['donch_r'] = df['r'] * signal

    plt.style.use("dark_background")
    df['donch_r'].cumsum().plot(color='red')
    plt.title("In-Sample Donchian Breakout")
    plt.ylabel('Cumulative Log Return')
    plt.show()
