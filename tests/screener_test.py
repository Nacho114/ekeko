import ekeko

def test_screener_without_params():

    passes_screener = ekeko.backtrader.screener(ticker='AAPL')
    assert passes_screener

marketCapMin = int(2000*1e9)
marketCapMax = int(9000*1e9)
volumeMin = int(20*1e6)

def test_screener_with_params():

    passes_screener = ekeko.backtrader.screener(ticker='AAPL', marketCapMin=marketCapMin, marketCapMax=marketCapMax, volumeMin=volumeMin)
    assert passes_screener

def test_screener_false_with_min_volume_too_high():
    volumeMinTooHigh = int(1e9)
    passes_screener = ekeko.backtrader.screener(ticker='AAPL', marketCapMin=marketCapMin, marketCapMax=marketCapMax, volumeMin=volumeMinTooHigh)
    assert not passes_screener
