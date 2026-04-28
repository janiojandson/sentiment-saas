import os
import logging
import numpy as np
from typing import Tuple, Optional
import joblib

# Importações condicionais para evitar erros se as bibliotecas não estiverem instaladas
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger("sentiment-saas.model_handler")

class ModelHandler:
    """
    Gerenciador de modelos para análise de sentimentos.
    Implementa dois tipos de modelos:
    1. Baseline: Modelo simples e rápido baseado em TF-IDF + Regressão Logística
    2. Transformer: Modelo mais preciso baseado em DistilBERT
    """
    
    def __init__(self):
        self.baseline_model = None
        self.baseline_vectorizer = None
        self.transformer_model = None
        self.transformer_tokenizer = None
        self.models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
        self.sentiment_labels = {0: "negative", 1: "neutral", 2: "positive"}
        
    def load_models(self):
        """
        Carrega os modelos de ML na memória
        """
        self._load_baseline_model()
        self._load_transformer_model()
    
    def _load_baseline_model(self):
        """
        Carrega o modelo baseline (ou cria um simples se não existir)
        """
        try:
            model_path = os.path.join(self.models_dir, "baseline_model.joblib")
            vectorizer_path = os.path.join(self.models_dir, "baseline_vectorizer.joblib")
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                logger.info("Carregando modelo baseline do disco...")
                self.baseline_model = joblib.load(model_path)
                self.baseline_vectorizer = joblib.load(vectorizer_path)
            else:
                logger.info("Modelo baseline não encontrado. Criando modelo simples...")
                self._create_simple_baseline()
                
            logger.info("Modelo baseline carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo baseline: {str(e)}")
            self._create_simple_baseline()
    
    def _create_simple_baseline(self):
        """
        Cria um modelo baseline simples para demonstração
        """
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn não está instalado. Não é possível criar modelo baseline.")
            return
            
        # Dados de exemplo para treinamento
        texts = [
            "Adorei o produto! Superou minhas expectativas.",
            "Excelente atendimento, recomendo!",
            "Produto de ótima qualidade, vale cada centavo.",
            "Estou muito satisfeito com a compra.",
            "Serviço incrível, rápido e eficiente.",
            "Não gostei do produto, qualidade inferior.",
            "Péssimo atendimento, nunca mais compro.",
            "Produto quebrou no primeiro uso, decepcionante.",
            "Demorou muito para entregar, insatisfeito.",
            "Experiência terrível, não recomendo.",
            "Produto ok, nada excepcional.",
            "Entrega dentro do prazo, produto conforme descrito.",
            "Preço justo pelo que oferece.",
            "Nem bom nem ruim, atendeu às expectativas básicas.",
            "Poderia ser melhor, mas não é ruim."
        ]
        
        # 0: negativo, 1: neutro, 2: positivo
        labels = [2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
        
        # Criar e treinar o modelo
        self.baseline_vectorizer = CountVectorizer()
        X = self.baseline_vectorizer.fit_transform(texts)
        self.baseline_model = LogisticRegression(max_iter=1000)
        self.baseline_model.fit(X, labels)
        
        # Salvar o modelo se o diretório existir
        try:
            os.makedirs(self.models_dir, exist_ok=True)
            joblib.dump(self.baseline_model, os.path.join(self.models_dir, "baseline_model.joblib"))
            joblib.dump(self.baseline_vectorizer, os.path.join(self.models_dir, "baseline_vectorizer.joblib"))
            logger.info("Modelo baseline simples criado e salvo")
        except Exception as e:
            logger.error(f"Erro ao salvar modelo baseline: {str(e)}")
    
    def _load_transformer_model(self):
        """
        Carrega o modelo transformer DistilBERT
        """
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Biblioteca transformers não está instalada. Modelo transformer não será carregado.")
            return
            
        try:
            model_path = os.path.join(self.models_dir, "distilbert-sentiment")
            
            if os.path.exists(model_path):
                logger.info("Carregando modelo transformer do disco...")
                self.transformer_tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.transformer_model = AutoModelForSequenceClassification.from_pretrained(model_path)
            else:
                logger.info("Modelo local não encontrado. Carregando modelo pré-treinado da Hugging Face...")
                # Usar modelo pré-treinado para sentimentos
                self.transformer_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
                self.transformer_model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
                
                # Salvar o modelo localmente
                try:
                    os.makedirs(model_path, exist_ok=True)
                    self.transformer_tokenizer.save_pretrained(model_path)
                    self.transformer_model.save_pretrained(model_path)
                    logger.info("Modelo transformer salvo localmente")
                except Exception as e:
                    logger.error(f"Erro ao salvar modelo transformer: {str(e)}")
            
            # Colocar o modelo em modo de avaliação
            self.transformer_model.eval()
            logger.info("Modelo transformer carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo transformer: {str(e)}")
    
    def analyze_baseline(self, text: str) -> Tuple[str, float]:
        """
        Analisa o sentimento usando o modelo baseline
        
        Args:
            text: Texto para análise
            
        Returns:
            Tupla (sentimento, confiança)
        """
        if self.baseline_model is None or self.baseline_vectorizer is None:
            logger.error("Modelo baseline não está carregado")
            return "neutral", 0.5
            
        try:
            # Vetorizar o texto
            X = self.baseline_vectorizer.transform([text])
            
            # Prever o sentimento
            prediction = self.baseline_model.predict(X)[0]
            probabilities = self.baseline_model.predict_proba(X)[0]
            confidence = float(max(probabilities))
            
            return self.sentiment_labels[prediction], confidence
        except Exception as e:
            logger.error(f"Erro na análise baseline: {str(e)}")
            return "neutral", 0.5
    
    def analyze_transformer(self, text: str) -> Tuple[str, float]:
        """
        Analisa o sentimento usando o modelo transformer
        
        Args:
            text: Texto para análise
            
        Returns:
            Tupla (sentimento, confiança)
        """
        if self.transformer_model is None or self.transformer_tokenizer is None:
            logger.warning("Modelo transformer não está carregado. Usando baseline como fallback.")
            return self.analyze_baseline(text)
            
        try:
            # Preparar o texto para o modelo
            inputs = self.transformer_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
            
            # Fazer a inferência
            with torch.no_grad():
                outputs = self.transformer_model(**inputs)
            
            # Processar os resultados
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            prediction = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][prediction].item()
            
            # Mapear para nossos rótulos (ajustar conforme necessário)
            # O modelo SST-2 usa 0=negativo, 1=positivo
            # Precisamos mapear para nosso esquema: 0=negativo, 1=neutro, 2=positivo
            if prediction == 1:  # positivo no SST-2
                sentiment = "positive"
            else:  # negativo no SST-2
                # Verificar se é muito negativo ou neutro baseado na confiança
                if confidence > 0.8:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                    confidence = 1.0 - confidence  # ajustar confiança para neutro
            
            return sentiment, confidence
        except Exception as e:
            logger.error(f"Erro na análise transformer: {str(e)}")
            return self.analyze_baseline(text)  # fallback para o modelo baseline