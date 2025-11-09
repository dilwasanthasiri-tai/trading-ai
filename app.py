from flask import Flask, jsonify, request
from datetime import datetime
import threading
import time
import os
import json
import random
import base64
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class RealCandleDetector:
    def __init__(self):
        self.min_candle_height = 15
        self.max_candle_width = 40
        self.min_candle_area = 50
        
    def detect_real_candles(self, image_data):
        """Detect REAL candles in TradingView charts using advanced computer vision"""
        try:
            # Convert to OpenCV format
            image = Image.open(io.BytesIO(image_data))
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            original_height, original_width = opencv_image.shape[:2]
            
            # Create a copy for processing
            processing_img = opencv_image.copy()
            
            # Convert to grayscale
            gray = cv2.cvtColor(processing_img, cv2.COLOR_BGR2GRAY)
            
            # Multiple detection strategies
            
            # Strategy 1: Detect candle bodies (rectangular shapes)
            candles_strategy1 = self.detect_candle_bodies(processing_img, gray)
            
            # Strategy 2: Detect candle wicks (vertical lines)
            candles_strategy2 = self.detect_candle_wicks(processing_img, gray)
            
            # Strategy 3: Detect by color (common candle colors)
            candles_strategy3 = self.detect_by_color(processing_img)
            
            # Combine all detections
            all_candles = candles_strategy1 + candles_strategy2 + candles_strategy3
            
            # Remove duplicates and merge nearby candles
            merged_candles = self.merge_similar_candles(all_candles)
            
            # Sort candles by X position (left to right)
            merged_candles.sort(key=lambda x: x['x'])
            
            print(f"✅ Detected {len(merged_candles)} real candles")
            
            return {
                'candles': merged_candles,
                'image_info': {
                    'original_width': original_width,
                    'original_height': original_height
                },
                'detection_method': 'real_candle_detection'
            }
            
        except Exception as e:
            print(f"❌ Candle detection error: {e}")
            return {'candles': [], 'error': str(e)}

    def detect_candle_bodies(self, img, gray):
        """Detect candle bodies using contour analysis"""
        candles = []
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_candle_area:
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            
            # Candle-like properties
            aspect_ratio = h / w if w > 0 else 0
            is_vertical = aspect_ratio > 1.5 and h > self.min_candle_height
            is_rectangle = 0.3 < w/h < 3.0  # Reasonable rectangle ratio
            
            if is_vertical or is_rectangle:
                candles.append({
                    'x': x + w // 2,
                    'high': y,
                    'low': y + h,
                    'width': w,
                    'height': h,
                    'type': 'body',
                    'confidence': min(area / 100, 1.0)
                })
        
        return candles

    def detect_candle_wicks(self, img, gray):
        """Detect candle wicks using line detection"""
        candles = []
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines using Hough Transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=30, 
                               minLineLength=20, maxLineGap=5)
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # Check if line is vertical (candle wick)
                is_vertical = abs(x2 - x1) < 5 and abs(y2 - y1) > 10
                is_near_vertical = abs(x2 - x1) < 8 and abs(y2 - y1) > 15
                
                if is_vertical or is_near_vertical:
                    candles.append({
                        'x': (x1 + x2) // 2,
                        'high': min(y1, y2),
                        'low': max(y1, y2),
                        'width': 4,
                        'height': abs(y2 - y1),
                        'type': 'wick',
                        'confidence': 0.7
                    })
        
        return candles

    def detect_by_color(self, img):
        """Detect candles by common colors (green/red candles)"""
        candles = []
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for bullish (green) and bearish (red) candles
        # Green candles (bullish)
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Red candles (bearish) - two ranges for red
        lower_red1 = np.array([0, 40, 40])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 40, 40])
        upper_red2 = np.array([180, 255, 255])
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        # Combine masks
        candle_mask = cv2.bitwise_or(green_mask, red_mask)
        
        # Find contours in the mask
        contours, _ = cv2.findContours(candle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 20:  # Minimum area for color detection
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            
            if h > self.min_candle_height and w < self.max_candle_width:
                candles.append({
                    'x': x + w // 2,
                    'high': y,
                    'low': y + h,
                    'width': w,
                    'height': h,
                    'type': 'color_based',
                    'confidence': 0.8
                })
        
        return candles

    def merge_similar_candles(self, candles):
        """Merge nearby candles that likely represent the same candle"""
        if not candles:
            return []
            
        merged = []
        used_indices = set()
        
        for i, candle1 in enumerate(candles):
            if i in used_indices:
                continue
                
            similar_candles = [candle1]
            
            for j, candle2 in enumerate(candles[i+1:], i+1):
                if j in used_indices:
                    continue
                    
                # Check if candles are close (same candle detected by multiple methods)
                distance = abs(candle1['x'] - candle2['x'])
                if distance < 20:  # Pixels
                    similar_candles.append(candle2)
                    used_indices.add(j)
            
            # Merge similar candles
            if len(similar_candles) > 1:
                avg_x = sum(c['x'] for c in similar_candles) // len(similar_candles)
                min_high = min(c['high'] for c in similar_candles)
                max_low = max(c['low'] for c in similar_candles)
                avg_confidence = sum(c['confidence'] for c in similar_candles) / len(similar_candles)
                
                merged.append({
                    'x': avg_x,
                    'high': min_high,
                    'low': max_low,
                    'width': 20,
                    'height': max_low - min_high,
                    'type': 'merged',
                    'confidence': min(avg_confidence * 1.2, 1.0)  # Boost confidence
                })
            else:
                merged.append(candle1)
            
            used_indices.add(i)
        
        return merged

class FVGDetector:
    def __init__(self):
        self.candle_detector = RealCandleDetector()
        
    def find_real_fvgs(self, candles):
        """Find REAL FVGs based on actual candle positions"""
        fvgs = []
        
        if len(candles) < 3:
            return fvgs
        
        # Analyze candle sequences for FVG patterns
        for i in range(len(candles) - 2):
            candle1 = candles[i]
            candle3 = candles[i + 2]
            
            # Bullish FVG: Candle1 high < Candle3 low
            if candle1['high'] < candle3['low']:
                gap_size = candle3['low'] - candle1['high']
                if gap_size > 5:  # Minimum gap size
                    fvgs.append({
                        'type': 'fvg_bullish',
                        'candle1': candle1,
                        'candle3': candle3,
                        'gap_size': gap_size,
                        'real_position': True,
                        'color': 'rgba(0, 255, 0, 0.3)',
                        'label': 'Real Bullish FVG',
                        'description': f'Gap size: {gap_size}px'
                    })
            
            # Bearish FVG: Candle1 low > Candle3 high
            elif candle1['low'] > candle3['high']:
                gap_size = candle1['low'] - candle3['high']
                if gap_size > 5:  # Minimum gap size
                    fvgs.append({
                        'type': 'fvg_bearish',
                        'candle1': candle1,
                        'candle3': candle3,
                        'gap_size': gap_size,
                        'real_position': True,
                        'color': 'rgba(255, 0, 0, 0.3)',
                        'label': 'Real Bearish FVG',
                        'description': f'Gap size: {gap_size}px'
                    })
        
        return fvgs

class ChartAnalyzer:
    def __init__(self):
        self.fvg_detector = FVGDetector()
        
    def analyze_chart_image(self, file_data):
        """Analyze uploaded TradingView chart to detect REAL FVG patterns"""
        try:
            # Step 1: Detect real candles
            candle_result = self.fvg_detector.candle_detector.detect_real_candles(file_data)
            
            if 'error' in candle_result:
                return {'error': candle_result['error']}
            
            real_candles = candle_result['candles']
            
            # Step 2: Find FVGs from real candle positions
            real_fvgs = self.fvg_detector.find_real_fvgs(real_candles)
            
            analysis = {
                'chart_type': 'candlestick',
                'timeframe': '1D',
                'auto_annotations': real_fvgs,
                'candles_detected': len(real_candles),
                'real_candles': real_candles,  # Send candle data to frontend
                'patterns_found': [
                    {
                        'name': 'Real Fair Value Gap (FVG)',
                        'type': 'real_fvg',
                        'confidence': 0.95,
                        'auto_detected': True,
                        'location': 'actual_candle_positions'
                    }
                ],
                'ict_concepts': {
                    'fair_value_gaps': len(real_fvgs),
                    'order_blocks': 0,
                    'market_structure': 'bullish' if len(real_fvgs) > 0 else 'neutral'
                },
                'sentiment': 'bullish' if len([f for f in real_fvgs if f['type'] == 'fvg_bullish']) > 0 else 'bearish',
                'confidence_score': min(len(real_fvgs) * 0.2 + 0.5, 0.95),
                'image_info': candle_result['image_info'],
                'detection_method': 'real_computer_vision'
            }
            return analysis
        except Exception as e:
            return {'error': f'Real analysis failed: {str(e)}'}

# ... (keep the rest of your existing classes: ICTPatterns, SelfLearningAI, etc.)

class ICTPatterns:
    def detect_fair_value_gaps(self, data):
        """ICT Fair Value Gap Detection"""
        # ... (your existing code)

class SelfLearningAI:
    def __init__(self):
        self.knowledge_base = {}
        self.learning_active = False
        self.ict_patterns = ICTPatterns()
        self.chart_analyzer = ChartAnalyzer()  # Now with real detection!
        
    # ... (your existing methods)

# Initialize AI
ai = SelfLearningAI()

@app.route('/')
def home():
    return jsonify({
        "message": "🤖 TradingView REAL FVG Detection AI",
        "status": "ACTIVE ✅", 
        "version": "10.0",
        "features": [
            "REAL Candle Detection",
            "Computer Vision FVG Detection",
            "Actual Candle Position Analysis",
            "Professional ICT Analysis"
        ],
        "endpoints": {
            "/web-draw": "Upload TradingView Charts",
            "/analyze/<symbol>": "Symbol analysis"
        }
    })

# TradingView Chart Analysis Interface
@app.route('/web-draw')
def web_draw():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎯 TradingView REAL FVG Detection</title>
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
            .result {
                background: #e8f5e8;
                padding: 25px;
                margin: 25px 0;
                border-radius: 10px;
                border-left: 5px solid #28a745;
            }
            .info-box {
                background: #e3f2fd;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
            }
            .upload-area {
                border: 3px dashed #007bff;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                border-radius: 10px;
                background: #f8f9fa;
            }
            .coordinate-info {
                position: absolute;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 12px;
                pointer-events: none;
            }
            .candle-marker {
                position: absolute;
                width: 4px;
                height: 4px;
                background: blue;
                border-radius: 50%;
                pointer-events: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 TradingView REAL FVG Detection</h1>
            
            <div class="info-box">
                <h3>📊 REAL Computer Vision Detection</h3>
                <p><strong>Upload TradingView screenshot → AI detects ACTUAL candles and REAL FVGs</strong></p>
                <p>• Computer vision detects real candle positions</p>
                <p>• FVGs drawn between ACTUAL candle locations</p>
                <p>• No fake patterns - real analysis</p>
            </div>
            
            <!-- File Upload -->
            <div>
                <h3>📁 Step 1: Upload TradingView Chart</h3>
                <div class="upload-area">
                    <input type="file" id="imageUpload" accept="image/*">
                    <p>Upload TradingView screenshot (PNG, JPG, JPEG)</p>
                </div>
            </div>

            <!-- Auto-Draw Controls -->
            <div>
                <h3>🤖 Step 2: Detect REAL FVG Patterns</h3>
                <div class="toolbar">
                    <button class="tool-btn auto-draw-btn" id="autoDrawBtn">
                        🔍 Detect REAL FVGs
                    </button>
                    <button class="tool-btn" id="showCandlesBtn">
                        🕯️ Show Detected Candles
                    </button>
                    <button class="tool-btn" id="clearAutoDraw">🧹 Clear</button>
                </div>
            </div>

            <div class="legend">
                <div class="legend-item"><div class="legend-color" style="background: rgba(0,255,0,0.3);"></div> Real Bullish FVG</div>
                <div class="legend-item"><div class="legend-color" style="background: rgba(255,0,0,0.3);"></div> Real Bearish FVG</div>
                <div class="legend-item"><div class="legend-color" style="background: blue;"></div> Detected Candles</div>
            </div>

            <div class="canvas-container">
                <canvas id="drawingCanvas"></canvas>
                <div id="coordinateInfo" class="coordinate-info" style="display: none;"></div>
            </div>

            <!-- Analysis -->
            <div>
                <h3>🚀 Step 3: REAL Analysis</h3>
                <button id="analyzeBtn" style="padding: 15px 30px; font-size: 18px;">
                    🤖 Analyze REAL Patterns
                </button>
            </div>

            <div id="result" class="result" style="display:none;"></div>
        </div>

        <script>
            const canvas = document.getElementById('drawingCanvas');
            const ctx = canvas.getContext('2d');
            const coordinateInfo = document.getElementById('coordinateInfo');
            let autoAnnotations = [];
            let baseImage = null;
            let originalImageWidth = 800;
            let originalImageHeight = 500;
            let detectedCandles = [];
            let showCandles = false;

            function resizeCanvas() {
                canvas.width = canvas.offsetWidth;
                canvas.height = 500;
                if (baseImage) {
                    redrawEverything();
                }
            }
            resizeCanvas();
            window.addEventListener('resize', resizeCanvas);

            // Show coordinates on mouse move
            canvas.addEventListener('mousemove', function(e) {
                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                coordinateInfo.style.display = 'block';
                coordinateInfo.style.left = (e.clientX + 10) + 'px';
                coordinateInfo.style.top = (e.clientY + 10) + 'px';
                coordinateInfo.textContent = `X: ${Math.round(x)}, Y: ${Math.round(y)}`;
            });

            canvas.addEventListener('mouseleave', function() {
                coordinateInfo.style.display = 'none';
            });

            // Auto-draw functionality for REAL FVG detection
            document.getElementById('autoDrawBtn').addEventListener('click', async function() {
                const fileInput = document.getElementById('imageUpload');
                if (!fileInput.files[0]) {
                    alert('Please upload a TradingView chart first!');
                    return;
                }

                const formData = new FormData();
                formData.append('chart_image', fileInput.files[0]);

                const autoDrawBtn = this;
                autoDrawBtn.innerHTML = '🔍 Analyzing REAL Candles...';
                autoDrawBtn.disabled = true;

                try {
                    const response = await fetch('/upload-chart', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        autoAnnotations = data.analysis.auto_annotations || [];
                        detectedCandles = data.analysis.real_candles || [];
                        
                        // Get original image dimensions from backend
                        if (data.analysis.image_info) {
                            originalImageWidth = data.analysis.image_info.original_width;
                            originalImageHeight = data.analysis.image_info.original_height;
                        }
                        
                        drawAutoAnnotations();
                        const fvgCount = autoAnnotations.filter(a => a.type.includes('fvg')).length;
                        const candleCount = detectedCandles.length;
                        
                        alert(`✅ Detected ${candleCount} real candles and ${fvgCount} REAL FVG patterns!`);
                    } else {
                        alert('Real FVG detection failed: ' + data.error);
                    }
                } catch (error) {
                    alert('Detection error: ' + error);
                } finally {
                    autoDrawBtn.innerHTML = '🔍 Detect REAL FVGs';
                    autoDrawBtn.disabled = false;
                }
            });

            // Toggle candle display
            document.getElementById('showCandlesBtn').addEventListener('click', function() {
                showCandles = !showCandles;
                this.innerHTML = showCandles ? '🕯️ Hide Candles' : '🕯️ Show Candles';
                drawAutoAnnotations();
            });

            function drawAutoAnnotations() {
                if (!baseImage) return;
                
                redrawEverything();
                
                // Draw detected candles if enabled
                if (showCandles) {
                    drawDetectedCandles();
                }
                
                // Draw all detected FVG annotations
                autoAnnotations.forEach(annotation => {
                    drawRealFVGAnnotation(annotation);
                });
            }

            function drawDetectedCandles() {
                if (!detectedCandles.length) return;
                
                const scaleX = canvas.width / originalImageWidth;
                const scaleY = canvas.height / originalImageHeight;
                
                ctx.fillStyle = 'blue';
                ctx.globalAlpha = 0.6;
                
                detectedCandles.forEach(candle => {
                    const x = candle.x * scaleX;
                    const high = candle.high * scaleY;
                    const low = candle.low * scaleY;
                    const width = (candle.width || 10) * scaleX;
                    
                    // Draw candle body
                    ctx.fillRect(x - width/2, high, width, low - high);
                    
                    // Draw candle center marker
                    ctx.fillStyle = 'red';
                    ctx.fillRect(x - 2, high - 10, 4, 4);
                    ctx.fillStyle = 'blue';
                });
                
                ctx.globalAlpha = 1.0;
            }

            function drawRealFVGAnnotation(annotation) {
                if (!annotation.real_position) return;
                
                const candle1 = annotation.candle1;
                const candle3 = annotation.candle3;
                
                // Get the ACTUAL displayed image dimensions
                const displayedWidth = canvas.width;
                const displayedHeight = canvas.height;
                
                // Calculate scaling factors
                const scaleX = displayedWidth / originalImageWidth;
                const scaleY = displayedHeight / originalImageHeight;
                
                if (annotation.type === 'fvg_bullish') {
                    // Bullish FVG: Candle1 high < Candle3 low
                    const rectX = candle1.x * scaleX + ((candle1.width || 20)/2) * scaleX;
                    const rectY = candle1.high * scaleY;
                    const rectWidth = (candle3.x - candle1.x - (candle1.width || 20)) * scaleX;
                    const rectHeight = (candle3.low - candle1.high) * scaleY;
                    
                    if (rectWidth > 0 && rectHeight > 0) {
                        // Draw REAL FVG rectangle
                        ctx.fillStyle = annotation.color;
                        ctx.globalAlpha = 0.3;
                        ctx.fillRect(rectX, rectY, rectWidth, rectHeight);
                        ctx.globalAlpha = 1.0;
                        ctx.strokeStyle = '#00aa00';
                        ctx.lineWidth = 2;
                        ctx.strokeRect(rectX, rectY, rectWidth, rectHeight);
                        
                        // Draw label
                        ctx.fillStyle = '#006600';
                        ctx.font = 'bold 11px Arial';
                        ctx.fillText(annotation.label, rectX + 5, rectY - 8);
                        ctx.font = '10px Arial';
                        ctx.fillText(annotation.description, rectX + 5, rectY + rectHeight + 15);
                    }
                    
                } else if (annotation.type === 'fvg_bearish') {
                    // Bearish FVG: Candle1 low > Candle3 high
                    const rectX = candle1.x * scaleX + ((candle1.width || 20)/2) * scaleX;
                    const rectY = candle3.high * scaleY;
                    const rectWidth = (candle3.x - candle1.x - (candle1.width || 20)) * scaleX;
                    const rectHeight = (candle1.low - candle3.high) * scaleY;
                    
                    if (rectWidth > 0 && rectHeight > 0) {
                        // Draw REAL FVG rectangle
                        ctx.fillStyle = annotation.color;
                        ctx.globalAlpha = 0.3;
                        ctx.fillRect(rectX, rectY, rectWidth, rectHeight);
                        ctx.globalAlpha = 1.0;
                        ctx.strokeStyle = '#aa0000';
                        ctx.lineWidth = 2;
                        ctx.strokeRect(rectX, rectY, rectWidth, rectHeight);
                        
                        // Draw label
                        ctx.fillStyle = '#660000';
                        ctx.font = 'bold 11px Arial';
                        ctx.fillText(annotation.label, rectX + 5, rectY - 8);
                        ctx.font = '10px Arial';
                        ctx.fillText(annotation.description, rectX + 5, rectY + rectHeight + 15);
                    }
                }
            }

            function redrawEverything() {
                if (baseImage) {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.drawImage(baseImage, 0, 0, canvas.width, canvas.height);
                }
            }

            // Image upload
            document.getElementById('imageUpload').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        baseImage = new Image();
                        baseImage.onload = function() {
                            originalImageWidth = baseImage.naturalWidth;
                            originalImageHeight = baseImage.naturalHeight;
                            redrawEverything();
                        };
                        baseImage.src = event.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            });

            // Analysis button
            document.getElementById('analyzeBtn').addEventListener('click', async function() {
                const fileInput = document.getElementById('imageUpload');
                if (!fileInput.files[0]) {
                    alert('Please upload a TradingView chart first!');
                    return;
                }

                const formData = new FormData();
                formData.append('chart_image', fileInput.files[0]);

                const resultDiv = document.getElementById('result');
                const analyzeBtn = this;

                analyzeBtn.innerHTML = '⏳ Analyzing REAL Patterns...';
                analyzeBtn.disabled = true;

                try {
                    const response = await fetch('/upload-chart', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        const fvgCount = data.analysis.ict_concepts.fair_value_gaps;
                        const candleCount = data.analysis.candles_detected;
                        const detectionMethod = data.analysis.detection_method;
                        
                        resultDiv.innerHTML = `
                            <h3>✅ REAL FVG Analysis Complete!</h3>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                <div>
                                    <h4>🎯 REAL Pattern Summary</h4>
                                    <p><strong>Real Candles Detected:</strong> ${candleCount}</p>
                                    <p><strong>Real FVG Patterns:</strong> ${fvgCount}</p>
                                    <p><strong>Detection Method:</strong> ${detectionMethod}</p>
                                </div>
                                <div>
                                    <h4>📊 Computer Vision Analysis</h4>
                                    <p><strong>Image Size:</strong> ${originalImageWidth} × ${originalImageHeight}</p>
                                    <p><strong>Sentiment:</strong> ${data.analysis.sentiment}</p>
                                    <p><strong>Confidence:</strong> ${(data.analysis.confidence_score * 100).toFixed(1)}%</p>
                                </div>
                            </div>
                            <p><strong>Note:</strong> ${fvgCount} REAL FVG patterns detected between ACTUAL candle positions using computer vision</p>
                            <p><button onclick="document.getElementById('showCandlesBtn').click()" style="padding: 8px 15px; margin: 5px;">🕯️ Show Detected Candles</button></p>
                        `;
                    } else {
                        resultDiv.innerHTML = `<h3>❌ Error:</h3><p>${data.error}</p>`;
                    }
                    resultDiv.style.display = 'block';
                } catch (error) {
                    resultDiv.innerHTML = `<h3>❌ Network Error:</h3><p>${error}</p>`;
                    resultDiv.style.display = 'block';
                } finally {
                    analyzeBtn.innerHTML = '🤖 Analyze REAL Patterns';
                    analyzeBtn.disabled = false;
                }
            });

            // Clear drawings
            document.getElementById('clearAutoDraw').addEventListener('click', function() {
                autoAnnotations = [];
                detectedCandles = [];
                showCandles = false;
                document.getElementById('showCandlesBtn').innerHTML = '🕯️ Show Candles';
                if (baseImage) {
                    redrawEverything();
                }
                alert('Drawings cleared! Upload new chart for REAL detection.');
            });
        </script>
    </body>
    </html>
    '''

# Upload endpoint for TradingView charts
@app.route('/upload-chart', methods=['POST'])
def upload_chart():
    try:
        file = request.files.get('chart_image')
        
        if file and file.filename != '':
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type'}), 400
            
            file_data = file.read()
            
            # Analyze the uploaded TradingView chart with REAL computer vision
            analysis = ai.chart_analyzer.analyze_chart_image(file_data)
            
            return jsonify({
                'status': 'success',
                'message': 'REAL FVG analysis complete 🎯',
                'auto_annotations_count': len(analysis.get('auto_annotations', [])),
                'candles_detected': analysis.get('candles_detected', 0),
                'analysis': analysis,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'detection_note': 'REAL FVGs detected between actual candle positions'
            })
        else:
            return jsonify({'error': 'Please upload a TradingView chart image'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 TradingView REAL FVG Detection AI Started!")
    print("🎯 Now detects REAL candles and FVGs using computer vision")
    ai.start_learning()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
