from pandas import Series, DataFrame

# Add BoS and CHoCh logic using price

def swings(df, internal_shift_mode="High/Low", lookback=1000):
    """
    Detects Swing Highs (HH/LH) and Lows (LL/HL) based on price structure
    """
    # Initialize columns
    swings = DataFrame(dtype="string")
    position_map = {'LH': 'above', 'LL': 'below', 'HH': 'above', 'HL': 'below'}
    color_map = {'LH': '#00bd84', 'LL': '#f24e53', 'HH': '#00bd84', 'HL': '#f24e53'}
    shape_map = {'LH': 'arrow_down', 'LL': 'arrow_up', 'HH': 'arrow_down', 'HL': 'arrow_up'}
    swing_type_series = Series(index=df.index, dtype="string")  # Initialize empty series
    
    # State tracking variables
    last_internal_shift = 0
    last_bullish_shift_bar = None
    last_bearish_shift_bar = None
    prev_swing_high = None
    prev_swing_low = None
    
    # Track bullish/bearish streaks
    is_bullish = df['close'] > df['open']
    is_bearish = df['close'] < df['open']
    
    # Streak counters
    bullish_count = 0
    bearish_count = 0
    lowest_bullish_price = None
    highest_bearish_price = None
    first_bullish_open = None
    first_bearish_open = None

    for i, (index, row) in enumerate(df.iterrows()):
        # Update streak counters
        if is_bullish.iloc[i]:
            bullish_count += 1
            bearish_count = 0
            if bullish_count == 1 or row['low'] < lowest_bullish_price:
                lowest_bullish_price = row['low']
            if bullish_count == 1:
                first_bullish_open = row['open']
        elif is_bearish.iloc[i]:
            bearish_count += 1
            bullish_count = 0
            if bearish_count == 1 or row['high'] > highest_bearish_price:
                highest_bearish_price = row['high']
            if bearish_count == 1:
                first_bearish_open = row['open']

        # Check internal shifts
        if internal_shift_mode == "Open":
            internal_shift_bullish = (first_bearish_open is not None and 
                                      row['close'] > first_bearish_open)
            internal_shift_bearish = (first_bullish_open is not None and 
                                      row['close'] < first_bullish_open)
        else:
            internal_shift_bullish = (highest_bearish_price is not None and 
                                      row['close'] > highest_bearish_price)
            internal_shift_bearish = (lowest_bullish_price is not None and 
                                      row['close'] < lowest_bullish_price)

        # Detect bullish shift (LL/HL)
        if internal_shift_bullish and last_internal_shift != 1:
            last_internal_shift = 1
            last_bullish_shift_bar = index
            
            if last_bearish_shift_bar is not None:
                window = df.loc[last_bearish_shift_bar:index]
                if len(window) <= lookback:
                    lowest_idx = window['low'].idxmin()
                    lowest = window.at[lowest_idx, 'low']
                    
                    if prev_swing_low is not None:
                        if lowest < prev_swing_low:
                            swing_type_series.at[lowest_idx] = "LL"
                        elif lowest > prev_swing_low:
                            swing_type_series.at[lowest_idx] = "HL"
                    
                    prev_swing_low = lowest

        # Detect bearish shift (HH/LH)
        if internal_shift_bearish and last_internal_shift != -1:
            last_internal_shift = -1
            last_bearish_shift_bar = index
            
            if last_bullish_shift_bar is not None:
                window = df.loc[last_bullish_shift_bar:index]
                if len(window) <= lookback:
                    highest_idx = window['high'].idxmax()
                    highest = window.at[highest_idx, 'high']
                    
                    if prev_swing_high is not None:
                        if highest > prev_swing_high:
                            swing_type_series.at[highest_idx] = "HH"
                        elif highest < prev_swing_high:
                            swing_type_series.at[highest_idx] = "LH"
                    
                    prev_swing_high = highest
    swings['time'] = df['time']
    swings['Text'] = swing_type_series
    swings['Position'] = swings['Text'].map(position_map)
    swings['Color'] = swings['Text'].map(color_map)
    swings['Shape'] = swings['Text'].map(shape_map)

    # Naming
    swings.name = f"Swings"
    swings.category = "drawings"
    swings = swings[swings['Text'].notna()]
    print(swings)

    return swings.dropna()
