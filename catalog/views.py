from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import inlineformset_factory
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from catalog.forms import ProductForm, VersionForm

from catalog.models import Article, Product, Version, Category
from django.contrib.auth.decorators import login_required, permission_required
from config.settings import CACHE_ENABLED
from django.core.cache import cache


class ProductListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Product
    permission_required = 'catalog.view_product'

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.views_counter += 1
        self.object.save()
        return self.object


    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        attributes_list = None

        if CACHE_ENABLED:
            key = f'attributes_list_{self.object.pk}'
            attributes_list = cache.get(key)
            print('Было Кэше ', attributes_list)

            if attributes_list is None:
                # Создаем словарь с сериализуемыми значениями
                attributes_list = {
                    field.name: str(getattr(self.object, field.name))  # Приводим к строке
                    for field in self.object._meta.get_fields()
                    if isinstance(getattr(self.object, field.name), (str, int, float))  # Проверяем тип
                }
                cache.set(key, attributes_list)
                print('Записали в Кэш ', attributes_list)
        else: 
            attributes_list = {
                field.name: str(getattr(self.object, field.name))  # Приводим к строке
                for field in self.object._meta.get_fields()
                if isinstance(getattr(self.object, field.name), (str, int, float))  # Проверяем тип
            }
            print('Работает без Кэша ', attributes_list)           

        context_data['attributes'] = attributes_list
        return context_data



class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    permission_required = 'catalog.create_product'
    success_url = reverse_lazy('catalog:products_list')

    def form_valid(self, form):
        product = form.save()
        user = self.request.user
        product.creator = user
        product.save()
        return super().form_valid(form)


class ProductUpdateView(PermissionRequiredMixin,
                        LoginRequiredMixin,
                        UpdateView):
    model = Product
    form_class = ProductForm
    #permission_required = 'catalog.change_product'
    permission_required = 'catalog.can_cancel_publish'
    success_url = reverse_lazy('catalog:products_list')

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        ProductFormSet = inlineformset_factory(Product, Version, VersionForm, extra=1)
        if self.request.method == 'POST':
            context_data['formset'] = ProductFormSet(self.request.POST, instance=self.object)
        else:
            context_data['formset'] = ProductFormSet(instance=self.object)
        return context_data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        self.object = form.save()
        if formset.is_valid():
            formset.instance = self.object
            formset.save()
        else:
            return self.form_invalid(form)
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        # Получаем стандартные аргументы формы
        kwargs = super().get_form_kwargs()
        # Добавляем текущего пользователя
        kwargs['user'] = self.request.user
        return kwargs
    




class ProductDeleteView(DeleteView, LoginRequiredMixin):
    model = Product
    success_url = reverse_lazy('catalog:products_list')


class ArticleListView(ListView):
    model = Article
    published_articles = Article.objects.published()

class ArticleDetailView(DetailView):
    model = Article

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.views_counter += 1
        self.object.save()
        return self.object


class ArticleCreateView(CreateView):
    model = Article
    fields = ('title', 'slug', 'content', 'preview', 'published')
    success_url = reverse_lazy('catalog:articles_list')


class ArticleUpdateView(UpdateView):
    model = Article
    fields = ('title', 'slug', 'content', 'preview', 'published')
    success_url = reverse_lazy('catalog:articles_list')

    def get_success_url(self):
        return reverse('catalog:articles_detail', args=[self.kwargs.get('pk')])


class ArticleDeleteView(DeleteView):
    model = Article
    success_url = reverse_lazy('catalog:articles_list')