async function executeTrade() {
    const symbol = document.getElementById("symbol").value;
    const interval = document.getElementById("interval").value;
    const starttime = document.getElementById("starttime").value;
  
    // Make API call to retrieve historical data
    const response = await fetch(`/api/get-data-frame?symbol=${symbol}&interval=${interval}&starttime=${starttime}`);
    const data = await response.json();
  
    // Calculate short and long ema
    const shortEMA = data['close'].ewm(span=12, adjust=False).mean();
    const longEMA = data['close'].ewm(span=26, adjust=False).mean();
  
    // Calculate MACD and signal line
    const MACD = shortEMA - longEMA;
    const signal = MACD.ewm(span=9, adjust=False).mean();
  
    // Generate buy and sell signals
    const trigger = MACD > signal ? 1 : 0;
    const position = trigger.diff();
  
    // Display results on page
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = `<p>Buy orders placed at: ${data['close'].filter(x => x == 1).join(", ")}</p>
    <p>Sell orders placed at: ${data['close'].filter(x => x == -1).join(", ")}</p>`;
}