from flask import Flask, request, jsonify, render_template_string
import cv2
import numpy as np
import base64
import os

app = Flask(__name__)

class TradingSignalAnalyzer:
    def analyze_chart(self, image):
        """Analyze chart image and return BUY/SELL signal"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 1. Trend Analysis
            trend_signal = self.analyze_trend(gray)
            
            # 2. Support/Resistance
            levels = self.find_key_levels(gray)
            
            # 3. Pattern Detection
            patterns = self.detect_patterns(gray)
            
            # 4. Candlestick Sentiment
            sentiment = self.analyze_candlestick_sentiment(image)
            
            # 5. Generate Final Signal
            signal, confidence = self.generate_signal(trend_signal, levels, patterns, sentiment)
            
            return {
                "signal": signal,
                "confidence": confidence,
                "trend": trend_signal,
                "key_levels": levels,
                "patterns_detected": patterns,
                "sentiment": sentiment
            }
        except Exception as e:
            return {
                "signal": "HOLD",
                "confidence": 50,
                "trend": "unknown",
                "key_levels": {"support": [], "resistance": []},
                "patterns_detected": [],
                "sentiment": "neutral",
                "error": str(e)
            }
    
    def analyze_trend(self, gray_image):
        """Analyze trend direction using OpenCV"""
        try:
            # Edge detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Detect lines (trend lines)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                   minLineLength=30, maxLineGap=10)
            
            if lines is None:
                return "neutral"
            
            # Analyze line angles
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                angles.append(angle)
            
            # Determine trend
            up_angles = [a for a in angles if a > 10]
            down_angles = [a for a in angles if a < -10]
            neutral_angles = [a for a in angles if -10 <= a <= 10]
            
            if len(up_angles) > len(down_angles) and len(up_angles) > len(neutral_angles):
                return "uptrend"
            elif len(down_angles) > len(up_angles) and len(down_angles) > len(neutral_angles):
                return "downtrend"
            else:
                return "neutral"
        except:
            return "neutral"
    
    def find_key_levels(self, gray_image):
        """Find support and resistance levels"""
        try:
            height, width = gray_image.shape
            
            # Horizontal line detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Detect horizontal lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            detected_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, horizontal_kernel)
            
            contours, _ = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            levels = []
            for contour in contours:
                if cv2.contourArea(contour) > 50:
                    x, y, w, h = cv2.boundingRect(contour)
                    if w > 50:  # Significant horizontal line
                        levels.append(y)
            
            # Remove duplicates (similar levels)
            levels = list(set(levels))
            levels.sort()
            
            # Convert to support/resistance (higher y = lower price in charts)
            if len(levels) >= 2:
                support = levels[-2:]  # Bottom levels (higher y values)
                resistance = levels[:2] # Top levels (lower y values)
            else:
                support = levels
                resistance = levels
            
            return {
                "support": support,
                "resistance": resistance
            }
        except:
            return {"support": [], "resistance": []}
    
    def detect_patterns(self, gray_image):
        """Detect basic chart patterns"""
        try:
            patterns = []
            
            # Simple pattern detection based on contours
            edges = cv2.Canny(gray_image, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 1000]
            
            if len(large_contours) >= 3:
                patterns.append("multiple_swings")
            
            # Check for consolidation (many small contours)
            if len(contours) > 10:
                patterns.append("consolidation")
            
            # Check for strong trend (few but large contours)
            if len(large_contours) >= 2 and len(contours) < 8:
                patterns.append("strong_trend")
                
            return patterns
        except:
            return []
    
    def analyze_candlestick_sentiment(self, image):
        """Analyze bullish/bearish sentiment from candle colors"""
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Detect green (bullish) areas
            green_lower = np.array([40, 40, 40])
            green_upper = np.array([80, 255, 255])
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            
            # Detect red (bearish) areas  
            red_lower1 = np.array([0, 40, 40])
            red_upper1 = np.array([10, 255, 255])
            red_lower2 = np.array([170, 40, 40])
            red_upper2 = np.array([180, 255, 255])
            red_mask = cv2.inRange(hsv, red_lower1, red_upper1) + \
                       cv2.inRange(hsv, red_lower2, red_upper2)
            
            # Count pixels
            green_pixels = cv2.countNonZero(green_mask)
            red_pixels = cv2.countNonZero(red_mask)
            
            if green_pixels > red_pixels * 1.2:
                return "bullish"
            elif red_pixels > green_pixels * 1.2:
                return "bearish"
            else:
                return "neutral"
        except:
            return "neutral"
    
    def generate_signal(self, trend, levels, patterns, sentiment):
        """Generate BUY/SELL signal with confidence"""
        score = 0
        confidence_factors = []
        
        # Trend scoring
        if trend == "uptrend":
            score += 2
            confidence_factors.append("📈 Uptrend detected")
        elif trend == "downtrend":
            score -= 2
            confidence_factors.append("📉 Downtrend detected")
        
        # Sentiment scoring
        if sentiment == "bullish":
            score += 1
            confidence_factors.append("🟢 Bullish candle sentiment")
        elif sentiment == "bearish":
            score -= 1
            confidence_factors.append("🔴 Bearish candle sentiment")
        
        # Pattern scoring
        if "multiple_swings" in patterns:
            score += 1
            confidence_factors.append("🔄 Multiple swing points detected")
        
        if "strong_trend" in patterns:
            score += 1.5
            confidence_factors.append("💪 Strong trend pattern")
        
        if "consolidation" in patterns:
            score += 0.5
            confidence_factors.append("⚖️ Consolidation pattern")
        
        # Support/Resistance scoring
        if len(levels.get("support", [])) >= 2:
            score += 0.5
            confidence_factors.append("🛡️ Strong support levels")
        
        if len(levels.get("resistance", [])) >= 2:
            score += 0.5
            confidence_factors.append("🚧 Strong resistance levels")
        
        # Generate final signal
        if score >= 2.5:
            signal = "STRONG BUY 🟢"
            confidence = min(90, 65 + score * 8)
        elif score >= 1:
            signal = "BUY 🟢"
            confidence = min(80, 60 + score * 7)
        elif score <= -2.5:
            signal = "STRONG SELL 🔴"
            confidence = min(90, 65 + abs(score) * 8)
        elif score <= -1:
            signal = "SELL 🔴"
            confidence = min(80, 60 + abs(score) * 7)
        else:
            signal = "HOLD ⚪"
            confidence = 50
            confidence_factors.append("⚪ Mixed signals - waiting for confirmation")
        
        return signal, round(confidence, 1)

# Initialize analyzer
analyzer = TradingSignalAnalyzer()

# HTML template for web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Chart Analysis - Get BUY/SELL Signals</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 30px; border-radius: 10px; }
        .upload-box { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
        .result { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .buy { border-left: 5px solid green; }
        .sell { border-left: 5px solid red; }
        .hold { border-left: 5px solid gray; }
        button { background: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 AI Chart Analysis</h1>
        <p>Upload any trading chart screenshot and get instant BUY/SELL signals using advanced computer vision!</p>
        
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="upload-box">
                <input type="file" id="imageInput" accept="image/*" required>
                <br><br>
                <button type="submit">Analyze Chart 📊</button>
            </div>
        </form>
        
        <div id="result" style="display:none;" class="result">
            <h2>Analysis Result:</h2>
            <div id="signal"></div>
            <div id="confidence"></div>
            <div id="details"></div>
        </div>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('imageInput');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a chart image');
                return;
            }
            
            // Convert image to base64
            const reader = new FileReader();
            reader.onload = async function(e) {
                const base64Image = e.target.result;
                
                try {
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({image: base64Image})
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        displayResult(data);
                    } else {
                        alert('Error: ' + data.error);
                    }
                } catch (error) {
                    alert('Error analyzing image: ' + error);
                }
            };
            reader.readAsDataURL(file);
        });
        
        function displayResult(data) {
            const resultDiv = document.getElementById('result');
            const signalDiv = document.getElementById('signal');
            const confidenceDiv = document.getElementById('confidence');
            const detailsDiv = document.getElementById('details');
            
            // Set signal with color coding
            let signalClass = 'hold';
            if (data.signal.includes('BUY')) signalClass = 'buy';
            if (data.signal.includes('SELL')) signalClass = 'sell';
            
            resultDiv.className = 'result ' + signalClass;
            signalDiv.innerHTML = `<h3 style="color: ${signalClass === 'buy' ? 'green' : signalClass === 'sell' ? 'red' : 'gray'}">${data.signal}</h3>`;
            confidenceDiv.innerHTML = `<p><strong>Confidence:</strong> ${data.confidence}%</p>`;
            
            // Details
            let details = `<p><strong>Trend:</strong> ${data.trend}</p>`;
            details += `<p><strong>Sentiment:</strong> ${data.sentiment}</p>`;
            details += `<p><strong>Patterns:</strong> ${data.patterns.join(', ') || 'None detected'}</p>`;
            details += `<p><strong>Key Levels:</strong> Support at ${data.key_levels.support.join(', ') || 'N/A'}, Resistance at ${data.key_levels.resistance.join(', ') || 'N/A'}</p>`;
            
            detailsDiv.innerHTML = details;
            resultDiv.style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for chart analysis"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image data provided"}), 400
        
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({"error": "Could not decode image"}), 400
        
        # Analyze chart
        result = analyzer.analyze_chart(image)
        
        return jsonify({
            "success": True,
            "signal": result["signal"],
            "confidence": result["confidence"],
            "trend": result["trend"],
            "sentiment": result["sentiment"],
            "patterns": result["patterns_detected"],
            "key_levels": result["key_levels"],
            "timestamp": "2024-01-01T00:00:00Z"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "AI Chart Analysis API"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
