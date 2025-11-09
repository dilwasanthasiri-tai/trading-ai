from flask import Flask, jsonify, request, render_template_string
from datetime import datetime
import random
import os
import base64
import json
import io

app = Flask(__name__)

# Create uploads directory if it doesn't exist
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

# Self-learning AI storage
AI_DATA_FILE = 'ai_learning_data.json'

class SelfLearningAI:
    def __init__(self):
        self.learning_data = self.load_learning_data()
        print(f"🤖 AI Loaded: {self.learning_data['total_predictions']} predictions | Accuracy: {self.learning_data['accuracy']:.1f}%")
        
    def load_learning_data(self):
        """Load AI learning data from file"""
        try:
            if os.path.exists(AI_DATA_FILE):
                with open(AI_DATA_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            'total_predictions': 0,
            'correct_predictions': 0,
            'accuracy': 0.0,
            'pattern_memory': {},
            'confidence_boost': 1.0,
            'learning_history': [],
            'performance_trend': 'STABLE'
        }
    
    def save_learning_data(self):
        """Save AI learning data to file"""
        try:
            with open(AI_DATA_FILE, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except:
            pass
    
    def learn_from_result(self, features, prediction, actual_result, user_confidence):
        """AI learns from every prediction result"""
        self.learning_data['total_predictions'] += 1
        
        # Check if prediction was correct
        was_correct = prediction == actual_result
        if was_correct:
            self.learning_data['correct_predictions'] += 1
        
        # Update accuracy
        total = self.learning_data['total_predictions']
        correct = self.learning_data['correct_predictions']
        self.learning_data['accuracy'] = (correct / total * 100) if total > 0 else 0
        
        # Create pattern signature
        pattern_key = self.create_pattern_signature(features)
        
        # Learn this pattern
        if pattern_key not in self.learning_data['pattern_memory']:
            self.learning_data['pattern_memory'][pattern_key] = {
                'bullish_wins': 0,
                'bearish_wins': 0,
                'total_occurrences': 0,
                'last_seen': datetime.now().isoformat()
            }
        
        # Update pattern memory
        if actual_result == 'BULLISH':
            self.learning_data['pattern_memory'][pattern_key]['bullish_wins'] += 1
        else:
            self.learning_data['pattern_memory'][pattern_key]['bearish_wins'] += 1
        
        self.learning_data['pattern_memory'][pattern_key]['total_occurrences'] += 1
        self.learning_data['pattern_memory'][pattern_key]['last_seen'] = datetime.now().isoformat()
        
        # Boost confidence if performing well
        if self.learning_data['accuracy'] > 70:
            self.learning_data['confidence_boost'] = min(2.0, 1.0 + (self.learning_data['accuracy'] - 70) / 30)
            self.learning_data['performance_trend'] = 'IMPROVING'
        elif self.learning_data['accuracy'] < 50:
            self.learning_data['confidence_boost'] = max(0.5, 1.0 - (50 - self.learning_data['accuracy']) / 50)
            self.learning_data['performance_trend'] = 'LEARNING'
        else:
            self.learning_data['performance_trend'] = 'STABLE'
        
        # Save learning
        self.learning_data['learning_history'].append({
            'timestamp': datetime.now().isoformat(),
            'pattern': pattern_key,
            'prediction': prediction,
            'actual': actual_result,
            'correct': was_correct,
            'user_confidence': user_confidence,
            'ai_confidence': self.learning_data['confidence_boost']
        })
        
        # Keep history manageable
        if len(self.learning_data['learning_history']) > 500:
            self.learning_data['learning_history'] = self.learning_data['learning_history'][-500:]
        
        self.save_learning_data()
        print(f"🧠 AI Learned: {pattern_key} -> {actual_result} (Correct: {was_correct})")
    
    def create_pattern_signature(self, features):
        """Create a unique signature for chart patterns"""
        trend = features.get('trend_direction', 0)
        green_pct = features.get('green_percentage', 0.5)
        red_pct = features.get('red_percentage', 0.5)
        
        # Quantize values to create pattern groups
        trend_level = 'BULL' if trend > 0 else 'BEAR' if trend < 0 else 'NEUTRAL'
        green_level = int(green_pct * 10)  # 0-10 scale
        red_level = int(red_pct * 10)     # 0-10 scale
        
        return f"{trend_level}_G{green_level}_R{red_level}"
    
    def get_ai_prediction(self, features):
        """Get AI-powered prediction using learned knowledge"""
        pattern_key = self.create_pattern_signature(features)
        
        # Check if we've learned this pattern
        if pattern_key in self.learning_data['pattern_memory']:
            pattern_data = self.learning_data['pattern_memory'][pattern_key]
            bullish_score = pattern_data['bullish_wins']
            bearish_score = pattern_data['bearish_wins']
            
            if bullish_score > bearish_score:
                base_confidence = (bullish_score / (bullish_score + bearish_score)) * 100
                confidence = min(95, base_confidence * self.learning_data['confidence_boost'])
                return 'BULLISH', confidence, 'LEARNED_PATTERN'
            elif bearish_score > bullish_score:
                base_confidence = (bearish_score / (bullish_score + bearish_score)) * 100
                confidence = min(95, base_confidence * self.learning_data['confidence_boost'])
                return 'BEARISH', confidence, 'LEARNED_PATTERN'
        
        # Fallback to basic analysis for new patterns
        green_pct = features.get('green_percentage', 0.5)
        red_pct = features.get('red_percentage', 0.5)
        trend = features.get('trend_direction', 0)
        
        if green_pct > red_pct + 0.1 and trend > 0:
            confidence = 70 * self.learning_data['confidence_boost']
            return 'BULLISH', confidence, 'BASIC_ANALYSIS'
        elif red_pct > green_pct + 0.1 and trend < 0:
            confidence = 70 * self.learning_data['confidence_boost']
            return 'BEARISH', confidence, 'BASIC_ANALYSIS'
        else:
            # Random with base confidence
            direction = random.choice(['BULLISH', 'BEARISH'])
            confidence = 60 * self.learning_data['confidence_boost']
            return direction, confidence, 'RANDOM_GUESS'

# Initialize AI
ai_brain = SelfLearningAI()

class ICTMarketPredictor:
    def __init__(self, image_data=None):
        self.image_data = image_data
        self.chart_features = self.simulate_chart_features() if image_data else None
        
    def simulate_chart_features(self):
        """Simulate chart features"""
        return {
            'image_uploaded': True,
            'green_percentage': random.uniform(0.3, 0.7),
            'red_percentage': random.uniform(0.3, 0.7),
            'trend_direction': random.choice([-1, 0, 1]),
            'volatility': random.uniform(0.1, 0.9)
        }
    
    def complete_ict_analysis(self):
        """Complete ICT analysis with AI prediction"""
        prediction, confidence, method = ai_brain.get_ai_prediction(
            self.chart_features or {}
        )
        
        return {
            'market_structure': self.analyze_market_structure(),
            'key_levels': self.find_ict_levels(),
            'order_blocks': self.find_order_blocks(),
            'fair_value_gaps': self.find_fvgs(),
            'liquidity': self.analyze_liquidity(),
            'time_analysis': self.time_based_analysis(),
            'chart_analysis': self.chart_features or {'image_uploaded': False},
            'prediction': self.create_prediction(prediction, confidence, method),
            'ai_learning': self.get_ai_status(),
            'trading_plan': self.create_trading_plan(prediction),
            'risk_management': self.calculate_risk(confidence)
        }
    
    def get_ai_status(self):
        """Get AI learning status"""
        return {
            'total_predictions': ai_brain.learning_data['total_predictions'],
            'accuracy': round(ai_brain.learning_data['accuracy'], 1),
            'confidence_boost': round(ai_brain.learning_data['confidence_boost'], 2),
            'performance_trend': ai_brain.learning_data['performance_trend'],
            'patterns_learned': len(ai_brain.learning_data['pattern_memory'])
        }
    
    def create_prediction(self, direction, confidence, method):
        """Create prediction with AI context"""
        return {
            'direction': direction,
            'probability': round(confidence, 1),
            'reason': f'AI {method} | Confidence: {confidence:.1f}%',
            'method': method,
            'targets': {
                'immediate': round(random.uniform(156, 160), 2) if direction == 'BULLISH' else round(random.uniform(144, 148), 2),
                'secondary': round(random.uniform(160, 164), 2) if direction == 'BULLISH' else round(random.uniform(140, 144), 2)
            }
        }
    
    def analyze_market_structure(self):
        return {
            'primary_trend': random.choice(['BULLISH', 'BEARISH']),
            'market_phase': random.choice(['ACCUMULATION', 'MARKUP', 'DISTRIBUTION', 'MARKDOWN']),
            'structure_break': random.choice([True, False])
        }
    
    def find_ict_levels(self):
        return {
            'previous_week_high': round(random.uniform(160, 165), 2),
            'previous_week_low': round(random.uniform(135, 140), 2)
        }
    
    def find_order_blocks(self):
        return {
            'bullish_ob': [{'price': round(random.uniform(142, 148), 2), 'strength': 'STRONG'}],
            'bearish_ob': [{'price': round(random.uniform(158, 162), 2), 'strength': 'STRONG'}]
        }
    
    def find_fvgs(self):
        return {
            'bullish_fvgs': [{'range': [150, 155], 'strength': 'HIGH'}],
            'bearish_fvgs': [{'range': [160, 155], 'strength': 'HIGH'}]
        }
    
    def analyze_liquidity(self):
        return {
            'buy_side_liquidity': round(random.uniform(138, 142), 2),
            'sell_side_liquidity': round(random.uniform(162, 168), 2)
        }
    
    def time_based_analysis(self):
        return {
            'london_killzone': random.choice(['ACTIVE', 'INACTIVE']),
            'new_york_killzone': random.choice(['ACTIVE', 'INACTIVE'])
        }
    
    def create_trading_plan(self, direction):
        return {
            'entry_strategy': random.choice(['OB Reaction', 'FVG Bounce', 'Liquidity Grab']),
            'entry_price': round(random.uniform(148, 158), 2),
            'stop_loss': round(random.uniform(146, 152), 2),
            'take_profit': round(random.uniform(158, 162), 2),
            'position_size': f"{random.randint(2, 5)}%",
            'risk_reward': f"1:{random.uniform(2.0, 3.5):.1f}"
        }
    
    def calculate_risk(self, confidence):
        risk_level = 'LOW' if confidence > 80 else 'MEDIUM' if confidence > 60 else 'HIGH'
        return {
            'max_risk_per_trade': f"{random.randint(1, 3)}%",
            'confidence_score': round(confidence, 1),
            'risk_level': risk_level
        }

@app.route('/')
def home():
    return jsonify({
        "message": "🤖 ICT Market Predictor with Self-Learning AI",
        "status": "ACTIVE ✅", 
        "version": "7.0 - AI Powered",
        "ai_status": ai_brain.get_ai_status(),
        "features": [
            "Self-Learning AI Brain",
            "Automatically Improves Over Time", 
            "Pattern Recognition Memory",
            "Real-time Accuracy Tracking"
        ]
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_accuracy": f"{ai_brain.learning_data['accuracy']:.1f}%",
        "total_predictions": ai_brain.learning_data['total_predictions']
    })

@app.route('/ai-status')
def ai_status():
    return jsonify(ai_brain.get_ai_status())

@app.route('/analyze', methods=['POST'])
def complete_analysis():
    try:
        data = request.get_json()
        image_data = data.get('image_data') if data else None
            
        predictor = ICTMarketPredictor(image_data)
        analysis = predictor.complete_ict_analysis()
        
        return jsonify({
            'status': 'success',
            'analysis': analysis,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/learn', methods=['POST'])
def learn_from_result():
    """Endpoint for AI to learn from actual results"""
    try:
        data = request.get_json()
        features = data.get('features', {})
        prediction = data.get('prediction')
        actual_result = data.get('actual_result')
        user_confidence = data.get('user_confidence', 1)
        
        if not all([prediction, actual_result]):
            return jsonify({'error': 'Missing prediction or actual_result'}), 400
        
        ai_brain.learn_from_result(features, prediction, actual_result, user_confidence)
        
        return jsonify({
            'status': 'success',
            'message': 'AI learned from this result',
            'new_accuracy': f"{ai_brain.learning_data['accuracy']:.1f}%"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/web-analyzer')
def web_analyzer():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎯 ICT Predictor with Self-Learning AI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                padding: 30px; 
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .upload-area {
                border: 3px dashed #007bff;
                padding: 40px;
                text-align: center;
                border-radius: 10px;
                margin: 20px 0;
                background: #f8f9fa;
            }
            .analyze-btn {
                padding: 20px 40px;
                font-size: 22px;
                background: #28a745;
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                margin: 20px 0;
                width: 100%;
            }
            .ai-status {
                background: #e7f3ff;
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid #17a2b8;
            }
            .section {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 15px 0;
                border-left: 5px solid #007bff;
            }
            .prediction-bullish { background: #d4edda; border-color: #28a745; }
            .prediction-bearish { background: #f8d7da; border-color: #dc3545; }
            .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
            @media (max-width: 768px) {
                .grid-2, .grid-3 { grid-template-columns: 1fr; }
            }
            #preview { 
                max-width: 100%; 
                max-height: 400px; 
                margin: 20px 0; 
                border-radius: 10px;
                display: none;
            }
            .loading-spinner {
                border: 5px solid #f3f3f3;
                border-top: 5px solid #007bff;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 ICT Predictor with Self-Learning AI</h1>
            <p><strong>Watch the AI get smarter with every prediction! 🧠</strong></p>
            
            <div class="ai-status" id="aiStatus">
                <h3>🤖 AI Brain Status</h3>
                <p>Loading AI status...</p>
            </div>
            
            <div class="upload-area">
                <input type="file" id="imageUpload" accept="image/*" style="display: none;">
                <button onclick="document.getElementById('imageUpload').click()" 
                        style="padding: 15px 30px; font-size: 18px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    📁 Upload Chart Image
                </button>
                <p>Supported formats: PNG, JPG, JPEG</p>
                <img id="preview">
            </div>

            <div style="text-align: center;">
                <button class="analyze-btn" onclick="runImageAnalysis()" id="analyzeBtn" disabled>
                    🤖 ANALYZE WITH SELF-LEARNING AI
                </button>
            </div>

            <div id="loading" style="display: none; text-align: center; padding: 20px;">
                <div class="loading-spinner"></div>
                <h3>AI Analyzing Chart & Learning Patterns...</h3>
            </div>

            <div id="results" style="display: none;"></div>
        </div>

        <script>
            let uploadedImageData = null;
            let currentAnalysis = null;

            // Load AI status on page load
            loadAIStatus();

            async function loadAIStatus() {
                try {
                    const response = await fetch('/ai-status');
                    const data = await response.json();
                    document.getElementById('aiStatus').innerHTML = `
                        <h3>🤖 AI Brain Status</h3>
                        <div class="grid-3">
                            <div><strong>Total Predictions:</strong> ${data.total_predictions}</div>
                            <div><strong>Accuracy:</strong> ${data.accuracy}%</div>
                            <div><strong>Patterns Learned:</strong> ${data.patterns_learned}</div>
                            <div><strong>Confidence Boost:</strong> ${data.confidence_boost}x</div>
                            <div><strong>Performance:</strong> ${data.performance_trend}</div>
                        </div>
                    `;
                } catch (error) {
                    console.error('Failed to load AI status:', error);
                }
            }

            document.getElementById('imageUpload').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        uploadedImageData = e.target.result;
                        const preview = document.getElementById('preview');
                        preview.src = uploadedImageData;
                        preview.style.display = 'block';
                        document.getElementById('analyzeBtn').disabled = false;
                    }
                    reader.readAsDataURL(file);
                }
            });

            async function runImageAnalysis() {
                if (!uploadedImageData) {
                    alert('Please upload a chart image first!');
                    return;
                }

                const btn = document.getElementById('analyzeBtn');
                const loading = document.getElementById('loading');
                const results = document.getElementById('results');
                
                btn.style.display = 'none';
                loading.style.display = 'block';
                results.style.display = 'none';

                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({image_data: uploadedImageData})
                    });
                    
                    const data = await response.json();
                    currentAnalysis = data.analysis;
                    
                    setTimeout(() => {
                        displayAnalysis(data.analysis);
                        loading.style.display = 'none';
                        results.style.display = 'block';
                        loadAIStatus(); // Refresh AI status
                    }, 1500);
                    
                } catch (error) {
                    alert('Analysis error! Please try again.');
                    btn.style.display = 'block';
                    loading.style.display = 'none';
                }
            }

            function displayAnalysis(analysis) {
                const prediction = analysis.prediction;
                const predictionClass = prediction.direction === 'BULLISH' ? 'prediction-bullish' : 'prediction-bearish';
                
                document.getElementById('results').innerHTML = `
                    <div class="section ${predictionClass}">
                        <h2>🎯 AI PREDICTION: ${prediction.direction}</h2>
                        <div class="grid-2">
                            <div>
                                <p><strong>Probability:</strong> ${prediction.probability}%</p>
                                <p><strong>Method:</strong> ${prediction.method}</p>
                                <p><strong>Reason:</strong> ${prediction.reason}</p>
                            </div>
                            <div>
                                <p><strong>Immediate Target:</strong> ${prediction.targets.immediate}</p>
                                <p><strong>Secondary Target:</strong> ${prediction.targets.secondary}</p>
                            </div>
                        </div>
                    </div>

                    <div class="section">
                        <h2>🧠 AI LEARNING STATUS</h2>
                        <div class="grid-3">
                            <div>
                                <p><strong>Total Predictions:</strong> ${analysis.ai_learning.total_predictions}</p>
                                <p><strong>Accuracy:</strong> ${analysis.ai_learning.accuracy}%</p>
                            </div>
                            <div>
                                <p><strong>Patterns Learned:</strong> ${analysis.ai_learning.patterns_learned}</p>
                                <p><strong>Confidence Boost:</strong> ${analysis.ai_learning.confidence_boost}x</p>
                            </div>
                            <div>
                                <p><strong>Performance Trend:</strong> ${analysis.ai_learning.performance_trend}</p>
                                <p><strong>Risk Level:</strong> ${analysis.risk_management.risk_level}</p>
                            </div>
                        </div>
                    </div>

                    <div class="section">
                        <h2>📈 TRADING PLAN</h2>
                        <div class="grid-2">
                            <div>
                                <p><strong>Entry Strategy:</strong> ${analysis.trading_plan.entry_strategy}</p>
                                <p><strong>Entry Price:</strong> ${analysis.trading_plan.entry_price}</p>
                            </div>
                            <div>
                                <p><strong>Stop Loss:</strong> ${analysis.trading_plan.stop_loss}</p>
                                <p><strong>Risk/Reward:</strong> ${analysis.trading_plan.risk_reward}</p>
                            </div>
                        </div>
                    </div>

                    <div class="section">
                        <h2>🤖 TEACH THE AI</h2>
                        <p>Help the AI learn by providing feedback on this prediction:</p>
                        <div class="grid-2">
                            <button onclick="teachAI('BULLISH')" style="padding: 15px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px;">
                                ✅ Actual Result was BULLISH
                            </button>
                            <button onclick="teachAI('BEARISH')" style="padding: 15px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px;">
                                ❌ Actual Result was BEARISH
                            </button>
                        </div>
                    </div>
                `;
            }

            async function teachAI(actualResult) {
                if (!currentAnalysis) {
                    alert('No analysis to learn from!');
                    return;
                }

                try {
                    const response = await fetch('/learn', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            features: currentAnalysis.chart_analysis,
                            prediction: currentAnalysis.prediction.direction,
                            actual_result: actualResult,
                            user_confidence: 1
                        })
                    });

                    const result = await response.json();
                    alert(`✅ AI has learned from this result! New accuracy: ${result.new_accuracy}`);
                    loadAIStatus(); // Refresh status
                    
                } catch (error) {
                    alert('Error teaching AI: ' + error);
                }
            }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 ICT Market Predictor with Self-Learning AI Started!")
    print("🧠 AI Brain Activated - Ready to Learn!")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
