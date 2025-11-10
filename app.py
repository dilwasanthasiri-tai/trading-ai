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
            print("🔄 Starting chart analysis...")
            
            # Resize image for consistent processing
            image = cv2.resize(image, (800, 600))
            
            # 1. Preprocess image
            processed = self.preprocess_image(image)
            
            # 2. Trend Analysis
            trend_signal, trend_confidence = self.analyze_trend(processed)
            print(f"📈 Trend: {trend_signal} ({trend_confidence}%)")
            
            # 3. Price Action Analysis
            price_action = self.analyze_price_action(processed)
            print(f"💰 Price Action: {price_action}")
            
            # 4. Candlestick Sentiment
            sentiment = self.analyze_candlestick_sentiment(image)
            print(f"🎯 Sentiment: {sentiment}")
            
            # 5. Generate Final Signal
            signal, confidence = self.generate_signal(
                trend_signal, trend_confidence, price_action, sentiment
            )
            
            print(f"✅ Final Signal: {signal} ({confidence}%)")
            
            return {
                "signal": signal,
                "confidence": confidence,
                "trend": trend_signal,
                "trend_confidence": trend_confidence,
                "price_action": price_action,
                "sentiment": sentiment,
                "analysis_quality": "good" if confidence > 60 else "medium"
            }
            
        except Exception as e:
            print(f"❌ Analysis error: {str(e)}")
            return {
                "signal": "HOLD ⚪",
                "confidence": 50,
                "trend": "unknown",
                "trend_confidence": 0,
                "price_action": "unclear",
                "sentiment": "neutral",
                "analysis_quality": "poor",
                "error": "Analysis failed - try a clearer chart image"
            }
    
    def preprocess_image(self, image):
        """Preprocess chart image for better analysis"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Reduce noise
        denoised = cv2.medianBlur(enhanced, 5)
        
        return denoised
    
    def analyze_trend(self, processed_image):
        """Improved trend analysis"""
        try:
            # Multiple edge detection methods
            edges1 = cv2.Canny(processed_image, 50, 150)
            edges2 = cv2.Canny(processed_image, 30, 100)
            
            # Combine edges
            edges = cv2.bitwise_or(edges1, edges2)
            
            # Detect lines with different parameters
            lines1 = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                   minLineLength=50, maxLineGap=20)
            
            lines2 = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=30,
                                   minLineLength=30, maxLineGap=15)
            
            all_lines = []
            if lines1 is not None:
                all_lines.extend(lines1)
            if lines2 is not None:
                all_lines.extend(lines2)
            
            if not all_lines:
                return "neutral", 50
            
            # Analyze line angles for trend
            angles = []
            for line in all_lines:
                x1, y1, x2, y2 = line[0]
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                angles.append(angle)
            
            # Categorize angles
            up_angles = [a for a in angles if 5 < a < 85]      # Rising lines
            down_angles = [a for a in angles if -85 < a < -5]  # Falling lines
            neutral_angles = [a for a in angles if -5 <= a <= 5]  # Horizontal
            
            total_significant = len(up_angles) + len(down_angles)
            
            if total_significant == 0:
                return "neutral", 50
            
            # Calculate trend strength
            up_ratio = len(up_angles) / total_significant
            down_ratio = len(down_angles) / total_significant
            
            if up_ratio > 0.6:
                confidence = min(90, int(up_ratio * 100))
                return "uptrend", confidence
            elif down_ratio > 0.6:
                confidence = min(90, int(down_ratio * 100))
                return "downtrend", confidence
            else:
                return "neutral", max(50, int((1 - abs(up_ratio - down_ratio)) * 100))
                
        except Exception as e:
            print(f"Trend analysis error: {e}")
            return "unknown", 0
    
    def analyze_price_action(self, processed_image):
        """Analyze price action patterns"""
        try:
            # Detect significant horizontal levels (support/resistance)
            edges = cv2.Canny(processed_image, 50, 150)
            
            # Find horizontal lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, horizontal_kernel)
            
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            levels = []
            for contour in contours:
                if cv2.contourArea(contour) > 100:
                    x, y, w, h = cv2.boundingRect(contour)
                    if w > 100:  # Significant horizontal level
                        levels.append(y)
            
            # Analyze level distribution
            if len(levels) >= 3:
                return "ranging"
            elif len(levels) == 2:
                return "consolidating"
            else:
                return "trending"
                
        except Exception as e:
            print(f"Price action error: {e}")
            return "unclear"
    
    def analyze_candlestick_sentiment(self, image):
        """Improved candlestick color analysis"""
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for bullish (green) and bearish (red) candles
            # Bullish (green) range
            green_lower = np.array([35, 50, 50])
            green_upper = np.array([85, 255, 255])
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            
            # Bearish (red) range - two ranges for red
            red_lower1 = np.array([0, 50, 50])
            red_upper1 = np.array([10, 255, 255])
            red_lower2 = np.array([160, 50, 50])
            red_upper2 = np.array([180, 255, 255])
            red_mask = cv2.inRange(hsv, red_lower1, red_upper1) + \
                      cv2.inRange(hsv, red_lower2, red_upper2)
            
            # Count significant color areas (filter noise)
            green_pixels = cv2.countNonZero(green_mask)
            red_pixels = cv2.countNonZero(red_mask)
            
            total_pixels = image.shape[0] * image.shape[1]
            min_significant = total_pixels * 0.01  # At least 1% of image
            
            print(f"🎨 Color Analysis - Green: {green_pixels}, Red: {red_pixels}")
            
            if green_pixels > red_pixels * 1.5 and green_pixels > min_significant:
                return "bullish"
            elif red_pixels > green_pixels * 1.5 and red_pixels > min_significant:
                return "bearish"
            else:
                return "neutral"
                
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return "neutral"
    
    def generate_signal(self, trend, trend_conf, price_action, sentiment):
        """Generate trading signal with improved logic"""
        score = 0
        confidence_factors = []
        
        # Trend scoring (weighted by confidence)
        if trend == "uptrend":
            score += (trend_conf / 100) * 3
            confidence_factors.append(f"📈 {trend_conf}% Uptrend confidence")
        elif trend == "downtrend":
            score -= (trend_conf / 100) * 3
            confidence_factors.append(f"📉 {trend_conf}% Downtrend confidence")
        
        # Sentiment scoring
        if sentiment == "bullish":
            score += 1
            confidence_factors.append("🟢 Bullish candle colors")
        elif sentiment == "bearish":
            score -= 1
            confidence_factors.append("🔴 Bearish candle colors")
        
        # Price action scoring
        if price_action == "ranging" and abs(score) < 2:
            score *= 0.5  # Reduce signal strength in ranging markets
            confidence_factors.append("⚖️ Market is ranging")
        elif price_action == "trending":
            score *= 1.2  # Strengthen signal in trending markets
            confidence_factors.append("💨 Strong trending market")
        
        # Generate final signal with confidence
        base_confidence = max(50, trend_conf)
        
        if score >= 2.0:
            signal = "STRONG BUY 🟢"
            confidence = min(90, base_confidence + 20)
        elif score >= 1.0:
            signal = "BUY 🟢"
            confidence = min(85, base_confidence + 15)
        elif score <= -2.0:
            signal = "STRONG SELL 🔴"
            confidence = min(90, base_confidence + 20)
        elif score <= -1.0:
            signal = "SELL 🔴"
            confidence = min(85, base_confidence + 15)
        else:
            signal = "HOLD ⚪"
            confidence = max(50, base_confidence - 10)
            confidence_factors.append("⚪ Mixed signals - cautious approach")
        
        print(f"🎯 Signal Score: {score:.2f}")
        print(f"📊 Confidence Factors: {confidence_factors}")
        
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
        .buy { border-left: 5px solid green; background: #f0fff0; }
        .sell { border-left: 5px solid red; background: #fff0f0; }
        .hold { border-left: 5px solid gray; background: #f8f8f8; }
        button { background: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .loading { display: none; color: #007bff; text-align: center; }
        .signal { font-size: 24px; font-weight: bold; margin: 10px 0; }
        .confidence { font-size: 18px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 AI Chart Analysis</h1>
        <p>Upload any trading chart screenshot and get instant BUY/SELL signals using advanced computer vision!</p>
        
        <form id="uploadForm">
            <div class="upload-box">
                <input type="file" id="imageInput" accept="image/*" required style="margin-bottom: 20px;">
                <br>
                <button type="submit">Analyze Chart 📊</button>
            </div>
        </form>
        
        <div class="loading" id="loading">
            <p>🔄 Analyzing your chart... This may take a few seconds.</p>
        </div>
        
        <div id="result" style="display:none;" class="result">
            <h2>Analysis Result:</h2>
            <div id="signal" class="signal"></div>
            <div id="confidence" class="confidence"></div>
            <div id="details"></div>
        </div>

        <div style="margin-top: 30px; padding: 20px; background: #e8f4f8; border-radius: 8px;">
            <h3>💡 Tips for Best Results:</h3>
            <ul>
                <li>Use clear TradingView or charting platform screenshots</li>
                <li>Avoid images with too many indicators or text</li>
                <li>Ensure good contrast between candles and background</li>
                <li>Use standard candlestick charts for best analysis</li>
            </ul>
        </div>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('imageInput');
            const file = fileInput.files[0];
            const loadingDiv = document.getElementById('loading');
            const resultDiv = document.getElementById('result');
            
            if (!file) {
                alert('Please select a chart image');
                return;
            }
            
            // Show loading, hide previous results
            loadingDiv.style.display = 'block';
            resultDiv.style.display = 'none';
            
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
                    
                    // Hide loading
                    loadingDiv.style.display = 'none';
                    
                    if (data.success) {
                        displayResult(data);
                    } else {
                        alert('Error: ' + (data.error || 'Unknown error occurred'));
                    }
                } catch (error) {
                    loadingDiv.style.display = 'none';
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
            signalDiv.innerHTML = data.signal;
            confidenceDiv.innerHTML = `<strong>Confidence:</strong> ${data.confidence}%`;
            
            // Details
            let details = `<p><strong>Trend Analysis:</strong> ${data.trend} (${data.trend_confidence}% confidence)</p>`;
            details += `<p><strong>Market Condition:</strong> ${data.price_action}</p>`;
            details += `<p><strong>Candle Sentiment:</strong> ${data.sentiment}</p>`;
            details += `<p><strong>Analysis Quality:</strong> ${data.analysis_quality}</p>`;
            
            if (data.message) {
                details += `<div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                           <strong>💡 Recommendation:</strong> ${data.message}</div>`;
            }
            
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
        
        print("📥 Received image for analysis...")
        
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({"error": "Could not decode image - please try a different image format"}), 400
        
        print("🖼️ Image decoded successfully, starting analysis...")
        
        # Analyze chart
        result = analyzer.analyze_chart(image)
        
        response = {
            "success": True,
            "signal": result["signal"],
            "confidence": result["confidence"],
            "trend": result["trend"],
            "trend_confidence": result["trend_confidence"],
            "price_action": result["price_action"],
            "sentiment": result["sentiment"],
            "analysis_quality": result["analysis_quality"],
            "message": get_signal_message(result),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Add error info if present
        if "error" in result:
            response["error"] = result["error"]
            
        print("✅ Analysis complete, sending response...")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

def get_signal_message(result):
    """Generate helpful message based on analysis"""
    signal = result["signal"]
    confidence = result["confidence"]
    
    if "BUY" in signal:
        return f"Consider buying opportunities with {confidence}% confidence"
    elif "SELL" in signal:
        return f"Consider selling opportunities with {confidence}% confidence"
    else:
        return f"Market conditions unclear - wait for better setup ({confidence}% confidence)"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "AI Chart Analysis API"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
