from rest_framework import serializers
from core.models import Tag,Ingredient,Recipe


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','name']
        read_only_fields = ['id']




class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for an ingredient object"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """serialize the recipe object"""

    ingredients = serializers.PrimaryKeyRelatedField(
    many=True,
    queryset = Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
    many=True,
    queryset = Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id','title','price','time_minutes','ingredients','tags','link')
        read_only_fields=('id',)

class RecipeDetailSerializer(RecipeSerializer):
    """serialize the recipe detail"""
    ingredients  =IngredientSerializer(many=True,read_only=True)
    tags = TagSerializer(many=True,read_only=True)
