from app.services.news_service import get_exchange_rates, search_news
from app.services.youtube_service import search_google_resources, search_youtube


def run(topic: str) -> dict:
    learning_query = topic or "career growth"
    yt = search_youtube(learning_query, max_results=4)
    google = search_google_resources(f"{learning_query} roadmap course", num=4)
    news = search_news(learning_query, page_size=4)
    exchange = get_exchange_rates(base_currency="USD", symbols="INR,EUR")

    return {
        "youtube": yt,
        "google": google,
        "news": news,
        "exchange": exchange,
    }
