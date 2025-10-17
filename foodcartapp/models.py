from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

from collections import defaultdict

class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
        unique=True
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name

class RestaurantMenuItemQuerySet(models.QuerySet):
    def get_restaurants_by_order(self, order_id):
        order = Order.objects.select_related('restaurant').get(pk=order_id)
        if order.restaurant:
            return {order.restaurant}

        product_ids = order.items.all().values_list('product_id', flat=True)
        restaurants = Restaurant.objects.filter(
            menu_items__product_id__in=product_ids,
            menu_items__availability=True
        ).distinct()

        restaurants = restaurants.filter(menu_items__product_id__in=product_ids)

        return set(restaurants)

class RestaurantMenuItem(models.Model):
    objects = RestaurantMenuItemQuerySet.as_manager()
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

class OrderQuerySet(models.QuerySet):
    def with_available_restaurants(self):

        restaurant_menu_items = RestaurantMenuItem.objects.select_related('restaurant', 'product')

        menu_by_restaurant = defaultdict(set)
        for item in restaurant_menu_items:
            menu_by_restaurant[item.restaurant].add(item.product)

        for order in self:
            order_products = set(item.product for item in order.items.all())
            available_restaurants = [
                restaurant for restaurant, products in menu_by_restaurant.items()
                if order_products.issubset(products)
            ]
            order.restaurants = available_restaurants

        return self

class Order(models.Model):
    ORDER_STATUS = {
        ('Done', 'Выполнен'),
        ('In progress', 'В процессе'),
        ('In delivery', 'На доставке'),
        ('Raw', 'Не обработан'),
    }

    PAY_METHODS = {
        ('Cash', 'Наличными'),
        ('Card', 'Картой'),
        ('Online', 'Онлайн'),
    }

    status = models.CharField(
        'статус',
        max_length=20,
        choices=ORDER_STATUS,
        default='Raw',
        db_index=True,
    )
    products = models.ManyToManyField(
        Product,
        through='OrderItem',
        verbose_name='товары',
    )
    firstname = models.CharField(
        'имя',
        max_length=50,
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50,
    )
    phonenumber = PhoneNumberField(
        'номер телефона',
        db_index=True,
    )
    address = models.CharField(
        'адрес доставки',
        max_length=255,
        db_index=True,
    )
    registered_at = models.DateTimeField(
        'дата регистрации',
        db_index=True,
        default=timezone.now,
    )
    called_at = models.DateTimeField(
        'дата звонка',
        db_index=True,
        null=True,
        blank=True,
    )
    delivered_at = models.DateTimeField(
        'дата доставки',
        db_index=True,
        null=True,
        blank=True,
    )
    payment_method = models.CharField(
        'способ оплаты',
        max_length=20,
        choices=PAY_METHODS,
        db_index=True,
    )
    comment = models.TextField(
        'комментарий',
        blank=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name='ресторан',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ №{self.id} ({self.address})'

    
    
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name='заказ',
    )
    product = models.ForeignKey(
        Product,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name='товар',
    )
    quantity = models.PositiveIntegerField(
        'количество',
        validators=[MinValueValidator(1)],
    )

    price = models.DecimalField(
        'цена за единицу',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = 'позиция заказа'
        verbose_name_plural = 'позиции заказа'

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'
