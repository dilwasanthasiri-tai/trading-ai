import cv2
import numpy as np

class TradingSignalAnalyzer:
    def analyze_chart(self, image):
        try:
            print("🔄 Starting chart analysis...")

            image = cv2.resize(image, (800, 600))
            candles = self.extract_candles(image)
            if len(candles) < 3:
                return self.failed_result("Too few candles detected")

            trend_signal, trend_confidence = self.analyze_trend(candles)
            price_action = self.analyze_price_action(candles)
            sentiment = self.analyze_candlestick_sentiment(image, candles)
            signal, confidence = self.generate_signal(trend_signal, trend_confidence, price_action, sentiment)

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
            return self.failed_result(str(e))

    def failed_result(self, msg):
        return {
            "signal": "HOLD ⚪",
            "confidence": 50,
            "trend": "unknown",
            "trend_confidence": 0,
            "price_action": "unclear",
            "sentiment": "neutral",
            "analysis_quality": "poor",
            "error": msg
        }

    def extract_candles(self, image):
        """Detect candlestick bodies and positions"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candles = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if h > 5 and w < 20:  # likely a candle body
                candles.append((x, y, w, h))
        candles.sort(key=lambda c: c[0])  # left to right
        return candles

    def analyze_trend(self, candles):
        """Determine trend from candle positions"""
        closes = [c[1] + c[3] for c in candles]  # bottom of candle as close
        if len(closes) < 3:
            return "neutral", 50

        # Simple linear regression slope
        x = np.arange(len(closes))
        slope = np.polyfit(x, closes, 1)[0]

        if slope < -0.5:
            return "downtrend", min(90, int(abs(slope)*100))
        elif slope > 0.5:
            return "uptrend", min(90, int(abs(slope)*100))
        else:
            return "neutral", 50

    def analyze_price_action(self, candles):
        """Basic market condition based on candle heights"""
        heights = [c[3] for c in candles]
        if max(heights) / np.mean(heights) > 2:
            return "trending"
        elif np.std(heights) < 3:
            return "ranging"
        else:
            return "consolidating"

    def analyze_candlestick_sentiment(self, image, candles):
        """Detect bullish or bearish sentiment using candle colors"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        green_lower = np.array([35, 50, 50])
        green_upper = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, green_lower, green_upper)

        red_lower1 = np.array([0, 50, 50])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([160, 50, 50])
        red_upper2 = np.array([180, 255, 255])
        red_mask = cv2.inRange(hsv, red_lower1, red_upper1) + cv2.inRange(hsv, red_lower2, red_upper2)

        green_pixels = cv2.countNonZero(green_mask)
        red_pixels = cv2.countNonZero(red_mask)
        total_pixels = image.shape[0] * image.shape[1]
        min_significant = total_pixels * 0.01

        if green_pixels > red_pixels * 1.5 and green_pixels > min_significant:
            return "bullish"
        elif red_pixels > green_pixels * 1.5 and red_pixels > min_significant:
            return "bearish"
        else:
            return "neutral"

    def generate_signal(self, trend, trend_conf, price_action, sentiment):
        """Generate a final BUY/SELL/HOLD signal"""
        score = 0
        if trend == "uptrend": score += trend_conf/100 * 3
        elif trend == "downtrend": score -= trend_conf/100 * 3

        if sentiment == "bullish": score += 1
        elif sentiment == "bearish": score -= 1

        if price_action == "ranging" and abs(score) < 2: score *= 0.5
        elif price_action == "trending": score *= 1.2

        base_conf = max(50, trend_conf)
        if score >= 2.0: return "STRONG BUY 🟢", min(90, base_conf + 20)
        elif score >= 1.0: return "BUY 🟢", min(85, base_conf + 15)
        elif score <= -2.0: return "STRONG SELL 🔴", min(90, base_conf + 20)
        elif score <= -1.0: return "SELL 🔴", min(85, base_conf + 15)
        else: return "HOLD ⚪", max(50, base_conf - 10)
