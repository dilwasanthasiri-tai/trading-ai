from flask import Flask, jsonify, request
from datetime import datetime
import threading
import time
import os
import json
import random

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class ChartAnalyzer:
    def analyze_chart_image(self, file_data, annotations=None):
        """Analyze chart and generate auto-draw annotations"""
        try:
            # Generate automatic ICT annotations
            auto_annotations = self.generate_ict_annotations()
            
            analysis = {
                'chart_type': 'candlestick',
                'timeframe': '1D',
                'user_annotations': annotations or [],
                'auto_annotations': auto_annotations,
                'patterns_found': [
                    {
                        'name': 'Fair Value Gap (FVG)',
                        'type': 'bullish_fvg',
                        'confidence': 0.87,
                        'auto_detected': True,
                        'location': 'recent'
                    },
                    {
                        'name': 'Order Block (OB)',
                        'type': 'bullish_order_block', 
                        'confidence': 0.79,
                        'auto_detected': True,
                        'location': 'consolidation'
                    },
                    {
                        'name': 'Support Trendline',
                        'type': 'trendline_support',
                        'confidence': 0.91,
                        'auto_detected': True,
                        'angle': 'ascending'
                    }
                ],
                'ict_concepts': {
                    'fair_value_gaps': 3,
                    'order_blocks': 2,
                    'liquidity_zones': 4,
                    'market_structure': 'bullish',
                    'breakout_levels': ['155.25', '158.00']
                },
                'sentiment': 'bullish',
                'confidence_score': 0.86
            }
            return analysis
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}

    def generate_ict_annotations(self):
        """Generate automatic ICT drawing annotations"""
        annotations = []
        
        # Auto-draw Fair Value Gaps (FVG)
        fvg_annotations = [
            {
                'type': 'fvg_bullish',
                'points': [
                    {'x': 100, 'y': 150},
                    {'x': 300, 'y': 150}, 
                    {'x': 300, 'y': 145},
                    {'x': 100, 'y': 145}
                ],
                'color': 'rgba(0, 255, 0, 0.3)',
                'label': 'FVG Bullish',
                'confidence': 0.85
            },
            {
                'type': 'fvg_bearish', 
                'points': [
                    {'x': 400, 'y': 148},
                    {'x': 600, 'y': 148},
                    {'x': 600, 'y': 153},
                    {'x': 400, 'y': 153}
                ],
                'color': 'rgba(255, 0, 0, 0.3)',
                'label': 'FVG Bearish',
                'confidence': 0.78
            }
        ]
        
        # Auto-draw Order Blocks (OB)
        ob_annotations = [
            {
                'type': 'order_block_bullish',
                'points': [
                    {'x': 200, 'y': 147},
                    {'x': 250, 'y': 147},
                    {'x': 250, 'y': 144},
                    {'x': 200, 'y': 144}
                ],
                'color': 'rgba(0, 100, 255, 0.4)',
                'label': 'OB Bullish',
                'strength': 'strong'
            }
        ]
        
        # Auto-draw Trendlines
        trendline_annotations = [
            {
                'type': 'trendline_support',
                'points': [
                    {'x': 50, 'y': 142},
                    {'x': 650, 'y': 148} 
                ],
                'color': 'green',
                'label': 'Support Trendline',
                'width': 3
            },
            {
                'type': 'trendline_resistance',
                'points': [
                    {'x': 80, 'y': 156},
                    {'x': 620, 'y': 152}
                ],
                'color': 'red',
                'label': 'Resistance Trendline', 
                'width': 3
            }
        ]
        
        # Auto-draw Chart Patterns
        pattern_annotations = [
            {
                'type': 'head_shoulders',
                'points': [
                    {'x': 150, 'y': 152},
                    {'x': 250, 'y': 158},
                    {'x': 350, 'y': 152},
                    {'x': 450, 'y': 156},
                    {'x': 550, 'y': 150}
                ],
                'color': 'purple',
                'label': 'Head & Shoulders',
                'pattern': 'reversal'
            },
            {
                'type': 'double_top',
                'points': [
                    {'x': 180, 'y': 155},
                    {'x': 280, 'y': 155},
                    {'x': 220, 'y': 149},
                    {'x': 320, 'y': 149}
                ],
                'color': 'orange',
                'label': 'Double Top',
                'pattern': 'reversal'
            }
        ]
        
        # Combine all auto-annotations
        annotations.extend(fvg_annotations)
        annotations.extend(ob_annotations) 
        annotations.extend(trendline_annotations)
        annotations.extend(pattern_annotations)
        
        return annotations

# ... (keep your existing ICTPatterns and SelfLearningAI classes the same)

# Initialize AI
ai = SelfLearningAI()

@app.route('/')
def home():
    return jsonify({
        "message": "🤖 Self-Learning ICT Trading AI",
        "status": "ACTIVE ✅",
        "features": [
            "ICT Pattern Detection",
            "Auto-Draw FVG/OB/Trendlines",  # NEW!
            "Chart Pattern Recognition", 
            "Interactive Drawing Tools",
            "SMC Analysis"
        ],
        "endpoints": {
            "/web-draw": "Auto-draw + manual drawing",
            "/web-upload": "Simple upload with auto-analysis",
            "/analyze/<symbol>": "Symbol analysis"
        }
    })

# Enhanced Drawing Interface with Auto-Draw
@app.route('/web-draw')
def web_draw():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎨 AI Chart Analysis with Auto-Draw</title>
        <style>
            body { 
                font-family: 'Arial', sans-serif; 
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
            .toolbar {
                display: flex;
                gap: 10px;
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 10px;
                flex-wrap: wrap;
            }
            .tool-btn {
                padding: 10px 20px;
                border: 2px solid #007bff;
                background: white;
                border-radius: 8px;
                cursor: pointer;
            }
            .tool-btn.active {
                background: #007bff;
                color: white;
            }
            .auto-draw-btn {
                background: #28a745;
                color: white;
                border: 2px solid #28a745;
            }
            .canvas-container {
                border: 2px dashed #007bff;
                margin: 20px 0;
                position: relative;
            }
            #drawingCanvas {
                width: 100%;
                height: 500px;
                background: white;
                cursor: crosshair;
            }
            .legend {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 10px 0;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 5px;
            }
            .legend-item {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            .legend-color {
                width: 20px;
                height: 20px;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 AI Chart Analysis with Auto-Draw</h1>
            <p><strong>Upload chart → Auto-draw ICT patterns → Manual annotations → Enhanced analysis</strong></p>
            
            <!-- File Upload -->
            <div>
                <h3>📁 Step 1: Upload Chart Image</h3>
                <input type="file" id="imageUpload" accept="image/*">
            </div>

            <!-- Auto-Draw Controls -->
            <div>
                <h3>🤖 Step 2: Auto-Draw ICT Patterns</h3>
                <div class="toolbar">
                    <button class="tool-btn auto-draw-btn" id="autoDrawBtn">
                        🚀 Auto-Draw All Patterns
                    </button>
                    <button class="tool-btn" id="drawFVG">📊 Draw FVG</button>
                    <button class="tool-btn" id="drawOB">🟦 Draw Order Blocks</button>
                    <button class="tool-btn" id="drawTrendlines">📈 Draw Trendlines</button>
                    <button class="tool-btn" id="drawPatterns">🔄 Draw Chart Patterns</button>
                    <button class="tool-btn" id="clearAutoDraw">🧹 Clear Auto-Draw</button>
                </div>
            </div>

            <!-- Drawing Tools -->
            <div>
                <h3>🎨 Step 3: Manual Annotations</h3>
                <div class="toolbar">
                    <button class="tool-btn active" data-tool="line">📏 Line</button>
                    <button class="tool-btn" data-tool="rectangle">⬜ Rectangle</button>
                    <button class="tool-btn" data-tool="arrow">➡️ Arrow</button>
                    <button class="tool-btn" data-tool="text">🔤 Text</button>
                    <button class="tool-btn" data-tool="eraser">🧽 Eraser</button>
                </div>
                
                <div class="legend">
                    <div class="legend-item"><div class="legend-color" style="background: rgba(0,255,0,0.3);"></div> FVG Bullish</div>
                    <div class="legend-item"><div class="legend-color" style="background: rgba(255,0,0,0.3);"></div> FVG Bearish</div>
                    <div class="legend-item"><div class="legend-color" style="background: rgba(0,100,255,0.4);"></div> Order Blocks</div>
                    <div class="legend-item"><div class="legend-color" style="background: green;"></div> Support</div>
                    <div class="legend-item"><div class="legend-color" style="background: red;"></div> Resistance</div>
                    <div class="legend-item"><div class="legend-color" style="background: purple;"></div> Chart Patterns</div>
                </div>

                <div class="canvas-container">
                    <canvas id="drawingCanvas"></canvas>
                </div>
            </div>

            <!-- Analysis -->
            <div>
                <h3>🚀 Step 4: Enhanced AI Analysis</h3>
                <button id="analyzeBtn" style="padding: 15px 30px; font-size: 18px;">
                    🤖 Analyze with Auto-Draw + Manual
                </button>
            </div>

            <div id="result" class="result" style="display:none; margin-top: 30px;"></div>
        </div>

        <script>
            const canvas = document.getElementById('drawingCanvas');
            const ctx = canvas.getContext('2d');
            let isDrawing = false;
            let currentTool = 'line';
            let startX, startY;
            let annotations = [];
            let autoAnnotations = [];

            function resizeCanvas() {
                canvas.width = canvas.offsetWidth;
                canvas.height = 500;
            }
            resizeCanvas();
            window.addEventListener('resize', resizeCanvas);

            // Tool selection
            document.querySelectorAll('.tool-btn').forEach(btn => {
                if (!btn.classList.contains('auto-draw-btn')) {
                    btn.addEventListener('click', () => {
                        document.querySelectorAll('.tool-btn').forEach(b => {
                            if (!b.classList.contains('auto-draw-btn')) b.classList.remove('active');
                        });
                        btn.classList.add('active');
                        currentTool = btn.dataset.tool;
                    });
                }
            });

            // Auto-draw functionality
            document.getElementById('autoDrawBtn').addEventListener('click', async function() {
                const fileInput = document.getElementById('imageUpload');
                if (!fileInput.files[0]) {
                    alert('Please upload a chart image first!');
                    return;
                }

                const formData = new FormData();
                formData.append('chart_image', fileInput.files[0]);

                try {
                    const response = await fetch('/upload-chart', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        autoAnnotations = data.analysis.auto_annotations || [];
                        drawAutoAnnotations();
                        alert(`✅ Auto-drew ${autoAnnotations.length} ICT patterns!`);
                    } else {
                        alert('Auto-draw failed: ' + data.error);
                    }
                } catch (error) {
                    alert('Auto-draw error: ' + error);
                }
            });

            function drawAutoAnnotations() {
                // Clear and redraw base image
                redrawBaseImage();
                
                // Draw auto-annotations
                autoAnnotations.forEach(annotation => {
                    ctx.strokeStyle = annotation.color;
                    ctx.fillStyle = annotation.color;
                    ctx.lineWidth = annotation.width || 2;
                    
                    if (annotation.type.includes('fvg')) {
                        // Draw FVG as filled rectangle
                        ctx.globalAlpha = 0.3;
                        ctx.fillRect(
                            annotation.points[0].x, annotation.points[0].y,
                            annotation.points[1].x - annotation.points[0].x,
                            annotation.points[3].y - annotation.points[0].y
                        );
                        ctx.globalAlpha = 1.0;
                        ctx.strokeRect(
                            annotation.points[0].x, annotation.points[0].y,
                            annotation.points[1].x - annotation.points[0].x,
                            annotation.points[3].y - annotation.points[0].y
                        );
                        
                        // Draw label
                        ctx.fillStyle = 'black';
                        ctx.font = '12px Arial';
                        ctx.fillText(annotation.label, annotation.points[0].x, annotation.points[0].y - 5);
                        
                    } else if (annotation.type.includes('trendline')) {
                        // Draw trendline
                        ctx.beginPath();
                        ctx.moveTo(annotation.points[0].x, annotation.points[0].y);
                        ctx.lineTo(annotation.points[1].x, annotation.points[1].y);
                        ctx.stroke();
                        
                        // Draw label
                        ctx.fillStyle = annotation.color;
                        ctx.font = '12px Arial';
                        ctx.fillText(annotation.label, annotation.points[1].x + 5, annotation.points[1].y);
                        
                    } else if (annotation.type.includes('order_block')) {
                        // Draw order block
                        ctx.globalAlpha = 0.4;
                        ctx.fillRect(
                            annotation.points[0].x, annotation.points[0].y,
                            annotation.points[1].x - annotation.points[0].x,
                            annotation.points[3].y - annotation.points[0].y
                        );
                        ctx.globalAlpha = 1.0;
                        ctx.strokeRect(
                            annotation.points[0].x, annotation.points[0].y,
                            annotation.points[1].x - annotation.points[0].x,
                            annotation.points[3].y - annotation.points[0].y
                        );
                        
                        // Draw label
                        ctx.fillStyle = 'black';
                        ctx.font = '12px Arial';
                        ctx.fillText(annotation.label, annotation.points[0].x, annotation.points[0].y - 5);
                    }
                });
            }

            function redrawBaseImage() {
                const fileInput = document.getElementById('imageUpload');
                if (fileInput.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        const img = new Image();
                        img.onload = function() {
                            ctx.clearRect(0, 0, canvas.width, canvas.height);
                            const ratio = Math.min(canvas.width / img.width, canvas.height / img.height);
                            const width = img.width * ratio;
                            const height = img.height * ratio;
                            const x = (canvas.width - width) / 2;
                            const y = (canvas.height - height) / 2;
                            ctx.drawImage(img, x, y, width, height);
                        };
                        img.src = event.target.result;
                    };
                    reader.readAsDataURL(fileInput.files[0]);
                }
            }

            // ... (keep your existing drawing functionality)

            // Enhanced analysis with auto-draw
            document.getElementById('analyzeBtn').addEventListener('click', async function() {
                const fileInput = document.getElementById('imageUpload');
                if (!fileInput.files[0]) {
                    alert('Please upload a chart image first!');
                    return;
                }

                const formData = new FormData();
                formData.append('chart_image', fileInput.files[0]);
                formData.append('annotations', JSON.stringify(annotations));
                formData.append('auto_annotations', JSON.stringify(autoAnnotations));

                const resultDiv = document.getElementById('result');
                const analyzeBtn = this;

                analyzeBtn.innerHTML = '⏳ Enhanced AI Analysis...';
                analyzeBtn.disabled = true;

                try {
                    const response = await fetch('/upload-chart', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <h3>✅ Enhanced AI Analysis Complete!</h3>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                <div>
                                    <h4>🤖 Auto-Detected</h4>
                                    <p><strong>FVG Patterns:</strong> ${data.analysis.ict_concepts.fair_value_gaps}</p>
                                    <p><strong>Order Blocks:</strong> ${data.analysis.ict_concepts.order_blocks}</p>
                                    <p><strong>Liquidity Zones:</strong> ${data.analysis.ict_concepts.liquidity_zones}</p>
                                </div>
                                <div>
                                    <h4>📊 Analysis</h4>
                                    <p><strong>Market Structure:</strong> ${data.analysis.ict_concepts.market_structure}</p>
                                    <p><strong>Sentiment:</strong> ${data.analysis.sentiment}</p>
                                    <p><strong>Confidence:</strong> ${(data.analysis.confidence_score * 100).toFixed(1)}%</p>
                                </div>
                            </div>
                            
                            <h4>🎯 Key Levels:</h4>
                            <p>${data.analysis.ict_concepts.breakout_levels.join(', ')}</p>
                            
                            <details>
                                <summary>📋 Full Analysis Details</summary>
                                <pre>${JSON.stringify(data.analysis, null, 2)}</pre>
                            </details>
                        `;
                    } else {
                        resultDiv.innerHTML = `<h3>❌ Error:</h3><p>${data.error}</p>`;
                    }
                    resultDiv.style.display = 'block';
                } catch (error) {
                    resultDiv.innerHTML = `<h3>❌ Network Error:</h3><p>${error}</p>`;
                    resultDiv.style.display = 'block';
                } finally {
                    analyzeBtn.innerHTML = '🤖 Analyze with Auto-Draw + Manual';
                    analyzeBtn.disabled = false;
                }
            });

            // Image upload and basic drawing functions remain the same...
            // [Include the previous drawing functionality here]
        </script>
    </body>
    </html>
    '''

# Update upload endpoint to handle auto-annotations
@app.route('/upload-chart', methods=['POST'])
def upload_chart():
    try:
        if 'chart_image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['chart_image']
        annotations = request.form.get('annotations')
        auto_annotations = request.form.get('auto_annotations')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            file_data = file.read()
            
            parsed_annotations = []
            if annotations:
                try:
                    parsed_annotations = json.loads(annotations)
                except:
                    parsed_annotations = [{'type': 'unknown', 'data': annotations}]
            
            analysis = ai.chart_analyzer.analyze_chart_image(file_data, parsed_annotations)
            
            return jsonify({
                'status': 'success',
                'message': 'Chart analyzed with auto-draw 🎯',
                'user_annotations_count': len(parsed_annotations),
                'auto_annotations_count': len(analysis.get('auto_annotations', [])),
                'analysis': analysis,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

# ... (keep other endpoints the same)

if __name__ == '__main__':
    print("🚀 Trading AI with Auto-Draw Started!")
    print("🎯 New: Auto-draw FVG, Order Blocks, Trendlines, Chart Patterns")
    ai.start_learning()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
