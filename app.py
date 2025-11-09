from flask import Flask, jsonify, render_template
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import time
import os

app = Flask(__name__)

class ICTPatterns:
    def detect_fair_value_gaps(self, data):
        """ICT Fair Value Gap Detection"""
        fvgs = []
        
        if not isinstance(data, pd.DataFrame) or len(data) < 2:
            return fvgs
            
        try:
            for i in range(1, len(data)):
                # Get current and previous candle data
                current_low = float(data['Low'].iloc[i])
                previous_high = float(data['High'].iloc[i-1])
                current_high = float(data['High'].iloc[i])
                previous_low = float(data['Low'].iloc[i-1])
                
                # Bullish FVG
                if current_low > previous_high:
                    fvgs.append({
                        'type': 'bullish_fvg',
                        'level': float((previous_high + current_low) / 2),
                        'size': float(current_low - previous_high),
                        'timestamp': str(datetime.now())
                    })
                # Bearish FVG
                elif current_high < previous_low:
                    fvgs.append({
                        'type': 'bearish_fvg',
                        'level': float((current_high + previous_low) / 2),
                        'size': float(previous_low - current_high),
                        'timestamp': str(datetime.now())
                    })
                    
        except Exception as e:
            print(f"FVG detection error: {e}")
            
        return fvgs

class SelfLearningAI:
    def __init__(self):
        self.knowledge_base = {}
        self.learning_active = False
        self.ict_patterns = ICTPatterns()
        
    def start_learning(self):
        """Start autonomous learning"""
        def learning_loop():
            while self.learning_active:
                try:
                    self.learn_from_markets()
                    print("💤 AI sleeping for 30 seconds...")
                    time.sleep(30)
                except Exception as e:
                    print(f"❌ Learning error: {e}")
                    time.sleep(10)
        
        self.learning_active = True
        thread = threading.Thread(target=learning_loop, daemon=True)
        thread.start()
        return "🚀 AI started autonomous learning!"
    
    def learn_from_markets(self):
        """AI learning from market patterns"""
        print(f"📊 {datetime.now()} - AI learning cycle...")
        
        # Demo market data (replace with real data later)
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'BTC-USD']
        
        for symbol in symbols:
            try:
                # Create demo price data
                demo_data = pd.DataFrame({
                    'High': [150 + i * 2 for i in range(10)],
                    'Low': [148 + i * 2 for i in range(10)],
                    'Close': [149 + i * 2 for i in range(10)],
                    'Open': [149 + i * 2 for i in range(10)]
                })
                
                # Detect patterns
                patterns = self.ict_patterns.detect_fair_value_gaps(demo_data)
                
                # Store knowledge
                self.knowledge_base[symbol] = {
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'ict_patterns': patterns,
                    'total_patterns': len(patterns),
                    'current_price': 150.75,  # Demo price
                    'status': 'Active'
                }
                
                print(f"✅ {symbol}: Found {len(patterns)} patterns")
                
            except Exception as e:
                print(f"❌ Error with {symbol}: {e}")

# Initialize AI
ai = SelfLearningAI()

@app.route('/')
def home():
    return jsonify({
        "message": "🤖 Self-Learning ICT Trading AI",
        "status": "ACTIVE",
        "version": "1.0",
        "endpoints": {
            "/": "API status",
            "/start-learning": "Start AI learning", 
            "/knowledge": "View AI knowledge",
            "/analyze/<symbol>": "Analyze any symbol",
            "/web": "Web interface"
        }
    })

@app.route('/web')
def web_interface():
    return render_template('index.html')

@app.route('/start-learning')
def start_learning():
    result = ai.start_learning()
    return jsonify({"message": result, "status": "success"})

@app.route('/knowledge')
def get_knowledge():
    return jsonify({
        "knowledge_base": ai.knowledge_base,
        "total_symbols": len(ai.knowledge_base),
        "ai_status": "Active" if ai.learning_active else "Inactive"
    })

@app.route('/analyze/<symbol>')
def analyze_symbol(symbol):
    try:
        # Demo analysis (replace with real data later)
        demo_data = pd.DataFrame({
            'High': [150, 152, 155, 153, 157],
            'Low': [148, 150, 152, 151, 155],
            'Close': [149, 151, 154, 152, 156],
            'Open': [149, 151, 153, 152, 156]
        })
        
        patterns = ai.ict_patterns.detect_fair_value_gaps(demo_data)
        
        return jsonify({
            "symbol": symbol,
            "analysis": "ICT Pattern Analysis Complete",
            "patterns_found": len(patterns),
            "patterns": patterns,
            "current_price": 150.75,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "Using demo data - Ready for real market integration"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("🚀 Starting Self-Learning ICT Trading AI...")
    print("📍 API Endpoints:")
    print("   - /start-learning - Start AI learning")
    print("   - /knowledge - View patterns learned") 
    print("   - /analyze/SYMBOL - Analyze any symbol")
    print("   - /web - Web interface")
    
    # Start AI learning
    ai.start_learning()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
