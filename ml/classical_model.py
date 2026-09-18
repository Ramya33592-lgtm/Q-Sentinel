import time
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report

class ClassicalSecurityModel:
    def __init__(self, model_type="random_forest"):
        self.model_type = model_type
        self.model = None
        self.binary_model = None
        self.is_trained = False
        self.metrics = {}
        self.classes = []
        self.feature_names = []

    def train(self, X_train, y_train_binary, y_train_multi, X_test, y_test_binary, y_test_multi, classes, feature_names):
        self.classes = classes
        self.feature_names = feature_names
        
        start_time = time.time()
        
        # Binary detector model
        if self.model_type == "svm":
            self.binary_model = SVC(probability=True, kernel='rbf', C=1.0, random_state=42)
            self.model = SVC(probability=True, kernel='rbf', C=1.0, random_state=42)
        else:
            self.binary_model = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
            self.model = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
            
        # Fit multi-class classifier
        self.model.fit(X_train, y_train_multi)
        # Fit binary detector
        self.binary_model.fit(X_train, y_train_binary)
        
        training_time = time.time() - start_time
        
        # Test evaluation on binary classification (Normal vs Attack)
        inference_start = time.time()
        y_pred_binary = self.binary_model.predict(X_test)
        inference_time = (time.time() - inference_start) / max(1, len(X_test))
        
        acc = float(accuracy_score(y_test_binary, y_pred_binary))
        prec, rec, f1, _ = precision_recall_fscore_support(y_test_binary, y_pred_binary, average='weighted', zero_division=0)
        
        # Binary confusion matrix [[TN, FP], [FN, TP]]
        cm_binary = confusion_matrix(y_test_binary, y_pred_binary).tolist()
        
        # Multi-class evaluation
        y_pred_multi = self.model.predict(X_test)
        acc_multi = float(accuracy_score(y_test_multi, y_pred_multi))
        cm_multi = confusion_matrix(y_test_multi, y_pred_multi).tolist()
        report_dict = classification_report(y_test_multi, y_pred_multi, target_names=self.classes, output_dict=True, zero_division=0)
        
        # Feature importances (if Random Forest)
        importances = []
        if hasattr(self.model, "feature_importances_"):
            for name, score in zip(self.feature_names, self.model.feature_importances_):
                importances.append({"feature": name, "importance": round(float(score), 4)})
            importances.sort(key=lambda x: x["importance"], reverse=True)
            
        self.metrics = {
            "model_type": "Classical " + ("Random Forest" if self.model_type == "random_forest" else "SVM"),
            "accuracy": round(acc, 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "multi_accuracy": round(acc_multi, 4),
            "training_time_sec": round(training_time, 3),
            "inference_time_ms": round(inference_time * 1000, 3),
            "confusion_matrix_binary": cm_binary,
            "confusion_matrix_multi": cm_multi,
            "classes": self.classes,
            "classification_report": report_dict,
            "feature_importances": importances[:10]
        }
        
        self.is_trained = True
        return self.metrics

    def predict(self, x_vector):
        if not self.is_trained:
            raise ValueError("Classical model is not trained yet.")
            
        if len(x_vector.shape) == 1:
            x_vector = x_vector.reshape(1, -1)
            
        # Binary prediction (0 = Normal, 1 = Attack)
        is_attack_pred = int(self.binary_model.predict(x_vector)[0])
        binary_probs = self.binary_model.predict_proba(x_vector)[0]
        attack_prob = float(binary_probs[1]) if len(binary_probs) > 1 else float(binary_probs[0])
        
        # Multi-class attack prediction
        multi_pred_idx = int(self.model.predict(x_vector)[0])
        multi_probs = self.model.predict_proba(x_vector)[0]
        predicted_class = self.classes[multi_pred_idx] if multi_pred_idx < len(self.classes) else "Unknown"
        confidence = float(multi_probs[multi_pred_idx])
        
        if is_attack_pred == 0:
            attack_type = "Normal"
            threat_level = "Low"
            risk_color = "emerald"
        else:
            attack_type = predicted_class if predicted_class.lower() not in ["normal", "benign"] else "Generic Attack"
            if confidence > 0.85:
                threat_level = "Critical"
                risk_color = "crimson"
            elif confidence > 0.65:
                threat_level = "High"
                risk_color = "rose"
            else:
                threat_level = "Medium"
                risk_color = "amber"
                
        all_class_probabilities = {
            self.classes[i]: round(float(multi_probs[i]), 4)
            for i in range(len(self.classes))
        }
        
        return {
            "is_attack": bool(is_attack_pred),
            "attack_type": attack_type,
            "confidence": round(confidence, 4),
            "attack_probability": round(attack_prob, 4),
            "threat_level": threat_level,
            "risk_color": risk_color,
            "all_probabilities": all_class_probabilities
        }

# Global singleton classical model
classical_model = ClassicalSecurityModel()
