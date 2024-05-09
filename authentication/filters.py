from django_filters import rest_framework as filters

from authentication.models import Account


class BlogPostFilter(filters.FilterSet):
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    first_name = filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='last_name', lookup_expr='icontains')

    class Meta:
        model = Account
        fields = ['email', 'first_name', 'last_name']
