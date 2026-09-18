import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_classif

class DataPreprocessor:
    def __init__(self):
        self.raw_df = None
        self.filepath = None
        self.label_col = None
        self.feature_cols = []
        self.selected_feature_indices = []
        self.selected_feature_names = []
        self.scaler_classical = StandardScaler()
        self.scaler_quantum = MinMaxScaler(feature_range=(0, np.pi))
        self.label_encoder = LabelEncoder()
        self.classes_ = []
        self.normal_class_name = "Normal"
        self.is_fitted = False
        
        # Train / Test splits
        self.X_train_orig = None
        self.X_test_orig = None
        self.X_train_classical = None
        self.X_test_classical = None
        self.X_train_quantum = None
        self.X_test_quantum = None
        self.y_train_binary = None
        self.y_test_binary = None
        self.y_train_multi = None
        self.y_test_multi = None

    def load_dataset(self, filepath):
        self.filepath = filepath
        self.raw_df = pd.read_csv(filepath)
        
        # Detect label column
        candidates = ['label', 'attack', 'attack_type', 'class', 'target']
        detected = None
        for col in self.raw_df.columns:
            if col.strip().lower() in candidates:
                detected = col
                break
        if not detected:
            detected = self.raw_df.columns[-1]
        self.label_col = detected
        
        return self.get_summary()

    def get_summary(self):
        if self.raw_df is None:
            return {}
        
        df = self.raw_df
        total_records = len(df)
        total_features = len(df.columns) - 1
        
        # Missing values
        missing_dict = df.isnull().sum().to_dict()
        total_missing = sum(missing_dict.values())
        
        # Label distribution
        label_counts = df[self.label_col].value_counts().to_dict()
        
        # Normal vs Attack count
        normal_count = 0
        for k, v in label_counts.items():
            if str(k).strip().lower() in ['normal', 'benign', '0']:
                normal_count += v
                self.normal_class_name = k
        
        attack_count = total_records - normal_count
        attack_percentage = round((attack_count / total_records) * 100, 2) if total_records > 0 else 0
        
        # Threat level heuristic
        if attack_percentage > 60:
            threat_level = "Critical"
        elif attack_percentage > 35:
            threat_level = "High"
        elif attack_percentage > 15:
            threat_level = "Medium"
        else:
            threat_level = "Low"
            
        # Column summaries
        col_summaries = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            is_num = pd.api.types.is_numeric_dtype(df[col])
            col_summaries.append({
                "name": col,
                "type": dtype,
                "is_label": col == self.label_col,
                "missing": int(df[col].isnull().sum()),
                "unique": int(df[col].nunique()),
                "min": round(float(df[col].min()), 2) if is_num else "-",
                "max": round(float(df[col].max()), 2) if is_num else "-",
                "mean": round(float(df[col].mean()), 2) if is_num else "-"
            })
            
        # Preview data (first 10 records)
        preview_rows = df.head(10).fillna("").to_dict(orient="records")

        return {
            "total_records": total_records,
            "total_features": total_features,
            "total_missing": total_missing,
            "missing_per_col": missing_dict,
            "class_distribution": label_counts,
            "normal_count": normal_count,
            "attack_count": attack_count,
            "attack_percentage": attack_percentage,
            "threat_level": threat_level,
            "label_column": self.label_col,
            "columns": col_summaries,
            "preview": preview_rows
        }

    def prepare_and_split(self, n_quantum_features=4, test_size=0.2, random_state=42):
        if self.raw_df is None:
            raise ValueError("No dataset loaded.")
            
        df = self.raw_df.copy()
        
        # Handle missing values
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mode()[0])
                    
        # Separate features and target
        y_raw = df[self.label_col].astype(str)
        X_raw = df.drop(columns=[self.label_col])
        
        # Convert categoricals in features (e.g. protocol_type)
        cat_cols = X_raw.select_dtypes(include=['category', 'string', 'object']).columns
        if len(cat_cols) > 0:
            X_raw = pd.get_dummies(X_raw, columns=cat_cols, drop_first=True)
            
        self.feature_cols = list(X_raw.columns)
        
        # Target encoding
        # Binary target: 0 = Normal/Benign, 1 = Attack
        y_binary = np.array([
            0 if str(val).strip().lower() in ['normal', 'benign', '0'] else 1 
            for val in y_raw
        ])
        
        # Multi-class target
        y_multi = self.label_encoder.fit_transform(y_raw)
        self.classes_ = list(self.label_encoder.classes_)
        
        # Train / test split
        X_train_df, X_test_df, y_train_b, y_test_b, y_train_m, y_test_m = train_test_split(
            X_raw, y_binary, y_multi, test_size=test_size, random_state=random_state, stratify=y_binary
        )
        
        self.X_train_orig = X_train_df
        self.X_test_orig = X_test_df
        self.y_train_binary = y_train_b
        self.y_test_binary = y_test_b
        self.y_train_multi = y_train_m
        self.y_test_multi = y_test_m
        
        # Feature Selection for Quantum Qubits (SelectKBest with ANOVA F-value)
        k = min(n_quantum_features, X_raw.shape[1])
        selector = SelectKBest(score_func=f_classif, k=k)
        selector.fit(X_train_df, y_train_b)
        
        self.selected_feature_indices = selector.get_support(indices=True).tolist()
        self.selected_feature_names = [self.feature_cols[i] for i in self.selected_feature_indices]
        
        # Feature scores
        scores = selector.scores_
        feature_rankings = []
        for i, col in enumerate(self.feature_cols):
            feature_rankings.append({
                "feature": col,
                "f_score": round(float(scores[i]), 2) if not np.isnan(scores[i]) else 0.0,
                "selected_for_quantum": i in self.selected_feature_indices
            })
        feature_rankings.sort(key=lambda x: x["f_score"], reverse=True)
        
        # Scale for Classical (all features)
        self.X_train_classical = self.scaler_classical.fit_transform(X_train_df)
        self.X_test_classical = self.scaler_classical.transform(X_test_df)
        
        # Scale for Quantum (selected K features into [0, pi])
        X_train_k = X_train_df.iloc[:, self.selected_feature_indices].values
        X_test_k = X_test_df.iloc[:, self.selected_feature_indices].values
        
        self.X_train_quantum = self.scaler_quantum.fit_transform(X_train_k)
        self.X_test_quantum = self.scaler_quantum.transform(X_test_k)
        # Clip to ensure valid angle range [0, pi]
        self.X_train_quantum = np.clip(self.X_train_quantum, 0, np.pi)
        self.X_test_quantum = np.clip(self.X_test_quantum, 0, np.pi)
        
        self.is_fitted = True
        
        return {
            "train_samples": len(X_train_df),
            "test_samples": len(X_test_df),
            "total_features": len(self.feature_cols),
            "quantum_features": self.selected_feature_names,
            "feature_rankings": feature_rankings[:15],
            "classes": self.classes_
        }

    def transform_single_record(self, record_dict):
        """Preprocesses a single user input or simulated packet dictionary for inference."""
        if not self.is_fitted:
            raise ValueError("Preprocessor has not been fitted on a dataset yet.")
            
        df_row = pd.DataFrame([record_dict])
        
        # Ensure all columns exist
        for col in self.feature_cols:
            if col not in df_row.columns:
                # If dummy col, check base col
                df_row[col] = 0
                
        # Drop unexpected columns and order identically
        df_ordered = df_row[self.feature_cols].copy()
        
        # Handle missing
        for col in self.feature_cols:
            df_ordered[col] = pd.to_numeric(df_ordered[col], errors='coerce').fillna(0)
            
        # Classical feature vector
        x_classical = self.scaler_classical.transform(df_ordered)
        
        # Quantum feature vector
        x_k = df_ordered.iloc[:, self.selected_feature_indices].values
        x_quantum = self.scaler_quantum.transform(x_k)
        x_quantum = np.clip(x_quantum, 0, np.pi)
        
        return x_classical, x_quantum, dict(zip(self.selected_feature_names, x_k[0]))

# Global singleton preprocessor instance
preprocessor = DataPreprocessor()
