from pandas import Series, to_datetime
import pandas_ta as ta
import numpy as np

def flux_oscillator(df,
    # Crypto-specific hardcoded parameters
    adxlen=10, rsi_length=12, atr_period=10,
    cmf_period=14, norm_lookback=30, w_trend=0.2,
    w_momentum=0.3, w_volatility=0.3, w_volume=0.2,
    delta_smoothing=3, use_adaptive_weights=True,
    buy_threshold=25, sell_threshold=-25,
    peak_threshold=35, early_delta_threshold=0.5,
    volatility_regime_threshold=0.025,
    **kwargs
):
    # Validate input series
    close = ta.utils.verify_series(df['close'])
    high = ta.utils.verify_series(df['high'])
    low = ta.utils.verify_series(df['low'])
    volume = ta.utils.verify_series(df['volume'])
    
    # ===== Core Indicators =====
    # ADX and Directional Movement
    adx_data = ta.adx(high, low, close, length=adxlen)
    adx = adx_data[f'ADX_{adxlen}']
    plusDi = adx_data[f'DMP_{adxlen}']
    minusDi = adx_data[f'DMN_{adxlen}']
    
    # RSI Momentum
    rsidf = ta.multi_rsi((high+low+2*close)/4)
    df['RSI'] = rsidf[f'RSI']
    df['RSIMA'] = ta.wma(df['RSI'], length=rsi_length)
    df['upper'] = rsidf['upper']
    df['lower'] = rsidf['lower']
    # df['RSI_Region'] = rsidf[f'ULT_RSI_{rsi_length}_A_50'] - rsidf[f'ULT_RSI_{rsi_length}_B_50']
    
    # ATR Volatility
    df['ATR'] = ta.atr(high, low, close, length=atr_period)
    
    # Chaikin Money Flow
    cmf = ta.cmf(high, low, close, volume, length=cmf_period)
    # ===== Normalized Components =====
    # Trend Component
    di_diff = plusDi - minusDi
    adx_scaled = ((adx - 20) / 20).clip(0, 1)
    norm_trend = di_diff * adx_scaled
    
    # Momentum Component
    norm_mom = (df['RSI'] - 50) / 50
    
    # Volatility Component
    atr_ratio = df['ATR'] / close
    roll_min = atr_ratio.rolling(norm_lookback).min()
    roll_max = atr_ratio.rolling(norm_lookback).max()
    nor_volatility = 2 * ((atr_ratio - roll_min) / 
                               (roll_max - roll_min + 1e-7)) - 1
    
    # Volume Component
    norm_vol = cmf.clip(-1, 1)
    
    # ===== Adaptive Weights =====
    if use_adaptive_weights:
        dyn_trend = np.where(adx > 25, w_trend * 1.5, w_trend * 0.75)
        dyn_volatility = np.where(
            atr_ratio > volatility_regime_threshold, 
            w_volatility * 2.0, 
            w_volatility * 0.5
        )
        dyn_mom = np.where(
            np.abs(df['RSI'] - 50) > 30, 
            w_momentum * 1.2, 
            w_momentum * 0.8
        )
        weights = [
            dyn_trend,
            dyn_mom,
            dyn_volatility,
            w_volume
        ]
        total_weight = sum([w.mean() if isinstance(w, Series) else w for w in weights])
    else:
        weights = [w_trend, w_momentum, w_volatility, w_volume]
        total_weight = sum(weights)
    
    # ===== Flux Oscillator =====
    weighted_sum = (
        weights[0] * norm_trend +
        weights[1] * norm_mom +
        weights[2] * nor_volatility +
        weights[3] * norm_vol
    )
    df['flux'] = (weighted_sum / total_weight) * 100
    
    # ===== Oscillator Features =====
    # Moving Average
    df['flux_ma'] = ta.ema(df['flux'], length=10)
    
    # Delta Calculations
    oscDelta = df['flux'].diff()
    oscDeltaSmooth = ta.sma(oscDelta, length=delta_smoothing)
    
    # Dynamic Bands
    band_length = 20
    df['basis'] = ta.ema(df['flux'], length=band_length)
    dev = ta.stdev(df['flux'], band_length) * 1.5
    df['upper_band'] = df['basis'] + dev
    df['lower_band'] = df['basis'] - dev
    
    # ===== Signal Generation =====
    # Trend Direction
    trendDir = np.where(plusDi > minusDi, 1, -1)
    
    # Advanced Signal Conditions
    conditions = [
        # Strong Buy/Sell
        (df['flux'] > peak_threshold) & (trendDir == 1),
        (df['flux'] < -peak_threshold) & (trendDir == -1),
        
        # Early Signals
        (oscDeltaSmooth > early_delta_threshold) &
        (df['flux'] < buy_threshold) & (trendDir == 1),
        
        (oscDeltaSmooth < -early_delta_threshold) &
        (df['flux'] > sell_threshold) & (trendDir == -1),
        
        # Momentum Peaks
        (df['flux'] > buy_threshold) & 
        (oscDeltaSmooth < 0) & (trendDir == 1),
        
        (df['flux'] < sell_threshold) & 
        (oscDeltaSmooth > 0) & (trendDir == -1),
        
        # Pullback Signals
        (df['flux'].between(sell_threshold, buy_threshold)) & 
        (norm_trend > 0.2) & (trendDir == 1),
        
        (df['flux'].between(sell_threshold, buy_threshold)) & 
        (norm_trend < -0.2) & (trendDir == -1),
        
        # Neutral Condition
        (df['flux'].between(sell_threshold, buy_threshold)) &
        (norm_trend.abs() <= 0.2)
    ]
    
    choices = [
        'Strong Buy', 'Strong Sell',
        'Early Buy - Momentum Building', 'Early Sell - Momentum Building',
        'Momentum Peak - Consider Exit', 'Momentum Peak - Consider Exit',
        'Pullback Buy - Re-entry', 'Pullback Sell - Re-entry',
        'No Trade'
    ]
    
    df['Advanced Signal'] = np.select(conditions, choices, default='No Trade')
    
    # ===== Market Regime =====
    # Strength Classification
    regime_strength = np.select(
        [
            adx < 20,
            (adx >= 20) & (adx < 30),
            adx >= 30
        ],
        ['Neutral', 'Weak Trend', 'Strong Trend'],
        default='Neutral'
    )
    
    # Direction Classification
    regime_direction = np.where(trendDir == 1, 'Bullish', 'Bearish')
    regime_strength_series = Series(regime_strength, index=df.index, name='strength')
    regime_direction_series = Series(regime_direction, index=df.index, name='direction')
    # Combined Regime
    df['Regime'] = np.where(
        regime_strength_series == 'Neutral',
        'Neutral',
        regime_strength_series.str.cat(regime_direction_series, sep=' - ')
    )
    
    # ===== Dashboard Metrics =====
    df['Basic Signal'] = np.select(
        [df['flux'] > buy_threshold, df['flux'] < sell_threshold],
        ['Buy', 'Sell'],
        default='Neutral'
    )
    
    df['Trend'] = np.where(plusDi > minusDi, 'Bullish', 'Bearish')
    df['Momentum'] = np.select(
        [df['RSI'] > 70, df['RSI'] < 30, df['RSI'].between(30,70)],
        ['Overbought', 'Oversold', 'Neutral']
    )
    df['Volume Pressure'] = np.where(cmf > 0, 'Bullish', 'Bearish')
    
    # ===== Cleanup =====
    del dyn_trend, dyn_volatility, dyn_mom, regime_strength, regime_direction
    df.dropna(inplace=True)
    return df
