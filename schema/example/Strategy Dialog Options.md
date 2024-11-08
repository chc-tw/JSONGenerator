# Strategy Dialog Options

This document outlines the various options used in the lego block rules.

##Condition Type Options

The `conditionTypeOptions` objects of array contains the following options for condition types:

| Label | Value | Example | 
|---|---|---|
| Price | price | [link](https://gitlab.mimirlab.xyz/mimir-lab/crypto-arsenal/-/issues/2) | 
| Candlestick | candlestick | [link](https://gitlab.mimirlab.xyz/mimir-lab/crypto-arsenal/-/issues/4) | 
| Moving Average | ma | [link](https://gitlab.mimirlab.xyz/mimir-lab/crypto-arsenal/-/issues/5) | 
| Bollinger Bands | bb | [link](https://gitlab.mimirlab.xyz/mimir-lab/crypto-arsenal/-/issues/3) | 
| RSI | rsi | [link](https://gitlab.mimirlab.xyz/mimir-lab/crypto-arsenal/-/issues/6) | 
| MACD | macd | [link](https://gitlab.mimirlab.xyz/mimir-lab/crypto-arsenal/-/issues/7) | 

## Formula Options

The `formulaOptions` objects of array contains the following options for formulas:

| Label | Value | Type | 
|---|---|---|
| Price / Price | price/price | price | 
| N Ticks Price Comparison | n_ticks_price | price | 
| N Ticks Candlestick Type | n_ticks_candle_type | candlestick | 
| SMA compare with SMA | sma/sma | ma | 
| N Ticks SMA | n_ticks_sma | ma | 
| Latest Price compare with SMA | price/sma | ma | 
| SMA Cross Strategy | sma_cross | ma | 
| SMA Slope | sma_slope | ma | 
| Bollinger Bands Comparison | bb_comparison | bb | 
| Bandwidth Comparison | bandwidth_comparison | bb | 
| Percent B (%B) Comparison | percent_b_comparison | bb | 
| Price / Bollinger Bands | price/bb | bb | 
| N Ticks Bandwidth | n_ticks_bandwidth | bb | 
| N Ticks Percent B (%B) | n_ticks_percent_b | bb | 
| RSI Comparison | rsi_comparison | rsi | 
| RSI Cross Strategy | rsi_cross | rsi | 
| MACD Comparison | macd_comparison | macd | 

## Time Frame Options

The `timeFrameOptions` objects of array contains the following options for time frames:

| Label | Value | 
|---|---|
| Min | T | 
| Hour | H | 
| Day | D | 

## Min or Max Options

The `minOrMaxOptions` objects of array contains the following options for minimum or maximum selection:

| Label | Value | 
|---|---|
| Minimum | min | 
| Maximum | max | 

## Bollinger Bands Options

The `bbOptions` objects of array contains the following options for Bollinger Bands:

| Label | Value | 
|---|---|
| Upper Band | upper | 
| Middle Band | middle | 
| Lower Band | lower | 

## Strategy Form

The `strategyForm` is a reactive object that holds the current state of the strategy being created or edited. It contains the following properties:

| Property | Type | Description | 
|---|---|---|
| conditionStyle | String | The style of the condition ('and' or 'or') | 
| conditionType | Object | The selected condition type (e.g., {label: 'Price', value: 'price'}) | 
| formula | Object | The selected formula (e.g., {label: 'Price / Price', value: 'price/price', type: 'price'}) | 
| timeFrameValue | Number | The numeric value for the time frame (e.g., 1, 5, 15) | 
| timeFrameUnit | Object | The selected time frame unit (e.g., {label: 'Min', value: 'T'}) | 
| detail | Object | Contains the details of the strategy | 
| detail.numerator | Object | Properties for the numerator part of the formula | 
| detail.denominator | Object | Properties for the denominator part of the formula | 
| [detail.compare](detail.compare) | String | The comparison operator (e.g., '>', '<', '=') | 
| detail.compareValue | Number | The value to compare against | 
| params | Object | Additional parameters for specific strategies | 
| params.bbValue | Object | Bollinger Bands specific values (sma and std) | 
| params.macdValue | Object | MACD specific values (fast, slow, and signal) | 

The `detail.numerator` and `detail.denominator` objects contain properties such as:

- minusNumber: Number of days to subtract

- priceType: Type of price (e.g., 'Close', 'Open')

- smaValue: SMA period

- rsiValue: RSI period

- minOrMax: Object for min/max selection

- bbType: Object for Bollinger Band type selection

- candleType: Type of candle (e.g., 'bullish', 'bearish')

This structure allows for flexible configuration of various trading strategies within the application.

### Default strategyForm JSON

Below is the default JSON representation of the `strategyForm` object:

```json
{
    "conditionStyle": "and",
    "conditionType": {
        "label": "Price",
        "value": "price"
    },
    "formula": {
        "label": "Price / Price",
        "value": "price/price",
        "type": "price"
    },
    "timeFrameValue": 1,
    "timeFrameUnit": {
        "label": "Min",
        "value": "T"
    },
    "detail": {
        "numerator": {
            "minusNumber": 0,
            "priceType": "Close",
            "smaValue": 5,
            "rsiValue": 6,
            "minOrMax": {
                "label": "Minimum",
                "value": "min"
            },
            "bbType": {
                "label": "Upper Band",
                "value": "upper"
            },
            "candleType": "bullish"
        },
        "denominator": {
            "minusNumber": 0,
            "priceType": "Close",
            "smaValue": 20,
            "rsiValue": 12,
            "minOrMax": {
                "label": "Minimum",
                "value": "min"
            },
            "bbType": {
                "label": "Upper Band",
                "value": "upper"
            },
            "candleType": "bullish"
        },
        "compare": ">",
        "compareValue": 0
    },
    "params": {
        "bbValue": {
            "sma": 20,
            "std": 2
        },
        "macdValue": {
            "fast": 12,
            "slow": 26,
            "signal": 9
        }
    }
}
```