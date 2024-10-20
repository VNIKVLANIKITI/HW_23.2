from .models import Category
from config.settings import CACHE_ENABLED
from django.core.cache import cache

# Функция выборки Категорий
def get_category_all():
    #from models import Category
    categories = []
    # Проверяем включени ли Кэш
    if CACHE_ENABLED:
        categories = cache.get('categories')
        print('Было Кэше ', categories)

        if categories is None:
            categories = []
            # Получим категории из БД
            rows = Category.objects.all()
            for row in rows:
                row_item = []
                row_item.append(row.id)
                row_item.append(row.title)
                categories.append(row_item)
            cache.set('categories', categories)
            print('Записали в Кэш ', categories)
    else:
        # Получим категории из БД
        rows = Category.objects.all()
        for row in rows:
            row_item = []
            row_item.append(row.id)
            row_item.append(row.title)
            categories.append(row_item)
        print('Работает без Кэша ', categories)           
    return categories