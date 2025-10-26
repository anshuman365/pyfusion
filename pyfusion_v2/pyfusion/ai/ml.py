"""
AI and Machine Learning integration for PyFusion
"""
import numpy as np
from typing import Any, Dict, List, Union
from ..core.exceptions import PyFusionError
from ..core.logging import log

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    import joblib
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    log.warning("scikit-learn not available. AI features limited.")

class AIModule:
    """AI and Machine Learning utilities"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.vectorizers: Dict[str, Any] = {}
        
        if not HAS_SKLEARN:
            log.warning("AI features require scikit-learn. Install with: pip install scikit-learn")
    
    def sentiment_analysis(self, text: str, model_type: str = 'basic') -> Dict[str, Any]:
        """
        Perform sentiment analysis on text
        
        Args:
            text: Input text to analyze
            model_type: Type of model to use ('basic' or 'advanced')
        
        Returns:
            Dictionary with sentiment scores
        """
        if not HAS_SKLEARN:
            raise PyFusionError("scikit-learn required for sentiment analysis")
        
        # Simple rule-based sentiment as fallback
        if model_type == 'basic':
            return self._basic_sentiment(text)
        
        # More advanced approach with ML
        elif model_type == 'advanced':
            return self._ml_sentiment(text)
        
        else:
            raise PyFusionError(f"Unknown model type: {model_type}")
    
    def _basic_sentiment(self, text: str) -> Dict[str, Any]:
        """Basic rule-based sentiment analysis"""
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
                         'awesome', 'love', 'like', 'nice', 'best', 'better', 'happy'}
        negative_words = {'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 
                         'worst', 'worse', 'sad', 'angry', 'mad', 'upset'}
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        total_words = len(words)
        
        if total_words == 0:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
        
        sentiment_score = (positive_count - negative_count) / total_words
        
        if sentiment_score > 0.1:
            sentiment = 'positive'
        elif sentiment_score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        confidence = min(abs(sentiment_score) * 5, 1.0)  # Simple confidence calculation
        
        return {
            'sentiment': sentiment,
            'score': float(sentiment_score),
            'confidence': float(confidence),
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def _ml_sentiment(self, text: str) -> Dict[str, Any]:
        """Machine learning based sentiment analysis (placeholder)"""
        # This would use a trained model in a real implementation
        # For now, we'll use the basic method
        result = self._basic_sentiment(text)
        result['method'] = 'ml_placeholder'
        return result
    
    def text_classification(self, text: str, categories: List[str], 
                          model_name: str = 'default') -> Dict[str, Any]:
        """
        Classify text into categories
        
        Args:
            text: Input text to classify
            categories: List of possible categories
            model_name: Name of the classification model
        
        Returns:
            Dictionary with classification results
        """
        if not HAS_SKLEARN:
            raise PyFusionError("scikit-learn required for text classification")
        
        # Simple keyword-based classification
        category_scores = {}
        
        for category in categories:
            # Simple keyword matching (would use ML model in real implementation)
            keywords = self._get_category_keywords(category)
            matches = sum(1 for keyword in keywords if keyword in text.lower())
            category_scores[category] = matches / len(keywords) if keywords else 0
        
        # Normalize scores
        total_score = sum(category_scores.values())
        if total_score > 0:
            category_scores = {k: v/total_score for k, v in category_scores.items()}
        
        predicted_category = max(category_scores.items(), key=lambda x: x[1])
        
        return {
            'predicted_category': predicted_category[0],
            'confidence': predicted_category[1],
            'all_scores': category_scores
        }
    
    def _get_category_keywords(self, category: str) -> List[str]:
        """Get keywords for a category"""
        keyword_map = {
            'sports': ['game', 'team', 'player', 'score', 'win', 'loss', 'sport', 'match'],
            'technology': ['computer', 'software', 'tech', 'code', 'program', 'app', 'digital'],
            'politics': ['government', 'election', 'policy', 'law', 'political', 'vote'],
            'entertainment': ['movie', 'music', 'show', 'celebrity', 'film', 'actor', 'song'],
            'business': ['company', 'market', 'stock', 'money', 'business', 'finance', 'economic']
        }
        return keyword_map.get(category.lower(), [])
    
    def cluster_data(self, data: List[List[float]], n_clusters: int = 3) -> Dict[str, Any]:
        """
        Cluster data using K-means
        
        Args:
            data: List of data points (each point is a list of features)
            n_clusters: Number of clusters to create
        
        Returns:
            Dictionary with clustering results
        """
        if not HAS_SKLEARN:
            raise PyFusionError("scikit-learn required for clustering")
        
        if len(data) < n_clusters:
            raise PyFusionError(f"Not enough data points for {n_clusters} clusters")
        
        # Convert to numpy array
        X = np.array(data)
        
        # Standardize the data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(X_scaled)
        
        # Calculate cluster centers in original scale
        centers = scaler.inverse_transform(kmeans.cluster_centers_)
        
        return {
            'labels': labels.tolist(),
            'centers': centers.tolist(),
            'inertia': float(kmeans.inertia_),
            'n_clusters': n_clusters,
            'n_samples': len(data)
        }
    
    def train_text_classifier(self, texts: List[str], labels: List[str],
                            model_name: str = 'text_classifier') -> bool:
        """
        Train a text classification model
        
        Args:
            texts: List of training texts
            labels: List of corresponding labels
            model_name: Name to save the model under
        
        Returns:
            True if training successful
        """
        if not HAS_SKLEARN:
            raise PyFusionError("scikit-learn required for model training")
        
        if len(texts) != len(labels):
            raise PyFusionError("Texts and labels must have same length")
        
        try:
            # Create TF-IDF features
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            X = vectorizer.fit_transform(texts)
            
            # Train classifier
            classifier = LogisticRegression()
            classifier.fit(X, labels)
            
            # Save models
            self.vectorizers[model_name] = vectorizer
            self.models[model_name] = classifier
            
            log.info(f"Trained text classifier '{model_name}' on {len(texts)} samples")
            return True
            
        except Exception as e:
            log.error(f"Error training classifier: {e}")
            return False
    
    def predict_text(self, text: str, model_name: str = 'text_classifier') -> Dict[str, Any]:
        """
        Predict label for text using trained model
        
        Args:
            text: Input text to classify
            model_name: Name of the trained model
        
        Returns:
            Dictionary with prediction results
        """
        if model_name not in self.models or model_name not in self.vectorizers:
            raise PyFusionError(f"Model '{model_name}' not found. Train it first.")
        
        vectorizer = self.vectorizers[model_name]
        classifier = self.models[model_name]
        
        # Transform text
        X = vectorizer.transform([text])
        
        # Predict
        prediction = classifier.predict(X)[0]
        probabilities = classifier.predict_proba(X)[0]
        
        # Get confidence scores for all classes
        class_scores = {
            class_name: float(score) 
            for class_name, score in zip(classifier.classes_, probabilities)
        }
        
        return {
            'prediction': prediction,
            'confidence': float(max(probabilities)),
            'all_probabilities': class_scores
        }
    
    def save_model(self, model_name: str, filepath: str) -> bool:
        """Save trained model to file"""
        if model_name not in self.models:
            raise PyFusionError(f"Model '{model_name}' not found")
        
        try:
            joblib.dump({
                'model': self.models[model_name],
                'vectorizer': self.vectorizers.get(model_name)
            }, filepath)
            log.info(f"Saved model '{model_name}' to {filepath}")
            return True
        except Exception as e:
            log.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, model_name: str, filepath: str) -> bool:
        """Load trained model from file"""
        try:
            data = joblib.load(filepath)
            self.models[model_name] = data['model']
            if 'vectorizer' in data:
                self.vectorizers[model_name] = data['vectorizer']
            log.info(f"Loaded model '{model_name}' from {filepath}")
            return True
        except Exception as e:
            log.error(f"Error loading model: {e}")
            return False
    
    def chat_completion(self, prompt: str, context: str = None, 
                       max_tokens: int = 150) -> Dict[str, Any]:
        """
        Simple chat completion (placeholder for AI integration)
        
        Note: In a real implementation, this would integrate with OpenAI, 
        Hugging Face, or similar services.
        """
        # Simple rule-based response for demonstration
        responses = {
            'hello': 'Hello! How can I help you today?',
            'help': 'I can help with sentiment analysis, text classification, and data clustering.',
            'thanks': 'You\'re welcome! Is there anything else I can help with?',
            'bye': 'Goodbye! Have a great day!'
        }
        
        prompt_lower = prompt.lower()
        response = "I'm a simple AI assistant. For advanced AI features, integrate with external services like OpenAI."
        
        for key, value in responses.items():
            if key in prompt_lower:
                response = value
                break
        
        return {
            'response': response,
            'tokens_used': len(prompt.split()),
            'model': 'pyfusion_basic',
            'finish_reason': 'length' if len(response.split()) >= max_tokens else 'stop'
        }