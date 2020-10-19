from rest_framework import mixins,viewsets
from recipe import serializers
from core.models import Tag,Ingredient
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe

class BaseRecipeAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,mixins.CreateModelMixin):
    """Base class for tag and ıngredient viewsets """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self,serializer):
        """create new tag"""
        serializer.save(user=self.request.user)



class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """manage recipes in the database """
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user= self.request.user).order_by('-id')

    def get_serializer_class(self):
        """return appropirate serializer class """
        if self.action =='retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self,serializer):
        """create a new recipe"""
        serializer.save(user = self.request.user)
