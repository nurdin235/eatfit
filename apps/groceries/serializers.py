from rest_framework import serializers
from .models import GroceryList, GroceryItem

class GroceryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroceryItem
        fields = '__all__'

class GroceryListSerializer(serializers.ModelSerializer):
    items = GroceryItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = GroceryList
        fields = '__all__'
