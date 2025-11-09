from flask import Flask, jsonify
import yfinance as yf
import pandas as pd
from datetime import datetime
import threading
import time
import os

app = Flask(__name__)

class ICTPatterns:
    def detect_fair_value_gaps(self, data):
        """YOUR ICT Knowledge - Fair Value Gaps - BULLETPROOF VERSION"""
        fvgs = []
        
        print(f"🔍 Checking {len(data)} candles for FVGs...")
        
        # Convert to DataFrame if it's not already
        if not isinstance(data, pd.DataFrame):
            return fvgs
            
        # Check if we have enough data and required columns
        if len(data) < 2 or 'High' not in data.columns or 'Low' not in data.columns:
            return fvgs
            
        try:
            # Reset index to make sure we can use iloc properly
            data_reset = data.reset_index(drop=True)
            
            for i in range(1, len(data_reset)):
                # SAFE way to get values
                current_low = data_reset['Low'].iloc[i]
                previous_high = data_reset['High'].iloc[i-1]
                current_high = data_reset['High'].iloc[i]
                previous_low = data_reset['Low'].iloc[i-1]
                
                # Convert to float safely
                try:
                    current_low = float(current_low)
                    previous_high = float(previous_high)
                    current_high = float(current_high)
                    previous_low = float(previous_low)
                except:
                    continue
                
                # DEBUG: Print candle comparison (less verbose)
                if i % 10 == 0:  # Print every 10th candle to reduce spam
                    print(f"Candle {i}: Low={current_low:.2f}, Prev High={previous_high:.2f}, Diff={current_low - previous_high:.2f}")
                
                # YOUR FVG RULES HERE
                if current_low > previous_high:
                    print(f"🎯 FOUND Bullish FVG! Current Low {current_low:.2f} > Previous High {previous_high:.2f}")
                    fvgs.append({
                        'type': 'bullish_fvg',
                        'level': float((previous_high + current_low) / 2),
                        'size': float(current_low - previous_high),
                        'timestamp': str(datetime.now())
                    })
                elif current_high < previous_low:
                    print(f"🎯 FOUND Bearish FVG! Current High {current_high:.2f} < Previous Low {previous_low:.2f}")
                    fvgs.append({
                        'type': 'bearish_fvg',
                        'level': float((current_high + previous_low) / 2),
                        'size': float(previous_low - current_high),
                        'timestamp': str(datetime.now())
                    })
                # NEAR FVG detection
                elif abs(current_low - previous_high) < (previous_high * 0.001):  # 0.1% threshold
                    print(f"🟡 NEAR FVG: Current Low {current_low:.2f} almost > Previous High {previous_high:.2f}")
                    
        except Exception as e:
            print(f"❌ Error in FVG detection: {e}")
            
        print(f"📊 Found {len(fvgs)} FVGs total")
        return fvgs

class SelfLearningAI:
    def __init__(self):
        self.knowledge_base = {}
        self.learning_active = False
        self.ict_patterns = ICTPatterns()
        
    def start_learning(self):
        def learning_loop():
            while self.learning_active:
                try:
                    self.learn_from_markets()
                    print("💤 Waiting 30 seconds for next learning cycle...")
                    time.sleep(30)  # Slightly longer for better analysis
                except Exception as e:
                    print(f"❌ Learning loop error: {e}")
                    time.sleep(10)
        
        self.learning_active = True
        thread = threading.Thread(target=learning_loop, daemon=True)
        thread.start()
        return "🔄 AI started learning autonomously!"
    
    def learn_from_markets(self):
        print(f"📊 {datetime.now()} - Learning from markets...")
        
        # ENHANCED: Added Gold and Forex symbols
        symbols = [
            'GC=F',        # Gold Futures (XAUUSD equivalent)
            'GLD',         # Gold ETF
            'EURUSD=X',    # Euro/USD
            'GBPUSD=X',    # GBP/USD  
            'NVDA',        # NVIDIA (often has clear patterns)
            'META'         # Meta Platforms
        ]
        
        for symbol in symbols:
            try:
                print(f"🔍 Analyzing {symbol}...")
                
                # Get data with error handling
                data = yf.download(symbol, period='3mo', interval='1d', progress=False)
                
                if data.empty:
                    print(f"❌ No data for {symbol}")
                    continue
                
                # Apply YOUR ICT knowledge
                ict_analysis = self.ict_patterns.detect_fair_value_gaps(data)
                
                # Get current price safely
                try:
                    current_price = float(data['Close'].iloc[-1])
                except:
                    current_price = 0
                
                # Store learned patterns
                self.knowledge_base[symbol] = {
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'ict_patterns': ict_analysis,
                    'total_patterns': len(ict_analysis),
                    'current_price': current_price,
                    'symbol_name': self.get_symbol_name(symbol)
                }
                
                print(f"✅ {symbol}: Found {len(ict_analysis)} ICT patterns | Price: ${current_price:.2f}")
                
            except Exception as e:
                print(f"❌ Error with {symbol}: {str(e)}")
    
    def get_symbol_name(self, symbol):
        """Get human-readable symbol names"""
        symbol_names = {
            'GC=F': 'Gold Futures (XAUUSD)',
            'GLD': 'Gold ETF', 
            'EURUSD=X': 'EUR/USD',
            'GBPUSD=X': 'GBP/USD',
            'NVDA': 'NVIDIA',
            'META': 'Meta Platforms'
        }
        return symbol_names.get(symbol, symbol)

# Initialize AI
ai = SelfLearningAI()

@app.route('/')
def home():
    return jsonify({
        "message": "🤖 Self-Learning ICT AI is Running!",
        "status": "active",
        "endpoints": {
            "/start-learning": "Start autonomous learning",
            "/knowledge": "See what AI has learned",
            "/analyze/<symbol>": "Analyze any symbol"
        }
    })

@app.route('/start-learning')
def start_learning():
    result = ai.start_learning()
    return jsonify({"message": result})

@app.route('/knowledge')
def get_knowledge():
    return jsonify(ai.knowledge_base)

@app.route('/analyze/<symbol>')
def analyze_symbol(symbol):
    try:
        data = yf.download(symbol, period='3mo', interval='1d', progress=False)
        
        if data.empty:
            return jsonify({"error": f"No data found for {symbol}"})
            
        ict_analysis = ai.ict_patterns.detect_fair_value_gaps(data)
        current_price = float(data['Close'].iloc[-1]) if len(data) > 0 else 0
        
        return jsonify({
            "symbol": symbol,
            "symbol_name": ai.get_symbol_name(symbol),
            "current_price": current_price,
            "ict_patterns_found": len(ict_analysis),
            "analysis": ict_analysis,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("🚀 Starting Self-Learning ICT AI...")
    print("📍 Your API will be available at: http://127.0.0.1:5000")
    ai.start_learning()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)