import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("sentiment-saas.collectors.twitter")

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    logger.warning("Tweepy não está instalado. O coletor do Twitter não estará disponível.")

class TwitterCollector:
    """
    Coletor de dados do Twitter/X usando a API v2
    """
    
    def __init__(self):
        """
        Inicializa o coletor do Twitter.
        As credenciais devem estar disponíveis como variáveis de ambiente:
        - TWITTER_API_KEY
        - TWITTER_API_SECRET
        - TWITTER_ACCESS_TOKEN
        - TWITTER_ACCESS_SECRET
        - TWITTER_BEARER_TOKEN (para API v2)
        """
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """
        Inicializa o cliente da API do Twitter
        """
        if not TWEEPY_AVAILABLE:
            logger.error("Tweepy não está instalado. Não é possível inicializar o cliente.")
            return
            
        try:
            bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
            
            if bearer_token:
                self.client = tweepy.Client(
                    bearer_token=bearer_token,
                    consumer_key=os.getenv("TWITTER_API_KEY"),
                    consumer_secret=os.getenv("TWITTER_API_SECRET"),
                    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                    access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
                    wait_on_rate_limit=True
                )
                logger.info("Cliente do Twitter inicializado com sucesso")
            else:
                logger.error("Token de autenticação do Twitter não encontrado")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente do Twitter: {str(e)}")
    
    def search_recent(self, query: str, max_results: int = 100, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Busca tweets recentes com base em uma query
        
        Args:
            query: Termo de busca
            max_results: Número máximo de resultados
            days_back: Número de dias para trás na busca
            
        Returns:
            Lista de tweets formatados
        """
        if not TWEEPY_AVAILABLE or self.client is None:
            logger.error("Cliente do Twitter não está disponível")
            return self._generate_mock_data(query, max_results)
            
        try:
            # Calcular data de início
            start_time = datetime.utcnow() - timedelta(days=days_back)
            
            # Definir campos para retornar
            tweet_fields = ['created_at', 'public_metrics', 'text', 'author_id']
            user_fields = ['name', 'username', 'profile_image_url']
            expansions = ['author_id']
            
            # Realizar a busca
            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=tweet_fields,
                user_fields=user_fields,
                expansions=expansions,
                start_time=start_time
            )
            
            # Processar resultados
            if not response.data:
                logger.warning(f"Nenhum tweet encontrado para a query: {query}")
                return []
                
            # Criar um dicionário de usuários para fácil acesso
            users = {user.id: user for user in response.includes['users']} if 'users' in response.includes else {}
            
            # Formatar os tweets
            formatted_tweets = []
            for tweet in response.data:
                author = users.get(tweet.author_id)
                
                tweet_data = {
                    'platform': 'twitter',
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'author': {
                        'id': tweet.author_id,
                        'username': author.username if author else None,
                        'name': author.name if author else None,
                        'profile_image': author.profile_image_url if author else None
                    },
                    'metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else {},
                    'url': f"https://twitter.com/user/status/{tweet.id}"
                }
                
                formatted_tweets.append(tweet_data)
                
            return formatted_tweets
            
        except Exception as e:
            logger.error(f"Erro ao buscar tweets: {str(e)}")
            return self._generate_mock_data(query, max_results)
    
    def _generate_mock_data(self, query: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Gera dados simulados para demonstração quando a API não está disponível
        
        Args:
            query: Termo de busca
            count: Número de tweets simulados
            
        Returns:
            Lista de tweets simulados
        """
        logger.info(f"Gerando {count} tweets simulados para a query: {query}")
        
        mock_tweets = []
        current_time = datetime.utcnow()
        
        # Templates de tweets positivos, negativos e neutros
        positive_templates = [
            f"Adorei o produto da {query}! Superou minhas expectativas. #satisfeito",
            f"A {query} tem o melhor atendimento que já vi. Recomendo! #clientesatisfeito",
            f"Acabei de comprar na {query} e foi uma experiência incrível! #recomendo",
            f"Os produtos da {query} são de excelente qualidade. Vale cada centavo!",
            f"A {query} resolveu meu problema rapidamente. Atendimento nota 10!"
        ]
        
        negative_templates = [
            f"Decepcionado com a {query}. Produto de baixa qualidade. #nãorecomendo",
            f"Péssimo atendimento da {query}. Nunca mais compro lá. #insatisfeito",
            f"A {query} demorou muito para entregar meu pedido. Muito insatisfeito.",
            f"Produto da {query} quebrou no primeiro uso. Decepcionante!",
            f"Experiência terrível com a {query}. Não recomendem! #decepção"
        ]
        
        neutral_templates = [
            f"Alguém já comprou na {query}? Estou pensando em fazer um pedido.",
            f"A {query} lançou novos produtos hoje. Alguém já testou?",
            f"Comparando preços entre a {query} e concorrentes. Dicas?",
            f"Vi uma propaganda da {query} hoje. Parece interessante.",
            f"A {query} está com promoção este fim de semana. #informação"
        ]
        
        # Gerar tweets simulados
        for i in range(count):
            # Escolher aleatoriamente entre positivo, negativo e neutro
            sentiment_type = i % 3  # 0: positivo, 1: negativo, 2: neutro
            
            if sentiment_type == 0:
                text = positive_templates[i % len(positive_templates)]
            elif sentiment_type == 1:
                text = negative_templates[i % len(negative_templates)]
            else:
                text = neutral_templates[i % len(neutral_templates)]
                
            # Criar tweet simulado
            tweet = {
                'platform': 'twitter',
                'id': f"mock_{i}",
                'text': text,
                'created_at': current_time - timedelta(hours=i),
                'author': {
                    'id': f"user_{i}",
                    'username': f"user{i}",
                    'name': f"Usuário {i}",
                    'profile_image': "https://via.placeholder.com/48"
                },
                'metrics': {
                    'retweet_count': i * 2,
                    'reply_count': i,
                    'like_count': i * 5,
                    'quote_count': i // 2
                },
                'url': f"https://twitter.com/user/status/mock_{i}"
            }
            
            mock_tweets.append(tweet)
            
        return mock_tweets