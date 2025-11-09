from flask import Flask, jsonify, request, render_template
from datetime import datetime
import threading
import time
import os
import base64
from io import BytesIO

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class ChartAnalyzer:
    def analyze_chart_image(self, image_path):
        """Analyze uploaded chart image for trading patterns"""
        try:
            # This is where you'll add computer vision analysis
            # For now, returning demo analysis
            analysis = {
                'chart_type': 'candlestick',
                'timeframe': '1D',
                'patterns_found': [
                    {
                        'name': 'Fair Value Gap',
                        'type': 'bullish_fvg',
                        'confidence': 0.85,
                        'location': 'recent'
                    },
                    {
                        'name': 'Support Level',
                        'type': 'support',
                        'confidence': 0.92,
                        'level': 145.50
                    },
                    {
                        'name': 'Resistance Level', 
                        'type': 'resistance',
                        'confidence': 0.78,
                        'level': 155.25
                    }
                ],
                'smc_analysis': {
                    'order_blocks': 2,
                    'liquidity_zones': 3,
                    'market_structure': 'bullish',
                    'breakout_probability': 0.72
                },
                'sentiment': 'bullish',
                'confidence_score': 0.82
            }
            return analysis
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}

class ICTPatterns:
    def detect_fair_value_gaps(self, data):
        """ICT Fair Value Gap Detection"""
        fvgs = []
        
        try:
            # Demo patterns for testing
            demo_patterns = [
                {
                    'type': 'bullish_fvg',
                    'level': 150.25,
                    'size': 2.5,
                    'timestamp': str(datetime.now()),
                    'strength': 'strong'
                },
                {
                    'type': 'bearish_fvg', 
                    'level': 148.75,
                    'size': 1.8,
                    'timestamp': str(datetime.now()),
                    'strength': 'medium'
                }
            ]
            return demo_patterns
        except Exception as e:
            print(f"Pattern detection error: {e}")
            return []

class SelfLearningAI:
    def __init__(self):
        self.knowledge_base = {}
        self.learning_active = False
        self.ict_patterns = ICTPatterns()
        self.chart_analyzer = ChartAnalyzer()
        
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
        
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'BTC-USD', 'ETH-USD', 'GC=F', 'EURUSD=X']
        
        for symbol in symbols:
            try:
                patterns = self.ict_patterns.detect_fair_value_gaps(None)
                
                self.knowledge_base[symbol] = {
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'ict_patterns': patterns,
                    'total_patterns': len(patterns),
                    'current_price': 150.75,
                    'trend': 'bullish',
                    'momentum': 'strong',
                    'status': 'Active'
                }
                
                print(f"✅ {symbol}: Found {len(patterns)} ICT patterns")
                
            except Exception as e:
                print(f"❌ Error with {symbol}: {e}")

# Initialize AI
ai = SelfLearningAI()

@app.route('/')
def home():
    return jsonify({
        "message": "🤖 Self-Learning ICT Trading AI",
        "status": "ACTIVE ✅",
        "version": "2.0",
        "features": [
            "ICT Pattern Detection",
            "Fair Value Gaps (FVG)",
            "Self-Learning AI", 
            "Multi-Asset Analysis",
            "Chart Image Analysis",  # NEW!
            "SMC Analysis"          # NEW!
        ],
        "endpoints": {
            "/": "API status (this page)",
            "/start-learning": "Start AI autonomous learning", 
            "/knowledge": "View everything AI has learned",
            "/analyze/<symbol>": "Analyze any trading symbol",
            "/upload-chart": "Upload chart image for analysis",  # NEW!
            "/health": "System health check"
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# NEW: Image Upload Endpoint
@app.route('/upload-chart', methods=['POST'])
def upload_chart():
    try:
        if 'chart_image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['chart_image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save the file
            filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Analyze the chart
            analysis = ai.chart_analyzer.analyze_chart_image(filepath)
            
            return jsonify({
                'status': 'success',
                'message': 'Chart analyzed successfully',
                'filename': filename,
                'analysis': analysis,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

# NEW: Web interface for easy uploads
@app.route('/web-upload')
def web_upload():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>📈 Upload Chart for Analysis</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f0f2f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .upload-area { border: 2px dashed #007bff; padding: 40px; text-align: center; margin: 20px 0; }
            .result { background: #e8f5e8; padding: 20px; margin: 20px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📈 Upload Trading Chart</h1>
            <p>Upload a chart image for AI analysis (SMC, ICT Patterns, etc.)</p>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area">
                    <input type="file" name="chart_image" accept="image/*" required>
                    <br><br>
                    <button type="submit">Analyze Chart</button>
                </div>
            </form>
            
            <div id="result" class="result" style="display:none;"></div>
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const resultDiv = document.getElementById('result');
                
                try {
                    const response = await fetch('/upload-chart', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <h3>✅ Analysis Complete!</h3>
                            <p><strong>Patterns Found:</strong> ${data.analysis.patterns_found.length}</p>
                            <p><strong>Sentiment:</strong> ${data.analysis.sentiment}</p>
                            <p><strong>Confidence:</strong> ${(data.analysis.confidence_score * 100).toFixed(1)}%</p>
                            <pre>${JSON.stringify(data.analysis, null, 2)}</pre>
                        `;
                    } else {
                        resultDiv.innerHTML = `<h3>❌ Error:</h3><p>${data.error}</p>`;
                    }
                    resultDiv.style.display = 'block';
                } catch (error) {
                    resultDiv.innerHTML = `<h3>❌ Network Error:</h3><p>${error}</p>`;
                    resultDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    '''

# Keep your existing endpoints...
@app.route('/start-learning')
def start_learning():
    result = ai.start_learning()
    return jsonify({
        "message": result, 
        "status": "success",
        "ai_status": "learning_active",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/knowledge')
def get_knowledge():
    return jsonify({
        "knowledge_base": ai.knowledge_base,
        "total_symbols_analyzed": len(ai.knowledge_base),
        "total_patterns_found": sum(len(data.get('ict_patterns', [])) for data in ai.knowledge_base.values()),
        "ai_status": "Active" if ai.learning_active else "Inactive",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/analyze/<symbol>')
def analyze_symbol(symbol):
    try:
        patterns = ai.ict_patterns.detect_fair_value_gaps(None)
        
        return jsonify({
            "symbol": symbol.upper(),
            "analysis": "ICT Pattern Analysis Complete ✅",
            "patterns_found": len(patterns),
            "patterns": patterns,
            "summary": {
                "bullish_fvg": len([p for p in patterns if p['type'] == 'bullish_fvg']),
                "bearish_fvg": len([p for p in patterns if p['type'] == 'bearish_fvg']),
                "total_signals": len(patterns)
            },
            "price_data": {
                "current": 150.75,
                "support": 145.20,
                "resistance": 155.80,
                "trend": "bullish"
            },
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error",
            "symbol": symbol
        })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy ✅",
        "service": "ICT Trading AI",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "memory_usage": "optimal",
        "ai_learning": ai.learning_active,
        "symbols_tracked": len(ai.knowledge_base)
    })

if __name__ == '__main__':
    print("🚀 Starting Self-Learning ICT Trading AI...")
    print("📍 Now with Chart Image Upload!")
    print("📊 Monitoring: Stocks, Crypto, Forex, Gold")
    print("🖼️  New: Chart image analysis endpoint")
    print("🌐 API Endpoints:")
    print("   - /start-learning - Start AI learning")
    print("   - /knowledge - View learned patterns") 
    print("   - /analyze/SYMBOL - Analyze any symbol")
    print("   - /upload-chart - Upload chart images")  # NEW!
    print("   - /web-upload - Web upload interface")   # NEW!
    print("   - /health - System status")
    
    # Start AI learning automatically
    ai.start_learning()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    print(f"🌍 Server starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
